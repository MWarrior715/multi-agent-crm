"""task_planner.py — Agente Planificador de Tareas.

Genera follow-ups de ventas a partir del lead y su clasificación.
"""
from __future__ import annotations

from textwrap import dedent
from typing import List

from ..models import Classification, Lead, Task
from ..providers import LLMProvider
from .base import SYSTEM_PROMPT, parse_json_safe


def _prompt(lead: Lead, classification: Classification) -> str:
    return dedent(
        f"""\
        Planifica tareas de seguimiento comercial para este lead. Devuelve SOLO un JSON:
        {{"tasks": [
          {{"description": "enviar email de bienvenida", "due_in_days": 0}},
          {{"description": "llamada de descubrimiento", "due_in_days": 1}}
        ]}}

        Lead:
        Nombre: {lead.name}
        Empresa: {lead.company or "No especificada"}
        Necesidad: {lead.need or "No especificada"}
        Presupuesto: {lead.budget or "No especificado"}
        Timing: {lead.timing or "No especificado"}

        Clasificación: {classification.category} · score {classification.score}/100 · urgencia {classification.urgency}

        Genera entre 2 y 4 tareas concretas. due_in_days debe ser 0, 1, 2, 3, 7 o 14.
        """
    ).strip()


def run_task_planner(lead: Lead, classification: Classification, llm: LLMProvider) -> List[Task]:
    raw = llm.complete(_prompt(lead, classification), system=SYSTEM_PROMPT)
    data = parse_json_safe(raw, fallback={"tasks": []})
    tasks = data.get("tasks", [])
    if not isinstance(tasks, list):
        tasks = []

    return [
        Task(
            lead_id=lead.id,
            description=t.get("description", "Tarea de seguimiento"),
            due_in_days=int(t.get("due_in_days", 1)),
        )
        for t in tasks
    ]
