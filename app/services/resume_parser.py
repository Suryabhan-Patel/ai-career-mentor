"""
Resume PDF text extraction using PyMuPDF.
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import Optional


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract all text from a PDF file using PyMuPDF.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from all pages
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not a valid PDF
    """
    try:
        # Check if file exists
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Open PDF file
        pdf_document = fitz.open(file_path)
        extracted_text = []
        
        # Extract text from each page
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            text = page.get_text()
            extracted_text.append(text)
        
        # Close the document
        pdf_document.close()
        
        # Combine all pages
        full_text = "\n".join(extracted_text)
        
        return full_text
    
    except fitz.FileError:
        raise ValueError(f"Invalid PDF file: {file_path}")
    except Exception as e:
        raise Exception(f"Error extracting PDF text: {str(e)}")


def extract_text_from_pdf_with_metadata(file_path: str) -> dict:
    """
    Extract text and metadata from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        dict: Dictionary with 'text' and 'metadata'
    """
    try:
        pdf_document = fitz.open(file_path)
        
        # Extract metadata
        metadata = pdf_document.metadata
        
        # Extract text
        text = extract_text_from_pdf(file_path)
        
        return {
            "text": text,
            "metadata": metadata,
            "page_count": len(pdf_document)
        }
    
    except Exception as e:
        raise Exception(f"Error extracting PDF metadata: {str(e)}")
