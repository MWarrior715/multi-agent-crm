# Multi-Agent CRM Assistant — API

Referencia de la CLI y los endpoints REST (FastAPI).

## CLI

```bash
python -m crm "<raw_input>" [--source <origen>] [--json]
```

| Flag | Descripción | Default |
|---|---|---|
| `raw_input` (posicional) | Texto libre del lead | — |
| `--source` | Origen del lead (`manual` \| `form` \| `email` \| `whatsapp`) | `manual` |
| `--json` | Imprime el resultado como JSON | `false` |

Sin `--json` imprime un reporte legible (lead, score, resumen, email, propuesta, tareas).

### Ejemplo

```bash
python -m crm "Hola, soy Juan Pérez de Acme SAS, necesitamos plataforma de reservas para 5 sedes. Presupuesto 20M COP, decisión en 2 semanas. juan@acme.co 3101234567" --json
```

## REST (FastAPI)

Levantar el servidor:

```bash
uvicorn crm.api:app --reload
```

Base URL local: `http://127.0.0.1:8000`. Docs interactivas en `/docs` (OpenAPI).

### `GET /health`

Healthcheck.

```bash
curl http://127.0.0.1:8000/health
```

```json
{ "status": "ok" }
```

### `POST /leads`

Procesa un mensaje de lead con el pipeline completo (6 agentes) y devuelve el resultado.

**Request body**

```json
{
  "raw_input": "Hola, soy Juan Pérez de Acme SAS, necesitamos plataforma de reservas...",
  "source": "manual"
}
```

**Ejemplo**

```bash
curl -X POST http://127.0.0.1:8000/leads \
  -H "Content-Type: application/json" \
  -d '{"raw_input":"Hola, soy Juan Pérez de Acme SAS, necesitamos plataforma de reservas para 5 sedes. Presupuesto 20M COP. juan@acme.co","source":"email"}'
```

**Response 200** — `CRMResult.to_dict()`

```json
{
  "lead_id": "a1b2c3d4e5f6a7b8",
  "name": "Juan Pérez",
  "company": "Acme SAS",
  "score": 95,
  "category": "hot",
  "urgency": "high",
  "summary": "Lead warm-hot con necesidad concreta de plataforma de reservas multi-sede...",
  "email_subject": "Seguimiento — Plataforma de reservas para Acme SAS",
  "email_body": "Hola Juan, gracias por tu mensaje...",
  "proposal_title": "Plataforma de reservas multi-sede",
  "proposal_body": "Propuesta de valor...",
  "tasks": [
    "Enviar propuesta detallada",
    "Llamar para agendar demo",
    "Confirmar presupuesto con finanzas"
  ]
}
```

### `GET /leads`

Lista los leads persistidos con score, categoría y resumen.

```bash
curl http://127.0.0.1:8000/leads
```

**Response 200** — `LeadOut[]`

```json
[
  {
    "id": "a1b2c3d4e5f6a7b8",
    "name": "Juan Pérez",
    "email": "juan@acme.co",
    "phone": "3101234567",
    "company": "Acme SAS",
    "score": 95,
    "category": "hot",
    "summary": "Lead warm-hot con necesidad concreta..."
  }
]
```

### `GET /leads/{lead_id}`

Detalle completo de un lead: clasificación, resumen, emails, propuestas, tareas e historial (`HistoryEvent[]`).

```bash
curl http://127.0.0.1:8000/leads/a1b2c3d4e5f6a7b8
```

**Response 200**

```json
{
  "lead": { "id": "...", "name": "Juan Pérez", "email": "juan@acme.co", "company": "Acme SAS", "source": "email", "raw_input": "...", "need": "...", "budget": "20M COP", "timing": "2 semanas", "created_at": "2026-07-22T..." },
  "classification": { "score": 95, "category": "hot", "urgency": "high", "reasoning": "..." },
  "summary": { "text": "..." },
  "emails": [ { "subject": "...", "body": "...", "tone": "professional" } ],
  "proposals": [ { "title": "...", "body": "...", "price_estimate": "..." } ],
  "tasks": [ { "description": "...", "due_in_days": 2, "status": "pending" } ],
  "history": [
    { "agent": "extractor", "action": "Datos extraídos del lead", "created_at": "..." },
    { "agent": "classifier", "action": "Score 95/100 · hot · high", "created_at": "..." }
  ]
}
```

Si el lead no existe: `{ "error": "Lead not found" }`.

## Modelo de datos (resumen)

| Entidad | Campos clave |
|---|---|
| `Lead` | id, name, email, phone, company, source, raw_input, need, budget, timing |
| `Classification` | score (0-100), category (hot/warm/cold), urgency, reasoning |
| `Summary` | text |
| `EmailDraft` | subject, body, tone |
| `Proposal` | title, body, price_estimate |
| `Task` | description, due_in_days, status |
| `HistoryEvent` | agent, action, payload, created_at |