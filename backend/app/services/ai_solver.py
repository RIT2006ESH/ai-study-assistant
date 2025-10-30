import google.generativeai as genai
from PIL import Image
import json
from app.config import settings


class AISolver:
    """Service for solving questions using AI"""
    
    # Academic subjects
    ACADEMIC_SUBJECTS = {
        "mathematics", "math", "algebra", "geometry", "calculus", "trigonometry",
        "physics", "chemistry", "biology", "science",
        "computer science", "programming", "algorithms",
        "history", "geography", "economics", "english", "literature",
        "statistics", "probability", "engineering"
    }
    
    def __init__(self):
        """Initialize Gemini API"""
        try:
            api_key = getattr(settings, 'gemini_api_key', None)
            if not api_key:
                print("⚠️  No Gemini API key found")
                self.model = None
                return
            
            genai.configure(api_key=api_key)
            # Use gemini-2.0-flash-exp (available model)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            print("✅ AISolver initialized with gemini-2.0-flash-exp")
        except Exception as e:
            print(f"❌ AISolver init error: {e}")
            self.model = None
    
    async def validate_question(self, question_text: str) -> tuple[bool, str]:
        """
        Validate if the extracted text is an academic question
        
        Args:
            question_text: The extracted text to validate
            
        Returns:
            Tuple of (is_valid, detected_subject)
        """
        if not self.model:
            # Fallback validation without AI
            text_lower = question_text.lower()
            for subject in self.ACADEMIC_SUBJECTS:
                if subject in text_lower:
                    return True, subject.title()
            
            # Check for common question patterns
            question_indicators = ["what", "how", "why", "when", "where", "solve", "calculate", "prove", "explain", "find"]
            if any(indicator in text_lower for indicator in question_indicators):
                return True, "General"
            
            return False, "Unknown"
        
        try:
            prompt = f"""Analyze this text and determine:
1. Is this an academic or educational question? (yes/no)
2. What subject does it belong to?

Text: "{question_text}"

Respond in JSON format:
{{
    "is_academic": true/false,
    "subject": "subject name",
    "reason": "brief reason"
}}"""
            
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
            
            is_valid = result.get("is_academic", False)
            subject = result.get("subject", "General")
            
            return is_valid, subject
            
        except Exception as e:
            print(f"Validation error: {e}")
            # Fallback to simple validation
            return len(question_text.strip()) > 10, "General"
    
    async def solve_question(
        self, 
        image_path: str, 
        question_text: str, 
        subject: str
    ) -> dict:
        """
        Generate comprehensive solution for the question
        
        Args:
            image_path: Path to question image
            question_text: Extracted question text
            subject: Subject area
            
        Returns:
            Dictionary with solution, explanation, and steps
        """
        if not self.model:
            raise ValueError("Gemini API key not configured")
        
        try:
            # Open image
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create comprehensive prompt
            prompt = f"""You are an expert {subject} tutor. A student has asked the following question:

Question: {question_text}

Please provide a comprehensive solution following this structure:

1. **Understanding the Question**: Briefly explain what the question is asking

2. **Solution Approach**: Outline the method or approach to solve it

3. **Step-by-Step Solution**: 
   - Break down the solution into clear, numbered steps
   - Show all work and calculations
   - Explain the reasoning for each step

4. **Final Answer**: Clearly state the final answer

5. **Key Concepts**: List the main concepts used in this problem

6. **Common Mistakes**: Mention common errors students make with this type of question

Make your explanation clear and educational, as if you're helping a student learn, not just giving them an answer."""
            
            response = self.model.generate_content([prompt, img])
            
            if not response or not response.text:
                raise ValueError("Could not generate solution")
            
            solution_text = response.text.strip()
            
            # Extract steps (simplified parsing)
            steps = []
            lines = solution_text.split('\n')
            current_step = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', 'Step')):
                    if current_step:
                        steps.append(current_step)
                    current_step = line
                elif current_step:
                    current_step += " " + line
            
            if current_step:
                steps.append(current_step)
            
            # Determine difficulty
            difficulty = await self._assess_difficulty(question_text, subject)
            
            return {
                "answer": solution_text,
                "explanation": solution_text,
                "steps": steps[:10] if steps else ["See full solution above"],
                "confidence": 0.9,
                "difficulty": difficulty,
                "subject": subject
            }
            
        except Exception as e:
            raise Exception(f"Failed to solve question: {str(e)}")
    
    async def _assess_difficulty(self, question_text: str, subject: str) -> str:
        """Assess question difficulty level"""
        # Simple heuristic based on question length and keywords
        text_lower = question_text.lower()
        
        advanced_keywords = ["prove", "derive", "analyze", "evaluate", "differential", "integral"]
        intermediate_keywords = ["calculate", "solve", "find", "determine"]
        
        if any(keyword in text_lower for keyword in advanced_keywords):
            return "hard"
        elif any(keyword in text_lower for keyword in intermediate_keywords):
            return "medium"
        else:
            return "easy"
