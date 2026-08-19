# LLM provider options

The exploration core works without a hosted model. A provider is an optional planner, not a dependency for tests or the demo spike.

| Provider | Tool calling / structure | Latency/context | Free or low-cost path | Integration | Assessment |
|---|---|---|---|---|---|
| OpenAI Responses API | Official Responses API supports custom function tools and structured outputs; strict schemas are available for supported models. | Current platform docs expose large-context Responses models; exact model/price should be checked at implementation time. | No free tier assumed; do not create an account or add payment during exploration. | Medium; official Python/JS SDKs. | Strongest production-shaped adapter, but not a zero-cost assumption. |
| Google Gemini Developer API | Function calling and structured output are documented; Google AI Studio has a free tier for eligible models. | Good context and multimodal options; free-tier limits vary by model/account. | Official pricing page says free input/output tokens for the free tier, with limited model access. | Medium; official SDK/API. | Best no-payment candidate if the humans want a live prototype and account setup is simple. |
| Groq | OpenAI-compatible tool use with structured tool calls; strict structured outputs are model-limited and the docs state streaming/tool use are not supported with strict structured outputs. | Very low latency; context/model limits vary. | Free tier exists, but paid developer tier requires payment details; do not upgrade. | Low-medium; OpenAI-compatible endpoint. | Good for fast experimentation, but structured-output/tool-use trade-off needs testing. |
| Local/mock | Deterministic provider in this repo; no hosted tool calling required. | Fast and reproducible; context is local. | Free. | Already implemented. | Default for development/evaluation and safe fallback. |

## Recommendation for the next human-controlled phase

Keep mock mode as the acceptance baseline. If a live provider is desired without payment, investigate Gemini's free tier first; if production-shaped schema/tool semantics matter more than cost, implement the OpenAI adapter after explicit budget approval. Do not make either a blocker.

## Sources

[OpenAI developer quickstart](https://platform.openai.com/docs/quickstart/make-your-first-api-request), [OpenAI API reference: tools and structured outputs](https://platform.openai.com/docs/api-reference/evals/deleteRun?lang=python), [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [Groq tool use](https://console.groq.com/docs/tool-use/overview), [Groq structured outputs](https://console.groq.com/docs/structured-outputs), [Groq models/pricing](https://console.groq.com/docs/models).
