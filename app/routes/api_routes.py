from typing import Optional, List
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from app.database import get_db
from app.services.competency_engine import calculate_trainer_competency
from app.services.certificate_service import verify_certificate_by_id

router = APIRouter(prefix="/api", tags=["api"])

@router.get("/competency/query")
def api_competency_query(
    subject: str = Query(..., description="Subject or skill keywords"),
    domain: Optional[str] = Query(None),
    min_experience: int = Query(0)
):
    ranked = calculate_trainer_competency(
        subject=subject,
        domain=domain,
        required_skills=[],
        min_experience=min_experience
    )
    return JSONResponse({"status": "success", "subject": subject, "count": len(ranked), "results": ranked})

@router.get("/certificate/verify/{cert_id}")
def api_verify_certificate(cert_id: str):
    cert = verify_certificate_by_id(cert_id)
    if not cert:
        return JSONResponse({"status": "error", "message": "Certificate ID not found or invalid"}, status_code=404)
    return JSONResponse({"status": "success", "certificate": cert})

@router.get("/admin/chart-data")
def api_admin_charts():
    with get_db() as db:
        cursor = db.cursor()
        
        # Domain distribution
        cursor.execute("SELECT domain, COUNT(*) as count FROM courses GROUP BY domain")
        domains = [dict(row) for row in cursor.fetchall()]

        # Regional Observatory Participation (Realistic IMD Regional Meteorological Centers)
        regional_stats = [
            {"region": "RMC New Delhi (North)", "trainees": 42, "completed": 35},
            {"region": "RMC Kolkata (East)", "trainees": 38, "completed": 29},
            {"region": "RMC Chennai (South)", "trainees": 45, "completed": 39},
            {"region": "RMC Mumbai (West)", "trainees": 36, "completed": 30},
            {"region": "RMC Guwahati (North-East)", "trainees": 24, "completed": 19},
            {"region": "NCS / INCOIS (Oceanic & Seismo)", "trainees": 28, "completed": 24}
        ]

        # Monthly Certification Trends
        monthly_trends = [
            {"month": "Oct 2025", "certificates": 14, "attempts": 22},
            {"month": "Nov 2025", "certificates": 21, "attempts": 34},
            {"month": "Dec 2025", "certificates": 35, "attempts": 48},
            {"month": "Jan 2026", "certificates": 42, "attempts": 56},
            {"month": "Feb 2026", "certificates": 58, "attempts": 74},
            {"month": "Mar 2026", "certificates": 65, "attempts": 82}
        ]

        return JSONResponse({
            "domains": domains,
            "regional_stats": regional_stats,
            "monthly_trends": monthly_trends
        })
