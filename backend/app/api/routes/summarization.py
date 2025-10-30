from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
import google.generativeai as genai
from PIL import Image
import io

from app.core.database import get_db
from app.models.document import Document, ProcessingStatus
from app.schemas.summary import SummaryRequest, SummaryResponse
from app.services.ai_engine.llm_client import get_llm_client, LLMClient
from app.services.ai_engine.prompts import build_summary_prompt, SYSTEM_PROMPT
from app.services.summarization.chunking import intelligent_chunk_text
from app.config import settings

# Configure Gemini for Vision
if hasattr(settings, 'gemini_api_key') and settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)
    vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    vision_model = None

# Pydantic models for request bodies


class ProblemRequest(BaseModel):
    problem: str
    type: str = "doubt"


router = APIRouter()

# ==================== UPLOAD ENDPOINTS ====================


@router.post("/test-upload")
async def test_upload(
    file: UploadFile = File(...)
):
    """
    Simple test upload endpoint without authentication
    """
    try:
        contents = await file.read()

        return {
            "id": 1,
            "document_id": 1,
            "filename": file.filename,
            "size": len(contents),
            "message": "File uploaded successfully (test mode)"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


# ==================== PROBLEM SOLVING ====================



@router.post("/solve")
async def solve_problem(
    request: ProblemRequest,
    llm: LLMClient = Depends(get_llm_client)
):
    """
    Solve a problem or explain a concept

    - **problem**: The problem or concept to explain
    - **type**: Type of problem (doubt, math, or general)
    """
    try:
        problem = request.problem.strip()
        problem_type = request.type

        if not problem:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Problem description is required"
            )

        print(f"Solving {problem_type} problem: {problem[:100]}...")

        # Build appropriate prompt based on problem type
        if problem_type == "doubt":
            prompt = f"""A student is struggling with the following concept or problem:

{problem}

Please provide a comprehensive educational response:

1. **Concept Explanation**: Clear explanation of the underlying concept
2. **Step-by-Step Solution**: Detailed solution if applicable
3. **Common Mistakes**: What students often get wrong
4. **Memory Tips**: How to remember this concept
5. **Practice**: Suggest related practice problems or concepts

Be encouraging and educational."""

        elif problem_type == "math":
            prompt = f"""Solve this math problem with detailed explanation:

Problem: {problem}

Please provide:
1. **Understanding**: What the problem is asking
2. **Approach**: Best method to solve it
3. **Step-by-Step Solution**: Show all work clearly
4. **Verification**: Check the answer
5. **Similar Problems**: Suggest practice problems

Show all calculations and explain your reasoning."""

        else:  # general
            prompt = f"""Help explain or solve the following:

{problem}

Provide:
1. Clear explanation or solution
2. Relevant examples
3. Key points to remember
4. Additional resources or topics to explore

Be thorough and educational."""

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        solution = await llm.generate_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=2000
        )

        print(
            f"Solution generated successfully, length: {len(solution)} chars")

        return {
            "problem": problem,
            "problem_type": problem_type,
            "solution": solution,
            "word_count": len(solution.split()),
            "message": "Problem solved successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in solve_problem: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Problem solving failed: {str(e)}"
        )

# ==================== SUMMARIZATION ENDPOINTS ====================


@router.post("/{document_id}", response_model=SummaryResponse)
async def generate_summary(
    document_id: int,
    summary_request: SummaryRequest,
    db: AsyncSession = Depends(get_db),
    llm: LLMClient = Depends(get_llm_client)
):
    """
    Generate a summary of a document (NO AUTHENTICATION for testing)

    - **document_id**: ID of the document to summarize
    - **level**: Summary level (brief, moderate, detailed)
    - **focus_areas**: Optional list of topics to focus on
    """
    try:
        # Get document WITHOUT authentication check
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )

        # Check document status
        if document.processing_status != ProcessingStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Document is still {document.processing_status.value}. Please wait for processing to complete."
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
            print(
                f"Text too long ({len(text_to_summarize)} chars), chunking...")

            # Chunk the text
            chunks = intelligent_chunk_text(
                text_to_summarize, max_chunk_size=3000)
            print(f"Created {len(chunks)} chunks")

            # Summarize each chunk
            chunk_summaries = []
            for i, chunk in enumerate(chunks[:5]):  # Limit to first 5 chunks
                print(f"Summarizing chunk {i+1}/{min(len(chunks), 5)}...")

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
            print(
                f"Combined chunk summaries, final length: {len(text_to_summarize)} chars")

        # Generate final summary
        print(f"Generating final summary with level: {summary_request.level}")
        prompt = build_summary_prompt(text_to_summarize, summary_request.level)

        # Add focus areas if specified
        if summary_request.focus_areas:
            focus_text = ", ".join(summary_request.focus_areas)
            prompt += f"\n\nPay special attention to these topics: {focus_text}"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        summary = await llm.generate_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=1500
        )

        print(f"Summary generated successfully, length: {len(summary)} chars")

        # Update document summary count
        document.summary_count += 1
        await db.commit()

        return SummaryResponse(
            document_id=document_id,
            summary=summary,
            level=summary_request.level,
            word_count=len(summary.split()),
            original_length=document.text_length if document.text_length else len(
                document.extracted_text)
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in generate_summary: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )


@router.post("/{document_id}/key-points")
async def extract_key_points(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    llm: LLMClient = Depends(get_llm_client)
):
    """
    Extract key points and concepts from a document (NO AUTHENTICATION for testing)
    """
    try:
        # Get document
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document with ID {document_id} not found"
            )

        if not document.extracted_text:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No text available for key point extraction"
            )

        # Generate key points (limit text to avoid token limits)
        text_sample = document.extracted_text[:4000]

        prompt = f"""Extract the key points, concepts, and important information from this study material.

Material:
{text_sample}

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

        key_points = await llm.generate_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )

        return {
            "document_id": document_id,
            "key_points": key_points,
            "success": True
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in extract_key_points: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Key point extraction failed: {str(e)}"
        )


# ==================== IMAGE ANALYSIS (FIXED WITH GEMINI VISION) ====================

@router.post("/image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an image containing problems, diagrams, or notes using Gemini Vision
    """
    if not vision_model:
        raise HTTPException(
            status_code=503,
            detail="Image analysis not configured. Please add GEMINI_API_KEY to .env file"
        )
    
    try:
        # Read image file
        contents = await file.read()
        
        # Validate file size (max 10MB)
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        print(f"Analyzing image: {file.filename} ({len(contents)} bytes)")
        
        # Open and process image with PIL
        try:
            image = Image.open(io.BytesIO(contents))
            
            # Convert RGBA to RGB if necessary
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            elif image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
                
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image file: {str(e)}"
            )
        
        # Create comprehensive prompt for study assistance
        prompt = """You are an AI study assistant. Analyze this image carefully and provide a comprehensive response.

If the image contains:
1. **Math Problems**: Solve them step-by-step with clear explanations for each step
2. **Questions/Text**: Read and answer thoroughly with detailed explanations
3. **Diagrams/Charts**: Explain what they represent, their components, and significance
4. **Scientific Concepts**: Explain the concepts, formulas, or processes shown
5. **Handwritten Notes**: Read, transcribe, and explain the content
6. **Code**: Explain what the code does and any issues

Format your response with:
- **What I see**: Brief description of image content
- **Detailed Analysis**: Step-by-step solutions or thorough explanations
- **Key Concepts**: Important takeaways or concepts involved
- **Answer/Solution**: Clear final answer if applicable

Be thorough, educational, and easy to understand."""

        # Generate response using Gemini Vision
        response = vision_model.generate_content([prompt, image])
        
        if not response or not response.text:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate analysis from image"
            )
        
        return {
            "filename": file.filename,
            "file_size": len(contents),
            "content_type": file.content_type,
            "analysis": response.text,
            "message": "Image analyzed successfully with Gemini Vision"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze_image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {str(e)}"
        )


# ==================== AUDIO TRANSCRIPTION ====================

@router.post("/audio")
async def transcribe_audio(
    file: UploadFile = File(...),
    llm: LLMClient = Depends(get_llm_client)
):
    """
    Transcribe and summarize audio content
    """
    try:
        # Read audio file
        contents = await file.read()

        # Validate file type
        valid_audio_types = ['audio/mpeg', 'audio/mp3',
                             'audio/wav', 'audio/m4a', 'audio/webm']
        if not file.content_type or file.content_type not in valid_audio_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File must be an audio file. Supported: {', '.join(valid_audio_types)}"
            )

        print(f"Processing audio: {file.filename} ({len(contents)} bytes)")

        # Note: For actual audio transcription, integrate Whisper API or similar
        # This is a placeholder
        prompt = """Provide a structured transcription summary:

1. Full Transcription: [Transcribed text would go here]
2. Key Points: [Main topics discussed]
3. Summary: [Brief overview]
4. Action Items: [Any tasks or important notes]

Note: Integrate Whisper API or Google Speech-to-Text for actual transcription."""

        messages = [
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": prompt}
        ]

        transcription = await llm.generate_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=1500
        )

        return {
            "filename": file.filename,
            "file_size": len(contents),
            "content_type": file.content_type,
            "transcription": transcription,
            "message": "Audio processed (Note: Using placeholder - integrate Whisper API for real transcription)"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in transcribe_audio: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio processing failed: {str(e)}"
        )