"""
Summarization routes for generating document summaries
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.document import Document, ProcessingStatus
from app.schemas.summary import SummaryRequest, SummaryResponse
from app.services.ai_engine.llm_client import get_llm_client, LLMClient
from app.services.ai_engine.prompts import build_summary_prompt, SYSTEM_PROMPT
from app.services.summarization.chunking import intelligent_chunk_text

router = APIRouter()


@router.post("/{document_id}", response_model=SummaryResponse)
async def generate_summary(
    document_id: int,
    summary_request: SummaryRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    llm: LLMClient = Depends(get_llm_client)
):
    """
    Generate a summary of a document
    
    - **document_id**: ID of the document to summarize
    - **level**: Summary level (brief, moderate, detailed)
    - **focus_areas**: Optional list of topics to focus on
    """
    # Get document
    result = await db.execute(
        select(Document).where(
            and_(
                Document.id == document_id,
                Document.user_id == user_id
            )
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
    
    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text content available for summarization"
        )
    
    # Prepare text for summarization
    text_to_summarize = document.extracted_text
    
    # If text is too long, chunk it and summarize chunks first
    max_length = 8000  # Approximate token limit
    if len(text_to_summarize) > max_length:
        # Chunk the text
        chunks = intelligent_chunk_text(text_to_summarize, max_chunk_size=3000)
        
        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks[:5]:  # Limit to first 5 chunks for now
            prompt = build_summary_prompt(chunk, summary_request.level)
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            chunk_summary = await llm.generate_completion(
                messages=messages,
                temperature=0.5,
                max_tokens=800
            )
            chunk_summaries.append(chunk_summary)
        
        # Combine chunk summaries
        text_to_summarize = "\n\n".join(chunk_summaries)
    
    # Generate final summary
    prompt = build_summary_prompt(text_to_summarize, summary_request.level)
    
    # Add focus areas if specified
    if summary_request.focus_areas:
        focus_text = ", ".join(summary_request.focus_areas)
        prompt += f"\n\nPay special attention to these topics: {focus_text}"
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    try:
        summary = await llm.generate_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=1500
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )
    
    # Update document summary count
    document.summary_count += 1
    await db.commit()
    
    return SummaryResponse(
        document_id=document_id,
        summary=summary,
        level=summary_request.level,
        word_count=len(summary.split()),
        original_length=document.text_length
    )


@router.post("/{document_id}/key-points")
async def extract_key_points(
    document_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
    llm: LLMClient = Depends(get_llm_client)
):
    """
    Extract key points and concepts from a document
    """
    # Get document
    result = await db.execute(
        select(Document).where(
            and_(
                Document.id == document_id,
                Document.user_id == user_id
            )
        )
    )
    document = result.scalar_one_or_none()
    
    if not document or not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or no text available"
        )
    
    # Generate key points
    prompt = f"""Extract the key points, concepts, and important information from this study material.

Material:
{document.extracted_text[:4000]}

Provide:
1. Main concepts (bullet points)
2. Important definitions
3. Key formulas or equations (if any)
4. Critical facts to remember

Format as structured bullet points."""
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    try:
        key_points = await llm.generate_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key point extraction failed: {str(e)}"
        )
    
    return {
        "document_id": document_id,
        "key_points": key_points
    }