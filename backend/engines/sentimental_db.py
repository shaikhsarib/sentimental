import sqlite3
import json
import os
from typing import Dict, List, Optional

class SentiDatabase:
    """
    SentiFlow V6 SQLite Database Engine.
    Implements the full schema from Blueprint Page 21-23.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize all V6 tables."""
        with self._get_connection() as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            # 1. Agent Profiles
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_profiles (
                    agent_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    role TEXT,
                    domain TEXT,
                    tier INTEGER,
                    type TEXT,
                    behavioral_rules TEXT,
                    sentiment_triggers TEXT,
                    expertise_areas TEXT,
                    emotion_profile TEXT,
                    accuracy_score REAL DEFAULT 0,
                    total_runs INTEGER DEFAULT 0,
                    created_at INTEGER,
                    source_entity_id TEXT,
                    is_synthetic INTEGER DEFAULT 0
                )
            """)

            # 2. Agent Data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    knowledge_snippets TEXT,
                    facts TEXT,
                    opinions TEXT,
                    relationships TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agent_profiles(agent_id)
                )
            """)

            # 3. Agent Skills
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_skills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    skill_name TEXT,
                    skill_level REAL,
                    domain TEXT,
                    description TEXT,
                    activation_triggers TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agent_profiles(agent_id)
                )
            """)

            # 4. Projects
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    project_id TEXT PRIMARY KEY,
                    name TEXT,
                    description TEXT,
                    domain TEXT,
                    agent_count INTEGER,
                    status TEXT,
                    created_at INTEGER,
                    latest_debate TEXT
                )
            """)

            # 5. Documents
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    title TEXT,
                    content TEXT,
                    content_type TEXT,
                    extracted_entities TEXT,
                    domain_analysis TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                )
            """)

            # 6. Debate Results
            conn.execute("""
                CREATE TABLE IF NOT EXISTS debate_results (
                    run_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    intent TEXT,
                    total_agents INTEGER,
                    shards_processed INTEGER,
                    aggregation TEXT,
                    detailed_debate TEXT,
                    graph_data TEXT,
                    consensus TEXT,
                    created_at INTEGER,
                    FOREIGN KEY (project_id) REFERENCES projects(project_id)
                )
            """)

            # 7. Training Examples
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_examples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    scenario TEXT,
                    virality_risk INTEGER,
                    emotion TEXT,
                    outcome TEXT,
                    lesson TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agent_profiles(agent_id)
                )
            """)

            # 8. FTS5 for Content
            try:
                conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(title, content)")
            except sqlite3.OperationalError:
                # FTS5 might not be available in all sqlite builds, but required by blueprint
                print("[WARNING] FTS5 not available. Search features may be limited.")

            conn.commit()

    # --- CRUD OPERATIONS ---

    def create_project(self, name: str, description: str, domain: str = "GENERAL") -> str:
        import uuid
        import time
        project_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO projects (project_id, name, description, domain, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_id, name, description, domain, "ACTIVE", int(time.time())))
            conn.commit()
        return project_id

    def add_document(self, project_id: str, title: str, content: str, content_type: str) -> str:
        import uuid
        doc_id = str(uuid.uuid4())
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO documents (doc_id, project_id, title, content, content_type)
                VALUES (?, ?, ?, ?, ?)
            """, (doc_id, project_id, title, content, content_type))
            # Sync FTS
            conn.execute("INSERT INTO content_fts (title, content) VALUES (?, ?)", (title, content))
            conn.commit()
        return doc_id

    def save_agent_swarm(self, agents: List[Dict]):
        """Batch save agents with skills and training (V6 Pipeline)."""
        import time
        created_at = int(time.time())
        with self._get_connection() as conn:
            for agent in agents:
                # 1. Profile
                conn.execute("""
                    INSERT OR REPLACE INTO agent_profiles (
                        agent_id, name, role, domain, tier, type, 
                        emotion_profile, is_synthetic, created_at, source_entity_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent["agent_id"], agent["name"], agent["role"], agent["domain"],
                    agent["tier"], agent["type"], agent["emotion_profile"],
                    agent["is_synthetic"], created_at, agent.get("source_entity_id")
                ))
                
                # 2. Skills
                for skill in agent.get("skills", []):
                    conn.execute("""
                        INSERT INTO agent_skills (
                            agent_id, skill_name, skill_level, domain, activation_triggers
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        agent["agent_id"], skill["skill_name"], skill["skill_level"],
                        skill["domain"], json.dumps(skill["activation_triggers"])
                    ))
                
                # 3. Training
                for t in agent.get("training", []):
                    conn.execute("""
                        INSERT INTO training_examples (
                            agent_id, scenario, virality_risk, emotion, outcome, lesson
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        agent["agent_id"], t["scenario"], t["virality_risk"],
                        t["emotion"], t["outcome"], t["lesson"]
                    ))
            conn.commit()

    def get_project(self, project_id: str) -> Optional[Dict]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
            return dict(row) if row else None

    def list_projects(self) -> List[Dict]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM projects ORDER BY created_at DESC").fetchall()
            return [dict(r) for r in rows]
