import sqlite3
import json
import os
from datetime import datetime


class CrisisDatabase:
    """
    Proprietary database of real-world brand crises.
    This generates the True Data Moat.
    """
    
    def __init__(self, db_path: str = "engines/crisis_knowledge.db"):
        self.db_path = db_path
        # Ensure the directory for the databases exists
        db_dir = os.path.dirname(os.path.abspath(db_path))
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        
        # Lazy import ChromaDB for vector search
        try:
            import chromadb
            chroma_path = os.path.join(db_dir, "chroma_db")
            self.chroma_client = chromadb.PersistentClient(path=chroma_path)
            self.collection = self.chroma_client.get_or_create_collection(name="crises")
        except ImportError:
            self.chroma_client = None
            self.collection = None
        
        self._init_tables()
        self._seed_if_empty()
    
    def _init_tables(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS crises (
                id TEXT PRIMARY KEY,
                brand TEXT NOT NULL,
                date TEXT,
                
                -- What happened
                original_content TEXT,
                content_type TEXT,
                industry TEXT,
                
                -- The crisis
                crisis_summary TEXT,
                trigger_phrases TEXT,
                first_platform TEXT,
                
                -- Who reacted
                primary_attacker_type TEXT,
                attacker_demographics TEXT,
                coalition_formed TEXT,
                
                -- Timeline
                hour_1 TEXT,
                hour_6 TEXT,
                hour_24 TEXT,
                day_7 TEXT,
                day_30 TEXT,
                
                -- Impact
                revenue_impact TEXT,
                stock_impact TEXT,
                brand_sentiment_change TEXT,
                customer_churn TEXT,
                legal_consequences TEXT,
                
                -- Resolution
                brand_response TEXT,
                response_effectiveness TEXT,
                recovery_timeline TEXT,
                
                -- Analysis
                root_cause TEXT,
                warning_signs TEXT,
                what_would_have_prevented_it TEXT,
                similar_crises TEXT,
                
                -- Metadata
                sources TEXT,
                confidence_in_data TEXT,
                added_date TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT
            )
        """)
        
        # Full-text search for similarity matching
        self.db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS crises_fts 
            USING fts5(
                brand, original_content, crisis_summary, 
                trigger_phrases, root_cause, warning_signs,
                content='crises', content_rowid='rowid'
            )
        """)
        
        self.db.commit()

    def _seed_if_empty(self):
        count = self.db.execute("SELECT COUNT(*) FROM crises").fetchone()[0]
        if count == 0:
            self.seed_initial_data()
    
    def find_similar_crises(self, content: str, industry: str = None, limit: int = 5) -> list:
        """Find historical crises similar to the given content using ChromaDB vector search."""
        if not content:
            return []

        try:
            # Vector search via ChromaDB
            results = self.collection.query(
                query_texts=[content],
                n_results=limit,
                where={"industry": industry} if (industry and industry != 'all' and industry != 'general') else None
            )
            
            ids = results.get('ids', [[]])[0]
            if not ids:
                # Fallback to SQLite FTS if vector search returns nothing
                return self._find_similar_fts(content, industry, limit)
            
            # Fetch full data from SQLite using the IDs from Chroma
            placeholders = ", ".join(["?" for _ in ids])
            query = f"SELECT * FROM crises WHERE id IN ({placeholders})"
            self.db.row_factory = sqlite3.Row
            cursor = self.db.execute(query, ids)
            
            # Re-order results to match Chroma's similarity ranking
            rows = {row['id']: dict(row) for row in cursor.fetchall()}
            sorted_results = [rows[id] for id in ids if id in rows]
            return sorted_results
            
        except Exception as e:
            print(f"[DB WARN] Chroma query failed, falling back to FTS: {e}")
            return self._find_similar_fts(content, industry, limit)

    def _find_similar_fts(self, content: str, industry: str = None, limit: int = 5) -> list:
        """Historical FTS fallback."""
        words = content.lower().split()
        words = [w for w in words if len(w) > 3]
        search_query = " OR ".join(words[:15])
        
        if not search_query: return []
        
        try:
            query = """
                SELECT c.*, rank
                FROM crises_fts fts
                JOIN crises c ON c.rowid = fts.rowid
                WHERE crises_fts MATCH ?
            """
            params = [search_query]
            if industry and industry not in ['all', 'general']:
                query += " AND c.industry = ?"
                params.append(industry)
            query += " ORDER BY rank LIMIT ?"
            params.append(limit)
            
            self.db.row_factory = sqlite3.Row
            cursor = self.db.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
    
    def get_crisis_context_for_prompt(self, content: str, industry: str = None) -> str:
        """Generate context string for the LLM prompt based on similar crises."""
        similar = self.find_similar_crises(content, industry, limit=3)
        if not similar:
            return "No similar historical crises found in database."
        
        context = "HISTORICAL CRISIS CONTEXT (use this to ground your analysis):\n\n"
        for crisis in similar:
            context += f"""
SIMILAR CRISIS: {crisis['brand']} ({crisis['date']})
What happened: {crisis['crisis_summary']}
Trigger phrases: {crisis['trigger_phrases']}
Impact: {crisis['revenue_impact']}
Root cause: {crisis['root_cause']}
Warning signs: {crisis['warning_signs']}
---
"""
        return context
    
    def seed_initial_data(self):
        """Seed with deeply researched crisis data."""
        crises = [
            {
                "id": "pepsi-kendall-2017",
                "brand": "Pepsi",
                "date": "2017-04-04",
                "original_content": "Live for Now campaign featuring Kendall Jenner offering Pepsi to police officer at protest. Keywords: protest, police, together, conversation",
                "content_type": "ad_copy",
                "industry": "food",
                "crisis_summary": "Ad trivialized Black Lives Matter protests by suggesting a can of Pepsi could resolve police-community tensions",
                "trigger_phrases": json.dumps(["bring people together", "join the conversation", "live for now", "protest imagery used commercially"]),
                "first_platform": "Twitter",
                "primary_attacker_type": "activist",
                "coalition_formed": json.dumps(["activist", "journalist", "genz"]),
                "hour_1": "Bernice King tweets 'If only Daddy would have known about the power of #Pepsi' with photo of MLK",
                "hour_6": "Trending worldwide. Every major outlet covering it. #PepsiGate",
                "hour_24": "Pepsi pulls ad. Issues apology.",
                "day_7": "Becomes textbook case of tone-deaf advertising",
                "day_30": "Permanent association. Still referenced in marketing classes.",
                "revenue_impact": "$5M+ in production costs wasted.",
                "stock_impact": "Minimal but brand favorability dropped 10%",
                "brand_sentiment_change": "-35% favorability in 18-34 demographic",
                "root_cause": "Using social justice imagery to sell product without genuine commitment",
                "warning_signs": json.dumps([
                    "Using protest imagery commercially",
                    "Celebrity without authentic connection to cause",
                    "Trivializing serious social movement"
                ]),
                "what_would_have_prevented_it": "Testing with actual activists and affected communities before production.",
                "sources": json.dumps(["NYT", "Washington Post", "AdAge"])
            },
            {
                "id": "budlight-mulvaney-2023",
                "brand": "Bud Light",
                "date": "2023-04-01",
                "original_content": "Partnership with transgender influencer Dylan Mulvaney celebrating 365 days of girlhood. Keywords: inclusive, influencer",
                "content_type": "social_post",
                "industry": "food",
                "crisis_summary": "Brand caught between progressive and conservative audiences. Both sides attacked. Lost trust of core customer base.",
                "trigger_phrases": json.dumps(["365 days of girlhood", "trans visibility", "partnership with trans influencer"]),
                "first_platform": "Instagram/Twitter simultaneously",
                "primary_attacker_type": "conservative",
                "coalition_formed": json.dumps(["conservative", "parent", "competitor"]),
                "hour_1": "Conservative influencers begin boycott calls",
                "hour_6": "Viral boycott videos load online",
                "hour_24": "Retailer reports declining sales.",
                "day_7": "Sales down 26%. CEO scrambles. No public defense of partnership.",
                "day_30": "Lost #1 US beer position.",
                "revenue_impact": "$1.4B market cap decline. Lost #1 US beer position to Modelo.",
                "stock_impact": "-20% over 3 months",
                "brand_sentiment_change": "-50% among core demographic",
                "root_cause": "Failed to anticipate backlash AND failed to support partner, alienating BOTH sides",
                "warning_signs": json.dumps([
                    "Content touching identity in polarized climate",
                    "Core customer base misaligned with messaging",
                    "No crisis response plan prepared"
                ]),
                "what_would_have_prevented_it": "Either don't do partnership, or prepare exact defense and stand by it.",
                "sources": json.dumps(["WSJ", "Bloomberg"])
            },
            {
                "id": "hm-monkey-2018",
                "brand": "H&M",
                "date": "2018-01-08",
                "original_content": "Product listing showing Black child modeling green hoodie with text 'coolest monkey in the jungle'. Keywords: fashion, kids, apparel",
                "content_type": "product_page",
                "industry": "fashion",
                "crisis_summary": "Racist imagery: Black child wearing 'monkey' text hoodie. Global outrage. Stores vandalized.",
                "trigger_phrases": json.dumps(["coolest monkey in the jungle", "monkey imagery with Black child"]),
                "first_platform": "Twitter",
                "primary_attacker_type": "activist",
                "coalition_formed": json.dumps(["activist", "journalist", "genz", "parent"]),
                "hour_1": "Screenshots spread on Twitter/Instagram",
                "hour_6": "Celebrities condemn. Worldwide trending.",
                "hour_24": "H&M issues apology. Removes product globally.",
                "day_7": "Stores vandalized in South Africa.",
                "day_30": "Hired diversity leader. Permanent brand association with racism.",
                "revenue_impact": "Multiple celebrity partnerships lost. Store damages.",
                "stock_impact": "-5% in first week",
                "brand_sentiment_change": "Severe damage to diverse buyer trust",
                "root_cause": "No diversity review in product/marketing pipeline.",
                "warning_signs": json.dumps([
                    "Animal references combined with children of color",
                    "No diverse review panel for product imagery",
                    "Automated product photography without editorial review"
                ]),
                "what_would_have_prevented_it": "One person of color in the approval chain would have caught this instantly.",
                "sources": json.dumps(["BBC", "CNN", "Guardian"])
            }
        ]
        
        for crisis in crises:
            columns = ", ".join(crisis.keys())
            placeholders = ", ".join(["?" for _ in crisis])
            try:
                # 1. Update SQLite
                self.db.execute(
                    f"INSERT OR REPLACE INTO crises ({columns}) VALUES ({placeholders})",
                    list(crisis.values())
                )
                # 2. Update ChromaDB
                self.collection.upsert(
                    ids=[crisis["id"]],
                    documents=[f"{crisis['brand']} {crisis['crisis_summary']} {crisis['trigger_phrases']} {crisis['root_cause']}"],
                    metadatas=[{"industry": crisis["industry"], "brand": crisis["brand"]}]
                )
            except Exception as e:
                print(f"[DB SEED ERROR] {e}")
        
        # Rebuild FTS table to ensure contents sync
        self.db.execute("INSERT INTO crises_fts(crises_fts) VALUES('rebuild')")
        self.db.commit()
