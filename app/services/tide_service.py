import httpx
from datetime import date
from app.config import settings

async def fetch_tide(target_date: date, obs_code: str) -> dict:
    """국립해양조사원 조석예보(고,저조) API"""
    if not settings.khoa_api_key or not obs_code:
        return _no_data(target_date)

    try:
        result = await _call_khoa(target_date, obs_code)
        if result:
            return result
    except Exception as e:
        print(f"[TIDE] KHOA 오류: {e}")

    return _no_data(target_date)


async def _call_khoa(target_date: date, obs_code: str) -> dict | None:
    # 인코딩 키를 그대로 사용 (재인코딩 금지)
    url = (
        f"https://www.khoa.go.kr/api/oceangrid/tideObsPreTab/search.do"
        f"?ServiceKey={settings.khoa_api_key}"
        f"&ObsCode={obs_code}&Date={target_date.strftime('%Y%m%d')}&ResultType=json"
    )
    async with httpx.AsyncClient(timeout=15.0, verify=False, follow_redirects=False) as client:
        resp = await client.get(url)

    if resp.status_code in (301, 302, 303, 307, 308):
        raise Exception(f"서버 점검 중 (리다이렉트 {resp.status_code})")
    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}")

    data = resp.json()

    items = data.get("result", {}).get("data", [])
    if not items:
        return None

    high_times, low_times = [], []
    for item in items:
        hl = item.get("hl_code", "")
        t = item.get("tide_time", "")
        h = item.get("tide_level")
        entry = {"time": t, "height": h}
        if hl == "H":
            high_times.append(entry)
        else:
            low_times.append(entry)

    tidal_range = None
    try:
        if high_times and low_times:
            max_high = max(float(x["height"]) for x in high_times if x["height"] is not None)
            min_low = min(float(x["height"]) for x in low_times if x["height"] is not None)
            tidal_range = round(max_high - min_low)
    except (ValueError, TypeError):
        pass

    return {
        "name": _tide_name(target_date),
        "level": "대조" if len(high_times) >= 2 else "소조",
        "high_times": high_times,
        "low_times": low_times,
        "tidal_range": tidal_range,
    }


def _no_data(d: date) -> dict:
    return {
        "name": _tide_name(d),
        "level": "API 미설정" if not settings.khoa_api_key else "관측소 코드 없음",
        "high_times": [],
        "low_times": [],
        "tidal_range": None,
    }

def _tide_name(d: date) -> str:
    names = ["조금", "무시", "1물", "2물", "3물", "4물", "5물",
             "6물", "7물", "8물", "9물", "10물", "11물", "12물", "13물"]
    return names[((d.day % 15) + 1) % 15]
