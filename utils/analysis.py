"""Business logic for agricultural price analysis."""

from __future__ import annotations

from typing import Any

import pandas as pd


TREND_INCREASING = "increasing"
TREND_DECREASING = "decreasing"
TREND_STABLE = "stable"

RECOMMENDATION_MAP = {
    TREND_DECREASING: "Vender ahora",
    TREND_INCREASING: "Esperar antes de vender",
    TREND_STABLE: "Monitorear el mercado",
}


def _detectar_tendencia(precios: list[float], tolerance: float = 0.02) -> str:
    """Classify the trend using the first and last observed prices."""
    if len(precios) < 2:
        return TREND_STABLE

    variacion = precios[-1] - precios[0]

    if variacion > tolerance:
        return TREND_INCREASING
    if variacion < -tolerance:
        return TREND_DECREASING
    return TREND_STABLE


def _calcular_promedio_movil(precios: list[float], window: int = 3) -> float:
    """Return a lightweight moving average using the latest observations."""
    if not precios:
        return 0.0

    serie = precios[-window:]
    return round(sum(serie) / len(serie), 2)


def preparar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and sort the dataset once so later analysis stays fast."""
    df_preparado = df.copy()
    df_preparado["fecha"] = pd.to_datetime(df_preparado["fecha"])
    df_preparado["producto"] = df_preparado["producto"].astype(str).str.strip()
    df_preparado["producto_key"] = df_preparado["producto"].str.lower()
    df_preparado["precio"] = df_preparado["precio"].astype(float)

    if "precio_predicho" in df_preparado.columns:
        df_preparado["precio_predicho"] = df_preparado["precio_predicho"].astype(float)
    if "volumen" in df_preparado.columns:
        df_preparado["volumen"] = df_preparado["volumen"].astype(float)

    return df_preparado.sort_values(["producto_key", "fecha"]).reset_index(drop=True)


def analizar_producto(df: pd.DataFrame, producto: str) -> dict[str, Any]:
    """Analyze price history for a product and build a recommendation."""
    producto_key = producto.strip().lower()
    df_producto = df[df["producto_key"] == producto_key].reset_index(drop=True)

    if df_producto.empty:
        raise ValueError(f"No se encontraron datos para el producto: {producto}")

    precios = df_producto["precio"].tolist()
    tendencia = _detectar_tendencia(precios)
    promedio_movil = _calcular_promedio_movil(precios)
    ultimo_registro = df_producto.iloc[-1]

    precio_actual = float(ultimo_registro["precio"])
    precio_predicho = float(ultimo_registro.get("precio_predicho", precio_actual))
    diferencia_prediccion = round(precio_predicho - precio_actual, 2)

    if diferencia_prediccion < -0.01:
        recomendacion = "Vender ahora"
    elif diferencia_prediccion > 0.01:
        recomendacion = "Esperar antes de vender"
    else:
        recomendacion = RECOMMENDATION_MAP[tendencia]

    return {
        "precios": precios,
        "tendencia": tendencia,
        "recomendacion": recomendacion,
        "promedio_movil": promedio_movil,
        "region": str(ultimo_registro.get("region", "")),
        "mercado": str(ultimo_registro.get("mercado", "")),
        "volumen_actual": float(ultimo_registro.get("volumen", 0)),
        "clima_actual": str(ultimo_registro.get("clima", "")),
        "demanda_actual": str(ultimo_registro.get("demanda", "")),
        "precio_actual": precio_actual,
        "precio_predicho": precio_predicho,
        "diferencia_prediccion": diferencia_prediccion,
        "tendencia_dataset": str(ultimo_registro.get("tendencia", "")),
    }
