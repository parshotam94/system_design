from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
CONTENT_DIR = BASE_DIR / "content"

APP_TITLE = "C++ Low-Level Design Mastery"
APP_SUBTITLE = "Learn how to design maintainable, extensible and scalable object-oriented systems in C++."
APP_VERSION = "1.0.0"
