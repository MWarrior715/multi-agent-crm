"""app.py — UI Streamlit del Multi-Agent CRM Assistant.

    streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from crm.db import init_db
from crm.engine import CRMPipeline

st.set_page_config(
    page_title="Multi-Agent CRM Assistant",
    page_icon="🤝",
    layout="wide",
)

st.title("🤝 Multi-Agent CRM Assistant")
st.caption(
    "Procesa leads con agentes especializados: extracción, clasificación, resumen, "
    "email, propuesta y tareas de seguimiento."
)

init_db()

# Cache del pipeline para no recrearlo en cada interacción.
@st.cache_resource
def get_pipeline() -> CRMPipeline:
    return CRMPipeline()


pipeline = get_pipeline()

with st.sidebar:
    st.markdown("### Configuración")
    st.markdown("Motor de IA: Local/Cloud (OpenAI-compatible). Configurable vía `.env`.")

raw_input = st.text_area(
    "Pega aquí el lead (texto libre)",
    placeholder="Ej: Hola, soy Juan Pérez de Acme SAS. Necesitamos una plataforma de reservas para 5 sedes. "
    "Presupuesto 20M COP, decisión en 2 semanas. juan@acme.co 3101234567",
    height=120,
)

source = st.selectbox("Origen del lead", ["manual", "formulario web", "email", "whatsapp"])

if st.button("Procesar lead", type="primary", disabled=not raw_input.strip()):
    with st.spinner("Agentes trabajando…"):
        result = pipeline.process(raw_input, source=source)

    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{result.classification.score}/100")
    col2.metric("Categoría", result.classification.category.upper())
    col3.metric("Urgencia", result.classification.urgency.upper())

    st.markdown("---")
    st.subheader("📝 Resumen ejecutivo")
    st.write(result.summary.text)

    st.markdown("---")
    st.subheader("📧 Email de primer contacto")
    st.text_input("Asunto", value=result.email.subject, disabled=True)
    st.text_area("Cuerpo", value=result.email.body, height=150, disabled=True)

    st.markdown("---")
    st.subheader("💼 Propuesta de valor")
    st.write(f"**{result.proposal.title}**")
    st.write(result.proposal.body)
    if result.proposal.price_estimate:
        st.write(f"*Estimación:* {result.proposal.price_estimate}")

    st.markdown("---")
    st.subheader("✅ Tareas de seguimiento")
    for t in result.tasks:
        st.checkbox(f"{t.description} (en {t.due_in_days} días)", key=f"task_{t.id}")

    st.markdown("---")
    st.info(f"Lead guardado en base de datos con ID: `{result.lead.id}`")
