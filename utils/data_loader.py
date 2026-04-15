"""Helpers for loading the public AgroIntel dataset."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from utils.analysis import preparar_datos


BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DATA_DIR = BASE_DIR / "data" / "public"
DEFAULT_PUBLIC_DATASET = PUBLIC_DATA_DIR / "precios_agrointel.csv"


def get_public_dataset_path() -> Path:
    """Return the expected path for the public dataset consumed by the app."""
    return DEFAULT_PUBLIC_DATASET


def load_public_dataset(path: Path | None = None) -> pd.DataFrame:
    """Load a processed public dataset and prepare it for the app."""
    dataset_path = path or get_public_dataset_path()

    if not dataset_path.exists():
        raise FileNotFoundError(
            "No se encontro el dataset publico procesado en "
            f"{dataset_path}. Exportalo primero desde el pipeline privado."
        )

    if dataset_path.suffix.lower() == ".parquet":
        df = pd.read_parquet(dataset_path)
    else:
        df = pd.read_csv(dataset_path)

    return preparar_datos(df)
