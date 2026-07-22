# Multi-Agent CRM

**PoC 03** del AI Product Lab — un pipeline de CRM con inteligencia artificial que procesa mensajes de leads con una orquestación de agentes especializados, genera seguimiento automático y persiste todo en SQLite.

> **Vivo en:** [github.com/MWarrior715/multi-agent-crm](https://github.com/MWarrior715/multi-agent-crm)

---

## Qué hace

Recibe un mensaje de entrada (email, WhatsApp, web) y lo enruta por 6 agentes especializados:

| Agente | Tarea |
|--------|-------|
| **Extractor** | Extrae datos estructurados del lead: nombre, email, teléfono, empresa, necesidad, presupuesto, timing. |
| **Clasificador** | Calcula `score` de calidad, categoría (`cold`/`warm`/`hot`), urgencia y razonamiento. |
| **Resumen** | Produce un resumen ejecutivo del contexto del lead. |
| **Redactor de Email** | Genera un borrador personalizado de seguimiento. |
| **Redactor de Propuesta** | Crea una propuesta de valor con estimación de precio. |
| **Planificador de Tareas** | Define tareas de seguimiento con fechas relativas. |

Todo se persiste en **SQLite** (`sqlmodel`) para consulta, auditoría y futuras integraciones.

---

## Arquitectura

```text
input text
   │
   ▼
┌─────────────┐
│  Extractor  │ → Lead
└─────────────┘
   │
   ▼
┌─────────────┐
┌─────────────┐
│ Clasificador│ → Classification
└─────────────┘
   │
   ▼
┌─────────────┐
│  Resumen    │ → Summary
└─────────────┘
   │
   ├──────────► Email Writer     → EmailDraft
   ├──────────► Proposal Writer  → Proposal
   └──────────► Task Planner     → Task[]
```

- **Motor LLM enchufable**: implementación genérica de `LLMProvider` con respaldo `OpenAIProvider` (compatible con Ollama / OpenAI API). Los tests usan un LLM falso.
- **Persistencia**: `SQLModel` sobre SQLite.
- **Interfaces**: CLI interactiva y FastAPI (`/process`, `/leads`, `/health`).

---

## Instalación

```bash
python -m venv .venv
. .venv/Scripts/activate  # o source .venv/bin/activate en Linux/macOS
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y ajusta:

```bash
cp .env.example .env
```

Ejemplo con Ollama local:

```dotenv
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_API_KEY=local-dev-key
LLM_MODEL=glm-5.2:cloud
DATABASE_URL=sqlite:///data/crm.db
```

---

## Uso

### CLI

```bash
python -m crm "Hola, soy Juan Pérez de Acme SAS, necesitamos plataforma de reservas para 5 sedes. Presupuesto 20M COP, decisión en 2 semanas. juan@acme.co 3101234567"
```

Salida JSON:

```bash
python -m crm "..." --json
```

### FastAPI

```bash
uvicorn crm.api:app --reload
```

Endpoints:
- `POST /process` — procesa un mensaje y devuelve el pipeline completo.
- `GET  /leads` — lista leads con resumen/clasificación.
- `GET  /health` — healthcheck.

### Tests

```bash
pytest -q
```

---

## Decisiones de diseño

1. **Python puro, sin LangChain/LangGraph**. Reduce dependencias y deja el control del prompt/completado al orquestador.
2. **Agentes con JSON forzado**. Cada agente devuelve JSON estructurado parseado por `pydantic`.
3. **Modelo enchufable**. Fácil migración de Ollama local a OpenAI, Claude, Gemini o cualquier API compatible.
4. **SQLite por defecto**. Ideal para demos y PoCs sin infraestructura.

---

## Roadmap

- [ ] Integración con email real (IMAP/SMTP o API de Gmail).
- [ ] Webhook de WhatsApp/Telegram.
- [ ] Dashboard UI con Next.js.
- [ ] Caché de embeddings para clasificación semántica.
- [ ] Historial de interacciones por lead.

---

## Licencia

MIT
