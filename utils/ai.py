"""Utilities for generating farmer-friendly AI explanations."""

from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx
import ollama


def _get_env_float(name: str, default: float, minimum: float) -> float:
    """Read a float from the environment and fall back safely when invalid."""
    module_logger = logging.getLogger(__name__)
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        parsed = float(raw_value)
    except ValueError:
        module_logger.warning("Invalid value for %s=%r. Using default %.1f.", name, raw_value, default)
        return default

    if parsed < minimum:
        module_logger.warning("Value for %s must be at least %.1f. Using default %.1f.", name, minimum, default)
        return default

    return parsed


DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b").strip() or "gemma4:e4b"
FALLBACK_MODELS = ("gemma4:e4b", "gemma4:e2b", "gemma4", "gemma4:26b", "gemma4:31b", "gemma:2b", "gemma")
REQUEST_TIMEOUT_SECONDS = _get_env_float("OLLAMA_TIMEOUT_SECONDS", 45.0, minimum=1.0)
OLLAMA_COOLDOWN_SECONDS = _get_env_float("OLLAMA_COOLDOWN_SECONDS", 15.0, minimum=0.0)
RESPONSE_CACHE: dict[tuple[str, tuple[tuple[str, str], ...], str], str] = {}
AVAILABLE_MODELS_CACHE: tuple[str, ...] | None = None
OLLAMA_DISABLED_UNTIL = 0.0

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(
    "Ollama configured with model=%s timeout=%.1fs cooldown=%.1fs",
    DEFAULT_MODEL,
    REQUEST_TIMEOUT_SECONDS,
    OLLAMA_COOLDOWN_SECONDS,
)

try:
    OLLAMA_CLIENT = ollama.Client(timeout=REQUEST_TIMEOUT_SECONDS)
except TypeError:
    OLLAMA_CLIENT = ollama.Client()
    logger.debug("Ollama client timeout is not supported in this environment.")


def _normalize_contexto(contexto: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    """Create a stable cache representation from the analysis context."""
    return tuple(sorted((str(key), str(value)) for key, value in contexto.items()))


def _cache_key(
    producto: str,
    contexto: dict[str, Any],
    model: str,
) -> tuple[str, tuple[tuple[str, str], ...], str]:
    """Create a stable in-memory cache key for repeated prompts."""
    return (producto.strip().lower(), _normalize_contexto(contexto), model)


def _extract_model_names(list_response: object) -> tuple[str, ...]:
    """Extract installed model names from different Ollama client response shapes."""
    models = getattr(list_response, "models", None)
    if models is None and isinstance(list_response, dict):
        models = list_response.get("models", [])

    nombres: list[str] = []
    for item in models or []:
        if isinstance(item, dict):
            nombre = item.get("model") or item.get("name")
        else:
            nombre = getattr(item, "model", None) or getattr(item, "name", None)
        if nombre:
            nombres.append(str(nombre))

    return tuple(nombres)


def _get_available_models() -> tuple[str, ...]:
    """Query installed Ollama models once and reuse the result."""
    global AVAILABLE_MODELS_CACHE

    if AVAILABLE_MODELS_CACHE is not None:
        return AVAILABLE_MODELS_CACHE

    try:
        AVAILABLE_MODELS_CACHE = _extract_model_names(OLLAMA_CLIENT.list())
        logger.info("Detected Ollama models: %s", AVAILABLE_MODELS_CACHE)
    except Exception as exc:
        logger.warning("Could not list Ollama models: %s", exc)
        AVAILABLE_MODELS_CACHE = ()

    return AVAILABLE_MODELS_CACHE


def _resolve_model(preferred_model: str) -> str | None:
    """Choose the best available model, preferring the configured one."""
    available = _get_available_models()
    if not available:
        return preferred_model

    if preferred_model in available:
        return preferred_model

    for candidate in FALLBACK_MODELS:
        if candidate in available:
            logger.info(
                "Preferred model %s not found. Falling back to installed model %s",
                preferred_model,
                candidate,
            )
            return candidate

    gemma4_models = [model for model in available if model.startswith("gemma4")]
    if gemma4_models:
        logger.info(
            "Preferred model %s not found. Falling back to detected Gemma 4 model %s",
            preferred_model,
            gemma4_models[0],
        )
        return gemma4_models[0]

    gemma_models = [model for model in available if model.startswith("gemma")]
    if gemma_models:
        logger.info(
            "No Gemma 4 model found. Falling back to legacy Gemma model %s",
            gemma_models[0],
        )
        return gemma_models[0]

    logger.warning("No Gemma-compatible model detected in Ollama.")
    return None


def _ollama_available_now() -> bool:
    """Return whether Ollama should be attempted right now."""
    if OLLAMA_DISABLED_UNTIL <= time.time():
        return True

    seconds_left = int(max(1, OLLAMA_DISABLED_UNTIL - time.time()))
    logger.info("Skipping Ollama request during cooldown. %s seconds remaining.", seconds_left)
    return False


def _activate_ollama_cooldown(reason: str) -> None:
    """Temporarily disable Ollama calls after a timeout or connectivity issue."""
    global OLLAMA_DISABLED_UNTIL

    if OLLAMA_COOLDOWN_SECONDS <= 0:
        logger.warning("Ollama cooldown skipped because OLLAMA_COOLDOWN_SECONDS is disabled. Reason: %s.", reason)
        return

    OLLAMA_DISABLED_UNTIL = time.time() + OLLAMA_COOLDOWN_SECONDS
    logger.warning(
        "Ollama cooldown activated for %.0f seconds due to %s.",
        OLLAMA_COOLDOWN_SECONDS,
        reason,
    )


def generar_respuesta_regla(producto: str, contexto: dict[str, Any]) -> str:
    """Return a deterministic explanation that does not depend on Ollama."""
    precio_actual = float(contexto["precio_actual"])
    precio_predicho = float(contexto["precio_predicho"])
    clima = contexto.get("clima_actual", "sin dato")
    demanda = contexto.get("demanda_actual", "sin dato")
    tendencia_dataset = contexto.get("tendencia_dataset", contexto["tendencia"])
    recomendacion = contexto["recomendacion"]

    return (
        f"Para {producto}, el precio actual es {precio_actual:.2f} y el precio predicho es {precio_predicho:.2f}. "
        f"La demanda esta {demanda} y el clima actual es {clima}, con una senal de mercado {tendencia_dataset}. "
        f"La recomendacion es: {recomendacion}."
    )


def generar_respuesta(
    producto: str,
    contexto: dict[str, Any],
    model: str = DEFAULT_MODEL,
) -> str:
    """Generate an explanation with Ollama, but safely fall back when needed."""
    fallback = generar_respuesta_regla(producto, contexto)
    selected_model = _resolve_model(model)
    cache_key = _cache_key(producto, contexto, selected_model or "rule-based")
    if cache_key in RESPONSE_CACHE:
        logger.info("Using cached response for %s", producto)
        return RESPONSE_CACHE[cache_key]

    if not selected_model:
        logger.warning("No available Ollama model for %s. Using fallback response.", producto)
        RESPONSE_CACHE[cache_key] = fallback
        return fallback

    if not _ollama_available_now():
        RESPONSE_CACHE[cache_key] = fallback
        return fallback

    prompt = f"""
Eres un asistente agricola para productores.
Responde en espanol simple, sin tecnicismos, como en una conversacion real.

Datos del producto:
- Producto: {producto}
- Region: {contexto['region']}
- Mercado: {contexto['mercado']}
- Precios recientes: {contexto['precios']}
- Precio actual: {contexto['precio_actual']}
- Precio predicho: {contexto['precio_predicho']}
- Tendencia historica: {contexto['tendencia']}
- Tendencia reportada: {contexto['tendencia_dataset']}
- Volumen actual: {contexto['volumen_actual']}
- Clima actual: {contexto['clima_actual']}
- Demanda actual: {contexto['demanda_actual']}
- Recomendacion sugerida: {contexto['recomendacion']}

Instrucciones:
- Explica que esta pasando con el precio.
- Indica si conviene vender ahora o esperar.
- Menciona como influyen demanda, clima, volumen y mercado.
- Usa el precio predicho para reforzar la decision.
- Cierra con una recomendacion corta y practica.
- Responde en maximo 4 oraciones.
""".strip()

    try:
        logger.info("Requesting Ollama response with model %s", selected_model)
        response = OLLAMA_CLIENT.chat(
            model=selected_model,
            messages=[{"role": "user", "content": prompt}],
        )
        contenido = response["message"]["content"].strip()
        if not contenido:
            logger.warning("Empty Ollama response for %s. Using fallback.", producto)
            contenido = fallback
    except (httpx.ReadTimeout, TimeoutError) as exc:
        _activate_ollama_cooldown("timeout")
        logger.warning("Ollama timed out for %s with model %s. Using fallback.", producto, selected_model)
        logger.debug("Timeout detail: %s", exc)
        contenido = fallback
    except Exception as exc:
        logger.warning("Ollama failed for %s with model %s. Using fallback. Detail: %s", producto, selected_model, exc)
        contenido = fallback

    RESPONSE_CACHE[cache_key] = contenido
    return contenido
