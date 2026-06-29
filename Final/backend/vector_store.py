import os
import sqlite3
import json
import numpy as np
import logging
from embedder import get_embedding

logger = logging.getLogger("VectorStore")

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "vector_store.db")

class VectorStore:
    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_embeddings (
                company_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                embedding TEXT NOT NULL,
                metadata TEXT,
                document TEXT
            )
        """)
        self.conn.commit()

    def remove_company(self, company_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM company_embeddings WHERE company_id = ?", (company_id,))
        self.conn.commit()
        logger.info(f"Evicted company ID {company_id} from VectorStore.")

    def get_cached_ids(self) -> set[int]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT company_id FROM company_embeddings")
        return {row[0] for row in cursor.fetchall()}

    def build_company_document(self, company: dict) -> str:
        """
        Creates a clean descriptive document from company attributes to generate embeddings.
        """
        name = company.get("name", "")
        category = company.get("category", "")
        overview = company.get("overview_text", "")
        sectors = company.get("focus_sectors", "")
        value_prop = company.get("core_value_proposition", "")
        differentiators = company.get("unique_differentiators", "")
        tech_stack = company.get("tech_stack", "")
        ai_adoption = company.get("ai_ml_adoption_level", "")
        
        doc = (
            f"Company Name: {name}\n"
            f"Category/Industry: {category}\n"
            f"Overview: {overview}\n"
            f"Focus Sectors: {sectors}\n"
            f"Core Value Proposition: {value_prop}\n"
            f"Unique Differentiators: {differentiators}\n"
            f"Technology Stack: {tech_stack}\n"
            f"AI and ML Adoption: {ai_adoption}"
        )
        return doc

    def index_companies(self, companies: list[dict]):
        """
        Indexes a list of companies from Supabase. Checks for duplicates and updates.
        """
        cached_ids = self.get_cached_ids()
        cursor = self.conn.cursor()
        
        indexed_count = 0
        for comp in companies:
            comp_id = comp.get("company_id")
            if not comp_id:
                continue
                
            # If already cached, we skip to save API costs.
            # But if metadata/name changed, we could overwrite it.
            if comp_id in cached_ids:
                continue
                
            name = comp.get("name", "")
            document = self.build_company_document(comp)
            logger.info(f"Generating embedding for: '{name}' (ID: {comp_id})")
            
            embedding = get_embedding(document)
            
            # Save to SQLite
            cursor.execute(
                "INSERT OR REPLACE INTO company_embeddings (company_id, name, embedding, metadata, document) VALUES (?, ?, ?, ?, ?)",
                (
                    comp_id,
                    name,
                    json.dumps(embedding),
                    json.dumps(comp),
                    document
                )
            )
            indexed_count += 1
            
        if indexed_count > 0:
            self.conn.commit()
            logger.info(f"Successfully indexed {indexed_count} new companies into VectorStore.")

    def load_all(self) -> list[dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT company_id, name, embedding, metadata, document FROM company_embeddings")
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append({
                "company_id": row[0],
                "name": row[1],
                "embedding": np.array(json.loads(row[2]), dtype=np.float32),
                "metadata": json.loads(row[3]) if row[4] else {},
                "document": row[4]
            })
        return results

    def cosine_similarity(self, v1, v2) -> float:
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))

    def semantic_search(self, query: str, top_n: int = 5) -> list[dict]:
        """
        Performs semantic cosine similarity search across all cached company embeddings.
        """
        query_vector = np.array(get_embedding(query), dtype=np.float32)
        all_records = self.load_all()
        
        if not all_records:
            return []
            
        scored_records = []
        for rec in all_records:
            score = self.cosine_similarity(query_vector, rec["embedding"])
            scored_records.append({
                "company_id": rec["company_id"],
                "name": rec["name"],
                "score": score,
                "metadata": rec["metadata"]
            })
            
        # Sort by similarity score descending
        scored_records.sort(key=lambda x: x["score"], reverse=True)
        return scored_records[:top_n]

    def get_similar_companies(self, target_company_id: int, top_n: int = 5) -> list[dict]:
        """
        Finds similar companies to a target company already in the vector database.
        """
        all_records = self.load_all()
        if not all_records:
            return []
            
        target_rec = None
        for rec in all_records:
            if rec["company_id"] == target_company_id:
                target_rec = rec
                break
                
        if target_rec is None:
            return []
            
        scored_records = []
        for rec in all_records:
            if rec["company_id"] == target_company_id:
                continue # Skip self
            score = self.cosine_similarity(target_rec["embedding"], rec["embedding"])
            scored_records.append({
                "company_id": rec["company_id"],
                "name": rec["name"],
                "score": score,
                "metadata": rec["metadata"]
            })
            
        scored_records.sort(key=lambda x: x["score"], reverse=True)
        return scored_records[:top_n]
