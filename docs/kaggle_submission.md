# Kaggle Hackathon Submission — AgroIntel AI

> Copy each section below into the corresponding field on the Kaggle submission form.

---

## Title

AgroIntel AI: Offline Gemma 4 Market Guidance for Small Farmers

---

## Subtitle

An explainable, low-connectivity decision assistant that helps agricultural producers decide when to sell using local Gemma 4 inference, structured market signals, and a reliable rule-based fallback.

---

## Card and Thumbnail Image

Use the file: `docs/assets/agrointel_card.png`

Suggested design (1200 × 675 px, 16:9):

- **Background**: a gradient from green (#2E7D32) to gold (#F9A825), evoking agriculture.
- **Top left**: the wheat emoji 🌾 or a simple crop icon.
- **Center text (bold, white)**:
  ```
  AgroIntel AI
  ```
- **Below center (lighter weight, white)**:
  ```
  Offline Gemma 4 Market Guidance for Small Farmers
  ```
- **Bottom strip**: small icons or labels for → Gemma 4 · Ollama · Streamlit · Python
- **Bottom right corner**: "Global Resilience" track badge.

> Generate this with any design tool (Canva, Figma, or a quick Python/Pillow script).

---

## Submission Tracks

**Primary**: `Global Resilience`

**Secondary**: `Digital Equity & Inclusivity`

Justification: AgroIntel AI supports rural producers facing volatile prices and uneven access to advisory tools. The local inference workflow reduces dependency on stable cloud connectivity. The response is simple, actionable, and understandable by non-technical users in bandwidth-constrained environments.

---

## Media Gallery

Upload at least three screenshots in 16:9 ratio:

1. **Product selection screen** — Streamlit interface showing the product dropdown and "Analizar producto" button.
2. **Analysis results** — Price chart, trend, recommendation, and market context metrics (precio actual, precio predicho, region, mercado, clima, demanda).
3. **AI explanation** — The Gemma 4-generated farmer-friendly explanation alongside the immediate rule-based recommendation.
4. *(Optional)* **CLI output** — Terminal showing the `python main.py` workflow with analysis and AI explanation.
5. *(Optional)* **Test results** — Terminal showing `pytest tests/ -v` passing all validations.

> Capture these by running `streamlit run app_streamlit.py`, analyzing "maiz" (rising trend → "Esperar antes de vender") and "papa" (falling trend → "Vender ahora").

---

## Video

**Status: PENDIENTE**

- Length: 3 minutes maximum.
- Use the script in `docs/hackathon_submission.md` (section "Three-minute video script").
- Record with OBS or Loom.
- Show: problem statement → live Streamlit demo (two products) → architecture overview → trust/fallback angle → impact close.
- Warm up the Gemma model before recording: `ollama run gemma4:e4b "test"`.

---

## Content — Project Description

*(Paste everything below this line into the "Project Description" field on Kaggle. Stays under 1,500 words.)*

---

### The Problem

Small agricultural producers in Latin America often decide when to sell their crops with incomplete market visibility. In many rural regions of Peru, internet access is intermittent, professional advisory services are limited, and price volatility directly affects household income. A farmer growing potatoes in Lima or corn in Cusco may have no timely way to know whether prices are rising, falling, or stable — and whether it makes more sense to sell today or wait.

Existing AI-powered tools are typically cloud-dependent, presented in English, designed for large-scale operations, or too abstract for a producer who needs a clear, practical answer.

### The Solution

AgroIntel AI analyzes recent crop price data and produces a simple, actionable recommendation: **sell now**, **wait**, or **monitor the market**. It combines a deterministic analysis layer with a **Gemma 4** natural-language explanation that translates structured signals into plain Spanish guidance for producers and field agents.

The key differentiator is not prediction accuracy alone — it is **accessible, trustworthy decision support** that works without a stable internet connection.

### How Gemma 4 Is Used

Gemma 4 is the explanation engine. It receives structured agricultural context — product name, region, market type, recent price history, predicted price, volume, climate, demand, and a suggested recommendation — and produces a short, farmer-friendly paragraph in Spanish explaining what is happening with the price and what the producer should do.

The model runs **locally via Ollama** using the `gemma4:e4b` variant (9.6 GB). This design keeps the system:

- **Grounded**: The explanation is anchored to deterministic inputs from the analysis layer, not hallucinated.
- **Private**: No farmer data leaves the local machine.
- **Resilient**: The app works without cloud connectivity.
- **Trustworthy**: The producer can see the same data the model sees and verify the reasoning.

The application implements an automatic **model resolution chain** that detects installed Gemma 4 variants and falls back through: `gemma4:e4b` → `gemma4:e2b` → `gemma4` → `gemma4:26b` → `gemma4:31b` → legacy `gemma:2b`. If no model is available or the response times out, a **deterministic rule-based fallback** generates the recommendation, guaranteeing the user always gets an answer.

### Technical Architecture

```
Private Pipeline (not published)
  └─ Raw data → Cleaning → Normalization → Export

Public App (this repository)
  └─ data/public/precios_agrointel.csv
      ↓
  └─ utils/data_loader.py → Load & prepare dataset
      ↓
  └─ utils/analysis.py → Trend detection, moving average, recommendation
      ↓
  └─ utils/ai.py → Gemma 4 explanation (or rule-based fallback)
      ↓
  └─ app_streamlit.py (web) / main.py (CLI)
```

**Key components:**

| Layer | Role |
|---|---|
| **Data boundary** | A private pipeline sanitizes raw agricultural data into a publication-safe CSV. Only the curated export is shipped in this repo. |
| **Analysis engine** | Detects price trend (increasing / decreasing / stable), computes a short moving average, and generates a base recommendation using predicted vs. actual price. |
| **Gemma 4 explanation** | Converts structured context into a 3–4 sentence farmer-friendly explanation in Spanish. Uses prompt engineering to keep the output practical and grounded. |
| **Fallback path** | A deterministic rule-based function produces the same recommendation structure without any model dependency. Activated automatically on timeout or model unavailability. |
| **Cooldown mechanism** | After an Ollama timeout, new model calls are skipped for a configurable period to avoid repeated delays. |
| **Response cache** | Identical prompts return cached results instantly. |
| **Automated tests** | Validate dataset contract, trend detection, recommendation logic, model resolution, and fallback path (`pytest tests/ -v`). |

**Stack**: Python 3.11+, Streamlit, Pandas, Ollama, httpx, pytest.

### The Dataset

The public dataset (`data/public/precios_agrointel.csv`) contains daily agricultural prices for four products across Peruvian regions:

| Product | Region | Market | Trend |
|---|---|---|---|
| Papa (potato) | Lima | Mayorista | Falling — sell now |
| Maíz (corn) | Cusco | Local | Rising — wait |
| Arroz (rice) | Lambayeque | Regional | Falling — sell now |
| Cebolla (onion) | Arequipa | Mayorista | Rising — wait |

Each record includes: price, predicted price, volume, climate, demand, and a market-reported trend signal. This provides the structured context that grounds every Gemma 4 explanation.

### Demo Evidence

Running the Streamlit app with **maíz** (Cusco) shows:
- Prices rising from S/ 1.20 to S/ 1.35 over four days.
- Predicted price: S/ 1.40.
- Demand: alta. Climate: soleado. Trend signal: subiendo.
- Recommendation: **"Esperar antes de vender"** (wait before selling).
- Gemma 4 explains why waiting makes sense given rising demand and favorable conditions.

Running with **papa** (Lima) shows:
- Prices falling from S/ 0.80 to S/ 0.68.
- Predicted price: S/ 0.65.
- Demand: alta. Climate: lluvia. Trend signal: bajando.
- Recommendation: **"Vender ahora"** (sell now).
- Gemma 4 explains the urgency given the downward trajectory.

The fallback path produces equivalent recommendations when the model is unavailable, proving the system never leaves the user without guidance.

### Why This Matters

The value of AgroIntel AI is not a dashboard or a chatbot. It is **closing the gap between raw agricultural data and a practical decision** in contexts where:

- Cloud AI cannot be assumed.
- Expert advisory support is scarce.
- The user needs an answer they can understand and trust in minutes.

By running Gemma 4 locally, the system brings AI-powered decision support to the farmers and cooperatives who need it most — without requiring connectivity, English fluency, or technical expertise.

### Track Fit: Global Resilience

AgroIntel AI directly addresses economic resilience for rural producers. Price timing is one of the highest-leverage decisions a small farmer makes. Getting it wrong means lower income, wasted harvest, or missed market windows. This tool makes that decision more informed, more accessible, and more reliable — even in infrastructure-limited settings.

The secondary framing under **Digital Equity & Inclusivity** reinforces that the same offline-first, explainable, Spanish-language design serves communities historically excluded from AI-powered tools.

### Next Steps

- **Multilingual output**: Serve responses in Quechua, Aymara, or regional Spanish variants.
- **Multimodal input**: Let farmers photograph their crop or describe conditions by voice.
- **Cooperative dashboards**: Aggregate recommendations and alerts for producer associations.
- **Retrieval-augmented explanations**: Ground advice with local agronomic bulletins and market reports.
- **Impact evaluation**: Structured feedback from producers and extension agents.

---

## Project Links

**Status: PENDIENTE**

Fill in when available:

- **Repository**: `https://github.com/<user>/agrointel_ai` *(or Kaggle notebook link)*
- **Live demo**: *(if deployed on Streamlit Cloud or Hugging Face Spaces)*
- **Video**: *(YouTube or Loom link once recorded)*

---

## Pre-Submission Checklist

- [x] Title filled
- [x] Subtitle filled
- [ ] Card/thumbnail image created and uploaded
- [x] Submission tracks selected (Global Resilience + Digital Equity)
- [ ] Media gallery screenshots captured and uploaded
- [ ] Video recorded and linked
- [x] Project description written (under 1,500 words)
- [ ] Project links added
- [ ] Repository is public and README is clear
- [ ] Tests pass: `python -m pytest tests/ -v`
