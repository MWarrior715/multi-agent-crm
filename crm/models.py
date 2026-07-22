"""models.py — entidades del CRM con SQLModel (sin relationships bidireccionales)."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


def generate_id() -> str:
    return uuid.uuid4().hex[:16]


class Lead(SQLModel, table=True):
    id: str = Field(default_factory=generate_id, primary_key=True)
    name: str
    email: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    company: Optional[str] = Field(default=None)
    source: str = Field(default="manual")  # manual | form | email | whatsapp
    raw_input: str
    need: Optional[str] = Field(default=None)
    budget: Optional[str] = Field(default=None)
    timing: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Classification(SQLModel, table=True):
    id: str = Field(default_factory=generate_id, primary_key=True)
    lead_id: str = Field(foreign_key="lead.id", unique=True)
    score: int = Field(ge=0, le=100)
    category: str  # hot | warm | cold
    urgency: str  # high | medium | low
    reasoning: str


class Summary(SQLModel, table=True):
    id: str = Field(default_factory=generate_id, primary_key=True)
    lead_id: str = Field(foreign_key="lead.id", unique=True)
    text: str


class EmailDraft(SQLModel, table=True):
    id: str = Field(default_factory=generate_id, primary_key=True)
    lead_id: str = Field(foreign_key="lead.id")
    subject: str
    body: str
    tone: str = Field(default="professional")


class Proposal(SQLModel, table=True):
    id: str = Field(default_factory=generate_id, primary_key=True)
    lead_id: str = Field(foreign_key="lead.id")
    title: str
    body: str
    price_estimate: Optional[str] = Field(default=None)


class Task(SQLModel, table=True):
    id: str = Field(default_factory=generate_id, primary_key=True)
    lead_id: str = Field(foreign_key="lead.id")
    description: str
    due_in_days: int
    status: str = Field(default="pending")  # pending | done


class HistoryEvent(SQLModel, table=True):
    id: str = Field(default_factory=generate_id, primary_key=True)
    lead_id: str = Field(foreign_key="lead.id")
    agent: str
    action: str
    payload_json: str = Field(default="{}")
    created_at: datetime = Field(default_factory=datetime.utcnow)
