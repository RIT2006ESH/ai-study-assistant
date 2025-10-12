import google.generativeai as genai
from app.config import settings
from typing import List, Dict, Optional


class LLMClient:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        if self.api_key:
            genai.configure(api_key=self.api_key)
        # Using Gemini 2.0 Flash - fast and efficient
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    async def generate_response(self, prompt: str, max_tokens: int = 1000):
        """Generate a response to a prompt"""
        try:
            if not self.api_key:
                return "Please configure your Gemini API key in the .env file"

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"Error: {str(e)}"

    async def generate_summary(self, text: str):
        """Generate a summary of the given text"""
        prompt = f"Summarize the following text concisely:\n\n{text}"
        return await self.generate_response(prompt)
    
    async def generate_completion(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Generate completion using message format
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            if not self.api_key:
                raise ValueError("Gemini API key not configured")
            
            # Convert messages to a single prompt
            prompt_parts = []
            for msg in messages:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                
                if role == 'system':
                    prompt_parts.append(f"Instructions: {content}")
                elif role == 'user':
                    prompt_parts.append(content)
            
            full_prompt = "\n\n".join(prompt_parts)
            
            # Generate response
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            model = genai.GenerativeModel(
                'gemini-2.0-flash-exp',
                generation_config=generation_config
            )
            
            response = model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            raise Exception(f"Completion generation failed: {str(e)}")


def get_llm_client() -> LLMClient:
    """Dependency for getting LLM client"""
    return LLMClient()
