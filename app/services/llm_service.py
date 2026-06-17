"""
.env의 LLM_PROVIDER 설정에 따라 Polaris / OpenAI / Claude를 동적 호출
"""
import httpx
from app.config import settings

class LLMService:
    def __init__(self):
        self.provider = settings.llm_provider

    async def chat(self, system_prompt: str, user_message: str) -> str:
        if self.provider == "polaris":
            return await self._call_polaris(system_prompt, user_message)
        elif self.provider == "openai":
            return await self._call_openai(system_prompt, user_message)
        elif self.provider == "claude":
            return await self._call_claude(system_prompt, user_message)
        else:
            raise ValueError(f"지원하지 않는 LLM 프로바이더: {self.provider}")

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

llm_service = LLMService()
