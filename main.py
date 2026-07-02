from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, users, fishing_logs, catches, schedules, stats, weather, ai, admin, public
from app.services.scheduler_service import start_scheduler

# 모든 모델 임포트 (테이블 생성을 위해)
from app.models import user, fishing_log, catch, harbor, schedule

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fishing Daily API",
    description="선상 낚시 기록 관리 플랫폼",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in [
    auth.router, users.router, fishing_logs.router,
    catches.router, schedules.router, stats.router,
    weather.router, ai.router, admin.router, public.router
]:
    app.include_router(router)

@app.on_event("startup")
async def startup_event():
    start_scheduler()
    _seed_initial_data()

def _seed_initial_data():
    """초기 항구 데이터 시딩"""
    from app.database import SessionLocal
    from app.models.harbor import Harbor
    db = SessionLocal()
    try:
        if db.query(Harbor).count() == 0:
            harbors = [
                Harbor(name="통영항", region="경남 통영", latitude=34.8544, longitude=128.4330, obs_code="DT_0024"),
                Harbor(name="여수항", region="전남 여수", latitude=34.7404, longitude=127.7403, obs_code="DT_0006"),
                Harbor(name="부산 다대포항", region="부산 사하구", latitude=35.0470, longitude=128.9617, obs_code="DT_0002"),
                Harbor(name="인천항", region="인천", latitude=37.4563, longitude=126.6061, obs_code="DT_0001"),
                Harbor(name="속초항", region="강원 속초", latitude=38.2067, longitude=128.5904, obs_code="DT_0051"),
                Harbor(name="포항 구룡포항", region="경북 포항", latitude=35.9870, longitude=129.5600, obs_code="DT_0019"),
                Harbor(name="제주 성산포항", region="제주 서귀포", latitude=33.4684, longitude=126.9272, obs_code="DT_0061"),
            ]
            db.add_all(harbors)
            db.commit()
    finally:
        db.close()

@app.get("/health")
def health_check():
    import os
    return {
        "status": "ok",
        "service": "Fishing Daily",
        "llm_provider": os.environ.get("LLM_PROVIDER", "NOT SET"),
        "gemini_key_set": bool(os.environ.get("GEMINI_API_KEY")),
        "gemini_key_prefix": os.environ.get("GEMINI_API_KEY", "")[:5] or "EMPTY"
    }
