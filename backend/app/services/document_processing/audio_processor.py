import google.generativeai as genai
from pathlib import Path
import os
from app.config import settings


async def process_audio(file_path: str) -> str:
    """
    Transcribe audio file to text using Google Gemini API
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Transcribed text
        
    Raises:
        Exception: If audio processing fails
    """
    try:
        if not settings.gemini_api_key:
            raise ValueError("Gemini API key not configured")
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        
        # Upload audio file to Gemini
        audio_file = genai.upload_file(path=file_path)
        
        # Use Gemini 2.0 Flash for audio transcription
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Generate transcription
        prompt = "Please transcribe this audio file accurately. Provide only the transcription text without any additional commentary."
        
        response = model.generate_content([prompt, audio_file])
        
        # Clean up - delete the uploaded file from Gemini
        try:
            genai.delete_file(audio_file.name)
        except:
            pass
        
        transcribed_text = response.text
        
        if not transcribed_text.strip():
            raise ValueError("No text could be transcribed from the audio")
        
        return transcribed_text
        
    except Exception as e:
        raise Exception(f"Audio processing failed: {str(e)}")


async def get_audio_metadata(file_path: str) -> dict:
    """
    Extract metadata from an audio file
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Dictionary containing audio metadata
    """
    try:
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1]
        
        metadata = {
            "file_size": file_size,
            "file_name": file_name,
            "format": file_extension.lstrip('.').upper(),
        }
        
        return metadata
        
    except Exception as e:
        return {"error": str(e)}


def get_supported_audio_formats() -> list:
    """
    Get list of supported audio formats
    
    Returns:
        List of supported file extensions
    """
    return ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma']
