"""Tests for the analysis layer and dataset contract."""

from __future__ import annotations

import pandas as pd
import pytest

from utils.analysis import (
    TREND_DECREASING,
    TREND_INCREASING,
    TREND_STABLE,
    _calcular_promedio_movil,
    _detectar_tendencia,
    analizar_producto,
    preparar_datos,
)
from utils.data_loader import get_public_dataset_path, load_public_dataset


# ---------------------------------------------------------------------------
# Dataset contract
# ---------------------------------------------------------------------------

REQUIRED_COLUMNS = {
    "producto",
    "fecha",
    "precio",
    "region",
    "mercado",
    "volumen",
    "clima",
    "demanda",
    "tendencia",
    "precio_predicho",
}


def test_public_dataset_exists() -> None:
    path = get_public_dataset_path()
    assert path.exists(), f"Public dataset not found at {path}"


def test_public_dataset_has_required_columns() -> None:
    df = load_public_dataset()
    missing = REQUIRED_COLUMNS - set(df.columns)
    assert not missing, f"Missing columns in public dataset: {missing}"


def test_public_dataset_has_rows() -> None:
    df = load_public_dataset()
    assert len(df) > 0, "Public dataset is empty"


# ---------------------------------------------------------------------------
# Trend detection
# ---------------------------------------------------------------------------


def test_trend_increasing() -> None:
    assert _detectar_tendencia([1.0, 1.1, 1.3]) == TREND_INCREASING


def test_trend_decreasing() -> None:
    assert _detectar_tendencia([1.3, 1.1, 1.0]) == TREND_DECREASING


def test_trend_stable() -> None:
    assert _detectar_tendencia([1.0, 1.01, 1.0]) == TREND_STABLE


def test_trend_single_price() -> None:
    assert _detectar_tendencia([1.0]) == TREND_STABLE


# ---------------------------------------------------------------------------
# Moving average
# ---------------------------------------------------------------------------


def test_promedio_movil_basic() -> None:
    result = _calcular_promedio_movil([1.0, 2.0, 3.0], window=3)
    assert result == 2.0


def test_promedio_movil_empty() -> None:
    assert _calcular_promedio_movil([]) == 0.0


# ---------------------------------------------------------------------------
# Product analysis
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_df() -> pd.DataFrame:
    data = {
        "producto": ["papa", "papa", "papa", "maiz", "maiz"],
        "fecha": ["2026-04-01", "2026-04-02", "2026-04-03", "2026-04-01", "2026-04-02"],
        "precio": [0.80, 0.75, 0.70, 1.20, 1.30],
        "region": ["Lima", "Lima", "Lima", "Cusco", "Cusco"],
        "mercado": ["Mayorista", "Mayorista", "Mayorista", "Local", "Local"],
        "volumen": [1200, 1400, 1600, 900, 850],
        "clima": ["soleado", "lluvia", "lluvia", "soleado", "soleado"],
        "demanda": ["media", "alta", "alta", "media", "alta"],
        "tendencia": ["estable", "bajando", "bajando", "estable", "subiendo"],
        "precio_predicho": [0.78, 0.72, 0.68, 1.22, 1.35],
    }
    return preparar_datos(pd.DataFrame(data))


def test_analizar_producto_returns_expected_keys(sample_df: pd.DataFrame) -> None:
    resultado = analizar_producto(sample_df, "papa")
    expected_keys = {
        "precios",
        "tendencia",
        "recomendacion",
        "promedio_movil",
        "region",
        "mercado",
        "volumen_actual",
        "clima_actual",
        "demanda_actual",
        "precio_actual",
        "precio_predicho",
        "diferencia_prediccion",
        "tendencia_dataset",
    }
    assert expected_keys == set(resultado.keys())


def test_analizar_producto_decreasing_recommends_sell(sample_df: pd.DataFrame) -> None:
    resultado = analizar_producto(sample_df, "papa")
    assert resultado["tendencia"] == TREND_DECREASING
    assert resultado["recomendacion"] == "Vender ahora"


def test_analizar_producto_increasing(sample_df: pd.DataFrame) -> None:
    resultado = analizar_producto(sample_df, "maiz")
    assert resultado["tendencia"] == TREND_INCREASING


def test_analizar_producto_unknown_raises(sample_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="No se encontraron datos"):
        analizar_producto(sample_df, "quinoa")
