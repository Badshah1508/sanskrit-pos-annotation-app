import sys
import os

# Ensure backend directory is in sys.path if it exists
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
if os.path.isdir(backend_dir) and backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from backend.main import app
except (ModuleNotFoundError, ImportError):
    try:
        from main import app
    except (ModuleNotFoundError, ImportError):
        import main
        app = main.app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
