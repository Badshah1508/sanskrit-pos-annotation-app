import sys
import os

# Ensure backend directory and repo directory are in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
repo_dir = os.path.dirname(backend_dir)
if repo_dir not in sys.path:
    sys.path.insert(0, repo_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from config import settings
from models import TagInventory, User, Sentence
from auth import get_password_hash

# Import routers
from routes.auth_routes import router as auth_router
from routes.dataset_routes import router as dataset_router
from routes.annotation_routes import router as annotation_router
from routes.admin_routes import router as admin_router
from routes.export_routes import router as export_router

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Cross-Domain Sanskrit POS Annotation & Expert Verification Web Application API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For flexible local access, can restrict via settings.CORS_ORIGINS in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup routine: Seed tags and default admin if needed
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # 1. Seed Tag Inventory if empty
        tag_count = db.query(TagInventory).count()
        if tag_count == 0:
            print("Seeding Sanskrit Consortium Tag Inventory...")
            for tag_name in settings.APPROVED_SANSKRIT_TAGS:
                tag_record = TagInventory(
                    tag=tag_name,
                    name=f"Sanskrit Consortium Tag {tag_name}",
                    description=f"Approved Consortium Tag: {tag_name}"
                )
                db.add(tag_record)
            db.commit()

        # 2. Check and ensure 7 expert assignments are set up if sentences exist
        sentence_count = db.query(Sentence).count()
        if sentence_count == 7000:
            assigned_count = db.query(Sentence).filter(Sentence.assigned_expert_id.isnot(None)).count()
            user7_exists = db.query(User).filter(User.username == "user7").first()
            if assigned_count < 7000 or not user7_exists:
                print("Setting up 7 expert workspace assignments...")
                from scripts.setup_expert_assignments import setup_assignments
                setup_assignments(db)
        elif db.query(User).count() == 0:
            # Seed fallback default admin
            admin_user = User(
                username="admin",
                email="admin@example.ac.in",
                password_hash=get_password_hash("admin123"),
                role="admin",
                display_name="Administrator"
            )
            db.add(admin_user)
            db.commit()
    finally:
        db.close()

# Health check endpoint
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "database": settings.DATABASE_URL.split("://")[0]
    }

# Tag listing endpoint
@app.get("/api/tags")
def get_approved_tags():
    return {
        "tags": settings.APPROVED_SANSKRIT_TAGS
    }

# Mount routers under /api
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(dataset_router, prefix=settings.API_PREFIX)
app.include_router(annotation_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)
app.include_router(export_router, prefix=settings.API_PREFIX)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
