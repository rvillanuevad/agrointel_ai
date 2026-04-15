# AgroIntel AI Hackathon Submission Guide

## Recommended track

Primary track: `Global Resilience`

Secondary framing: `Digital Equity & Inclusivity`

Why this fits:

- The product supports rural producers facing volatile prices and uneven access to advisory tools.
- The local inference workflow reduces dependency on stable cloud connectivity.
- The response is simple, actionable, and can be understood by non-technical users.

## Core story

AgroIntel AI helps small agricultural producers decide when to sell by combining recent market data with local AI explanations. Instead of exposing users to raw tables or abstract forecasts, it turns price history, predicted price, demand, climate, and market context into a recommendation that can be understood quickly. This matters in communities where internet access is inconsistent and expert advisory support is limited.

The strongest narrative is not "we built a chatbot." The stronger narrative is "we built an offline-capable decision assistant for a high-stakes rural workflow."

## What to emphasize about Gemma 4

The writeup and demo show where Gemma 4 adds value:

- Gemma 4 converts structured market signals into plain-language advice via local inference.
- The recommendation is grounded by deterministic inputs from the analysis layer.
- The app degrades safely through a rule-based fallback when the model is slow or unavailable.
- Local execution supports privacy, resilience, and usability in low-connectivity contexts.
- The model resolution chain prioritizes Gemma 4 variants and auto-detects installed models.

If you later add more advanced capabilities, these are the strongest extensions:

- multilingual advisory responses for regional users
- audio or image input for multimodal farmer workflows
- retrieval over agronomic guidance, market bulletins, or extension documents
- function calling for alerting, report generation, or cooperative workflows

## Architecture implemented

1. Data preparation happens in a separate private pipeline.
2. A publication-safe export is loaded from `data/public/precios_agrointel.csv`.
3. The analysis layer computes trend, moving average, and a base recommendation.
4. Gemma 4 (default: `gemma4:e4b` via Ollama) receives structured context and produces a short, user-facing explanation.
5. A fallback rule-based response guarantees reliability when inference is slow.
6. Automated tests validate the dataset contract, analysis, model resolution, and fallback path.

## Kaggle writeup draft structure

Use this structure to stay under the 1,500-word limit.

### Title

AgroIntel AI: Offline Gemma 4 Market Guidance for Small Farmers

### Subtitle

An explainable, low-connectivity decision assistant for agricultural price timing

### Section 1: Problem

Small farmers often decide when to sell with incomplete market visibility. In many regions, internet access is intermittent, advisory services are limited, and price volatility can directly affect household income. Existing AI tools are often cloud-dependent, generic, or hard to trust in practical decision settings.

### Section 2: Solution

AgroIntel AI analyzes recent crop price data and produces a simple recommendation such as sell now, wait, or monitor the market. It combines deterministic analysis with a Gemma 4 explanation layer that transforms structured signals into clear natural language for producers and field agents.

### Section 3: How Gemma 4 is used

Gemma 4 is used locally to explain the recommendation in plain language using product, region, market, recent prices, predicted price, volume, climate, and demand. This design keeps the system grounded while making the output more useful for non-technical users.

### Section 4: Technical architecture

- Public Streamlit app and CLI for easy demonstration
- Private-to-public data boundary for safe publication
- Lightweight analysis engine for trend and recommendation
- Gemma-powered natural language explanation layer
- Rule-based fallback for reliability

### Section 5: Why this matters

The value is not only prediction. The value is accessible decision support. AgroIntel AI reduces the gap between raw agricultural data and practical action in contexts where cloud AI may not be dependable.

### Section 6: Demo evidence

Show one product with rising prices and one with falling prices. Demonstrate that the app surfaces the trend, recommendation, and user-facing explanation in a few seconds. If possible, mention that the fallback path preserves usability under degraded local inference conditions.

### Section 7: Next steps

- multilingual support
- multimodal farmer inputs
- cooperative dashboards and alerts
- retrieval over agronomy and market bulletins

## Three-minute video script

### Minute 0:00 to 0:30

Open with the real problem. Farmers often need to decide when to sell under uncertainty, and internet connectivity cannot be assumed.

### Minute 0:30 to 1:15

Show the app selecting a product and generating the market view. Point out recent prices, predicted price, market context, and the recommendation.

### Minute 1:15 to 2:00

Explain the architecture simply. Structured agricultural data goes into the analysis layer, Gemma 4 turns the result into plain-language guidance, and the system runs locally for resilience.

### Minute 2:00 to 2:40

Show the trust angle. Highlight that the explanation is grounded in visible inputs and that the app has a deterministic fallback when the model is unavailable.

### Minute 2:40 to 3:00

Close on impact. AgroIntel AI makes practical AI assistance more accessible for rural producers, cooperatives, and field educators.

## Live demo checklist

- Show the Streamlit interface first because it communicates faster than the CLI.
- Use two products with visibly different trends.
- Keep one example where the recommendation is "sell now" and another where it is "wait".
- Make sure the local Gemma model is warmed up before recording.
- Keep the explanation short and readable on screen.

## Repository checklist

- README clearly states the problem, track fit, and Gemma role.
- The repo includes setup instructions and demo instructions.
- The public dataset is safe to publish.
- The code path that uses Gemma is easy to inspect.
- The fallback path is visible and defensible.

## Roadmap for next iteration

These extensions would strengthen the project further if time allows:

1. Gemma 4 benchmarking: compare response quality and latency against the rule-based baseline.
2. Retrieval layer: ground explanations with local agronomic bulletins and market reports.
3. Multilingual output: serve responses in Quechua, Aymara or regional Spanish variants.
4. Impact evaluation: structured user feedback from producers or extension agents.