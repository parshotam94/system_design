from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import STATIC_DIR, APP_TITLE, APP_SUBTITLE, APP_VERSION
from app.routes.pages import router as pages_router
from app.routes.modules_api import router as modules_router
from app.routes.search_api import router as search_router

app = FastAPI(
    title=APP_TITLE,
    description=APP_SUBTITLE,
    version=APP_VERSION,
    docs_url="/api/docs",
    redoc_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include routers
app.include_router(modules_router)
app.include_router(search_router)
app.include_router(pages_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": APP_TITLE, "version": APP_VERSION}
