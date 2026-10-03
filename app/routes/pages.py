import json
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import TEMPLATES_DIR, DATA_DIR, CONTENT_DIR, APP_TITLE, APP_SUBTITLE, APP_VERSION

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def get_roadmap():
    roadmap_file = DATA_DIR / "roadmap.json"
    if roadmap_file.exists():
        with open(roadmap_file, "r", encoding="utf-8") as f:
            return json.load(f).get("modules", [])
    return []

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    modules = get_roadmap()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "active_page": "home"
    })

@router.get("/module/{module_id}", response_class=HTMLResponse)
async def module_page(request: Request, module_id: str):
    modules = get_roadmap()
    matched_module = None
    prev_module = None
    next_module = None

    for idx, mod in enumerate(modules):
        if mod["id"] == module_id or mod["slug"] == module_id:
            matched_module = mod
            if idx > 0:
                prev_module = modules[idx - 1]
            if idx < len(modules) - 1:
                next_module = modules[idx + 1]
            break

    if not matched_module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Look for content in content/
    content_file = CONTENT_DIR / f"module_{matched_module['id']}.json"
    module_content = None
    if content_file.exists():
        try:
            with open(content_file, "r", encoding="utf-8") as cf:
                module_content = json.load(cf)
        except Exception as e:
            print(f"Error reading module content: {e}")

    return templates.TemplateResponse("module.html", {
        "request": request,
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "current_module": matched_module,
        "module_content": module_content,
        "prev_module": prev_module,
        "next_module": next_module,
        "active_page": "module",
        "active_module_id": matched_module["id"]
    })

@router.get("/playground", response_class=HTMLResponse)
async def playground_page(request: Request):
    modules = get_roadmap()
    return templates.TemplateResponse("playground.html", {
        "request": request,
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "active_page": "playground"
    })

@router.get("/interview-framework", response_class=HTMLResponse)
async def interview_framework_page(request: Request):
    modules = get_roadmap()
    return templates.TemplateResponse("framework.html", {
        "request": request,
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "active_page": "framework"
    })

@router.get("/cheat-sheets", response_class=HTMLResponse)
async def cheat_sheets_page(request: Request):
    modules = get_roadmap()
    return templates.TemplateResponse("cheatsheets.html", {
        "request": request,
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "active_page": "cheatsheets"
    })
