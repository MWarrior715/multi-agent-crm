# Multi-Agent CRM Assistant — ROADMAP

## V0.1.0 (actual)
- [x] Pipeline de 6 agentes: Extractor, Clasificador, Resumen, Email, Propuesta, Tareas.
- [x] Persistencia SQLite con SQLModel + historial auditable.
- [x] CLI + FastAPI.
- [x] Motor LLM enchufable vía API OpenAI-compatible.
- [x] Tests con LLM falso.
- [x] README, ARCHITECTURE, DECISIONS, CHANGELOG, LICENSE.

## V0.2.0 — Conexión con canales reales
- [ ] Ingesta de email real (IMAP/SMTP o API de Gmail).
- [ ] Webhook de WhatsApp/Telegram para entrada de leads.
- [ ] Envío real de los `EmailDraft` generados (cola + rate limit).

## V0.3.0 — Escalado de persistencia y concurrencia
- [ ] Migración a PostgreSQL.
- [ ] Clasificador y Resumen en paralelo (asyncio) cuando el cuello sea latencia de LLM.
- [ ] Caché de embeddings para clasificación semántica de leads similares.

## V0.4.0 — Dashboard y闭环 de seguimiento
- [ ] Dashboard UI (Next.js) con la línea de tiempo de cada lead.
- [ ] Cierre de `Task` (pending → done) y re-feed al orquestador.
- [ ] Métricas: tasa de conversión hot→respuesta, tiempo medio de seguimiento.

## Futuro
- [ ] Integración con PoC 05 (AI Operations Center) para observar el pipeline en vivo.
- [ ] Aprendizaje por retroalimentación: correcciones del vendedor afinan el prompt del clasificador.