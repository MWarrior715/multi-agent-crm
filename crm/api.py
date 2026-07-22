"""api.py — capa REST delgada sobre el CRM (FastAPI)."""
from __future__ import annotations

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlmodel import Session, select

from .db import engine, get_session, init_db
from .engine import CRMPipeline
from .models import Classification, EmailDraft, HistoryEvent, Lead, Proposal, Summary, Task

app = FastAPI(title="Multi-Agent CRM Assistant", version="0.1.0")
init_db()


class LeadIn(BaseModel):
    raw_input: str
    source: str = "manual"


class LeadOut(BaseModel):
    id: str
    name: str
    email: str | None
    phone: str | None
    company: str | None
    score: int | None
    category: str | None
    summary: str | None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/leads", response_model=dict)
def create_lead(req: LeadIn) -> dict:
    pipeline = CRMPipeline()
    result = pipeline.process(req.raw_input, source=req.source)
    return result.to_dict()


@app.get("/leads", response_model=list[LeadOut])
def list_leads(session: Session = Depends(get_session)) -> list[LeadOut]:
    leads = session.exec(select(Lead)).all()
    out = []
    for lead in leads:
        classification = session.exec(select(Classification).where(Classification.lead_id == lead.id)).first()
        summary = session.exec(select(Summary).where(Summary.lead_id == lead.id)).first()
        out.append(
            LeadOut(
                id=lead.id,
                name=lead.name,
                email=lead.email,
                phone=lead.phone,
                company=lead.company,
                score=classification.score if classification else None,
                category=classification.category if classification else None,
                summary=summary.text if summary else None,
            )
        )
    return out


@app.get("/leads/{lead_id}", response_model=dict)
def get_lead(lead_id: str, session: Session = Depends(get_session)) -> dict:
    lead = session.get(Lead, lead_id)
    if not lead:
        return {"error": "Lead not found"}

    classification = session.exec(select(Classification).where(Classification.lead_id == lead_id)).first()
    summary = session.exec(select(Summary).where(Summary.lead_id == lead_id)).first()
    emails = session.exec(select(EmailDraft).where(EmailDraft.lead_id == lead_id)).all()
    proposals = session.exec(select(Proposal).where(Proposal.lead_id == lead_id)).all()
    tasks = session.exec(select(Task).where(Task.lead_id == lead_id)).all()
    history = session.exec(select(HistoryEvent).where(HistoryEvent.lead_id == lead_id)).all()

    return {
        "lead": {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "source": lead.source,
            "raw_input": lead.raw_input,
            "need": lead.need,
            "budget": lead.budget,
            "timing": lead.timing,
            "created_at": lead.created_at.isoformat() if lead.created_at else None,
        },
        "classification": classification.dict() if classification else None,
        "summary": summary.dict() if summary else None,
        "emails": [e.dict() for e in emails],
        "proposals": [p.dict() for p in proposals],
        "tasks": [t.dict() for t in tasks],
        "history": [
            {
                "agent": h.agent,
                "action": h.action,
                "created_at": h.created_at.isoformat() if h.created_at else None,
            }
            for h in history
        ],
    }
