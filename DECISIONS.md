# Multi-Agent CRM Assistant — Decisiones

## ¿Por qué Python puro (sin LangChain/LangGraph)?

Un CRM multi-agente se puede construir con frameworks de orquestación, pero para un PoC el valor está en mostrar **la cadena de agentes y el contrato de datos entre ellos**, no en el boilerplate del framework. Python puro + pydantic deja el control del prompt, el parseo y el orden de ejecución totalmente visibles. Menos dependencias, menos magia oculta, demo más clara para un CTO.

## ¿Por qué agentes secuenciales y no concurrentes?

El extractor produce el `Lead` que todos los demás consumen. El clasificador y el resumen podrían correr en paralelo, pero el email, la propuesta y las tareas se benefician del score y la urgencia. Para un PoC, la secuencia lineal hace que la **trazabilidad** (un `HistoryEvent` por paso) sea trivial y el demo sea fácil de narrar. El paralelismo es material de ROADMAP cuando el cuello sea la latencia del LLM.

## ¿Por qué JSON forzado con pydantic?

Cada agente le pide al LLM un objeto JSON con esquema fijo y pydantic lo valida. Esto convierte "texto libre del modelo" en "datos con tipos" que se pueden persistir y encadenar al siguiente agente. Si el LLM se equivoca, el error se atrapa en el parseo, no silenciosamente downstream.

## ¿Por qué SQLite + SQLModel?

SQLite es cero-infra: un archivo `data/crm.db`, ideal para un PoC sin servidor. SQLModel combina pydantic (validación) y SQLAlchemy (persistencia) en una sola definición de entidades, así los modelos del dominio son también las tablas. Migrar a Postgres es cambiar `DATABASE_URL` y añadir un driver — decisión reversible.

## ¿Por qué motor LLM enchufable (OpenAI-compatible)?

El CRM no acopla a un proveedor concreto: usa la API OpenAI-compatible, que sirve para motores locales y cloud. Cambiar de motor es cambiar `OPENAI_BASE_URL` + `LLM_MODEL` en `.env`. Los tests usan un LLM falso que implementa el mismo `LLMProvider`, así la suite corre sin red ni API key.

## ¿Por qué un `HistoryEvent` por paso?

Auditoría y demo. Un lead procesado deja una línea de tiempo `extractor → classifier → summarizer → email_writer → proposal_writer → task_planner` con su acción y timestamp. Eso es exactamente lo que un dashboard futuro consume y lo que se muestra en una demo para probar que "el sistema hizo lo que tenía que hacer".

## Mago-compliance

- Motor LLM vía API OpenAI-compatible; el repo público no nombra proveedores concretos.
- `.env` y `data/crm.db` gitignored.
- README y docs hablan de "Motor de IA Local/Cloud".