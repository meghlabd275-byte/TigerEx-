from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/status")
async def admin_status():
    return {"status": "active", "service": "crypto-education"}

@router.post("/courses")
async def create_course(course: dict):
    return {"status": "created", "course": course}

@router.get("/metrics")
async def get_metrics():
    return {
        "total_enrollments": 0,
        "courses_completed": 0,
        "average_quiz_score": 0
    }