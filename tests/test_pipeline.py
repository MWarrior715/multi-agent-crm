"""test_pipeline.py — smoke tests end-to-end con LLM falso.

No toca Ollama ni ningún motor cloud: usa LLMProvider falso y determinista.
Verifica que el pipeline orquesta todos los agentes y persiste en SQLite.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from sqlmodel import Session, select

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.gettempdir()}/test_crm.db"

from crm.db import engine, init_db
from crm.engine import CRMPipeline
from crm.models import Classification, EmailDraft, Lead, Proposal, Summary, Task
from crm.providers import LLMProvider

TEST_DB_PATH = Path(tempfile.gettempdir()) / "test_crm.db"


class FakeLLM(LLMProvider):
    """LLM falso que devuelve JSON predecible según el prompt."""

    def complete(self, prompt: str, *, system: str | None = None) -> str:  # noqa: ARG002
        p = prompt.lower()
        if "extrae" in p or "extract" in p or ("datos" in p and "lead" in p):
            return (
                '{"name": "Juan Pérez", "email": "juan@acme.co", "phone": "3101234567", '
                '"company": "Acme SAS", "need": "plataforma de reservas", '
                '"budget": "20M COP", "timing": "2 semanas"}'
            )
        if "tareas" in p or "seguimiento" in p or "planifica" in p:
            return '{"tasks": [{"description": "Enviar email", "due_in_days": 0}, {"description": "Llamada de descubrimiento", "due_in_days": 1}]}'
        if "clasifica" in p:
            return '{"score": 85, "category": "hot", "urgency": "high", "reasoning": "Presupuesto claro y timing corto."}'
        if "resume" in p or "resumen" in p:
            return '{"text": "Lead hot que busca plataforma de reservas multi-sede con presupuesto definido."}'
        if "email" in p or "asunto" in p:
            return '{"subject": "Seguimiento Acme SAS", "body": "Hola Juan, gracias por contactarnos. ¿Agendamos una llamada?"}'
        if "propuesta" in p or "propuesta de valor" in p:
            return '{"title": "Propuesta Multi-Sede", "body": "Podemos desplegar un motor de reservas adaptable para sus 5 sedes.", "price_estimate": "Desde 15M COP"}'
        return "{}"


@pytest.fixture(autouse=True)
def setup_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    init_db()
    yield


def test_pipeline_creates_all_artifacts():
    pipeline = CRMPipeline(llm=FakeLLM())
    result = pipeline.process(
        "Hola, soy Juan Pérez de Acme SAS, necesitamos plataforma de reservas para 5 sedes. "
        "Presupuesto 20M COP, decisión en 2 semanas. juan@acme.co 3101234567",
        source="manual",
    )

    assert result.lead.name == "Juan Pérez"
    assert result.lead.company == "Acme SAS"
    assert result.classification.score == 85
    assert result.classification.category == "hot"
    assert result.summary.text
    assert result.email.subject
    assert result.proposal.title
    assert len(result.tasks) >= 1

    with Session(engine) as session:
        lead_id = result.lead.id
        assert session.exec(select(Lead).where(Lead.id == lead_id)).first()
        assert session.exec(select(Classification).where(Classification.lead_id == lead_id)).first()
        assert session.exec(select(Summary).where(Summary.lead_id == lead_id)).first()
        assert session.exec(select(EmailDraft).where(EmailDraft.lead_id == lead_id)).first()
        assert session.exec(select(Proposal).where(Proposal.lead_id == lead_id)).first()
        assert session.exec(select(Task).where(Task.lead_id == lead_id)).first()
