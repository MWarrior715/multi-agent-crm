"""base.py — utilidades comunes para agentes."""
from __future__ import annotations

import json
from textwrap import dedent


SYSTEM_PROMPT = dedent(
    """\
    Eres un agente especializado dentro de un CRM con IA. Tu trabajo es procesar
    información de leads de forma precisa y devolver ÚNICAMENTE un objeto JSON
    válido, sin explicaciones externas ni markdown.

    Reglas:
    - Respeta exactamente las claves solicitadas.
    - No inventes datos que no estén en el input.
    - Usa null para campos desconocidos.
    """
).strip()


def strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        t = "\n".join(lines)
    return t.strip()


def parse_json_safe(text: str, fallback: dict) -> dict:
    try:
        return json.loads(strip_code_fence(text))
    except json.JSONDecodeError:
        return fallback
