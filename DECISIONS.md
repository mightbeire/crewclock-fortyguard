# Decisions

## 2026-08-19 — Preserve the vendored quickstart

The existing FortyGuard quickstart contains the most valuable local research, client wrapper, notebooks, and sanitized fixtures. It is retained as a vendor/reference layer rather than rewritten.

## 2026-08-19 — Use official docs as the current API authority

The local quickstart and current official docs disagree on a few details, notably date coverage and some unit wording. We record both, prefer current official docs for request construction, and treat cached fixture values as evidence with explicit provenance.

## 2026-08-19 — No live analysis calls during exploration

Authentication was verified with the usage endpoint. Cached responses are sufficient for schema and metric work; repeating identical analysis requests would waste credits and create no new evidence.

## 2026-08-19 — Mock-first agent core

The agent loop is provider-neutral and deterministic by default. A hosted LLM may propose tool calls later, but it cannot bypass the registry, budgets, repeat-call protection, or human approval.

## 2026-08-19 — Do not select the MVP

The exploration run ranks three finalists but intentionally stops before product selection, as required by the brief.
