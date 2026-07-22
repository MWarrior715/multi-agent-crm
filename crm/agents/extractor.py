"""extractor.py — Agente Extractor.

Extrae datos estructurados de un texto libre de lead.
"""
from __future__ import annotations

from textwrap import dedent

from ..models import Lead
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, parse_json_safe


def _prompt(raw_input: str) -> str:
    return dedent(
        f"""\
        Extrae del siguiente texto los datos de un lead y devuélvelos como JSON:
        {{
          "name": "nombre de la persona de contacto",
          "email": "correo o null",
          "phone": "teléfono o null",
          "company": "empresa o null",
          "need": "necesidad principal en una frase",
          "budget": "presupuesto mencionado o null",
          "timing": "tiempo de decisión mencionado o null"
        }}

        Texto del lead:
        {raw_input}

        Devuelve SOLO el JSON.
        """
    ).strip()


def run_extractor(raw_input: str, llm: LLMProvider) -> Lead:
    prompt = _prompt(raw_input)
    raw = llm.complete(prompt, system=SYSTEM_PROMPT)
    data = parse_json_safe(
        raw,
        fallback={
            "name": "Lead sin nombre",
            "email": None,
            "phone": None,
            "company": None,
            "need": None,
            "budget": None,
            "timing": None,
        },
    )

    return Lead(
        name=data.get("name") or "Lead sin nombre",
        email=data.get("email") or None,
        phone=data.get("phone") or None,
        company=data.get("company") or None,
        raw_input=raw_input,
        need=data.get("need") or None,
        budget=data.get("budget") or None,
        timing=data.get("timing") or None,
    )
