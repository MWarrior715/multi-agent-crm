"""engine.py — orquestador del CRM multi-agente.

Coordina extractor → clasificador → resumidor → email → propuesta → tareas,
persiste todo en SQLite y guarda un historial de eventos.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from sqlmodel import Session

from .agents import (
    run_classifier,
    run_email_writer,
    run_extractor,
    run_proposal_writer,
    run_summarizer,
    run_task_planner,
)
from .db import engine
from .models import Classification, EmailDraft, HistoryEvent, Lead, Proposal, Summary, Task
from .providers import LLMProvider, default_llm


@dataclass
class CRMResult:
    lead: Lead
    classification: Classification
    summary: Summary
    email: EmailDraft
    proposal: Proposal
    tasks: list[Task]

    def to_dict(self) -> dict:
        return {
            "lead_id": self.lead.id,
            "name": self.lead.name,
            "company": self.lead.company,
            "score": self.classification.score,
            "category": self.classification.category,
            "urgency": self.classification.urgency,
            "summary": self.summary.text,
            "email_subject": self.email.subject,
            "email_body": self.email.body,
            "proposal_title": self.proposal.title,
            "proposal_body": self.proposal.body,
            "tasks": [t.description for t in self.tasks],
        }


class CRMPipeline:
    def __init__(self, llm: LLMProvider | None = None) -> None:
        self.llm = llm or default_llm()

    def process(self, raw_input: str, source: str = "manual") -> CRMResult:
        with Session(engine, expire_on_commit=False) as session:
            # 1. Extraer
            lead = run_extractor(raw_input, self.llm)
            lead.source = source
            session.add(lead)
            session.flush()  # obtiene lead.id
            self._log(session, lead, "extractor", "Datos extraídos del lead")

            # 2. Clasificar
            classification = run_classifier(lead, self.llm)
            session.add(classification)
            self._log(session, lead, "classifier", f"Score {classification.score}/100 · {classification.category} · {classification.urgency}")

            # 3. Resumir
            summary = run_summarizer(lead, self.llm)
            session.add(summary)
            self._log(session, lead, "summarizer", "Resumen ejecutivo generado")

            # 4. Email
            email = run_email_writer(lead, self.llm)
            session.add(email)
            self._log(session, lead, "email_writer", "Borrador de email generado")

            # 5. Propuesta
            proposal = run_proposal_writer(lead, self.llm)
            session.add(proposal)
            self._log(session, lead, "proposal_writer", "Propuesta de valor generada")

            # 6. Tareas
            tasks = run_task_planner(lead, classification, self.llm)
            for task in tasks:
                session.add(task)
            self._log(session, lead, "task_planner", f"{len(tasks)} tareas de seguimiento creadas")

            session.commit()

            return CRMResult(
                lead=lead,
                classification=classification,
                summary=summary,
                email=email,
                proposal=proposal,
                tasks=tasks,
            )

    def _log(self, session: Session, lead: Lead, agent: str, action: str, payload: Optional[dict] = None) -> None:
        event = HistoryEvent(
            lead_id=lead.id,
            agent=agent,
            action=action,
            payload_json=json.dumps(payload or {}),
        )
        session.add(event)
