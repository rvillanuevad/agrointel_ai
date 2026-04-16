"""Streamlit app for AgroIntel AI — mobile-first design."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.ai import DEFAULT_MODEL, generar_respuesta, generar_respuesta_regla
from utils.analysis import analizar_producto
from utils.data_loader import get_public_dataset_path, load_public_dataset


PAGE_ICON = "\U0001F33E"

TREND_LABELS = {
    "increasing": ("\U0001F4C8", "En alza", "green"),
    "decreasing": ("\U0001F4C9", "En baja", "red"),
    "stable": ("\u2796", "Estable", "orange"),
}

CLIMA_ICONS = {
    "soleado": "\u2600\uFE0F",
    "nublado": "\u2601\uFE0F",
    "lluvia": "\U0001F327\uFE0F",
}

DEMANDA_ICONS = {
    "alta": "\U0001F525",
    "media": "\u27A1\uFE0F",
    "baja": "\u2744\uFE0F",
}


@st.cache_data
def cargar_datos():
    """Load and preprocess agricultural prices once."""
    return load_public_dataset()


def _inject_mobile_css() -> None:
    """Inject mobile-first styles: compact, touch-friendly, single-column."""
    # Split into separate st.markdown calls to avoid Streamlit HTML parsing issues
    # with large blocks. The <meta> tag goes alone to prevent it from breaking
    # the <style> block in some Streamlit versions.
    st.markdown(
        '<style>'
        '  .stApp { max-width: 480px !important; margin: 0 auto !important; padding: 0 0.5rem !important; }'
        '  section[data-testid="stSidebar"] { display: none !important; }'
        '  header[data-testid="stHeader"] { display: none !important; }'
        '  .block-container { padding: 0.8rem 0.6rem 3rem 0.6rem !important; max-width: 480px !important; }'
        '  .app-bar { background: linear-gradient(135deg, #2E7D32 0%, #43A047 100%); color: white;'
        '    padding: 1rem 1rem 0.8rem 1rem; border-radius: 0 0 1.2rem 1.2rem;'
        '    margin: -0.8rem -0.6rem 1rem -0.6rem; text-align: center; }'
        '  .app-bar h1 { font-size: 1.5rem; margin: 0; font-weight: 700; color: white !important; }'
        '  .app-bar p { font-size: 0.82rem; margin: 0.2rem 0 0 0; opacity: 0.9; color: #E8F5E9; }'
        '</style>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<style>'
        '  .rec-card { border-radius: 1rem; padding: 1rem; text-align: center; margin-bottom: 0.8rem; }'
        '  .rec-card .rec-label { font-size: 0.75rem; text-transform: uppercase;'
        '    letter-spacing: 0.08em; opacity: 0.8; margin-bottom: 0.2rem; }'
        '  .rec-card .rec-action { font-size: 1.3rem; font-weight: 800; }'
        '  .rec-sell  { background: #FFCDD2; color: #B71C1C; }'
        '  .rec-wait  { background: #C8E6C9; color: #1B5E20; }'
        '  .rec-watch { background: #FFF9C4; color: #F57F17; }'
        '  .metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.8rem; }'
        '  .metric-card { background: #FAFAFA; border: 1px solid #E0E0E0;'
        '    border-radius: 0.8rem; padding: 0.7rem 0.6rem; text-align: center; }'
        '  .metric-card .m-label { font-size: 0.7rem; color: #757575;'
        '    text-transform: uppercase; letter-spacing: 0.04em; }'
        '  .metric-card .m-value { font-size: 1.2rem; font-weight: 700; color: #212121; margin-top: 0.1rem; }'
        '  .metric-card .m-delta { font-size: 0.75rem; font-weight: 600; margin-top: 0.1rem; }'
        '  .delta-up   { color: #2E7D32; }'
        '  .delta-down { color: #C62828; }'
        '</style>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<style>'
        '  .chip-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.8rem; }'
        '  .chip { display: inline-flex; align-items: center; gap: 0.25rem;'
        '    padding: 0.35rem 0.7rem; border-radius: 2rem; font-size: 0.78rem;'
        '    font-weight: 500; background: #F5F5F5; color: #424242; border: 1px solid #E0E0E0; }'
        '  .trend-badge { display: inline-flex; align-items: center; gap: 0.25rem;'
        '    padding: 0.35rem 0.75rem; border-radius: 2rem; font-size: 0.78rem; font-weight: 700; }'
        '  .trend-green  { background: #C8E6C9; color: #1B5E20; }'
        '  .trend-red    { background: #FFCDD2; color: #B71C1C; }'
        '  .trend-orange { background: #FFF9C4; color: #F57F17; }'
        '  .m-section { font-size: 0.82rem; font-weight: 700; color: #2E7D32;'
        '    text-transform: uppercase; letter-spacing: 0.06em; margin: 1rem 0 0.4rem 0; }'
        '</style>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<style>'
        '  .expl-card { background: #E3F2FD; border-left: 4px solid #1565C0;'
        '    border-radius: 0.6rem; padding: 0.8rem 0.9rem; font-size: 0.88rem;'
        '    line-height: 1.5; color: #0D47A1; margin-bottom: 0.8rem; }'
        '  .rule-card { background: #E8F5E9; border-left: 4px solid #2E7D32;'
        '    border-radius: 0.6rem; padding: 0.8rem 0.9rem; font-size: 0.88rem;'
        '    line-height: 1.5; color: #1B5E20; margin-bottom: 0.8rem; }'
        '  .stButton > button { width: 100% !important; height: 3.2rem !important;'
        '    font-size: 1.05rem !important; font-weight: 700 !important; border-radius: 0.8rem !important; }'
        '  .stSelectbox [data-baseweb="select"] { min-height: 3rem; font-size: 1rem; }'
        '  .model-footer { text-align: center; font-size: 0.7rem; color: #9E9E9E;'
        '    margin-top: 1.5rem; padding-bottom: 1rem; }'
        '</style>',
        unsafe_allow_html=True,
    )


def _recommendation_card(recomendacion: str, producto: str) -> str:
    """Return an HTML card for the recommendation."""
    if "Vender" in recomendacion:
        css = "rec-sell"
    elif "Esperar" in recomendacion:
        css = "rec-wait"
    else:
        css = "rec-watch"
    return (
        f'<div class="rec-card {css}">'
        f'<div class="rec-label">{producto.capitalize()}</div>'
        f'<div class="rec-action">{recomendacion}</div>'
        f"</div>"
    )


def _metric_card(label: str, value: str, delta: str = "", delta_dir: str = "") -> str:
    """Return an HTML metric card."""
    delta_html = ""
    if delta:
        css = "delta-up" if delta_dir == "up" else "delta-down"
        arrow = "\u25B2" if delta_dir == "up" else "\u25BC"
        delta_html = f'<div class="m-delta {css}">{arrow} {delta}</div>'
    return (
        f'<div class="metric-card">'
        f'<div class="m-label">{label}</div>'
        f'<div class="m-value">{value}</div>'
        f"{delta_html}"
        f"</div>"
    )


def _trend_badge(tendencia: str) -> str:
    """Return an HTML trend badge."""
    icon, label, color = TREND_LABELS.get(tendencia, ("\u2753", tendencia, "orange"))
    return f'<span class="trend-badge trend-{color}">{icon} {label}</span>'


def main() -> None:
    """Render the mobile-first Streamlit interface."""
    st.set_page_config(
        page_title="AgroIntel AI",
        page_icon=PAGE_ICON,
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    _inject_mobile_css()

    # ── App bar ──────────────────────────────────────────────────────────
    st.markdown(
        '<div class="app-bar">'
        f"<h1>{PAGE_ICON} AgroIntel AI</h1>"
        "<p>Asistente de precios para agricultores</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    df = cargar_datos()
    productos = sorted(df["producto"].dropna().unique().tolist())

    # ── Product selector (full width, large touch target) ────────────────
    producto = st.selectbox(
        "Producto",
        options=productos,
        label_visibility="collapsed",
        help="Elige el producto que quieres analizar.",
    )
    analizar = st.button("\U0001F50D Analizar producto", type="primary")

    if not analizar:
        st.markdown(
            '<div style="text-align:center; padding:2rem 0; color:#9E9E9E; font-size:0.9rem;">'
            "Selecciona un producto y toca <b>Analizar</b>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="model-footer">Modelo: {DEFAULT_MODEL} · {get_public_dataset_path().name}</div>',
            unsafe_allow_html=True,
        )
        return

    # ── Analysis ─────────────────────────────────────────────────────────
    try:
        resultado = analizar_producto(df, producto)
    except (ValueError, FileNotFoundError) as exc:
        st.error(str(exc))
        return

    # ── Recommendation card (hero) ───────────────────────────────────────
    st.markdown(
        _recommendation_card(resultado["recomendacion"], producto),
        unsafe_allow_html=True,
    )

    # ── 2×2 Metrics grid ────────────────────────────────────────────────
    delta = resultado["diferencia_prediccion"]
    delta_dir = "up" if delta >= 0 else "down"
    delta_str = f"S/ {delta:+.2f}"

    grid_html = (
        '<div class="metric-grid">'
        + _metric_card("Precio actual", f"S/ {resultado['precio_actual']:.2f}")
        + _metric_card("Precio predicho", f"S/ {resultado['precio_predicho']:.2f}", delta_str, delta_dir)
        + _metric_card("Volumen", f"{resultado['volumen_actual']:,.0f}")
        + _metric_card("Promedio movil", f"S/ {resultado['promedio_movil']:.2f}")
        + "</div>"
    )
    st.markdown(grid_html, unsafe_allow_html=True)

    # ── Price chart ──────────────────────────────────────────────────────
    st.markdown('<div class="m-section">\U0001F4C8 Precios</div>', unsafe_allow_html=True)
    df_producto = df[df["producto_key"] == producto.strip().lower()].copy()
    chart_data = df_producto[["fecha", "precio", "precio_predicho"]].set_index("fecha")
    chart_data.columns = ["Real", "Predicho"]
    st.line_chart(chart_data, use_container_width=True, height=200)

    # ── Context chips ────────────────────────────────────────────────────
    st.markdown('<div class="m-section">\U0001F30D Contexto</div>', unsafe_allow_html=True)

    clima = resultado["clima_actual"]
    demanda = resultado["demanda_actual"]
    clima_icon = CLIMA_ICONS.get(clima, "")
    demanda_icon = DEMANDA_ICONS.get(demanda, "")

    chips_html = (
        '<div class="chip-row">'
        f'<span class="chip">\U0001F4CD {resultado["region"]}</span>'
        f'<span class="chip">\U0001F3EA {resultado["mercado"]}</span>'
        f'<span class="chip">{clima_icon} {clima.capitalize()}</span>'
        f'<span class="chip">{demanda_icon} Demanda {demanda}</span>'
        f'<span class="chip">Senal: {resultado["tendencia_dataset"]}</span>'
        f'{_trend_badge(resultado["tendencia"])}'
        "</div>"
    )
    st.markdown(chips_html, unsafe_allow_html=True)

    # ── Rule-based explanation ───────────────────────────────────────────
    st.markdown('<div class="m-section">\u26A1 Recomendacion rapida</div>', unsafe_allow_html=True)
    regla = generar_respuesta_regla(producto=producto, contexto=resultado)
    st.markdown(f'<div class="rule-card">{regla}</div>', unsafe_allow_html=True)

    # ── AI explanation ───────────────────────────────────────────────────
    st.markdown(
        '<div class="m-section">\U0001F916 Explicacion con Gemma 4</div>',
        unsafe_allow_html=True,
    )
    with st.spinner("Consultando IA local..."):
        explicacion = generar_respuesta(producto=producto, contexto=resultado)
    st.markdown(f'<div class="expl-card">{explicacion}</div>', unsafe_allow_html=True)

    # ── Footer ───────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="model-footer">Modelo: {DEFAULT_MODEL} · {get_public_dataset_path().name}</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
