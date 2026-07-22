"""classifier.py — Agente Clasificador.

Da score 1-100, categoría y urgencia a un lead.
"""
from __future__ import annotations

from textwrap import dedent

from ..models import Classification, Lead
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, parse_json_safe


def _prompt(lead: Lead) -> str:
    return dedent(
        f"""\
        Clasifica el siguiente lead y devuelve SOLO un JSON:
        {{
          "score": 85,
          "category": "hot | warm | cold",
          "urgency": "high | medium | low",
          "reasoning": "una frase corta justificando la clasificación"
        }}

        Lead:
        Nombre: {lead.name}
        Empresa: {lead.company or "No especificada"}
        Necesidad: {lead.need or "No especificada"}
        Presupuesto: {lead.budget or "No especificado"}
        Timing: {lead.timing or "No especificado"}
        Texto original: {lead.raw_input}

        Criterios:
        - hot: presupuesto claro, decisión inminente, necesidad definida.
        - warm: interés real pero falta información o timing medio.
        - cold: exploratorio, sin presupuesto ni urgencia.
        """
    ).strip()


def run_classifier(lead: Lead, llm: LLMProvider) -> Classification:
    raw = llm.complete(_prompt(lead), system=SYSTEM_PROMPT)
    data = parse_json_safe(
        raw,
        fallback={
            "score": 50,
            "category": "warm",
            "urgency": "medium",
            "reasoning": "No se pudo clasificar automáticamente.",
        },
    )

    score = max(0, min(100, int(data.get("score", 50))))
    category = data.get("category", "warm")
    urgency = data.get("urgency", "medium")
    if category not in {"hot", "warm", "cold"}:
        category = "warm"
    if urgency not in {"high", "medium", "low"}:
        urgency = "medium"

    return Classification(
        lead_id=lead.id,
        score=score,
        category=category,
        urgency=urgency,
        reasoning=data.get("reasoning", ""),
    )
