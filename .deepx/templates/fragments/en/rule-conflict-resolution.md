## Rule Conflict Resolution (HARD GATE)

When a user's request conflicts with a HARD GATE rule, the agent MUST:

1. **Acknowledge the user's intent** — Show that you understand what they want.
2. **Explain the conflict** — Cite the specific rule and why it exists.
3. **Propose the correct alternative** — Show how to achieve the user's goal
   within the framework. For example, if the user asks for direct
   `InferenceEngine.run()` usage, explain that the IFactory pattern wraps
   the same API and propose the factory-based equivalent.
4. **Proceed with the correct approach** — Do NOT silently comply with the
   rule-violating request. Do NOT present it as "Option A vs Option B".

**Common conflict patterns** (from real sessions):
- User says "use `InferenceEngine.Run()`" → Must use IFactory pattern (engine
  calls go inside `run_inference()` method)
- User says "clone demo.py and swap onnxruntime" → Must use skeleton-first
  from `src/python_example/`, not clone user scripts
- User says "create demo_dxnn_sync.py" → Must use `<model>_sync.py` naming
  with SyncRunner, not a standalone script
- User says "use `run_async()` directly" → Must use AsyncRunner, not manual
  async loops

**This rule does NOT override explicit user overrides**: If the user, after being
informed of the conflict, explicitly says "I understand the rule, proceed with
direct API usage anyway", then comply. But the agent MUST explain the conflict
FIRST — silent compliance is always a violation.
