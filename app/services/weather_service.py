import httpx
import math
from datetime import date, datetime, timedelta
from app.config import settings

# ── 기상청 Lambert 격자 변환 ──────────────────────────────────────────────────
def _latlon_to_grid(lat: float, lon: float) -> tuple[int, int]:
    RE, GRID = 6371.00877, 5.0
    SLAT1, SLAT2 = 30.0, 60.0
    OLON, OLAT, XO, YO = 126.0, 38.0, 43, 136
    D = math.pi / 180.0

    re = RE / GRID
    s1, s2 = SLAT1 * D, SLAT2 * D
    sn = math.log(math.cos(s1) / math.cos(s2)) / math.log(
        math.tan(math.pi * 0.25 + s2 * 0.5) / math.tan(math.pi * 0.25 + s1 * 0.5)
    )
    sf = (math.tan(math.pi * 0.25 + s1 * 0.5) ** sn) * math.cos(s1) / sn
    ro = re * sf / (math.tan(math.pi * 0.25 + OLAT * D * 0.5) ** sn)
    ra = re * sf / (math.tan(math.pi * 0.25 + lat * D * 0.5) ** sn)
    theta = lon * D - OLON * D
    if theta > math.pi: theta -= 2 * math.pi
    if theta < -math.pi: theta += 2 * math.pi
    theta *= sn
    return int(ra * math.sin(theta) + XO + 0.5), int(ro - ra * math.cos(theta) + YO + 0.5)

def _base_datetime(now: datetime) -> tuple[str, str]:
    """가장 최근 기상청 예보 발표 시각 계산 (1시간 여유)"""
    hours = [2, 5, 8, 11, 14, 17, 20, 23]
    # 예보 발표 후 최소 1시간 지난 시각을 기준으로 사용
    safe = now - timedelta(hours=1)
    for h in reversed(hours):
        if safe.hour >= h:
            return safe.strftime("%Y%m%d"), f"{h:02d}00"
    prev = safe - timedelta(days=1)
    return prev.strftime("%Y%m%d"), "2300"

SKY = {1: "맑음", 3: "구름많음", 4: "흐림"}
PTY = {0: "", 1: "비", 2: "비/눈", 3: "눈", 4: "소나기"}


async def fetch_weather(target_date: date, lat: float, lng: float) -> dict:
    if settings.kma_api_key:
        try:
            return await _fetch_kma(target_date, lat, lng)
        except Exception as e:
            print(f"[KMA] 오류: {e}")

    if settings.openweather_api_key and settings.openweather_api_key != "your_openweathermap_api_key":
        try:
            return await _fetch_openweather(target_date, lat, lng)
        except Exception as e:
            print(f"[OWM] 오류: {e}")

    return _no_data()


async def _fetch_kma(target_date: date, lat: float, lng: float) -> dict:
    today = date.today()
    delta = (target_date - today).days
    if delta < -1 or delta > 3:
        return {**_no_data(), "description": f"단기예보 범위 외 ({target_date})"}

    nx, ny = _latlon_to_grid(lat, lng)
    base_date, base_time = _base_datetime(datetime.now())

    # 인코딩 키를 그대로 사용 (재인코딩 금지)
    url = (
        f"http://apis.data.go.kr/1360000/VilageFcstInfoService2.0/getVilageFcst"
        f"?ServiceKey={settings.kma_api_key}"
        f"&pageNo=1&numOfRows=300&dataType=JSON"
        f"&base_date={base_date}&base_time={base_time}&nx={nx}&ny={ny}"
    )
    async with httpx.AsyncClient(timeout=15.0, verify=False) as client:
        resp = await client.get(url)

    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")

    data = resp.json()
    result_code = data.get("response", {}).get("header", {}).get("resultCode", "")
    if result_code != "00":
        msg = data.get("response", {}).get("header", {}).get("resultMsg", "오류")
        raise Exception(f"기상청 오류 {result_code}: {msg}")

    items = data["response"]["body"]["items"]["item"]
    fcst_date = target_date.strftime("%Y%m%d")

    values = {}
    for target_time in ["0900", "0600", "1200", "0300", "1500", "0000"]:
        for item in items:
            if item.get("fcstDate") == fcst_date and item.get("fcstTime") == target_time:
                values[item["category"]] = item["fcstValue"]
        if values:
            break

    if not values:
        raise Exception("해당 날짜 예보 데이터 없음")

    sky_val = int(values.get("SKY", 1))
    pty_val = int(values.get("PTY", 0))
    description = PTY.get(pty_val) or SKY.get(sky_val, "알 수 없음")

    wav_raw = values.get("WAV")
    wave_height = float(wav_raw) if wav_raw and wav_raw not in ("-", "0") else None

    return {
        "temp": float(values["TMP"]) if "TMP" in values else None,
        "description": description,
        "wind_speed": float(values["WSD"]) if "WSD" in values else None,
        "humidity": None,
        "wave_height": wave_height,
        "water_temp": None,
    }


async def _fetch_openweather(target_date: date, lat: float, lng: float) -> dict:
    import time
    ts = int(time.mktime(target_date.timetuple()))
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            "https://api.openweathermap.org/data/3.0/onecall/timemachine",
            params={"lat": lat, "lon": lng, "dt": ts,
                    "appid": settings.openweather_api_key,
                    "units": "metric", "lang": "kr"},
        )
        resp.raise_for_status()
    h = resp.json().get("data", [{}])[0]
    return {
        "temp": h.get("temp"),
        "description": h.get("weather", [{}])[0].get("description", ""),
        "wind_speed": h.get("wind_speed"),
        "humidity": h.get("humidity"),
        "wave_height": h.get("wave_height"),
        "water_temp": h.get("sea_surface_temp"),
    }


def _no_data() -> dict:
    return {"temp": None, "description": "날씨 API 미설정", "wind_speed": None,
            "humidity": None, "wave_height": None, "water_temp": None}
