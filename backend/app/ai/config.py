"""LifeOS - Dynamic AI Runtime Configuration Provider (Step 10).

Allows AI services (Chat, Personal Intelligence, Tools) to dynamically resolve
the currently active AIModelVersion from PostgreSQL, falling back cleanly to
environment variables or Flask app config.
"""
import os
import requests
from typing import Dict, Any, Optional
from flask import current_app
from langchain_ollama import ChatOllama


class AIRuntimeConfig:
    """Manages active AI runtime configuration with database persistence."""

    _active_model_override: Optional[str] = None

    @classmethod
    def set_runtime_override(cls, model_tag: Optional[str]) -> None:
        """In-memory override primarily for unit tests or immediate hot-swapping."""
        cls._active_model_override = model_tag

    @classmethod
    def get_active_model_tag(cls) -> str:
        """Resolve active model tag: in-memory override -> database active model -> env var -> default."""
        if cls._active_model_override:
            return cls._active_model_override

        try:
            from app.repositories.ai_model_version_repository import AIModelVersionRepository
            repo = AIModelVersionRepository()
            active_model = repo.get_active_model()
            if active_model and active_model.model_tag:
                return active_model.model_tag
        except Exception:
            # Fallback gracefully if database or table is unavailable during initialization
            pass

        if current_app:
            return current_app.config.get("OLLAMA_MODEL", "qwen2.5:3b")
        return os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


def get_ai_config() -> Dict[str, Any]:
    """Retrieve active AI settings with dynamic active model resolution."""
    base_url = (
        current_app.config.get("OLLAMA_BASE_URL")
        if current_app
        else os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    model = AIRuntimeConfig.get_active_model_tag()
    timeout = (
        current_app.config.get("OLLAMA_TIMEOUT")
        if current_app
        else int(os.getenv("OLLAMA_TIMEOUT", "60"))
    )
    temperature = (
        current_app.config.get("OLLAMA_TEMPERATURE")
        if current_app
        else float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
    )
    max_tokens = (
        current_app.config.get("OLLAMA_MAX_TOKENS")
        if current_app
        else int(os.getenv("OLLAMA_MAX_TOKENS", "1024"))
    )

    return {
        "base_url": base_url,
        "model": model,
        "timeout": timeout,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def check_ollama_health() -> Dict[str, Any]:
    """Verify connectivity to local Ollama server and check target model existence."""
    cfg = get_ai_config()
    tags_url = f"{cfg['base_url'].rstrip('/')}/api/tags"

    try:
        resp = requests.get(tags_url, timeout=5)
        if resp.status_code != 200:
            return {
                "healthy": False,
                "model_available": False,
                "status": "degraded",
                "error": f"Ollama HTTP {resp.status_code}",
                "base_url": cfg["base_url"],
                "model": cfg["model"]
            }

        data = resp.json()
        models = [m.get("name", "") for m in data.get("models", [])]
        target_model = cfg["model"]

        model_found = any(
            target_model == m or target_model == m.split(":")[0] or m.startswith(target_model)
            for m in models
        )

        return {
            "healthy": True,
            "model_available": model_found,
            "status": "operational" if model_found else "model_missing",
            "model": target_model,
            "available_models": models,
            "base_url": cfg["base_url"],
            "error": None if model_found else f"Configured model '{target_model}' not found in installed models."
        }

    except requests.exceptions.RequestException as e:
        return {
            "healthy": False,
            "model_available": False,
            "status": "unreachable",
            "model": cfg["model"],
            "base_url": cfg["base_url"],
            "error": f"Cannot connect to Ollama runtime at {cfg['base_url']}: {str(e)}"
        }


def get_llm(
    temperature: Optional[float] = None,
    timeout: Optional[int] = None
) -> ChatOllama:
    """Instantiate a configured ChatOllama client."""
    cfg = get_ai_config()
    return ChatOllama(
        base_url=cfg["base_url"],
        model=cfg["model"],
        temperature=temperature if temperature is not None else cfg["temperature"],
        timeout=timeout if timeout is not None else cfg["timeout"]
    )
