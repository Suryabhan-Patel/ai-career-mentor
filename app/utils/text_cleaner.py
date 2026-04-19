"""
Text cleaning utilities for preprocessing extracted text from resumes.
"""

import re
import string


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing special characters and extra spaces.
    
    Args:
        text (str): Raw text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters but keep spaces and hyphens for multi-word terms
    text = re.sub(r'[^a-z0-9\s\-\+]', ' ', text)
    
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_keywords(text: str) -> list:
    """
    Extract keywords from cleaned text.
    
    Args:
        text (str): Cleaned text
        
    Returns:
        list: List of keywords (words)
    """
    if not text:
        return []
    
    # Split text into words and filter out short terms
    keywords = [word for word in text.split() if len(word) > 2]
    
    return keywords


def normalize_skill_name(skill: str) -> str:
    """
    Normalize skill name for consistent matching.
    
    Args:
        skill (str): Raw skill name
        
    Returns:
        str: Normalized skill name
    """
    return skill.lower().strip()
