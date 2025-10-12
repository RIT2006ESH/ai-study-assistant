from typing import List
import re


def intelligent_chunk_text(text: str, max_chunk_size: int = 3000, overlap: int = 200) -> List[str]:
    """
    Split text into intelligent chunks based on paragraphs and sentences
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    # Split into paragraphs first
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # If adding this paragraph would exceed the limit
        if len(current_chunk) + len(paragraph) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                
                # Add overlap from the end of current chunk
                if overlap > 0:
                    overlap_text = current_chunk[-overlap:]
                    current_chunk = overlap_text + "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                # Single paragraph is too large, split by sentences
                sentences = split_into_sentences(paragraph)
                for sentence in sentences:
                    if len(current_chunk) + len(sentence) > max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        current_chunk += " " + sentence if current_chunk else sentence
        else:
            current_chunk += "\n\n" + paragraph if current_chunk else paragraph
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences
    
    Args:
        text: Text to split
        
    Returns:
        List of sentences
    """
    # Simple sentence splitting
    sentence_endings = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_endings.split(text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_chunks_needed(text: str, max_chunk_size: int = 3000) -> int:
    """
    Calculate how many chunks will be needed for a text
    
    Args:
        text: Text to analyze
        max_chunk_size: Maximum chunk size
        
    Returns:
        Number of chunks needed
    """
    text_length = len(text)
    return max(1, (text_length + max_chunk_size - 1) // max_chunk_size)
