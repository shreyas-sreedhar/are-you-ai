"""HTTP client for NVIDIA NIM.

Deliberately thin: it sends messages and returns text. It knows nothing about
video, scams or verdicts. Prompt construction lives in `core.prompts`, reply
parsing in `core.envelope`, and judgement in the analysers.
"""

from __future__ import annotations

import asyncio
import base64
import logging
from io import BytesIO
from typing import Any

import httpx
from PIL import Image

from config.settings import settings

logger = logging.getLogger(__name__)


class NimUnavailable(RuntimeError):
    """The model could not be reached, or refused to answer.

    Callers are expected to degrade gracefully rather than fail the request —
    a user staring at a suspicious message deserves the local keyword check
    over a 500.
    """


def encode_image(image: Image.Image, quality: int = 85) -> str:
    """JPEG-encode a frame as base64, the form NIM's vision endpoint expects."""
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


class NimClient:
    """A shared, connection-pooled client for the NIM chat completions API."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.nim_timeout_seconds),
                headers={
                    "Authorization": f"Bearer {settings.nim_api_key}",
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def complete(
        self,
        prompt: str,
        *,
        images: list[Image.Image] | None = None,
        image_captions: list[str] | None = None,
        model: str | None = None,
        temperature: float = 0.1,
        max_tokens: int = 1400,
    ) -> str:
        """Send one prompt (optionally with images) and return the reply text.

        Raises NimUnavailable for anything the caller cannot fix by retrying.
        """
        if not settings.nim_configured:
            raise NimUnavailable("NIM_API_KEY is not set")

        images = images or []
        model = model or (
            settings.nim_vision_model if images else settings.nim_text_model
        )

        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for index, image in enumerate(images):
            if image_captions and index < len(image_captions):
                content.append({"type": "text", "text": image_captions[index]})
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image)}"},
                }
            )

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        return await self._post_with_retries(payload, model)

    async def _post_with_retries(self, payload: dict[str, Any], model: str) -> str:
        client = await self._http()
        last_error: Exception | None = None

        for attempt in range(settings.nim_max_retries + 1):
            try:
                response = await client.post(settings.nim_api_endpoint, json=payload)
                response.raise_for_status()
                return _extract_text(response.json())

            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                # 4xx other than rate limiting will not improve on retry.
                if status != 429 and 400 <= status < 500:
                    logger.error(
                        "NIM rejected the request (%s): %s", status, exc.response.text[:300]
                    )
                    raise NimUnavailable(f"NIM returned {status}") from exc
                last_error = exc

            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc

            if attempt < settings.nim_max_retries:
                backoff = 0.5 * (2**attempt)
                logger.warning(
                    "NIM call to %s failed (%s), retrying in %.1fs",
                    model,
                    type(last_error).__name__,
                    backoff,
                )
                await asyncio.sleep(backoff)

        raise NimUnavailable(f"NIM unreachable after {settings.nim_max_retries + 1} attempts") from last_error


def _extract_text(body: dict[str, Any]) -> str:
    choices = body.get("choices") or []
    if not choices:
        raise NimUnavailable("NIM returned no choices")

    message = choices[0].get("message") or {}
    content = message.get("content")

    if isinstance(content, list):
        # Some deployments return content as a list of parts.
        content = "".join(
            part.get("text", "") for part in content if isinstance(part, dict)
        )

    if not isinstance(content, str) or not content.strip():
        raise NimUnavailable("NIM returned an empty message")

    return content


# One client for the process lifetime; closed by the FastAPI lifespan handler.
nim_client = NimClient()
