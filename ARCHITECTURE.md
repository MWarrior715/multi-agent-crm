# Multi-Agent CRM Assistant — Arquitectura

## Diagrama conceptual

```
Mensaje de lead (email / WhatsApp / web / manual)
  │
  ▼
┌──────────────────────────────────────────────┐
│  CRMPipeline (engine.py)                     │
│  Orquesta 6 agentes en orden, persiste cada  │
│  paso en SQLite y registra HistoryEvent.     │
└──────────────────────────────────────────────┘
  │
  1.▶ Extractor        → Lead (nombre, email, teléfono, empresa, necesidad, presupuesto, timing)
  2.▶ Clasificador     → Classification (score 0-100, hot/warm/cold, urgencia, reasoning)
  3.▶ Resumen          → Summary (resumen ejecutivo)
  4.▶ Redactor Email   → EmailDraft (asunto + cuerpo, tono profesional)
  5.▶ Redactor Prop.   → Proposal (título, cuerpo, estimación de precio)
  6.▶ Planificador     → Task[] (seguimientos con due_in_days)

              │   cada agente llama a LLMProvider.complete()
              ▼
        ┌────────────────────────┐
        │  LLMProvider (providers)│  OpenAI-compatible API
        │  OpenAICompatibleLLM    │  (motor local o cloud enchufable)
        └────────────────────────┘

              │   persistencia
              ▼
        SQLite (SQLModel)
        lead · classification · summary · email_draft
        proposal · task · history_event
```

## Capas

1. **Proveedores de IA** (`providers.py`): `LLMProvider` (Protocol) con implementación `OpenAICompatibleLLM`. Un único punto para cambiar de motor local a cloud sin tocar agentes.
2. **Configuración** (`config.py`): variables de entorno vía `.env` (`OPENAI_BASE_URL`, `OPENAI_API_KEY`, `LLM_MODEL`, `DATABASE_URL`).
3. **Modelos** (`models.py`): entidades `SQLModel` — `Lead`, `Classification`, `Summary`, `EmailDraft`, `Proposal`, `Task`, `HistoryEvent`. IDs UUID hex de 16 chars.
4. **Agentes** (`agents/`): cada agente recibe datos previos, construye un prompt, fuerza JSON de salida, lo parsea con pydantic y devuelve un objeto de dominio. `base.py` factoriza la llamada al LLM + parseo.
5. **Orquestador** (`engine.py`): `CRMPipeline.process()` ejecuta los 6 agentes en orden dentro de una `Session`, hace `flush` para obtener `lead.id`, persiste cada artefacto y registra un `HistoryEvent` por paso.
6. **Persistencia** (`db.py`): engine SQLModel + `init_db()` + dependencia `get_session()` para FastAPI.
7. **Interfaces** (`cli.py`, `api.py`): CLI para demos rápidas, FastAPI para integración.

## Patrones clave

- **Pipeline secuencial con shared state.** El `Lead` extraído alimenta a los 5 agentes siguientes. Es secuencial (no concurrente) porque cada paso enriquece el contexto del siguiente y así la trazabilidad del demo es lineal.
- **JSON forzado + pydantic.** Cada agente pide al LLM una respuesta JSON con esquema fijo; el parseo valida tipos y descarta respuestas malformadas.
- **Historial auditable.** Cada paso genera un `HistoryEvent` (agente + acción), de modo que un lead tiene su línea de tiempo completa en BD — base para un dashboard futuro.
- **Motor enchufable.** Los tests usan un LLM falso; producción usa `OpenAICompatibleLLM` apuntando a la base_url que se configure.