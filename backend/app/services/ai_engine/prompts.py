SYSTEM_PROMPT = """You are an intelligent AI study assistant. Your role is to help students learn effectively by:
- Providing clear, accurate explanations
- Breaking down complex topics into understandable parts
- Creating helpful summaries and study materials
- Answering questions about study materials
- Maintaining an encouraging and supportive tone

Always prioritize accuracy and educational value in your responses."""


def build_summary_prompt(text: str, level: str = "moderate") -> str:
    """
    Build a prompt for text summarization
    
    Args:
        text: Text to summarize
        level: Summary level (brief, moderate, detailed)
        
    Returns:
        Formatted prompt string
    """
    level_instructions = {
        "brief": "Create a concise summary in 2-3 sentences capturing only the main idea.",
        "moderate": "Create a moderate summary in 1-2 paragraphs covering the key points and main concepts.",
        "detailed": "Create a detailed summary covering all important points, key concepts, and supporting details. Organize it with clear structure."
    }
    
    instruction = level_instructions.get(level, level_instructions["moderate"])
    
    prompt = f"""{instruction}

Text to summarize:
{text}

Summary:"""
    
    return prompt


def build_qa_prompt(question: str, context: str) -> str:
    """
    Build a prompt for question answering
    
    Args:
        question: User's question
        context: Context/document text
        
    Returns:
        Formatted prompt string
    """
    prompt = f"""Based on the following study material, answer the question accurately and helpfully.

Study Material:
{context}

Question: {question}

Answer:"""
    
    return prompt


def build_concept_explanation_prompt(concept: str, context: str = None) -> str:
    """
    Build a prompt for explaining a concept
    
    Args:
        concept: Concept to explain
        context: Optional context from study materials
        
    Returns:
        Formatted prompt string
    """
    if context:
        prompt = f"""Explain the concept of "{concept}" based on the following study material. 
Provide a clear, educational explanation that a student can understand.

Study Material:
{context}

Explanation:"""
    else:
        prompt = f"""Explain the concept of "{concept}" in a clear, educational way that a student can understand. 
Include examples if helpful.

Explanation:"""
    
    return prompt
