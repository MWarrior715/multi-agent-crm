# Changelog

## 0.1.0 — 2026-07-22

- MVP del Multi-Agent CRM Assistant.
- Pipeline de 6 agentes: Extractor, Clasificador, Resumen, Redactor de Email, Redactor de Propuesta, Planificador de Tareas.
- Persistencia en SQLite (SQLModel) con historial auditable (`HistoryEvent`).
- CLI (`python -m crm`) y API FastAPI (`/health`, `/leads`).
- Motor LLM enchufable vía API OpenAI-compatible.
- Smoke test del pipeline con LLM falso.