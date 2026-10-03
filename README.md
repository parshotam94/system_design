# C++ Low-Level Design Mastery Educational Platform

A comprehensive, production-grade interactive educational and interview-preparation platform built with modern HTML5, CSS3, Vanilla JavaScript, and a FastAPI Python backend.

---

## 🌟 Tech Stack

* **Frontend**: HTML5, CSS3 (Dark Glassmorphic Developer Theme), Vanilla JavaScript (No React/Vue/Node).
* **Backend**: Python 3.13, FastAPI, Jinja2, Uvicorn.
* **Domain Language**: Modern C++20 for all Low-Level System Design architecture examples.

---

## 🚀 How to Run

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python run.py
```

3. Open your browser:
* **Platform URL**: `http://127.0.0.1:8000`
* **API Documentation**: `http://127.0.0.1:8000/api/docs`

---

## 🏗️ Architecture & Core Components

1. **24-Module LLD Roadmap & Navigation**:
   * Complete metadata in `app/data/roadmap.json`
   * Left collapsible sidebar with progress badges (`Not Started`, `In Progress`, `Completed`)
   * Dynamic progress calculator stored in `localStorage`

2. **Interactive LLD Architecture Mental Pipeline**:
   * `Requirements → Entities → Responsibilities → Classes → Relationships → Interfaces → Design Patterns → Implementation → Trade-offs`
   * Interactive hover and click simulation with real-world examples.

3. **Reusable Educational Components**:
   * `CodeBlock`: C++ syntax highlighting, line numbers, copy button with tooltip, file headers.
   * `ClassDiagram`: UML Class diagrams with public (`+`), private (`-`), protected (`#`) symbols, relationship arrows (`──▷`, `──◆`, `──◇`, `..>`), and hover inspector cards.
   * `AnimationPlayer`: Step-by-step interactive simulation engine for object lifetimes, vtables, observer notifications, and mutex contention.
   * `ComparisonTable`: Structured matrix for side-by-side architectural trade-offs.
   * `RefactorMode`: Before vs After code refactoring with design smell detectors.
   * `PracticeMode`: "Design This Yourself" revealable challenge system.

4. **Global Search (`Ctrl+K`)**:
   * Fast fuzzy and token-based search modal across all design concepts and patterns.
