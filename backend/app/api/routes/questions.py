# app/api/routes/questions.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
import os
import shutil
from datetime import datetime
from pathlib import Path

from app.core.database import get_db
from app.models.question import Question
from app.models.user import User
from app.api.deps import get_current_user  # Use existing function
from app.services.image_processor import ImageProcessor
from app.services.ai_solver import AISolver
from app.schemas.question import QuestionResponse, QuestionListResponse

router = APIRouter()
image_processor = ImageProcessor()
ai_solver = AISolver()

UPLOAD_DIR = Path("uploads/images")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="File must be an image (JPEG, PNG, GIF, etc.)"
        )
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )


@router.post("/upload", response_model=QuestionResponse)
async def upload_question(
    file: UploadFile = File(...),
    subject: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a question image and get AI-generated solution."""
    validate_image_file(file)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = Path(file.filename).suffix
    filename = f"{current_user.id}_{timestamp}{file_ext}"
    filepath = UPLOAD_DIR / filename
    
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_SIZE:
            os.remove(filepath)
            raise HTTPException(
                status_code=400,
                detail=f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum allowed size (10MB)"
            )
        
        extracted_text = await image_processor.extract_text(str(filepath))
        
        if not extracted_text or len(extracted_text.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Could not extract any text from the image. Please ensure the image contains a clear question."
            )
        
        is_valid, detected_subject = await ai_solver.validate_question(extracted_text)
        
        if not is_valid:
            os.remove(filepath)
            raise HTTPException(
                status_code=400,
                detail="This doesn't appear to be an academic or study-related question. Please upload educational content only."
            )
        
        final_subject = subject or detected_subject
        
        solution_data = await ai_solver.solve_question(
            image_path=str(filepath),
            question_text=extracted_text,
            subject=final_subject
        )
        
        question = Question(
            user_id=current_user.id,
            image_path=str(filepath.relative_to(Path.cwd())),
            question_text=extracted_text,
            subject=final_subject,
            solution=solution_data["answer"],
            explanation=solution_data.get("explanation", ""),
            steps=solution_data.get("steps", []),
            confidence_score=solution_data.get("confidence", 0.85),
            difficulty_level=solution_data.get("difficulty", "medium")
        )
        
        db.add(question)
        await db.commit()
        await db.refresh(question)
        
        return question
        
    except HTTPException:
        raise
    except Exception as e:
        if filepath.exists():
            os.remove(filepath)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@router.get("/history", response_model=QuestionListResponse)
async def get_question_history(
    skip: int = 0,
    limit: int = 20,
    subject: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's question history with pagination and filtering."""
    query = select(Question).where(Question.user_id == current_user.id)
    
    if subject:
        query = query.where(Question.subject == subject)
    
    query = query.order_by(desc(Question.created_at)).offset(skip).limit(limit)
    
    result = await db.execute(query)
    questions = result.scalars().all()
    
    count_query = select(Question).where(Question.user_id == current_user.id)
    if subject:
        count_query = count_query.where(Question.subject == subject)
    
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())
    
    return {
        "questions": questions,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific question by ID"""
    result = await db.execute(
        select(Question).where(
            Question.id == question_id,
            Question.user_id == current_user.id
        )
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.delete("/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a question and its associated image"""
    result = await db.execute(
        select(Question).where(
            Question.id == question_id,
            Question.user_id == current_user.id
        )
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    image_path = Path(question.image_path)
    if image_path.exists():
        os.remove(image_path)
    
    await db.delete(question)
    await db.commit()
    
    return {"message": "Question deleted successfully", "id": question_id}


@router.get("/subjects/list")
async def list_subjects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of all subjects from user's questions"""
    result = await db.execute(
        select(Question.subject).where(
            Question.user_id == current_user.id
        ).distinct()
    )
    subjects = result.scalars().all()
    
    return {"subjects": subjects}
