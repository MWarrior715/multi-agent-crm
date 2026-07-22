"""Agentes especializados del CRM."""
from __future__ import annotations

from .classifier import run_classifier
from .email_writer import run_email_writer
from .extractor import run_extractor
from .proposal_writer import run_proposal_writer
from .summarizer import run_summarizer
from .task_planner import run_task_planner

__all__ = [
    "run_extractor",
    "run_classifier",
    "run_summarizer",
    "run_email_writer",
    "run_proposal_writer",
    "run_task_planner",
]
