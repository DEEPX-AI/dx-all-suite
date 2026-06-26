## Skill Router — Universal Pre-Flight (HARD GATE)

`/dx-skill-router` MUST be invoked as the **absolute first action** for
**every user message** — regardless of task type (development, analysis,
reading, explanation, or clarification).

This rule applies before:
- Any file read or codebase exploration
- Any response or clarifying question
- Any SWE gate check or path classification
- Any code generation or plan creation

**No exceptions.** The following rationalizations are ALL prohibited:

| Rationalization | Reality |
|----------------|---------|
| "This is just reading/analyzing files" | Reading IS a task. Invoke router first. |
| "The user only asked a question" | Questions are tasks. Invoke router first. |
| "This is not a development task" | Router applies to ALL tasks, not only dev. |
| "I'll check for skills after I understand the request" | Check BEFORE understanding. |
| "This doesn't trigger SWE gates" | SWE gates are separate. Router is universal. |
