from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import time
import uuid
import os
import json
from dotenv import load_dotenv

from engines.crisis_database import CrisisDatabase
from engines.multi_model import call_llm_with_settings
from services.project_store import ProjectStore
from services.graph_store import GraphStore
from services.run_store import RunStore
from services.simulation_runner import SimulationRunner
from sse_starlette.sse import EventSourceResponse
import asyncio

load_dotenv()

app = FastAPI(title="Sentimental V3 API", version="3.0.0")

# CORS setup
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:5173"),
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_CONTENT_CHARS = 50000

# Initialize engines
db_path = os.path.join(os.path.dirname(__file__), "data", "sentimental.db")
crisis_db = CrisisDatabase(db_path)
storage_path = os.path.join(os.path.dirname(__file__), "storage")
project_store = ProjectStore(storage_path)
graph_store = GraphStore(
    storage_path,
    os.getenv("NEO4J_URI"),
    os.getenv("NEO4J_USER"),
    os.getenv("NEO4J_PASSWORD"),
)
run_store = RunStore(storage_path)

# Event streams for SSE
run_event_queues: Dict[str, asyncio.Queue] = {}

simulation_runner = SimulationRunner(crisis_db)

# ─── MODELS ───
class AnalyzeRequest(BaseModel):
    content: str
    content_type: str = "social_post"
    industry: str = "general"
    mode: str = "shield" # 'shield' for B2B PR, 'macro' for Novel/Academic Time-Skip

class CreateProjectRequest(BaseModel):
    name: str
    description: str = ""

class AddDocumentRequest(BaseModel):
    title: str
    content: str
    content_type: str = "text"

class RunRequest(BaseModel):
    mode: str = "full"  # shield, macro, or full
    content_type: str = "social_post"
    industry: str = "general"
    objective: str = ""

class QARequest(BaseModel):
    question: str

async def _run_project_simulation(project_id: str, run_id: str, doc: Dict, request: RunRequest) -> None:
    async def on_persona(res):
        if run_id in run_event_queues:
            await run_event_queues[run_id].put({"event": "persona_reaction", "data": res})

    try:
        project = project_store.get_project(project_id)
        custom_personas = project.get("personas") if project else None
        
        # Load Tactical Memory (Lessons Learned)
        lessons = project.get("tactical_memory", [])

        if request.mode == "shield":
            result = await simulation_runner.run_shield(doc["content"], request.content_type, request.industry, request.objective, on_persona_result=on_persona, custom_personas=custom_personas, lessons=lessons)
        elif request.mode == "macro":
            result = await simulation_runner.run_macro(doc["content"], request.objective)
        else:
            result = await simulation_runner.run_full(doc["content"], request.content_type, request.industry, request.objective, on_persona_result=on_persona, custom_personas=custom_personas, lessons=lessons)

        # Extract contextually relevant lessons from the run results
        evaluation = result.get("evaluation") if request.mode == "shield" else (result.get("shield", {}).get("evaluation") if request.mode == "full" else None)
        
        if evaluation and evaluation.get("lessons_learned"):
            new_lessons = evaluation["lessons_learned"]
            # Merge and limit to last 50 lessons to prevent prompt bloating
            combined_lessons = (lessons + new_lessons)[-50:]
            project_store.update_project(project_id, {"tactical_memory": combined_lessons})

        run_store.update_run(project_id, run_id, {
            "status": "completed",
            "completed_at": int(time.time()),
            "result": result,
        })
        
        # Notify SSE
        if run_id in run_event_queues:
            await run_event_queues[run_id].put({"event": "status", "data": "completed"})

    except Exception as e:
        run_store.update_run(project_id, run_id, {
            "status": "failed",
            "completed_at": int(time.time()),
            "error": str(e),
        })
        if run_id in run_event_queues:
             await run_event_queues[run_id].put({"event": "error", "data": str(e)})

# ─── ENDPOINTS ───

@app.post("/api/analyze")
async def analyze_content(request: AnalyzeRequest):
    """Legacy endpoint: runs shield or macro for a single prompt."""
    if len(request.content) > MAX_CONTENT_CHARS:
        raise HTTPException(status_code=400, detail=f"Content too long. Max {MAX_CONTENT_CHARS} chars.")
    
    if request.mode == "macro":
        return await simulation_runner.run_macro(request.content)
    return await simulation_runner.run_shield(request.content, request.content_type, request.industry)


@app.get("/api/projects")
async def list_projects():
    base = project_store.base_path
    if not os.path.exists(base):
        return []
    projects = []
    for pid in os.listdir(base):
        path = os.path.join(base, pid, "project.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                projects.append(json.load(f))
    return sorted(projects, key=lambda x: x.get("created_at", 0), reverse=True)

@app.post("/api/projects")
async def create_project(request: CreateProjectRequest):
    return project_store.create_project(request.name, request.description)


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    project = project_store.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.post("/api/projects/{project_id}/documents/text")
async def add_text_document(project_id: str, request: AddDocumentRequest):
    if len(request.content) > MAX_CONTENT_CHARS:
        raise HTTPException(status_code=400, detail=f"Content too long. Max {MAX_CONTENT_CHARS} chars.")
    try:
        return project_store.add_document_text(project_id, request.title, request.content, request.content_type)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.post("/api/projects/{project_id}/documents/file")
async def add_file_document(project_id: str, file: UploadFile = File(...)):
    try:
        raw = await file.read()
        content = raw.decode("utf-8", errors="ignore")
        title = file.filename or "uploaded.txt"
        return project_store.add_document_text(project_id, title, content, "file")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.post("/api/projects/{project_id}/ontology")
async def generate_ontology(project_id: str):
    doc = project_store.get_latest_document(project_id)
    if not doc:
        raise HTTPException(status_code=400, detail="No document to analyze")
    
    ontology = await graph_store.generate_ontology(doc["content"])
    project_store.update_project(project_id, {"ontology": ontology})
    return ontology

@app.post("/api/projects/{project_id}/graph/extract")
async def extract_knowledge_graph(project_id: str):
    project = project_store.get_project(project_id)
    if not project or "ontology" not in project:
        raise HTTPException(status_code=400, detail="Ontology not defined. Generate ontology first.")
        
    docs = project_store.list_documents(project_id)
    texts = []
    for doc in docs:
        full = project_store.get_document(project_id, doc["doc_id"])
        if full:
            texts.append(full.get("content", ""))
            
    graph = await graph_store.extract_entities(texts, project["ontology"])
    graph_store.store_graph(project_id, graph)
    return graph

@app.post("/api/projects/{project_id}/graph/build")
async def build_graph_legacy(project_id: str):
    """Legacy word-co-occurrence build."""
    docs = project_store.list_documents(project_id)
    if not docs:
        raise HTTPException(status_code=400, detail="No documents to graph")
    texts = []
    for doc in docs:
        full = project_store.get_document(project_id, doc["doc_id"])
        if full:
            texts.append(full.get("content", ""))
    graph = graph_store.build_graph_from_texts(texts)
    graph_store.store_graph(project_id, graph)
    return graph


@app.get("/api/projects/{project_id}/graph")
async def get_graph(project_id: str):
    return graph_store.get_graph(project_id)


@app.get("/api/projects/{project_id}/graph/metrics")
async def get_graph_metrics(project_id: str):
    return graph_store.get_graph_metrics(project_id)


@app.post("/api/projects/{project_id}/runs")
async def start_run(project_id: str, request: RunRequest, background_tasks: BackgroundTasks):
    doc = project_store.get_latest_document(project_id)
    if not doc:
        raise HTTPException(status_code=400, detail="No document to analyze")

    run = run_store.create_run(
        project_id,
        request.mode,
        doc["doc_id"],
        request.objective,
        request.content_type,
        request.industry,
    )
    project_store.set_latest_run(project_id, run["run_id"])
    background_tasks.add_task(_run_project_simulation, project_id, run["run_id"], doc, request)
    return run


@app.post("/api/projects/{project_id}/personas/synthesize")
async def synthesize_personas(project_id: str):
    graph = graph_store.get_graph(project_id)
    if not graph or not graph.get("nodes"):
        raise HTTPException(status_code=400, detail="Graph not found. Extract graph first.")
    
    personas = await simulation_runner.synthesize_personas_from_graph(project_id, graph)
    project_store.update_project(project_id, {"personas": personas})
    return personas

@app.get("/api/projects/{project_id}/runs")
async def list_runs(project_id: str):
    return run_store.list_runs(project_id)


@app.get("/api/projects/{project_id}/runs/{run_id}")
async def get_run(project_id: str, run_id: str):
    run = run_store.get_run(project_id, run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.post("/api/projects/{project_id}/runs/{run_id}/qa")
async def run_qa(project_id: str, run_id: str, request: QARequest):
    run = run_store.get_run(project_id, run_id)
    if not run or run.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Run not ready")

    summary = json.dumps(run.get("result", {}))
    prompt = f"""You are a report analyst. Answer the question using the report JSON only.
Report JSON:\n{summary}\n
Question: {request.question}
Return JSON: {{"answer": "...", "sources": ["fields used"]}}"""
    res = await call_llm_with_settings(prompt, "llama-3.1-8b-instant", 0.7)
    return res

@app.post("/api/projects/{project_id}/personas/{persona_id}/chat")
async def persona_chat(project_id: str, persona_id: str, request: QARequest):
    project = project_store.get_project(project_id)
    if not project or "personas" not in project:
        raise HTTPException(status_code=400, detail="Personas not synthesized")
        
    persona = next((p for p in project["personas"] if p["persona_id"] == persona_id), None)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
        
    mission_context = project.get("ontology", {}).get("mission_context", project.get("description", ""))
    return await simulation_runner.chat_with_persona(persona, mission_context, request.question)

@app.post("/api/projects/{project_id}/runs/{run_id}/summarize")
async def summarize_run(project_id: str, run_id: str):
    project = project_store.get_project(project_id)
    run = run_store.get_run(project_id, run_id)
    if not project or not run:
        raise HTTPException(status_code=404, detail="Project or run not found")
        
    if not run.get("result") and not run.get("persona_reactions"):
         # For Step 4 grounded runs, they might have persona_reactions instead of a flat result list
         # Let's ensure we have data to summarize
         pass

    # Extract reactions for synthesis
    reactions = run.get("result", {}).get("persona_reactions", [])
    if not reactions:
        # Fallback if structure is different
        reactions = run.get("persona_reactions", [])

    summary = await simulation_runner.generate_strategic_summary(
        project["name"],
        run["objective"],
        reactions
    )
    
    run_store.update_run(project_id, run_id, {"summary": summary})
    return summary

@app.get("/api/projects/{project_id}/runs/{run_id}/stream")
async def stream_run_events(project_id: str, run_id: str):
    """SSE endpoint for real-time simulation updates."""
    if run_id not in run_event_queues:
        run_event_queues[run_id] = asyncio.Queue()

    async def event_generator():
        queue = run_event_queues[run_id]
        try:
            while True:
                msg = await queue.get()
                yield {
                    "event": msg.get("event", "message"),
                    "data": json.dumps(msg.get("data", ""))
                }
                if msg.get("event") in ["completed", "error"]:
                    break
        finally:
            # Clean up on disconnect
            pass

    return EventSourceResponse(event_generator())

@app.get("/api/health")
def health_check():
    """System health with detailed dependency diagnostics."""
    neo_status = "active" if graph_store.driver else "inactive"
    
    # Check if storage is writable
    storage_ok = os.access(storage_path, os.W_OK)
    
    # Check if database is connected
    try:
        crisis_db.db.execute("SELECT 1")
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "operational",
        "version": "3.0.0",
        "checks": {
            "sqlite": db_status,
            "neo4j": neo_status,
            "storage": "writable" if storage_ok else "readonly",
            "environment": os.getenv("ENVIRONMENT", "development")
        },
        "timestamp": int(time.time())
    }

@app.get("/")
def root():
    return {"status": "Sentimental V3 is operational.", "moats": "Triple Verification, SEIR Projection active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
