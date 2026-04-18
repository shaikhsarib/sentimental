import json
import os
from typing import Dict, List

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "dataset.jsonl")

SYSTEM_PROMPT = "You are a risk analyst. Respond with concise, structured findings."


def _load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _iter_runs(storage_dir: str) -> List[Dict]:
    runs = []
    if not os.path.exists(storage_dir):
        return runs
    for project_id in os.listdir(storage_dir):
        runs_dir = os.path.join(storage_dir, project_id, "runs")
        if not os.path.isdir(runs_dir):
            continue
        for filename in os.listdir(runs_dir):
            if not filename.endswith(".json"):
                continue
            run = _load_json(os.path.join(runs_dir, filename))
            if run.get("status") == "completed":
                runs.append(run)
    return runs


def _get_document(storage_dir: str, project_id: str, doc_id: str) -> Dict:
    doc_path = os.path.join(storage_dir, project_id, "uploads", f"{doc_id}.json")
    if not os.path.exists(doc_path):
        return {}
    return _load_json(doc_path)


def build_dataset() -> None:
    examples = []
    for run in _iter_runs(STORAGE_DIR):
        project_id = run.get("project_id")
        doc_id = run.get("doc_id")
        if not project_id or not doc_id:
            continue
        doc = _get_document(STORAGE_DIR, project_id, doc_id)
        content = doc.get("content")
        if not content:
            continue
        objective = run.get("objective", "General risk scan")
        result = run.get("result", {})
        assistant = json.dumps({"objective": objective, "result": result})
        examples.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
                {"role": "assistant", "content": assistant},
            ]
        })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")

    print(f"Wrote {len(examples)} examples to {OUTPUT_PATH}")


if __name__ == "__main__":
    build_dataset()
