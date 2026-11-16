# AetherRouter

Async LLM API router and gateway that routes requests using model configs you enter and store yourself.

> Work in progress.

---

<img width="1105" height="1004" alt="tikz-export (1)" src="https://github.com/user-attachments/assets/131d28db-4f35-4a7d-8850-9c492061d6e2" />

---

## How it works

1. **Register** a model by entering its config once: endpoint, API key, and context window.
2. **Store** the config in the local config store (`store.py` with a JSON mirror in `store.json`).
3. **Route** a prompt: the router looks up the stored config for the requested model, checks that the provider is up, and calls the stored endpoint.
4. **Broadcast** when no model is given or the provider is down: the prompt's token length is compared against every stored model's context window, and each model is flagged `POTENTIAL` or `RISKY`.

## Request layers

A request moves through these layers: `ENTRY`, `CHECK`, `BROADCAST`, `LOAD`, `UPDATE`, `API`, `RESPONSE`.

Router state (`NOT ROUTING`, `ROUTING`, `ROUTED`) and the current layer are tracked through an `asyncio.Queue` guarded by a lock, so concurrent requests see a consistent status.

## Config store

Each model entry holds the values the router needs to serve it. The supported config keys are `ContextWindow`, `OperationStatus`, `RPM`, and `PREFIX`, plus the endpoint and key. Changes made at runtime are written to the Python store and mirrored to JSON.

## Status

Under active development. Not all layers are finished.
