from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
CONTENT_DIR = BASE_DIR / "content"
HLD_CONTENT_DIR = CONTENT_DIR / "hld"

APP_TITLE = "C++ Low-Level & High-Level System Design Mastery"
APP_SUBTITLE = "The complete end-to-end platform for mastering LLD in C++ and large-scale distributed High-Level System Design."
APP_VERSION = "2.0.0"
