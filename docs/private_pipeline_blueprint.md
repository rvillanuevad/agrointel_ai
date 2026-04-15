# Private Pipeline Boundary

This document describes the boundary between the public AgroIntel application and an external private pipeline that prepares the dataset consumed by the app.

## Goal

The private pipeline should:

- ingest new source files safely
- normalize products, dates, units, and numeric fields
- deduplicate records
- compute base analytical features
- export a publication-safe dataset for `agrointel_ai`

## Suggested private repository structure

```text
private_price_pipeline/
+-- config/
+-- data/
¦   +-- raw/
¦   +-- staging/
¦   +-- processed/
¦   +-- exports/
+-- notebooks/
+-- src/
¦   +-- ingest/
¦   +-- transform/
¦   +-- validate/
¦   +-- export/
+-- tests/
+-- README.md
```

## Processing layers

### 1. Raw

Store the original source files exactly as received. Do not modify them.

### 2. Staging

Apply light standardization only:

- trim column names
- fix dtypes
- parse dates
- preserve source metadata for traceability

### 3. Processed

Build a canonical internal schema such as:

- `producto`
- `producto_key`
- `fecha`
- `region`
- `mercado`
- `canal`
- `unidad_medida`
- `equiv_kg`
- `precio`
- `precio_ayer`
- `precio_promedio_7d`
- `precio_por_kg`
- `ingreso_hoy_t`
- `ingreso_ayer_t`
- `ingreso_7d_t`
- `senal_oferta`
- `variacion_precio_pct`
- `tendencia_precio`
- `recomendacion_base`

### 4. Export

Publish only the fields needed by the public app.

## Recommended uniqueness rule

Use a technical uniqueness key that can survive future source growth:

- `fuente`
- `producto_key`
- `fecha`
- `unidad_medida`
- `mercado`

This is safer than `producto_key + fecha` alone if a future source introduces multiple valid presentations for the same day.

## Publication-safe export

Recommended public export fields:

- `producto`
- `producto_key`
- `fecha`
- `region`
- `mercado`
- `canal`
- `unidad_medida`
- `equiv_kg`
- `precio`
- `precio_ayer`
- `precio_promedio_7d`
- `precio_predicho`
- `precio_por_kg`
- `volumen`
- `clima`
- `demanda`
- `tendencia`

Remove these from the public export unless they are explicitly safe to disclose:

- raw file names
- file hashes
- source-specific ids
- ingestion audit metadata
- internal quality flags

## Export contract for agrointel_ai

The public repo should assume one file is delivered at a stable path such as:

- `data/public/precios_agrointel.csv`

or

- `data/public/precios_agrointel.parquet`

The application should not know how the private pipeline created that file.
