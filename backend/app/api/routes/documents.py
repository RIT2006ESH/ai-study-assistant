"""
Document management routes: upload, list, view, delete
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.document import Document, DocumentType, ProcessingStatus
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.config import settings
from app.utils.file_handlers import save_upload_file, get_file_type, validate_file
from app.services.document_processing.pdf_processor import process_pdf
from app.services.document_processing.docx_processor import process_docx

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a document for processing
    
    - **file**: Document file (PDF, DOCX, TXT, etc.)
    - **title**: Optional custom title (defaults to filename)
    - **subject**: Optional subject classification
    """
    # Validate file
    try:
        validate_file(file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Determine document type
    doc_type = get_file_type(file.filename)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Save file
    file_path = await save_upload_file(file, unique_filename)
    file_size = os.path.getsize(file_path)
    
    # Create document record
    document = Document(
        user_id=user_id,
        title=title or file.filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=file_size,
        document_type=doc_type,
        mime_type=file.content_type or "application/octet-stream",
        processing_status=ProcessingStatus.PENDING,
    )
    
    if subject:
        document.subject = subject
    
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # Trigger background processing (we'll implement Celery tasks later)
    # For now, process synchronously for simple files
    try:
        if doc_type == DocumentType.PDF:
            extracted_text = await process_pdf(file_path)
            document.extracted_text = extracted_text
            document.text_length = len(extracted_text)
            document.processing_status = ProcessingStatus.COMPLETED
            document.processed_at = datetime.utcnow()
        elif doc_type == DocumentType.DOCX:
            extracted_text = await process_docx(file_path)
            document.extracted_text = extracted_text
            document.text_length = len(extracted_text)
            document.processing_status = ProcessingStatus.COMPLETED
            document.processed_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(document)
    except Exception as e:
        document.processing_status = ProcessingStatus.FAILED
        document.processing_error = str(e)
        await db.commit()
    
    return DocumentResponse.from_orm(document)


@router.get("/", response_model=List[DocumentListResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    subject: Optional[str] = None,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    List all documents for the current user
    
    - **skip**: Number of documents to skip (pagination)
    - **limit**: Maximum number of documents to return
    - **subject**: Filter by subject
    """
    query = select(Document).where(Document.user_id == user_id)
    
    if subject:
        query = query.where(Document.subject == subject)
    
    query = query.order_by(desc(Document.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [DocumentListResponse.from_orm(doc) for doc in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific document by ID
    """
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Increment view count
    document.view_count += 1
    await db.commit()
    await db.refresh(document)
    
    return DocumentResponse.from_orm(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a document
    """
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete physical file
    if os.path.exists(document.file_path):
        os.remove(document.file_path)
    
    # Delete from database
    await db.delete(document)
    await db.commit()
    
    return None


@router.get("/{document_id}/text")
async def get_document_text(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """
    Get extracted text from a document
    """
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    if document.processing_status != ProcessingStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Document is still {document.processing_status.value}"
        )
    
    return {
        "document_id": document.id,
        "title": document.title,
        "text": document.extracted_text,
        "text_length": document.text_length,
        "page_count": document.page_count
    }