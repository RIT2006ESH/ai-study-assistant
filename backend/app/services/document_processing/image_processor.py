import google.generativeai as genai
from PIL import Image
import os
from typing import Optional, Dict
from app.config import settings


async def process_image(file_path: str) -> str:
    """
    Extract text from an image using Google Gemini Vision API
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Extracted text content
        
    Raises:
        Exception: If image processing fails
    """
    try:
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        
        # Load image
        image = Image.open(file_path)
        
        # Use Gemini 2.0 Flash with vision capabilities
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Extract text from image
        prompt = "Extract all text from this image accurately. If there are mathematical equations, formulas, or diagrams, describe them in detail."
        
        response = model.generate_content([prompt, image])
        
        extracted_text = response.text
        
        if not extracted_text.strip():
            raise ValueError("No text could be extracted from the image")
        
        return extracted_text
        
    except Exception as e:
        raise Exception(f"Image processing failed: {str(e)}")


async def solve_problem_from_image(file_path: str, problem_type: Optional[str] = None) -> Dict[str, str]:
    """
    Solve a problem shown in an image (math, physics, chemistry, etc.)
    
    Args:
        file_path: Path to the image file
        problem_type: Optional type of problem (math, physics, chemistry, etc.)
        
    Returns:
        Dictionary with extracted_text and solution
        
    Raises:
        Exception: If problem solving fails
    """
    try:
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        
        # Load image
        image = Image.open(file_path)
        
        # Use Gemini 2.0 Flash with vision capabilities
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Create problem-solving prompt
        if problem_type:
            prompt = f"""This image contains a {problem_type} problem. Please:
1. First, extract and clearly state the problem
2. Identify what is being asked
3. Provide a detailed, step-by-step solution
4. Show all work and calculations
5. Explain the reasoning behind each step
6. Provide the final answer

Be thorough and educational in your explanation."""
        else:
            prompt = """This image contains a problem or question. Please:
1. First, extract and clearly state the problem/question
2. Identify the subject area (math, physics, chemistry, etc.)
3. Identify what is being asked
4. Provide a detailed, step-by-step solution
5. Show all work and calculations
6. Explain the reasoning behind each step
7. Provide the final answer

Be thorough and educational in your explanation."""
        
        response = model.generate_content([prompt, image])
        
        solution = response.text
        
        if not solution.strip():
            raise ValueError("Could not generate a solution for the problem")
        
        # Also extract just the text/problem statement
        extract_prompt = "Extract only the problem statement or question from this image, without solving it."
        extract_response = model.generate_content([extract_prompt, image])
        extracted_text = extract_response.text
        
        return {
            "extracted_text": extracted_text,
            "solution": solution,
            "problem_type": problem_type or "general"
        }
        
    except Exception as e:
        raise Exception(f"Problem solving failed: {str(e)}")


async def analyze_diagram(file_path: str) -> str:
    """
    Analyze and describe a diagram or figure from an image
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Description of the diagram
        
    Raises:
        Exception: If diagram analysis fails
    """
    try:
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        
        # Load image
        image = Image.open(file_path)
        
        # Use Gemini 2.0 Flash with vision capabilities
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = """Analyze this diagram or figure and provide a detailed description including:
1. What type of diagram it is (flowchart, graph, circuit, etc.)
2. The main components or elements
3. The relationships or connections between elements
4. Any labels, annotations, or key information
5. The overall purpose or what it represents

Be thorough and educational in your description."""
        
        response = model.generate_content([prompt, image])
        
        description = response.text
        
        return description
        
    except Exception as e:
        raise Exception(f"Diagram analysis failed: {str(e)}")


async def get_image_metadata(file_path: str) -> dict:
    """
    Extract metadata from an image file
    
    Args:
        file_path: Path to the image file
        
    Returns:
        Dictionary containing image metadata
    """
    try:
        image = Image.open(file_path)
        
        metadata = {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode,
            "file_size": os.path.getsize(file_path),
        }
        
        return metadata
        
    except Exception as e:
        return {"error": str(e)}


def get_supported_image_formats() -> list:
    """
    Get list of supported image formats
    
    Returns:
        List of supported file extensions
    """
    return ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']
