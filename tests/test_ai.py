"""Tests for the AI explanation layer and model resolution."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from utils.ai import (
    _extract_model_names,
    _resolve_model,
    generar_respuesta,
    generar_respuesta_regla,
)


# ---------------------------------------------------------------------------
# Rule-based fallback
# ---------------------------------------------------------------------------

SAMPLE_CONTEXT = {
    "precios": [1.0, 1.1, 1.2],
    "tendencia": "increasing",
    "recomendacion": "Esperar antes de vender",
    "promedio_movil": 1.1,
    "region": "Lima",
    "mercado": "Mayorista",
    "volumen_actual": 1000,
    "clima_actual": "soleado",
    "demanda_actual": "alta",
    "precio_actual": 1.2,
    "precio_predicho": 1.3,
    "diferencia_prediccion": 0.1,
    "tendencia_dataset": "subiendo",
}


def test_fallback_returns_string() -> None:
    result = generar_respuesta_regla("maiz", SAMPLE_CONTEXT)
    assert isinstance(result, str)
    assert len(result) > 0


def test_fallback_contains_product_name() -> None:
    result = generar_respuesta_regla("maiz", SAMPLE_CONTEXT)
    assert "maiz" in result.lower()


def test_fallback_contains_recommendation() -> None:
    result = generar_respuesta_regla("maiz", SAMPLE_CONTEXT)
    assert SAMPLE_CONTEXT["recomendacion"] in result


# ---------------------------------------------------------------------------
# Model name extraction
# ---------------------------------------------------------------------------


def test_extract_model_names_from_dict() -> None:
    response = {"models": [{"model": "gemma4:e4b"}, {"model": "llama3:8b"}]}
    assert _extract_model_names(response) == ("gemma4:e4b", "llama3:8b")


def test_extract_model_names_from_object() -> None:
    item = MagicMock()
    item.model = "gemma4:e4b"
    response = MagicMock()
    response.models = [item]
    assert _extract_model_names(response) == ("gemma4:e4b",)


def test_extract_model_names_empty() -> None:
    assert _extract_model_names({"models": []}) == ()


# ---------------------------------------------------------------------------
# Model resolution
# ---------------------------------------------------------------------------


@patch("utils.ai._get_available_models", return_value=("gemma4:e4b", "gemma4:e2b"))
def test_resolve_preferred_model_found(_mock: MagicMock) -> None:
    assert _resolve_model("gemma4:e4b") == "gemma4:e4b"


@patch("utils.ai._get_available_models", return_value=("gemma4:e2b",))
def test_resolve_fallback_chain(_mock: MagicMock) -> None:
    result = _resolve_model("gemma4:e4b")
    assert result == "gemma4:e2b"


@patch("utils.ai._get_available_models", return_value=("llama3:8b",))
def test_resolve_no_gemma_returns_none(_mock: MagicMock) -> None:
    assert _resolve_model("gemma4:e4b") is None


@patch("utils.ai._get_available_models", return_value=())
def test_resolve_empty_returns_preferred(_mock: MagicMock) -> None:
    assert _resolve_model("gemma4:e4b") == "gemma4:e4b"


# ---------------------------------------------------------------------------
# generar_respuesta with mock — graceful fallback
# ---------------------------------------------------------------------------


@patch("utils.ai._resolve_model", return_value=None)
def test_generar_respuesta_no_model_uses_fallback(_mock: MagicMock) -> None:
    result = generar_respuesta("maiz", SAMPLE_CONTEXT)
    expected_fallback = generar_respuesta_regla("maiz", SAMPLE_CONTEXT)
    assert result == expected_fallback
