"""summarizer.py — Agente Resumidor.

Genera un resumen ejecutivo del lead.
"""
from __future__ import annotations

from textwrap import dedent

from ..models import Lead, Summary
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, parse_json_safe


def _prompt(lead: Lead) -> str:
    return dedent(
        f"""\
        Resume el siguiente lead en 2-3 oraciones. Devuelve SOLO un JSON:
        {{"text": "resumen ejecutivo"}}

        Lead:
        Nombre: {lead.name}
        Empresa: {lead.company or "No especificada"}
        Necesidad: {lead.need or "No especificada"}
        Presupuesto: {lead.budget or "No especificado"}
        Timing: {lead.timing or "No especificado"}
        Texto original: {lead.raw_input}
        """
    ).strip()


def run_summarizer(lead: Lead, llm: LLMProvider) -> Summary:
    raw = llm.complete(_prompt(lead), system=SYSTEM_PROMPT)
    data = parse_json_safe(raw, fallback={"text": "Resumen no disponible."})
    return Summary(lead_id=lead.id, text=data.get("text", "Resumen no disponible."))
