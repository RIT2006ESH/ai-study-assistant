"""
Question Analysis Routes
Handles image-based question analysis and text extraction
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from PIL import Image
import io
import re
import json
from datetime import datetime
from typing import Optional
import logging

from app.core.database import get_db
from app.models.models import User, QuestionHistory
from app.core.security import get_current_user_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/question-analysis")


# Helper function to get current user
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from user_id"""
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Academic keywords for filtering
ACADEMIC_KEYWORDS = [
    'solve', 'calculate', 'prove', 'explain', 'derive', 'find', 'evaluate',
    'analyze', 'compare', 'describe', 'define', 'theorem', 'equation',
    'formula', 'problem', 'question', 'what', 'how', 'why', 'when',
    'integrate', 'differentiate', 'factor', 'simplify', 'determine',
    'compute', 'verify', 'demonstrate', 'show', 'illustrate', 'given'
]

SUBJECT_KEYWORDS = {
    'mathematics': ['equation', 'integral', 'derivative', 'matrix', 'polynomial', 
                   'geometry', 'algebra', 'calculus', 'trigonometry', 'graph'],
    'physics': ['force', 'velocity', 'acceleration', 'energy', 'momentum', 
               'quantum', 'motion', 'mass', 'speed', 'newton'],
    'chemistry': ['molecule', 'atom', 'reaction', 'compound', 'element', 
                 'bond', 'solution', 'chemical', 'mole', 'acid'],
    'biology': ['cell', 'organism', 'protein', 'dna', 'gene', 
               'species', 'evolution', 'tissue', 'enzyme'],
    'computer_science': ['algorithm', 'code', 'function', 'data structure', 
                        'complexity', 'programming', 'loop', 'array']
}


def is_academic_query(text: str) -> tuple[bool, str]:
    """Check if the extracted text is an academic question"""
    text_lower = text.lower()
    has_keywords = any(keyword in text_lower for keyword in ACADEMIC_KEYWORDS)
    has_math_symbols = bool(re.search(r'[\+\-\*\/\=\^\(\)\[\]{}∫∑√π≤≥≠±×÷]', text))
    has_question = '?' in text or any(word in text_lower.split()[:3] for word in ['solve', 'find', 'calculate', 'prove'])
    word_count = len(text.split())
    
    if word_count < 3:
        return False, "Text too short to be a valid question"
    if not (has_keywords or has_math_symbols or has_question):
        return False, "No academic keywords, math symbols, or question markers found"
    return True, "Valid academic content detected"


def detect_subject(text: str) -> str:
    """Detect the subject area of the question"""
    text_lower = text.lower()
    subject_scores = {}
    for subject, keywords in SUBJECT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        subject_scores[subject] = score
    if max(subject_scores.values()) > 0:
        return max(subject_scores, key=subject_scores.get)
    return "general"


async def extract_text_from_image(image: Image.Image) -> str:
    """Extract text from image using Gemini Vision"""
    try:
        from app.services.gemini_service import gemini_service
        prompt = """Extract all text from this image accurately. 
        If it's a question, extract it exactly as written including:
        - Question numbers
        - All mathematical symbols and equations  
        - Diagrams descriptions (if any)
        - Multiple choice options (if any)
        
        Provide only the extracted text without any additional commentary."""
        extracted_text = await gemini_service.extract_text(image, prompt)
        return extracted_text.strip()
    except ImportError:
        raise HTTPException(status_code=503, detail="Gemini service not configured. Please set GEMINI_API_KEY.")
    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")


async def generate_solution(question_text: str, subject: str = "general") -> dict:
    """Generate step-by-step solution using Gemini AI"""
    try:
        from app.services.gemini_service import gemini_service
        subject_context = {
            "mathematics": "You are an expert mathematics tutor. Focus on mathematical rigor and clear algebraic steps.",
            "physics": "You are an expert physics tutor. Include relevant formulas, units, and physical intuition.",
            "chemistry": "You are an expert chemistry tutor. Include chemical equations, reactions, and molecular concepts.",
            "biology": "You are an expert biology tutor. Include scientific terminology and biological processes.",
            "computer_science": "You are an expert computer science tutor. Include code examples and algorithmic thinking.",
            "general": "You are an expert academic tutor across all subjects."
        }
        context = subject_context.get(subject, subject_context["general"])
        prompt = f"""{context}

Analyze this academic question and provide a comprehensive solution:

Question: {question_text}

Provide your response in valid JSON format with the following structure:
{{
    "understanding": "Brief 2-3 sentence explanation of what the problem is asking",
    "steps": [
        {{
            "title": "Clear step title",
            "content": "Detailed explanation with all work shown"
        }}
    ],
    "final_answer": "The complete final answer with units if applicable",
    "verification": "Verification or proof of the answer (if applicable)",
    "related_concepts": ["concept1", "concept2", "concept3"],
    "difficulty_level": "beginner|intermediate|advanced",
    "estimated_time": "estimated time to solve in minutes"
}}

Important guidelines:
- Break down the solution into clear, logical steps (3-8 steps typically)
- Explain each step thoroughly with reasoning
- Show ALL mathematical work and calculations
- Use proper notation and formatting
- Provide verification when possible
- List 3-5 related concepts students should understand
- Be precise and accurate
- If the question is ambiguous, state assumptions clearly

Respond ONLY with the JSON object, no additional text."""

        response = await gemini_service.generate_content(prompt)
        result_text = response.strip()
        
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        try:
            solution = json.loads(result_text)
            required_fields = ["understanding", "steps", "final_answer"]
            for field in required_fields:
                if field not in solution:
                    raise ValueError(f"Missing required field: {field}")
            solution.setdefault("verification", "")
            solution.setdefault("related_concepts", [])
            solution.setdefault("difficulty_level", "intermediate")
            solution.setdefault("estimated_time", "15-20")
            return solution
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return {
                "understanding": "Solution provided by AI",
                "steps": [{"title": "Complete Solution", "content": result_text}],
                "final_answer": "Please refer to the detailed solution above",
                "verification": "",
                "related_concepts": ["Problem Solving"],
                "difficulty_level": "intermediate",
                "estimated_time": "15-20"
            }
    except ImportError:
        raise HTTPException(status_code=503, detail="Gemini service not configured. Please set GEMINI_API_KEY.")
    except Exception as e:
        logger.error(f"Error generating solution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate solution: {str(e)}")


@router.post("/analyze-image")
async def analyze_question_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze an uploaded question image using Gemini Vision AI"""
    try:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image size must be less than 10MB")
        image = Image.open(io.BytesIO(contents))
        logger.info(f"Extracting text from image for user {current_user.id}")
        extracted_text = await extract_text_from_image(image)
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Could not extract text from image")
        logger.info(f"Extracted text: {extracted_text[:100]}...")
        is_academic, reason = is_academic_query(extracted_text)
        if not is_academic:
            return JSONResponse(status_code=400, content={
                "error": "non_academic",
                "message": "This doesn't appear to be an academic question. Please upload a question from your textbook or notes.",
                "extracted_text": extracted_text,
                "reason": reason
            })
        subject = detect_subject(extracted_text)
        logger.info(f"Generating solution for question in {subject}")
        solution = await generate_solution(extracted_text, subject)
        question_record = QuestionHistory(
            user_id=current_user.id,
            question_text=extracted_text,
            subject=subject,
            solution=json.dumps(solution),
            image_filename=file.filename,
            created_at=datetime.utcnow()
        )
        db.add(question_record)
        await db.commit()
        await db.refresh(question_record)
        return {
            "success": True,
            "extracted_text": extracted_text,
            "subject": subject,
            "solution": solution,
            "timestamp": datetime.utcnow().isoformat(),
            "question_id": question_record.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")


@router.post("/analyze-text")
async def analyze_text_question(
    question_data: dict = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyze a text-based question without image upload"""
    try:
        question_text = question_data.get("text", "").strip()
        if not question_text:
            raise HTTPException(status_code=400, detail="Question text is required")
        is_academic, reason = is_academic_query(question_text)
        if not is_academic:
            return JSONResponse(status_code=400, content={
                "error": "non_academic",
                "message": "This doesn't appear to be an academic question.",
                "reason": reason
            })
        subject = detect_subject(question_text)
        logger.info(f"Generating solution for text question in {subject}")
        solution = await generate_solution(question_text, subject)
        question_record = QuestionHistory(
            user_id=current_user.id,
            question_text=question_text,
            subject=subject,
            solution=json.dumps(solution),
            created_at=datetime.utcnow()
        )
        db.add(question_record)
        await db.commit()
        await db.refresh(question_record)
        return {
            "success": True,
            "subject": subject,
            "solution": solution,
            "timestamp": datetime.utcnow().isoformat(),
            "question_id": question_record.id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing text question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_question_history(
    limit: int = 20,
    offset: int = 0,
    subject: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's question history with optional filtering"""
    try:
        query = select(QuestionHistory).where(QuestionHistory.user_id == current_user.id)
        if subject:
            query = query.where(QuestionHistory.subject == subject)
        query = query.order_by(QuestionHistory.created_at.desc()).limit(limit).offset(offset)
        result = await db.execute(query)
        questions = result.scalars().all()
        return {
            "success": True,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "subject": q.subject,
                    "created_at": q.created_at.isoformat(),
                    "has_image": bool(q.image_filename)
                }
                for q in questions
            ],
            "total": len(questions)
        }
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{question_id}")
async def get_question_detail(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific question"""
    try:
        query = select(QuestionHistory).where(
            QuestionHistory.id == question_id,
            QuestionHistory.user_id == current_user.id
        )
        result = await db.execute(query)
        question = result.scalar_one_or_none()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return {
            "success": True,
            "question": {
                "id": question.id,
                "question_text": question.question_text,
                "subject": question.subject,
                "solution": json.loads(question.solution),
                "image_filename": question.image_filename,
                "created_at": question.created_at.isoformat()
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching question detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{question_id}")
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a question from history"""
    try:
        query = select(QuestionHistory).where(
            QuestionHistory.id == question_id,
            QuestionHistory.user_id == current_user.id
        )
        result = await db.execute(query)
        question = result.scalar_one_or_none()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        await db.delete(question)
        await db.commit()
        return {"success": True, "message": "Question deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
