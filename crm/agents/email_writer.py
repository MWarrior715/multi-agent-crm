"""email_writer.py — Agente Escritor de Emails.

Genera un borrador de primer contacto personalizado.
"""
from __future__ import annotations

from textwrap import dedent

from ..models import EmailDraft, Lead
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, parse_json_safe


def _prompt(lead: Lead, tone: str = "professional") -> str:
    return dedent(
        f"""\
        Escribe un email de primer contacto para este lead. Devuelve SOLO un JSON:
        {{"subject": "asunto", "body": "cuerpo del email"}}

        Tono: {tone}

        Lead:
        Nombre: {lead.name}
        Empresa: {lead.company or "No especificada"}
        Necesidad: {lead.need or "No especificada"}
        Presupuesto: {lead.budget or "No especificado"}
        Timing: {lead.timing or "No especificado"}

        El email debe ser corto, personalizado y con una llamada a la acción clara.
        """
    ).strip()


def run_email_writer(lead: Lead, llm: LLMProvider, tone: str = "professional") -> EmailDraft:
    raw = llm.complete(_prompt(lead, tone), system=SYSTEM_PROMPT)
    data = parse_json_safe(
        raw,
        fallback={
            "subject": f"Seguimiento: {lead.company or lead.name}",
            "body": "Hola, gracias por tu interés. ¿Podemos agendar una breve llamada?",
        },
    )
    return EmailDraft(
        lead_id=lead.id,
        subject=data.get("subject", ""),
        body=data.get("body", ""),
        tone=tone,
    )
