import json
from pathlib import Path
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.config import (
    TEMPLATES_DIR, DATA_DIR, CONTENT_DIR, HLD_CONTENT_DIR,
    APP_TITLE, APP_SUBTITLE, APP_VERSION
)

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

def get_roadmap():
    roadmap_file = DATA_DIR / "roadmap.json"
    if roadmap_file.exists():
        with open(roadmap_file, "r", encoding="utf-8") as f:
            return json.load(f).get("modules", [])
    return []

def get_hld_roadmap():
    hld_file = DATA_DIR / "hld_roadmap.json"
    if hld_file.exists():
        with open(hld_file, "r", encoding="utf-8") as f:
            return json.load(f).get("modules", [])
    return []

# =========================================================================
# LOW-LEVEL DESIGN (LLD) ROUTES
# =========================================================================

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    modules = get_roadmap()
    hld_modules = get_hld_roadmap()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_title": "C++ Low-Level Design Mastery",
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "hld_modules": hld_modules,
        "active_page": "home",
        "active_track": "lld"
    })

@router.get("/module/{module_id}", response_class=HTMLResponse)
async def module_page(request: Request, module_id: str):
    modules = get_roadmap()
    hld_modules = get_hld_roadmap()
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
        raise HTTPException(status_code=404, detail="LLD Module not found")

    content_file = CONTENT_DIR / f"module_{matched_module['id']}.json"
    module_content = None
    if content_file.exists():
        try:
            with open(content_file, "r", encoding="utf-8") as cf:
                module_content = json.load(cf)
        except Exception as e:
            print(f"Error reading LLD module content: {e}")

    return templates.TemplateResponse("module.html", {
        "request": request,
        "app_title": f"LLD Module {matched_module['id']}: {matched_module['title']}",
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "hld_modules": hld_modules,
        "current_module": matched_module,
        "module_content": module_content,
        "prev_module": prev_module,
        "next_module": next_module,
        "active_page": "module",
        "active_module_id": matched_module["id"],
        "active_track": "lld"
    })

@router.get("/playground", response_class=HTMLResponse)
async def playground_page(request: Request):
    modules = get_roadmap()
    hld_modules = get_hld_roadmap()
    return templates.TemplateResponse("playground.html", {
        "request": request,
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "hld_modules": hld_modules,
        "active_page": "playground",
        "active_track": "lld"
    })

@router.get("/interview-framework", response_class=HTMLResponse)
async def interview_framework_page(request: Request):
    modules = get_roadmap()
    hld_modules = get_hld_roadmap()
    return templates.TemplateResponse("framework.html", {
        "request": request,
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "hld_modules": hld_modules,
        "active_page": "framework",
        "active_track": "lld"
    })

@router.get("/cheat-sheets", response_class=HTMLResponse)
async def cheat_sheets_page(request: Request):
    modules = get_roadmap()
    hld_modules = get_hld_roadmap()
    return templates.TemplateResponse("cheatsheets.html", {
        "request": request,
        "app_title": APP_TITLE,
        "app_subtitle": APP_SUBTITLE,
        "app_version": APP_VERSION,
        "modules": modules,
        "hld_modules": hld_modules,
        "active_page": "cheatsheets",
        "active_track": "lld"
    })

# =========================================================================
# HIGH-LEVEL DESIGN (HLD) / SYSTEM DESIGN ROUTES
# =========================================================================

@router.get("/hld", response_class=HTMLResponse)
async def hld_home_page(request: Request):
    modules = get_roadmap()
    hld_modules = get_hld_roadmap()
    return templates.TemplateResponse("hld_index.html", {
        "request": request,
        "app_title": "High-Level Design & System Design Mastery",
        "app_subtitle": "Learn how real-world software systems are designed, scaled, secured, deployed, monitored, and evolved.",
        "app_version": APP_VERSION,
        "modules": modules,
        "hld_modules": hld_modules,
        "active_page": "hld_home",
        "active_track": "hld",
        "is_hld": True
    })

@router.get("/hld/module/{module_id}", response_class=HTMLResponse)
async def hld_module_page(request: Request, module_id: str):
    modules = get_roadmap()
    hld_modules = get_hld_roadmap()
    matched_module = None
    prev_module = None
    next_module = None

    for idx, mod in enumerate(hld_modules):
        if mod["id"] == module_id or mod["slug"] == module_id:
            matched_module = mod
            if idx > 0:
                prev_module = hld_modules[idx - 1]
            if idx < len(hld_modules) - 1:
                next_module = hld_modules[idx + 1]
            break

    if not matched_module:
        raise HTTPException(status_code=404, detail="HLD Module not found")

    content_file = HLD_CONTENT_DIR / f"module_{matched_module['id']}.json"
    module_content = None
    if content_file.exists():
        try:
            with open(content_file, "r", encoding="utf-8") as cf:
                module_content = json.load(cf)
        except Exception as e:
            print(f"Error reading HLD module content: {e}")

    return templates.TemplateResponse("hld_module.html", {
        "request": request,
        "app_title": f"HLD Module {matched_module['id']}: {matched_module['title']}",
        "app_subtitle": "High-Level System Design Mastery",
        "app_version": APP_VERSION,
        "modules": modules,
        "hld_modules": hld_modules,
        "current_module": matched_module,
        "module_content": module_content,
        "prev_module": prev_module,
        "next_module": next_module,
        "active_page": "hld_module",
        "active_module_id": matched_module["id"],
        "active_track": "hld",
        "is_hld": True
    })

@router.get("/hld/calculator", response_class=HTMLResponse)
async def hld_calculator_page(request: Request):
    modules = get_roadmap()
    hld_modules = get_hld_roadmap()
    return templates.TemplateResponse("hld_index.html", {
        "request": request,
        "app_title": "Capacity Estimation Calculator - High-Level Design",
        "app_subtitle": "Interactive Back-of-the-Envelope Capacity Estimator for System Design Interviews.",
        "app_version": APP_VERSION,
        "modules": modules,
        "hld_modules": hld_modules,
        "active_page": "hld_calculator",
        "active_track": "hld",
        "is_hld": True
    })
