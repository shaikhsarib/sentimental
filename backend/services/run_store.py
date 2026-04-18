import json
import os
import time
import uuid
from typing import Dict, List, Optional


class RunStore:
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _run_path(self, project_id: str, run_id: str) -> str:
        return os.path.join(self.base_path, project_id, "runs", f"{run_id}.json")

    def _write_json(self, path: str, data: Dict) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _read_json(self, path: str) -> Optional[Dict]:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def create_run(self, project_id: str, mode: str, doc_id: str, objective: str, content_type: str, industry: str) -> Dict:
        run_id = str(uuid.uuid4())
        payload = {
            "run_id": run_id,
            "project_id": project_id,
            "doc_id": doc_id,
            "mode": mode,
            "objective": objective,
            "content_type": content_type,
            "industry": industry,
            "status": "running",
            "created_at": int(time.time()),
            "completed_at": None,
            "result": None,
            "error": None,
        }
        self._write_json(self._run_path(project_id, run_id), payload)
        return payload

    def update_run(self, project_id: str, run_id: str, updates: Dict) -> None:
        data = self._read_json(self._run_path(project_id, run_id)) or {}
        data.update(updates)
        self._write_json(self._run_path(project_id, run_id), data)

    def get_run(self, project_id: str, run_id: str) -> Optional[Dict]:
        return self._read_json(self._run_path(project_id, run_id))

    def list_runs(self, project_id: str) -> List[Dict]:
        runs_dir = os.path.join(self.base_path, project_id, "runs")
        if not os.path.exists(runs_dir):
            return []
        runs = []
        for filename in os.listdir(runs_dir):
            if not filename.endswith(".json"):
                continue
            data = self._read_json(os.path.join(runs_dir, filename))
            if data:
                runs.append(data)
        return sorted(runs, key=lambda r: r.get("created_at", 0), reverse=True)
