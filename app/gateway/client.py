import re
import logfire
from portkey_ai import Portkey, createHeaders, PORTKEY_GATEWAY_URL
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from app.config import settings


def clean_think_tags(text: str) -> str:
    """Strip <think>...</think> reasoning blocks from model output."""
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


portkey_client = Portkey(
    api_key=settings.PORTKEY_API_KEY,
    config=settings.PORTKEY_PRIMARY_CONFIG_ID
)


def get_direct_groq_llm(feature: str = "rag", temperature: float = 0.0) -> ChatGroq:
    """Fallback direct Groq Chat LLM if Portkey Gateway is unavailable."""
    return ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_MODEL,
        temperature=temperature
    )


def get_langchain_llm(feature: str = "rag") -> ChatOpenAI:
    """
    Returns a Portkey-backed ChatOpenAI — a drop-in for ChatGroq in LangChain nodes.

    Why ChatOpenAI and not ChatGroq:
      Portkey is a proxy. It exposes an OpenAI-compatible endpoint at PORTKEY_GATEWAY_URL.
      ChatGroq is hardwired to Groq's API and does not support routing through a proxy.
      ChatOpenAI supports base_url (points at Portkey) and default_headers (passes Portkey
      auth + config).
    """
    headers = createHeaders(
        api_key=settings.PORTKEY_API_KEY,
        config=settings.PORTKEY_PRIMARY_CONFIG_ID,
        metadata={
            "feature": feature,
            "_user": "rag-system",
            "environment": "production"
        }
    ) if (settings.PORTKEY_API_KEY and settings.PORTKEY_PRIMARY_CONFIG_ID) else None

    return ChatOpenAI(
        api_key=settings.PORTKEY_API_KEY or "dummy_key",
        base_url=PORTKEY_GATEWAY_URL,
        model=f"@{settings.GROQ_SLUG}/{settings.GROQ_MODEL}",
        temperature=0,
        default_headers=headers
    )


def extract_cache_status(response) -> str:
    """
    Pull x-portkey-cache-status from the Portkey native client response headers.
    Tries multiple attribute paths defensively — returns 'MISS' if not found.
    """
    for attr in ("_raw_response", "_response", "_http_response"):
        raw = getattr(response, attr, None)
        if raw is not None:
            status = getattr(raw, "headers", {}).get("x-portkey-cache-status", "")
            if status:
                return status.upper()
    return "MISS"


def generate_completion(prompt: str, feature: str = "responder", temperature: float = 0.1) -> tuple[str, str]:
    """
    Execute chat completion via Portkey client with automatic fallback to direct Groq.
    Returns: (cleaned_content, cache_status)
    """
    try:
        response = portkey_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        raw_content = response.choices[0].message.content or ""
        content = clean_think_tags(raw_content)
        cache_status = extract_cache_status(response)
        return content, cache_status
    except Exception as e:
        logfire.warning(f"⚠️ Portkey Gateway failed ({e}), falling back to direct Groq...")
        fallback_llm = get_direct_groq_llm(feature=feature, temperature=temperature)
        res = fallback_llm.invoke(prompt)
        content = clean_think_tags(res.content if hasattr(res, "content") else str(res))
        return content, "MISS"