import os
import json
from datetime import datetime

class AuditLogger:
    """
    SentiFlow V6 Immutable Audit Logger.
    Logs agent reasoning chains and arbitration verdicts for compliance and debugging.
    Blueprint Page 35 (Phase 5 Fix).
    """
    
    def __init__(self, log_dir: str = "storage/audit"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def log_event(self, project_id: str, event_type: str, data: dict):
        """Logs a single event to a JSONL file."""
        log_file = os.path.join(self.log_dir, f"{project_id}_audit.jsonl")
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_provenance(self, project_id: str) -> list:
        """Retrieves the full reasoning chain for a project."""
        log_file = os.path.join(self.log_dir, f"{project_id}_audit.jsonl")
        if not os.path.exists(log_file):
            return []
            
        provenance = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                provenance.append(json.loads(line))
        return provenance
