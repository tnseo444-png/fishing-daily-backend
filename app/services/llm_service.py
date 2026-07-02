"""
.env의 LLM_PROVIDER 설정에 따라 Polaris / OpenAI / Claude / Gemini를 동적 호출
"""
import httpx
import os
from app.config import settings

class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider

    async def chat(self, system_prompt: str, user_message: str) -> str:
        provider = os.environ.get("LLM_PROVIDER", settings.llm_provider)
        gemini_key = os.environ.get("GEMINI_API_KEY", settings.gemini_api_key)
        if provider == "gemini" and gemini_key:
            return await self._call_gemini(system_prompt, user_message, gemini_key)
        if self.provider == "gemini" and settings.gemini_api_key:
            return await self._call_gemini(system_prompt, user_message, settings.gemini_api_key)
        elif self.provider == "claude" and settings.anthropic_api_key:
            return await self._call_claude(system_prompt, user_message)
        elif self.provider == "openai" and settings.openai_api_key:
            return await self._call_openai(system_prompt, user_message)
        elif self.provider == "polaris" and settings.polaris_api_url and settings.polaris_api_key:
            return await self._call_polaris(system_prompt, user_message)
        else:
            return "AI 기능이 설정되지 않았습니다."

    async def _call_polaris(self, system: str, user: str) -> str:
        """Polaris Agent 내부 호출 (OpenAI 호환 API)"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.polaris_api_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.polaris_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.polaris_model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000,
                },
                timeout=60.0,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def _call_openai(self, system: str, user: str) -> str:
        """OpenAI API 호출"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
                timeout=60.0,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def _call_claude(self, system: str, user: str) -> str:
        """Claude API 호출"""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 2000,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                },
                timeout=60.0,
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]

    async def _call_gemini(self, system: str, user: str, api_key: str = None) -> str:
        """Gemini API 호출 (429 시 최대 3회 재시도)"""
        import asyncio
        key = api_key or os.environ.get("GEMINI_API_KEY", settings.gemini_api_key)
        model = os.environ.get("GEMINI_MODEL", settings.gemini_model)
        for attempt in range(3):
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                    params={"key": key},
                    json={
                        "system_instruction": {"parts": [{"text": system}]},
                        "contents": [{"parts": [{"text": user}]}],
                        "generationConfig": {"maxOutputTokens": 2000, "temperature": 0.7},
                    },
                    timeout=60.0,
                )
                if resp.status_code == 429 and attempt < 2:
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                resp.raise_for_status()
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

llm_service = LLMService()
