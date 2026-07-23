# DX Agent Dev

A natural-language console for building DEEPX NPU apps: describe what you want, and a
coding agent generates and runs it. Also a chat assistant and a gallery of ready-made
showcases.

## Using it

1. **Connect an agent** — the console detects installed coding CLIs (e.g. Claude,
   OpenCode). A badge shows whether each is signed in; if a login is needed it shows the
   exact command to run, then re-checks.
2. **Describe your task** in the prompt — the agent works and streams its progress live.
3. **Chat** — ask questions in the assistant; besides the coding agents you can point it
   at a **local LLM** (Ollama / vLLM / LM Studio, OpenAI-compatible) or use a signed-in
   coding CLI as the chat backend.
4. **Showcases** — browse the gallery of example NPU apps for reference.

## Key features

- **Bring-your-own agent** — uses whatever coding CLI you have installed + signed in;
  one login powers both the generator and the chat.
- **Local / self-hosted LLM** support (any OpenAI-compatible endpoint; auto-discovers
  models). No API key stored — it is just an HTTP client.
- **SDK knowledge** — the assistant can pull in DEEPX SDK documentation to answer
  accurately, with a refresh button to update it.
- **Live streaming** of the agent's work, with a wall-clock timeout so a stuck run frees
  the slot for the next request.
- **6-language UI** (English / 한국어 / 日本語 / 简体中文 / 繁體中文 / Español).
