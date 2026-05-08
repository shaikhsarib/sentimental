import pypdf
import io
import re
from typing import Dict, List, Optional
from engines.security_engine import SecurityEngine

class DocumentProcessor:
    """
    SentiFlow V6 Document Processor.
    Handles text extraction from PDF, TXT, and Markdown files.
    Includes chunking logic for large documents.
    Phase 5 Hardening: Integrated SecurityEngine.
    """
    
    def __init__(self, chunk_size: int = 4000):
        self.chunk_size = chunk_size
        self.security_engine = SecurityEngine()

    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract raw text from various file formats."""
        ext = filename.split(".")[-1].lower()
        
        text = ""
        if ext == "pdf":
            text = self._extract_pdf(file_content)
        elif ext in ["txt", "md"]:
            text = file_content.decode("utf-8", errors="ignore")
        else:
            raise ValueError(f"Unsupported file type: {ext}")
        
        return text

    def scan_for_threats(self, text: str) -> Dict:
        """Runs the security engine on the extracted text."""
        return self.security_engine.scan_content(text)

    def _extract_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF bytes."""
        text = ""
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_content))
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
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            break_point = -1
            search_area = text[end-500:end]
            
            newline_idx = search_area.rfind("\n")
            if newline_idx != -1:
                break_point = end - 500 + newline_idx
            else:
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
