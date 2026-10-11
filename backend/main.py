import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from config import settings
from models import TagInventory, User
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

        # 2. Seed default admin and expert if users table is empty
        user_count = db.query(User).count()
        if user_count == 0:
            print("Creating default users (admin & scholar)...")
            admin_user = User(
                username="admin",
                email="admin@example.ac.in",
                password_hash=get_password_hash("admin123"),
                role="admin"
            )
            expert_user = User(
                username="sanskrit_scholar",
                email="scholar@example.ac.in",
                password_hash=get_password_hash("password123"),
                role="expert"
            )
            db.add(admin_user)
            db.add(expert_user)
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
