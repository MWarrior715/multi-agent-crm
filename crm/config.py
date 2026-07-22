"""config.py — carga de configuración por entorno."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _env(key: str, default: str) -> str:
    return os.getenv(key, default)


@dataclass
class Settings:
    openai_base_url: str = field(default_factory=lambda: _env("OPENAI_BASE_URL", "http://localhost:11434/v1"))
    openai_api_key: str = field(default_factory=lambda: _env("OPENAI_API_KEY", "local-dev-key"))
    llm_model: str = field(default_factory=lambda: _env("LLM_MODEL", "qwen2.5:7b-instruct"))
    database_url: str = field(default_factory=lambda: _env("DATABASE_URL", f"sqlite:///{DATA_DIR}/crm.db"))


settings = Settings()
