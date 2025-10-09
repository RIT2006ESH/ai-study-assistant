import google.generativeai as genai
from app.config import settings

class LLMClient:
    def __init__(self):
        self.api_key = settings.gemini_api_key
        genai.configure(api_key=self.api_key)
        # Using Gemini 2.0 Flash - fast and efficient
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def generate_response(self, prompt: str, max_tokens: int = 1000):
        try:
            if not self.api_key:
                return "Please configure your Gemini API key in the .env file"
            
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def generate_summary(self, text: str):
        prompt = f"Summarize the following text concisely:\n\n{text}"
        return await self.generate_response(prompt)
