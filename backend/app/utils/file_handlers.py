import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".doc", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def ensure_upload_dir():
    """Create upload directory if it doesn't exist."""
    Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

def get_file_type(filename: str) -> str:
    """
    Get the file type/extension from filename.
    Returns the extension without the dot (e.g., 'pdf', 'txt').
    """
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip(".")

def validate_file(filename: str, file_size: int) -> bool:
    """
    Validate if a file is allowed based on extension and size.
    Raises HTTPException if validation fails.
    """
    _, ext = os.path.splitext(filename)
    
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    return True

async def save_upload_file(upload_file: UploadFile, user_id: str) -> str:
    """
    Save an uploaded file to the uploads directory.
    Returns the file path relative to the project root.
    
    Args:
        upload_file: FastAPI UploadFile object
        user_id: User ID to organize files
        
    Returns:
        Path to the saved file
    """
    try:
        ensure_upload_dir()
        
        # Read file content to check size
        content = await upload_file.read()
        file_size = len(content)
        
        # Validate file
        validate_file(upload_file.filename, file_size)
        
        # Create user-specific directory
        user_dir = Path(UPLOAD_DIR) / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Create file path
        file_path = user_dir / upload_file.filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        return str(file_path)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )

def delete_file(file_path: str) -> bool:
    """
    Delete a file from the uploads directory.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if successful, raises HTTPException on failure
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete file: {str(e)}"
        )

def get_file_content(file_path: str) -> str:
    """
    Read the content of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content as string
    """
    try:
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
        
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read file: {str(e)}"
        )