with open('summarization.py', 'r') as f:
    content = f.read()

# Add TextSummaryRequest class after ProblemRequest
class_addition = '''
class TextSummaryRequest(BaseModel):
    text: str
    level: str = "moderate"  # brief, moderate, detailed
'''

# Find the position after ProblemRequest class
problem_request_end = content.find('router = APIRouter()')
if problem_request_end != -1:
    content = content[:problem_request_end] + class_addition + '\n' + content[problem_request_end:]

# Add the new endpoint at the end
endpoint_addition = '''

@router.post("/text")
async def summarize_text(
    request: TextSummaryRequest,
    llm: LLMClient = Depends(get_llm_client)
):
    """
    Summarize any text input
    
    - **text**: The text to summarize
    - **level**: Summary level (brief, moderate, detailed)
    """
    try:
        text = request.text.strip()
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text is required for summarization"
            )
        
        if len(text) < 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Text is too short to summarize (minimum 50 characters)"
            )
        
        print(f"Summarizing text of length: {len(text)} chars, level: {request.level}")
        
        # Build summary prompt
        if request.level == "brief":
            prompt = f"Provide a brief 2-3 sentence summary of the following text:\\n\\n{text}"
        elif request.level == "detailed":
            prompt = f"Provide a detailed summary with key points and important details from the following text:\\n\\n{text}"
        else:  # moderate
            prompt = f"Provide a clear and concise summary of the following text:\\n\\n{text}"
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        summary = await llm.generate_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=1000
        )
        
        print(f"Summary generated successfully, length: {len(summary)} chars")
        
        return {
            "summary": summary,
            "level": request.level,
            "original_length": len(text),
            "summary_length": len(summary),
            "word_count": len(summary.split()),
            "message": "Text summarized successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in summarize_text: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text summarization failed: {str(e)}"
        )
'''

content = content + endpoint_addition

with open('summarization.py', 'w') as f:
    f.write(content)

print("✅ summarization.py updated successfully!")
