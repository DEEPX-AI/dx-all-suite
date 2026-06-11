---
name: dx-swe-verify
description: 'Verify before claiming completion. Iron Law: no claims without fresh evidence.'
---

<!-- AUTO-GENERATED from .deepx/ — DO NOT EDIT DIRECTLY -->
<!-- Source: .deepx/skills/dx-swe-verify/SKILL.md -->
<!-- Run: dx-agent-gen generate -->

# Skill: Verify Before Completion

> **RIGID skill** — follow this process exactly. No shortcuts, no exceptions.

## Overview

Never claim any task is complete without running verification commands
and confirming their output. Evidence before assertions, always.

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this response, you cannot
claim it passes.

## The Gate Function

```
BEFORE claiming any build is complete:

1. IDENTIFY: What commands prove this claim?
2. RUN: Execute ALL verification commands (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. ONLY THEN: Make the claim
```

## Red Flags — STOP

- Using "should pass", "probably works", "looks correct"
- Expressing satisfaction before running checks ("Done!", "Complete!")
- Claiming completion without showing command output
- Trusting that the template "just works"

## Completion Report Template

Only after ALL checks pass, present:

```
Build Complete ✓
================
Scope:    <component or feature name>
Changes:  <summary of what changed>

Verification:
  ✓ <check 1>: PASS
  ✓ <check 2>: PASS
  ...

Next Steps:
  <relevant follow-up commands>
```

## Key Principle

**Evidence before claims.** Run the command. Read the output. THEN report
the result. Claiming completion without verification is dishonesty, not
efficiency.
