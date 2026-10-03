import sys
import uvicorn

if __name__ == "__main__":
    print("==================================================================")
    print("  Starting C++ Low-Level Design Mastery Educational Platform")
    print("  Local URL: http://127.0.0.1:8000")
    print("  API Docs:  http://127.0.0.1:8000/api/docs")
    print("==================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)
