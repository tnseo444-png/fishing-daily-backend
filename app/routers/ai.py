from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.fishing_log import FishingLog
from app.models.catch import Catch
from app.services.llm_service import llm_service
from app.utils.dependencies import get_current_user
import json

router = APIRouter(prefix="/api/ai", tags=["AI Analysis"])

SYSTEM_PROMPT = """당신은 선상 낚시 전문 분석가입니다.
낚시 기록 데이터를 분석하여 조과 패턴, 최적 시간대, 포인트 특성, 개선 방안을
전문적이고 친근한 어조로 한국어로 제공합니다.
수치 데이터를 근거로 구체적인 인사이트를 제시하세요."""

@router.post("/analyze/log/{log_id}")
async def analyze_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    log = db.query(FishingLog).filter(FishingLog.id == log_id, FishingLog.user_id == current_user.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="기록 없음")

    catches = db.query(Catch).filter(Catch.fishing_log_id == log_id).all()
    catch_summary = [
        {"어종": c.species, "마리수": c.count, "총무게(kg)": float(c.total_weight or 0)}
        for c in catches
    ]

    user_message = f"""다음 낚시 기록을 분석해 주세요:

- 출조 날짜: {log.log_date}
- 항구: {log.custom_harbor or log.harbor_id}
- 선박: {log.custom_boat}
- 낚시 포인트: {log.fishing_point}
- 날씨: {log.weather_desc}, 기온 {log.weather_temp}°C, 풍속 {log.weather_wind}m/s
- 물때: {log.tide_name} ({log.tide_level})
- 총 조과: {log.total_count}마리
- 어종별 결과: {json.dumps(catch_summary, ensure_ascii=False)}
- 메모: {log.memo}

1. 이날 조과 특성 분석
2. 날씨·물때와 조과의 상관관계
3. 다음 출조를 위한 핵심 조언 3가지"""

    try:
        result = await llm_service.chat(SYSTEM_PROMPT, user_message)
        return {"analysis": result, "provider": llm_service.provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석 실패: {str(e)}")

@router.post("/advice")
async def get_advice(
    message: dict,
    current_user=Depends(get_current_user)
):
    system = """당신은 선상 낚시 전문가입니다. 낚시에 관한 질문에 친절하고 전문적으로 답변합니다."""
    try:
        result = await llm_service.chat(system, message.get("question", ""))
        return {"advice": result, "provider": llm_service.provider}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 응답 실패: {str(e)}")
