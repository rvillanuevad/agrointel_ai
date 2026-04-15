# AgroIntel AI

AgroIntel AI is the public application layer of the project. It consumes a processed agricultural price dataset, analyzes recent trends by product, and uses a local LLM with Ollama to explain whether it is better to sell now or wait.

## Hackathon positioning

AgroIntel AI fits best in `Global Resilience`, with a strong secondary angle in `Digital Equity`.

Small farmers often make sale decisions with delayed or fragmented market information, unstable connectivity, and limited access to decision-support tools. AgroIntel AI turns recent agricultural price data into a simple local recommendation: sell now, wait, or keep monitoring. The key differentiator is that the explanation layer runs locally with Gemma, which keeps the experience available in low-connectivity settings and makes the recommendation easier to trust.

For a Gemma 4 submission, the strongest story is:

- local AI for rural decision-making
- explainable recommendations, not black-box scores
- low-infrastructure deployment through an offline-first workflow
- practical utility for producers, cooperatives, and extension agents

See [docs/hackathon_submission.md](/d:/EMPRESAS/Trabajos-Extra/agrointel_ai/docs/hackathon_submission.md) for a ready-to-adapt Kaggle writeup outline, video script, and asset checklist.

The raw ingestion, cleaning, normalization, and source-specific logic should live in a separate private pipeline. This repo is designed to be safe to publish on Kaggle by shipping only a curated dataset in `data/public/`.

## Public repo scope

- Load a curated public dataset from `data/public/`
- Detect price trends for each product
- Recommend whether to sell now or wait
- Generate natural-language explanations with offline AI
- Run as a Streamlit app or as a CLI tool

## Why this can stand out

- It solves a real economic decision instead of being a generic chatbot.
- It works with local inference, which matters in rural and bandwidth-constrained environments.
- It combines deterministic analysis with natural-language explanation, so the final answer stays grounded.
- It is easy to demo live: choose a crop, show the trend, and compare rule-based versus Gemma-generated guidance.

## Recommended architecture

```text
agrointel_ai/
+-- app_streamlit.py
+-- main.py
+-- data/
�   +-- public/
�   �   +-- precios_agrointel.csv
�   +-- exports/
+-- docs/
�   +-- private_pipeline_blueprint.md
+-- notebooks/
+-- tests/
+-- utils/
�   +-- ai.py
�   +-- analysis.py
�   +-- data_loader.py
+-- requirements.txt
+-- README.md
```

## Private pipeline boundary

Keep these parts out of this repo:

- raw source files
- scraping or source connectors
- cleaning rules tied to proprietary sources
- file hashes and traceability metadata
- normalization logic that reveals the origin workflow

The target private-to-public contract is a processed export such as:

- `precios_agrointel.csv`
- `precios_agrointel.parquet`

See [private_pipeline_blueprint.md](/d:/EMPRESAS/Trabajos-Extra/agrointel_ai/docs/private_pipeline_blueprint.md) for the suggested private project structure and export contract.

## Installation

```bash
python -m venv .venv
pip install -r requirements.txt
```

## Run the Streamlit app

```bash
streamlit run app_streamlit.py
```

## Run the CLI version

```bash
python main.py
```

## Using Gemma 4 with Ollama

This project uses **Gemma 4** via Ollama for local inference. The default model is `gemma4:e4b` (E4B, 9.6 GB).

```bash
# Pull the recommended model (E4B — 9.6 GB)
ollama pull gemma4:e4b

# Or use the lighter edge variant (E2B — 7.2 GB)
ollama pull gemma4:e2b
```

The app automatically detects installed Gemma 4 variants and falls back through a priority chain: `gemma4:e4b` > `gemma4:e2b` > `gemma4` > `gemma4:26b` > `gemma4:31b` > legacy `gemma:2b`.

You can override the model and tune runtime behavior with environment variables:

```bash
set OLLAMA_MODEL=gemma4:e4b
set OLLAMA_TIMEOUT_SECONDS=45
set OLLAMA_COOLDOWN_SECONDS=15
```

`OLLAMA_TIMEOUT_SECONDS` controls how long AgroIntel AI waits for a response before falling back to the rule-based explanation. `OLLAMA_COOLDOWN_SECONDS` controls how long new Ollama calls are skipped after a timeout. Set the cooldown to `0` if you want retries on every request.

The application keeps a deterministic fallback explanation even when the model is unavailable. That is a useful reliability point for the hackathon because it shows graceful degradation instead of a broken user flow.

## Submission-ready architecture summary

1. A private pipeline prepares and sanitizes agricultural price data for publication.
2. This public app loads the safe export from `data/public/`.
3. The analysis layer computes trend, moving average, and a recommendation.
4. Gemma 4 produces a farmer-friendly explanation using the structured context.
5. If the model times out or is unavailable, the app falls back to a grounded rule-based explanation.

This architecture ensures:

- Gemma 4 is used for decision explanation, not as an ungrounded generator.
- The output is anchored to structured agricultural signals.
- The app remains usable under imperfect local runtime conditions.

## Running tests

```bash
python -m pytest tests/ -v
```

Tests validate the dataset contract, trend detection, recommendation logic, model resolution, and the fallback path.
