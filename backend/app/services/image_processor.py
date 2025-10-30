import google.generativeai as genai
from PIL import Image
from app.config import settings


class ImageProcessor:
    def __init__(self):
        try:
            api_key = getattr(settings, 'gemini_api_key', None)
            if not api_key:
                print("⚠️  No Gemini API key found")
                self.model = None
                return
            
            genai.configure(api_key=api_key)
            # Use gemini-2.0-flash-exp (available model)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✅ ImageProcessor initialized with gemini-2.0-flash-exp")
        except Exception as e:
            print(f"❌ ImageProcessor init error: {e}")
            self.model = None
    
    async def extract_text(self, image_path: str) -> str:
        if not self.model:
            raise ValueError("Gemini API not configured. Please add GEMINI_API_KEY to your config.")
        
        try:
            print(f"📸 Opening image: {image_path}")
            img = Image.open(image_path)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            prompt = """Extract all text from this image accurately. 
            If it contains a question, extract the complete question including:
            - The main question text
            - Any sub-questions or parts (a, b, c, etc.)
            - Numbers, equations, formulas
            - Diagrams descriptions if any
            
            Return only the extracted text without any additional commentary."""
            
            print("🤖 Calling Gemini API...")
            response = self.model.generate_content([prompt, img])
            
            if not response or not response.text:
                raise ValueError("Gemini returned empty response")
            
            text = response.text.strip()
            print(f"✅ Extracted {len(text)} characters")
            return text
            
        except Exception as e:
            print(f"❌ Extract error: {e}")
            raise Exception(f"Image processing failed: {str(e)}")
    
    async def analyze_image(self, image_path: str) -> dict:
        if not self.model:
            return {"error": "API not configured"}
        
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            prompt = """Analyze this image and provide:
            1. Type of content (handwritten/printed/mixed)
            2. Subject area (Math/Physics/Chemistry/Biology/etc.)
            3. Complexity level (easy/medium/hard)
            4. Contains diagrams or figures (yes/no)
            5. Quality assessment (clear/unclear/partially visible)
            
            Respond in this format:
            Content Type: [type]
            Subject: [subject]
            Complexity: [level]
            Diagrams: [yes/no]
            Quality: [assessment]"""
            
            response = self.model.generate_content([prompt, img])
            
            # Parse response
            analysis = {}
            for line in response.text.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    analysis[key.strip().lower().replace(' ', '_')] = value.strip()
            
            return analysis
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return {"error": str(e)}
