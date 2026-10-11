from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database import get_db
from models import User
from dependencies import get_current_user
from services.export_service import generate_verified_csv

router = APIRouter(prefix="/export", tags=["Export"])

@router.get("/verified.csv")
def export_verified_csv(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Downloads the gold-standard verified Sanskrit POS dataset as a UTF-8 CSV.
    Accessible to authorized users/administrators.
    """
    csv_buffer = generate_verified_csv(db)
    csv_bytes = csv_buffer.getvalue().encode('utf-8')

    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=final_pos_verified.csv"
        }
    )
