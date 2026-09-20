from fastapi import APIRouter, Request

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/health")
async def health_check(request: Request):
    try:
        await request.app.state.db.command("ping")
        db_status = "connected"
    except Exception as exc:
        db_status = f"error: {exc}"
    return {
        "status": "ok",
        "environment": request.app.state.settings.environment,
        "database": db_status,
        "ml_artifacts_loaded": request.app.state.ml_artifacts is not None,
    }
