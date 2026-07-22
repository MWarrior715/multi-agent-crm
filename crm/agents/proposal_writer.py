"""proposal_writer.py — Agente Escritor de Propuestas.

Genera una propuesta de valor breve para el lead.
"""
from __future__ import annotations

from textwrap import dedent

from ..models import Lead, Proposal
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, parse_json_safe


def _prompt(lead: Lead) -> str:
    return dedent(
        f"""\
        Genera una propuesta de valor breve para este lead. Devuelve SOLO un JSON:
        {{
          "title": "título de la propuesta",
          "body": "cuerpo de 2-4 oraciones",
          "price_estimate": "estimación de precio opcional o null"
        }}

        Lead:
        Nombre: {lead.name}
        Empresa: {lead.company or "No especificada"}
        Necesidad: {lead.need or "No especificada"}
        Presupuesto: {lead.budget or "No especificado"}
        Timing: {lead.timing or "No especificado"}

        Sé concreto y alineado con la necesidad declarada. No inventes funcionalidades.
        """
    ).strip()


def run_proposal_writer(lead: Lead, llm: LLMProvider) -> Proposal:
    raw = llm.complete(_prompt(lead), system=SYSTEM_PROMPT)
    data = parse_json_safe(
        raw,
        fallback={
            "title": "Propuesta inicial",
            "body": "Basado en tu necesidad, podemos diseñar una solución a la medida. Agendemos una llamada para detallarla.",
            "price_estimate": None,
        },
    )
    return Proposal(
        lead_id=lead.id,
        title=data.get("title", ""),
        body=data.get("body", ""),
        price_estimate=data.get("price_estimate") or None,
    )
