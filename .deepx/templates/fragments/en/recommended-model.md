## Recommended Model (Pre-Flight Check)

DX Agentic Development requires strong instruction following and knowledge base
utilization. Before starting any task, check if you are running as one of the
recommended models:

- **Claude Sonnet 4.6** or later
- **Claude Opus 4.6** or later

If you are NOT one of these models (e.g., GPT-4.1, GPT-4o, Gemini, etc.),
output the following notice at the beginning of your first response:

```
══════════════════════════════════════════════════════════════
⚠  DX-AGENTIC-DEV: MODEL NOTICE

DX Agentic Development recommends Claude Sonnet 4.6+ or
Opus 4.6+. Your current model may produce lower quality
in instruction following, knowledge base utilization, and
API accuracy. Please switch to a recommended model.
══════════════════════════════════════════════════════════════
```

After the box notice, proceed with the task normally. This is an informational
warning, not a blocking gate.

### Model Notice Repeat (Non-Recommended Model Only)

If you output the MODEL NOTICE box above (i.e., you are NOT a recommended model),
you MUST also output this shortened reminder **immediately before the actual question
line** that the user needs to answer — NOT at the beginning of the brainstorming flow.

**Timing**: After all file reading, context analysis, and preamble text, right before
the line that contains the `?` (the actual question), insert this reminder:

```
---
⚠ **Non-recommended model** — output quality may be degraded. Recommended: Claude Sonnet 4.6+ / Opus 4.6+
---
```

**Example — WRONG** (repeat scrolls past with the box):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
---  ⚠ Non-recommended model ---     ← TOO EARLY, scrolls past
... (reads files, analyzes context) ...
First question: ...?
```

**Example — CORRECT** (repeat appears right before the question):
```
[DX-AGENTIC-DEV: START]
══ MODEL NOTICE ══
... (reads files, analyzes context) ...
---  ⚠ Non-recommended model ---     ← RIGHT BEFORE the question
First question: ...?
```

Only output this reminder ONCE (before the first question), not before every question.
