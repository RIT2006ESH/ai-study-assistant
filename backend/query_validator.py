# app/services/query_validator.py

import re
import logging
from typing import Dict, Tuple, Optional
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)


class StudyQueryValidator:
    """
    Validates if user queries are study-related before processing with Gemini API.
    Implements multiple validation layers for robust filtering.
    """
    
    # Keywords indicating study-related queries
    STUDY_KEYWORDS = {
        'education', 'learn', 'study', 'homework', 'assignment', 'exam', 'test',
        'quiz', 'course', 'class', 'lecture', 'tutorial', 'lesson', 'subject',
        'math', 'mathematics', 'science', 'history', 'literature', 'physics', 
        'chemistry', 'biology', 'algebra', 'calculus', 'geometry', 'grammar',
        'essay', 'research', 'thesis', 'dissertation', 'paper', 'project',
        'presentation', 'explain', 'solve', 'calculate', 'define', 'describe',
        'analyze', 'compare', 'summarize', 'understand', 'concept', 'theory',
        'formula', 'equation', 'proof', 'theorem', 'law', 'principle', 'problem',
        'question', 'answer', 'solution', 'help', 'teach', 'show', 'demonstrate',
        'what is', 'how to', 'why does', 'when did', 'where is', 'who was',
        'vocabulary', 'meaning', 'definition', 'example', 'practice', 'review',
        'prepare', 'preparation', 'chapter', 'topic', 'notes', 'revision',
        'summarize', 'summary', 'key points', 'main idea', 'learning',
        'programming', 'coding', 'algorithm', 'data structure', 'computer science',
        'economics', 'psychology', 'sociology', 'philosophy', 'geography',
        'anatomy', 'physiology', 'engineering', 'architecture', 'statistics'
    }
    
    # Patterns indicating non-study queries
    REJECT_PATTERNS = [
        r'\b(joke|funny|meme|lol|haha|comedy|humor)\b',
        r'\b(chat|gossip|bored|entertain me|talk to me)\b',
        r'\b(dating|relationship|love|crush|romance)\b',
        r'\b(game|gaming|play|entertainment|fun time)\b',
        r'\b(weather forecast|temperature today|climate now)\b',
        r'\b(recipe|cook|food|restaurant|menu)\b',
        r'\b(movie|film|music|song|artist|album|concert)\b',
        r'^(hi|hello|hey|sup|yo|wassup|howdy)[\s\?!]*$',
        r'\b(insult|offensive|inappropriate|vulgar)\b',
        r'\b(shopping|buy|purchase|sell|price)\b',
        r'\b(sports|football|basketball|cricket|match|score)\b',
    ]
    
    def __init__(self, use_ai_validation: bool = True, strict_mode: bool = False):
        """
        Initialize validator.
        
        Args:
            use_ai_validation: Use Gemini for semantic validation (recommended)
            strict_mode: Require both keyword AND AI validation to pass
        """
        self.use_ai_validation = use_ai_validation
        self.strict_mode = strict_mode
        
        # Configure Gemini API
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            
            if use_ai_validation:
                self.validator_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            self.study_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            
            logger.info("StudyQueryValidator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize StudyQueryValidator: {e}")
            raise
    
    def keyword_validation(self, query: str) -> bool:
        """Fast keyword-based validation (first layer)."""
        query_lower = query.lower()
        
        for pattern in self.REJECT_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.debug(f"Query rejected by pattern: {pattern}")
                return False
        
        has_keywords = any(keyword in query_lower for keyword in self.STUDY_KEYWORDS)
        
        if has_keywords:
            logger.debug("Query passed keyword validation")
        
        return has_keywords
    
    def ai_validation(self, query: str) -> Tuple[bool, str]:
        """AI-powered semantic validation (second layer)."""
        validation_prompt = f"""You are a query classifier for an educational AI assistant. Determine if this query is study/education-related.

Query: "{query}"

A query is STUDY-RELATED if it asks about:
- Academic subjects (math, science, history, languages, literature, arts, computer science, etc.)
- Learning concepts, theories, explanations, or educational content
- Homework, assignments, exams, quizzes, or test preparation
- Research, papers, essays, or academic writing
- Educational skills, techniques, strategies, or study methods
- School/college/university coursework or academic topics
- Understanding concepts, solving problems, or learning new skills
- Subject-specific questions requiring educational expertise

A query is NOT study-related if it's about:
- Personal chat, greetings, casual conversation, or small talk
- Entertainment (jokes, games, movies, music, memes, celebrities)
- Non-academic topics (weather, news, sports, dating, cooking, shopping)
- Inappropriate, offensive, or harmful content
- General chitchat without clear educational purpose
- Product recommendations or purchasing advice
- Current events unrelated to learning

Respond in this exact format:
VALID: yes/no
REASON: [brief explanation in one sentence]"""

        try:
            response = self.validator_model.generate_content(
                validation_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=100
                )
            )
            
            result = response.text.strip()
            is_valid = 'VALID: yes' in result.lower()
            reason_match = re.search(r'REASON:\s*(.+)', result, re.IGNORECASE)
            reason = reason_match.group(1).strip() if reason_match else "Classification complete"
            
            logger.debug(f"AI validation result: {is_valid} - {reason}")
            return is_valid, reason
            
        except Exception as e:
            logger.warning(f"AI validation error: {e}. Falling back to keyword validation.")
            return self.keyword_validation(query), "AI validation unavailable, used keyword fallback"
    
    def validate_query(self, query: str) -> Dict:
        """Main validation method combining all layers."""
        query = query.strip()
        
        if not query or len(query) < 3:
            return {
                'valid': False,
                'reason': 'Query too short or empty',
                'method': 'basic'
            }
        
        keyword_valid = self.keyword_validation(query)
        
        if self.strict_mode and not keyword_valid:
            logger.info(f"Query rejected in strict mode (keyword): {query[:50]}...")
            return {
                'valid': False,
                'reason': 'Query does not appear to be study-related',
                'method': 'keyword'
            }
        
        if self.use_ai_validation:
            ai_valid, ai_reason = self.ai_validation(query)
            
            if self.strict_mode:
                final_valid = keyword_valid and ai_valid
                method = 'keyword+ai_strict'
            else:
                final_valid = keyword_valid or ai_valid
                method = 'keyword+ai_flexible'
            
            if not final_valid:
                logger.info(f"Query rejected by AI validation: {query[:50]}...")
            
            return {
                'valid': final_valid,
                'reason': ai_reason,
                'method': method,
                'keyword_passed': keyword_valid,
                'ai_passed': ai_valid
            }
        
        return {
            'valid': keyword_valid,
            'reason': 'Based on keyword analysis',
            'method': 'keyword_only'
        }
    
    def process_query(self, query: str, context: Optional[str] = None) -> Dict:
        """Complete pipeline: validate and process study queries."""
        validation = self.validate_query(query)
        
        if not validation['valid']:
            logger.info(f"Rejected query: {query[:100]}... | Reason: {validation['reason']}")
            return {
                'success': False,
                'message': 'This assistant only answers study-related questions.',
                'details': validation['reason'],
                'query': query,
                'validation': validation
            }
        
        try:
            logger.info(f"Processing valid study query: {query[:100]}...")
            
            prompt = "You are a helpful study assistant. Answer this educational query clearly and accurately:\n\n"
            
            if context:
                prompt += f"Context: {context}\n\n"
            
            prompt += f"Question: {query}"
            
            response = self.study_model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=2048
                )
            )
            
            logger.info("Query processed successfully")
            
            return {
                'success': True,
                'response': response.text,
                'validation': validation,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                'success': False,
                'message': 'Error processing your study question. Please try again.',
                'details': str(e),
                'query': query
            }


_validator_instance: Optional[StudyQueryValidator] = None


def get_validator(use_ai_validation: bool = True, strict_mode: bool = False) -> StudyQueryValidator:
    """Get or create the validator singleton instance."""
    global _validator_instance
    
    if _validator_instance is None:
        _validator_instance = StudyQueryValidator(
            use_ai_validation=use_ai_validation,
            strict_mode=strict_mode
        )
    
    return _validator_instance
