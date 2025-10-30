"""
Gemini AI Service
Handles interactions with Google's Gemini API for vision and text generation
"""

import google.generativeai as genai
from PIL import Image
import logging
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Gemini AI API"""
    
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = settings.gemini_api_key
        self.is_configured = bool(self.api_key)
        
        if self.is_configured:
            genai.configure(api_key=self.api_key)
            self.vision_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.text_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            logger.info("✅ Gemini service initialized successfully")
        else:
            logger.warning("⚠️  Gemini API key not configured")
    
    def check_configured(self):
        """Check if service is properly configured"""
        if not self.is_configured:
            raise ValueError("Gemini API key not configured. Please set GEMINI_API_KEY in environment.")
    
    async def extract_text(self, image: Image.Image, prompt: str = None) -> str:
        """
        Extract text from an image using Gemini Vision AI
        
        Args:
            image: PIL Image object
            prompt: Optional custom prompt for extraction
            
        Returns:
            Extracted text from the image
        """
        self.check_configured()
        
        try:
            if prompt is None:
                prompt = "Extract all text from this image accurately. Provide only the extracted text."
            
            response = self.vision_model.generate_content([prompt, image])
            extracted_text = response.text.strip()
            
            logger.info(f"Successfully extracted text ({len(extracted_text)} chars)")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise Exception(f"Failed to extract text: {str(e)}")
    
    async def generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini text model
        
        Args:
            prompt: Text prompt for generation
            
        Returns:
            Generated text response
        """
        self.check_configured()
        
        try:
            response = self.text_model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}")
    
    async def analyze_image_with_prompt(self, image: Image.Image, prompt: str) -> str:
        """
        Analyze an image with a custom prompt
        
        Args:
            image: PIL Image object
            prompt: Custom analysis prompt
            
        Returns:
            Analysis result
        """
        self.check_configured()
        
        try:
            response = self.vision_model.generate_content([prompt, image])
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            raise Exception(f"Failed to analyze image: {str(e)}")


# Create singleton instance
gemini_service = GeminiService()


# Export for convenience
__all__ = ['gemini_service', 'GeminiService']
