import json
import os
import time
import uuid
import threading
from typing import Dict, List, Optional


class ProjectStore:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self._lock = threading.Lock()
        os.makedirs(self.base_path, exist_ok=True)

    def _project_path(self, project_id: str) -> str:
        return os.path.join(self.base_path, project_id)

    def _project_file(self, project_id: str) -> str:
        return os.path.join(self._project_path(project_id), "project.json")

    def _read_json(self, path: str) -> Dict:
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: str, data: Dict) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with self._lock:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                f.flush()
                # Ensure it's written to disk
                os.fsync(f.fileno())

    def create_project(self, name: str, description: str) -> Dict:
        project_id = str(uuid.uuid4())
        created_at = int(time.time())
        project_dir = self._project_path(project_id)
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, "uploads"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "runs"), exist_ok=True)
        metadata = {
            "project_id": project_id,
            "name": name,
            "description": description,
            "created_at": created_at,
            "documents": [],
            "latest_run_id": None,
        }
        self._write_json(self._project_file(project_id), metadata)
        return metadata

    def get_project(self, project_id: str) -> Optional[Dict]:
        path = self._project_file(project_id)
        if not os.path.exists(path):
            return None
        return self._read_json(path)

    def list_documents(self, project_id: str) -> List[Dict]:
        project = self.get_project(project_id)
        if not project:
            return []
        return project.get("documents", [])

    def add_document_text(self, project_id: str, title: str, content: str, content_type: str) -> Dict:
        project = self.get_project(project_id)
        if not project:
            raise FileNotFoundError("Project not found")

        doc_id = str(uuid.uuid4())
        created_at = int(time.time())
        payload = {
            "doc_id": doc_id,
            "title": title,
            "content": content,
            "content_type": content_type,
            "created_at": created_at,
        }
        doc_path = os.path.join(self._project_path(project_id), "uploads", f"{doc_id}.json")
        self._write_json(doc_path, payload)

        project["documents"].append({
            "doc_id": doc_id,
            "title": title,
            "content_type": content_type,
            "created_at": created_at,
        })
        self._write_json(self._project_file(project_id), project)
        return payload

    def get_latest_document(self, project_id: str) -> Optional[Dict]:
        docs = self.list_documents(project_id)
        if not docs:
            return None
        latest = sorted(docs, key=lambda d: d.get("created_at", 0))[-1]
        doc_path = os.path.join(self._project_path(project_id), "uploads", f"{latest['doc_id']}.json")
        return self._read_json(doc_path)

    def get_document(self, project_id: str, doc_id: str) -> Optional[Dict]:
        doc_path = os.path.join(self._project_path(project_id), "uploads", f"{doc_id}.json")
        return self._read_json(doc_path)

    def set_latest_run(self, project_id: str, run_id: str) -> None:
        project = self.get_project(project_id)
        if not project:
            raise FileNotFoundError("Project not found")
        project["latest_run_id"] = run_id
        self._write_json(self._project_file(project_id), project)

    def update_project(self, project_id: str, updates: Dict) -> Dict:
        project = self.get_project(project_id)
        if not project:
            raise FileNotFoundError("Project not found")
        project.update(updates)
        self._write_json(self._project_file(project_id), project)
        return project
