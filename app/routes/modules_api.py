import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.config import DATA_DIR, CONTENT_DIR

router = APIRouter(prefix="/api/modules", tags=["Modules"])

def get_roadmap_data():
    roadmap_file = DATA_DIR / "roadmap.json"
    if not roadmap_file.exists():
        raise HTTPException(status_code=500, detail="Roadmap data not found")
    with open(roadmap_file, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("")
def list_modules():
    data = get_roadmap_data()
    return data

@router.get("/{module_id}")
def get_module(module_id: str):
    data = get_roadmap_data()
    for mod in data.get("modules", []):
        if mod["id"] == module_id or mod["slug"] == module_id:
            # Check if specialized content json exists in content/
            content_file = CONTENT_DIR / f"module_{mod['id']}.json"
            content_data = None
            if content_file.exists():
                try:
                    with open(content_file, "r", encoding="utf-8") as cf:
                        content_data = json.load(cf)
                except Exception as e:
                    print(f"Error reading {content_file}: {e}")
            return {
                "meta": mod,
                "content": content_data,
                "is_ready": content_data is not None
            }
    raise HTTPException(status_code=404, detail=f"Module '{module_id}' not found")
