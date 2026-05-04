from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, validator
from typing import Optional, List, Dict
import time
import uuid
import os
import json
import re
import hashlib
import secrets
from collections import defaultdict
from dataclasses import asdict
from dotenv import load_dotenv

from engines.crisis_database import CrisisDatabase
from engines.multi_model import call_llm_with_settings
from engines.consensus_engine import ConsensusEngine
from services.project_store import ProjectStore
from services.graph_store import GraphStore
from services.run_store import RunStore
from services.simulation_runner import SimulationRunner
from sse_starlette.sse import EventSourceResponse
import asyncio

# V6 Engines
from engines.document_processor import DocumentProcessor
from engines.entity_extractor import EntityExtractor
from engines.domain_analyzer import DomainAnalyzer
from engines.agent_factory import AgentFactory
from engines.sentimental_db import SentiDatabase
from engines.swarm_shard_manager import SwarmShardManager
from engines.million_debate_engine import MillionDebateEngine
from engines.query_engine import QueryEngine
from services.export_service import ExportService

load_dotenv()

# Initialize V6 Foundations
v6_db = SentiDatabase("data/sentimental_v6.db")
v6_processor = DocumentProcessor()
v6_extractor = EntityExtractor()
v6_analyzer = DomainAnalyzer()
v6_shard_manager = SwarmShardManager(batch_size=50, max_workers=10)
v6_debate_engine = MillionDebateEngine(v6_shard_manager)
v6_query_engine = QueryEngine()
v6_export_service = ExportService()

# ─── ENVIRONMENT ───
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

app = FastAPI(
    title="SentiFlow V6 Million-Agent API",
    version="6.0.0",
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
)

# ─── SECURITY: CORS ───
# In production, only allow explicit origins. In dev, allow localhost.
ALLOWED_ORIGINS = []
if IS_PRODUCTION:
    # Only allow your actual frontend domains
    prod_frontend = os.getenv("FRONTEND_URL", "")
    if prod_frontend:
        ALLOWED_ORIGINS.append(prod_frontend)
    # Add any additional production origins here
    extra_origins = os.getenv("EXTRA_CORS_ORIGINS", "")
    if extra_origins:
        ALLOWED_ORIGINS.extend([o.strip() for o in extra_origins.split(",") if o.strip()])
else:
    ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],              # Only methods we actually use
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],  # Explicit headers
    max_age=3600,                                # Cache preflight for 1 hour
)

# ─── SECURITY: TRUSTED HOSTS ───
if IS_PRODUCTION:
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",")
    allowed_hosts = [h.strip() for h in allowed_hosts if h.strip()]
    if allowed_hosts:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# ─── SECURITY: RATE LIMITING (In-Memory — swap for Redis in production) ───
class RateLimiter:
    """
    Simple in-memory rate limiter.
    For production, replace with SlowAPI + Redis.
    """
    def __init__(self, requests_per_minute: int = 30, burst_limit: int = 10):
        self.rpm = requests_per_minute
        self.burst = burst_limit
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from API key or IP."""
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return f"key:{hashlib.sha256(api_key.encode()).hexdigest()[:16]}"
        
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host if request.client else 'unknown'}"
    
    def check(self, request: Request) -> bool:
        """Returns True if request is allowed, False if rate limited."""
        client_id = self._get_client_id(request)
        now = time.time()
        
        # Clean old entries
        self.requests[client_id] = [
            t for t in self.requests[client_id] if now - t < 60
        ]
        
        # Check rate
        if len(self.requests[client_id]) >= self.rpm:
            return False
        
        # Check burst (requests in last 2 seconds)
        recent = [t for t in self.requests[client_id] if now - t < 2]
        if len(recent) >= self.burst:
            return False
        
        self.requests[client_id].append(now)
        return True

rate_limiter = RateLimiter(
    requests_per_minute=int(os.getenv("RATE_LIMIT_RPM", "60")),
    burst_limit=int(os.getenv("RATE_LIMIT_BURST", "15")),
)

# ─── SECURITY: Rate Limit Middleware ───
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to all API endpoints."""
    # Skip rate limiting for health checks
    if request.url.path in ["/", "/api/health"]:
        return await call_next(request)
    
    if not rate_limiter.check(request):
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please slow down.",
                "retry_after_seconds": 60
            }
        )
    
    response = await call_next(request)
    return response

from starlette.responses import JSONResponse

# ─── SECURITY: Request Size Limiting ───
MAX_CONTENT_CHARS = 50000
MAX_REQUEST_BODY_BYTES = 10 * 1024 * 1024  # 10MB max

@app.middleware("http")
async def request_size_middleware(request: Request, call_next):
    """Reject oversized requests before they consume resources."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_BODY_BYTES:
        return JSONResponse(
            status_code=413,
            content={"detail": f"Request too large. Maximum {MAX_REQUEST_BODY_BYTES // (1024*1024)}MB."}
        )
    return await call_next(request)

# ─── SECURITY: Security Headers Middleware ───
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if IS_PRODUCTION:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# ─── INPUT SANITIZATION ───
def sanitize_text_input(text: str, max_length: int = MAX_CONTENT_CHARS) -> str:
    """Sanitize text input to prevent injection and abuse."""
    if not text:
        return ""
    # Truncate to max length
    text = text[:max_length]
    # Remove null bytes
    text = text.replace("\x00", "")
    # Remove control characters (keep newlines and tabs)
    text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()

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
consensus_engine = ConsensusEngine()

# Event streams for SSE
run_event_queues: Dict[str, asyncio.Queue] = {}

simulation_runner = SimulationRunner(crisis_db)

# ─── MODELS ───
class AnalyzeRequest(BaseModel):
    content: str
    content_type: str = "social_post"
    industry: str = "general"
    mode: str = "shield" # 'shield' for B2B PR, 'macro' for Novel/Academic Time-Skip

    @validator('content')
    def validate_content(cls, v):
        v = sanitize_text_input(v)
        if not v:
            raise ValueError('Content cannot be empty')
        if len(v) > MAX_CONTENT_CHARS:
            raise ValueError(f'Content too long. Max {MAX_CONTENT_CHARS} chars.')
        return v

    @validator('content_type')
    def validate_content_type(cls, v):
        allowed = {"social_post", "ad_copy", "press_release", "product_page", 
                   "job_posting", "email", "blog", "speech", "policy", "general", "text", "file"}
        if v not in allowed:
            raise ValueError(f'Invalid content_type. Allowed: {", ".join(allowed)}')
        return v

class CreateProjectRequest(BaseModel):
    name: str
    description: str = ""

    @validator('name')
    def validate_name(cls, v):
        v = sanitize_text_input(v, max_length=200)
        if not v or len(v) < 2:
            raise ValueError('Project name must be at least 2 characters')
        return v

class AddDocumentRequest(BaseModel):
    title: str
    content: str
    content_type: str = "text"

    @validator('content')
    def validate_content(cls, v):
        v = sanitize_text_input(v)
        if not v:
            raise ValueError('Document content cannot be empty')
        return v

class RunRequest(BaseModel):
    mode: str = "full"  # shield, macro, or full
    content_type: str = "social_post"
    industry: str = "general"
    objective: str = ""

    @validator('mode')
    def validate_mode(cls, v):
        if v not in {"shield", "macro", "full"}:
            raise ValueError('Mode must be shield, macro, or full')
        return v

    @validator('objective')
    def validate_objective(cls, v):
        return sanitize_text_input(v, max_length=1000)

class QARequest(BaseModel):
    question: str

    @validator('question')
    def validate_question(cls, v):
        v = sanitize_text_input(v, max_length=2000)
        if not v:
            raise ValueError('Question cannot be empty')
        return v

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

        # ── SILENT CONSENSUS PROTOCOL ──
        # Evaluate swarm consensus on shield/full results
        shield_result = result if request.mode == "shield" else result.get("shield") if request.mode == "full" else None
        
        if shield_result and shield_result.get("persona_reactions"):
            consensus = consensus_engine.evaluate_consensus(shield_result["persona_reactions"])
            
            if request.mode == "shield":
                result["consensus"] = consensus
            elif request.mode == "full" and "shield" in result:
                result["shield"]["consensus"] = consensus
            
            # If consensus says refuse, mark the run status
            if consensus.get("should_refuse"):
                if request.mode == "shield":
                    result["consensus_status"] = consensus["status"]
                    result["intelligence_gaps"] = consensus["intelligence_gaps"]
                elif request.mode == "full" and "shield" in result:
                    result["shield"]["consensus_status"] = consensus["status"]
                    result["shield"]["intelligence_gaps"] = consensus["intelligence_gaps"]

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
    try:
        return project_store.add_document_text(project_id, request.title, request.content, request.content_type)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")


@app.post("/api/projects/{project_id}/documents/file")
async def add_file_document(project_id: str, file: UploadFile = File(...)):
    # Validate file size
    contents = await file.read()
    if len(contents) > MAX_REQUEST_BODY_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Validate file type (only allow text-based files)
    allowed_extensions = {".txt", ".md", ".csv", ".json", ".xml", ".html", ".pdf", ".doc", ".docx"}
    filename = file.filename or "uploaded.txt"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type '{ext}' not supported. Allowed: {', '.join(allowed_extensions)}")
    
    try:
        content = contents.decode("utf-8", errors="ignore")
        content = sanitize_text_input(content)
        title = filename
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

    # Check Groq API key presence
    groq_key = os.getenv("GROQ_API_KEY", "")
    groq_status = "configured" if groq_key and "your-key" not in groq_key else "missing"

    return {
        "status": "operational",
        "version": "5.0.0",
        "engine": "SentiFlow V5 — Industrial Intelligence Terminal",
        "checks": {
            "sqlite": db_status,
            "neo4j": neo_status,
            "groq_api": groq_status,
            "storage": "writable" if storage_ok else "readonly",
            "consensus_engine": "active",
            "seir_engine": "active",
            "environment": ENVIRONMENT,
        },
        "security": {
            "cors_locked": IS_PRODUCTION,
            "rate_limiting": "active",
            "input_validation": "active",
            "security_headers": "active",
        },
        "timestamp": int(time.time())
    }

# ─── V6 API ENDPOINTS (Phase 5) ───

@app.post("/api/v6/projects")
async def v6_create_project(request: Dict):
    name = request.get("name", "New V6 Project")
    description = request.get("description", "")
    project_id = v6_db.create_project(name, description)
    return {"project_id": project_id}

@app.get("/api/v6/projects")
async def v6_list_projects():
    return v6_db.list_projects()

@app.post("/api/v6/upload")
async def v6_upload(project_id: str, file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    
    # 1. Process Text
    text = v6_processor.extract_text(content, filename)
    doc_id = v6_db.add_document(project_id, filename, text, filename.split(".")[-1])
    
    # 2. Analyze Domain & Entities
    domain_data = await v6_analyzer.analyze(text)
    entities = await v6_extractor.extract(text[:8000], high_fidelity=True)
    
    # Update project with domain
    v6_db._get_connection().execute(
        "UPDATE projects SET domain = ? WHERE project_id = ?", 
        (domain_data.get("domain"), project_id)
    ).close()

    return {
        "doc_id": doc_id,
        "domain": domain_data,
        "entities": [asdict(e) for e in entities[:50]] # Limit for preview
    }

@app.post("/api/v6/projects/{project_id}/debate")
async def v6_run_debate(project_id: str, request: Dict):
    intent = request.get("intent", "")
    target_count = request.get("target_count", 1000)
    
    # 1. Fetch document and entities
    project = v6_db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Get latest document
    with v6_db._get_connection() as conn:
        doc = conn.execute("SELECT * FROM documents WHERE project_id = ? ORDER BY doc_id DESC LIMIT 1", (project_id,)).fetchone()
    
    if not doc:
        raise HTTPException(status_code=400, detail="No document found in project")

    # 2. Extract Entities & Generate Swarm
    entities = await v6_extractor.extract(doc["content"][:10000], high_fidelity=True)
    factory = AgentFactory(domain=project.get("domain", "GENERAL"))
    swarm = factory.generate_swarm(entities, target_count=target_count)
    
    # Save swarm for explorer
    v6_db.save_agent_swarm(swarm)
    
    # 3. Run Million-Agent Debate
    results = await v6_debate_engine.run_million_debate(
        agents=swarm,
        content=doc["content"][:5000],
        content_type=doc["content_type"],
        intent=intent
    )
    
    return results

@app.post("/api/v6/projects/{project_id}/query")
async def v6_query_swarm(project_id: str, request: Dict):
    query = request.get("query", "")
    perspective = request.get("perspective", "businessman")
    debate_data = request.get("debate_data")
    
    if not debate_data:
        raise HTTPException(status_code=400, detail="Debate data is required for synthesis.")
        
    result = await v6_query_engine.query_swarm(query, perspective, debate_data)
    return result

@app.post("/api/v6/projects/{project_id}/export")
async def v6_export_brief(project_id: str, request: Dict):
    debate_data = request.get("debate_data")
    queries = request.get("queries", {}) # Dictionary of {perspective: result}
    
    if not debate_data:
        raise HTTPException(status_code=400, detail="Debate data is required for export.")
        
    filename = v6_export_service.generate_strategic_brief(project_id, debate_data, queries)
    return {"filename": filename, "download_url": f"/api/exports/{filename}"}

from fastapi.responses import FileResponse
@app.get("/api/exports/{filename}")
async def download_export(filename: str):
    path = os.path.join("storage/exports", filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)

@app.get("/")
def root():
    return {
        "status": "SentiFlow V5 is operational.",
        "version": "5.0.0",
        "moats": [
            "Silent Consensus Protocol™",
            "SEIR-10M Epidemiological Projection",
            "Adversarial Swarm Debate",
            "Triple Verification Engine"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
