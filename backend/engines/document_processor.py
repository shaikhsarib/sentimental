import PyPDF2
import io
import re
from typing import Dict, List, Optional

class DocumentProcessor:
    """
    SentiFlow V6 Document Processor.
    Handles text extraction from PDF, TXT, and Markdown files.
    Includes chunking logic for large documents.
    """
    
    def __init__(self, chunk_size: int = 4000):
        self.chunk_size = chunk_size

    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract raw text from various file formats."""
        ext = filename.split(".")[-1].lower()
        
        if ext == "pdf":
            return self._extract_pdf(file_content)
        elif ext in ["txt", "md"]:
            return file_content.decode("utf-8", errors="ignore")
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def _extract_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF bytes."""
        text = ""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"[ERROR] PDF Extraction failed: {e}")
            return ""
        return text

    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of roughly chunk_size characters."""
        # Simple chunking by character count, trying to break at newlines/periods
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Find a good breaking point (newline or period) within the last 500 chars of the chunk
            break_point = -1
            search_area = text[end-500:end]
            
            # Try newline first
            newline_idx = search_area.rfind("\n")
            if newline_idx != -1:
                break_point = end - 500 + newline_idx
            else:
                # Try period
                period_idx = search_area.rfind(".")
                if period_idx != -1:
                    break_point = end - 500 + period_idx
            
            if break_point != -1:
                end = break_point + 1
            
            chunks.append(text[start:end])
            start = end
            
        return [c.strip() for c in chunks if c.strip()]

    def clean_text(self, text: str) -> str:
        """Remove excess whitespace and artifacts."""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
