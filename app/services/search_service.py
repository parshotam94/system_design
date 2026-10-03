import json
from pathlib import Path
from typing import List, Dict, Any
from app.config import DATA_DIR

class SearchService:
    def __init__(self):
        self._index: List[Dict[str, Any]] = []
        self._load_index()

    def _load_index(self):
        index_file = DATA_DIR / "search_index.json"
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    self._index = json.load(f)
            except Exception as e:
                print(f"[SearchService] Failed to load search_index.json: {e}")
                self._index = []
        else:
            self._index = []

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self._index:
            self._load_index()

        if not query or not query.strip():
            return []
        
        q = query.strip().lower()
        results = []
        for item in self._index:
            title = (item.get("title") or item.get("term") or "").lower()
            summary = (item.get("summary") or item.get("snippet") or "").lower()
            category = (item.get("module_title") or item.get("category") or "").lower()
            tags = [t.lower() for t in item.get("tags", [])]
            
            score = 0
            if q in title:
                score += 50
                if title.startswith(q):
                    score += 50
            if any(q in t for t in tags):
                score += 35
            if q in summary:
                score += 20
            if q in category:
                score += 15
            
            if score > 0:
                result_item = dict(item)
                result_item["score"] = score
                results.append(result_item)
                
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

search_service = SearchService()
