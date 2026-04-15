"""Streamlit app for AgroIntel AI."""

from __future__ import annotations

import streamlit as st

from utils.ai import DEFAULT_MODEL, generar_respuesta, generar_respuesta_regla
from utils.analysis import analizar_producto
from utils.data_loader import get_public_dataset_path, load_public_dataset


PAGE_ICON = "\U0001F33E"
BOX_ICON = "\U0001F4E6"
CHART_ICON = "\U0001F4C8"
SEARCH_ICON = "\U0001F50D"
FAST_ICON = "\u26A1"
AI_ICON = "\U0001F916"
INFO_ICON = "\U00002139"


@st.cache_data
def cargar_datos():
    """Load and preprocess agricultural prices once."""
    return load_public_dataset()


def main() -> None:
    """Render the Streamlit interface."""
    st.set_page_config(page_title="AgroIntel AI", page_icon=PAGE_ICON, layout="centered")

    st.title(f"{PAGE_ICON} AgroIntel AI")
    st.subheader("Asistente inteligente para decidir cuando vender")
    st.markdown(
        "Consulta tendencias de precios y recibe una recomendacion inmediata. "
        "La explicacion con IA local usa tambien clima, demanda, mercado y precio predicho."
    )
    st.caption(f"Dataset publico cargado desde `{get_public_dataset_path()}`")

    df = cargar_datos()
    productos = sorted(df["producto"].dropna().unique().tolist())

    st.markdown(f"### {BOX_ICON} Selecciona un producto")
    producto = st.selectbox(
        "Producto agricola",
        options=productos,
        help="Elige el producto que quieres analizar.",
    )

    if st.button(f"{SEARCH_ICON} Analizar producto", use_container_width=True):
        try:
            resultado = analizar_producto(df, producto)

            st.markdown(f"### {CHART_ICON} Resultado del analisis")
            st.write(f"**Lista de precios:** {resultado['precios']}")
            st.line_chart(resultado["precios"])
            st.write(f"**Tendencia:** {resultado['tendencia']}")
            st.write(f"**Recomendacion:** {resultado['recomendacion']}")
            st.write(f"**Promedio movil corto:** {resultado['promedio_movil']}")

            st.markdown(f"### {INFO_ICON} Contexto del mercado")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Precio actual", f"S/ {resultado['precio_actual']:.2f}")
                st.metric("Precio predicho", f"S/ {resultado['precio_predicho']:.2f}")
                st.write(f"**Region:** {resultado['region']}")
                st.write(f"**Mercado:** {resultado['mercado']}")
            with col2:
                st.metric("Volumen", f"{resultado['volumen_actual']:.0f}")
                st.write(f"**Clima:** {resultado['clima_actual']}")
                st.write(f"**Demanda:** {resultado['demanda_actual']}")
                st.write(f"**Senal reportada:** {resultado['tendencia_dataset']}")

            st.markdown(f"### {FAST_ICON} Recomendacion inmediata")
            st.success(generar_respuesta_regla(producto=producto, contexto=resultado))

            st.markdown(f"### {AI_ICON} Explicacion para el agricultor")
            st.caption(f"Modelo configurado: `{DEFAULT_MODEL}`")
            with st.spinner("Analizando con IA..."):
                explicacion = generar_respuesta(producto=producto, contexto=resultado)
            st.info(explicacion)
        except ValueError as exc:
            st.error(str(exc))
        except FileNotFoundError as exc:
            st.error(str(exc))


if __name__ == "__main__":
    main()
