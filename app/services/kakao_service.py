import httpx
from app.config import settings
from datetime import date

async def send_fishing_reminder(kakao_user_id: str, fishing_date: date, harbor_name: str) -> bool:
    """카카오 비즈메시지 출조 알림 발송"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://kapi.kakao.com/v2/api/talk/memo/default/send",
                headers={"Authorization": f"Bearer {kakao_user_id}"},
                json={
                    "template_object": {
                        "object_type": "text",
                        "text": (
                            f"🎣 출조 알림!\n\n"
                            f"3일 후 예약된 낚시 일정이 있습니다.\n\n"
                            f"📅 일정: {fishing_date.strftime('%Y년 %m월 %d일')}\n"
                            f"⚓ 항구: {harbor_name}\n\n"
                            f"Fishing Daily에서 준비사항을 확인하세요!"
                        ),
                        "link": {"web_url": "http://localhost:5173/schedules"},
                    }
                },
            )
        return resp.status_code == 200
    except Exception as e:
        print(f"카카오 알림 발송 실패: {e}")
        return False
