# DX Agent Dev

A natural-language console for building DEEPX NPU apps: describe what you want, and a
coding agent generates and runs it. Also a chat assistant and a gallery of ready-made
showcases.

## Using it

1. **Connect an agent** — the console detects installed coding CLIs (e.g. Claude,
   OpenCode). A badge shows whether each is signed in; if a login is needed it shows the
   exact command to run, then re-checks.
2. **Describe your task** in the prompt — the agent works and streams its progress live.
3. **Stop** — a Stop button shows while the agent runs. The agent writes the app to
   `dx-agent-dev/<session_id>/` inside the project it worked on.
4. **Showcases** — browse the gallery of example NPU apps for reference.

## Key features

- **Bring-your-own agent** — uses whatever coding CLI you have installed + signed in;
  one login powers both the generator and the chat.
- **Studio chat (the button at the bottom right)** — separate from the Agent Console; it can
  answers through your signed-in coding agent by default, or a **local / self-hosted**
  OpenAI- or Ollama-compatible endpoint (models are auto-discovered) or a cloud API key;
  **Refresh knowledge** for the DEEPX SDK documentation is under Settings ▸ Advanced.
- **Live streaming** of the agent's work, with a wall-clock timeout so a stuck run frees
  the slot for the next request.
- **6-language UI** (English / 한국어 / 日本語 / 简体中文 / 繁體中文 / Español).
