# SPDX-License-Identifier: Apache-2.0
"""Showcase prompt reproducibility verification harness.

Drives the verbatim dx-agent-dev-showcase prompts through autopilot coding-agent
runners (claude-code, cursor) and scores each run's output against the checked-in
showcase ground truth on three tiers: artifacts, gates, metrics.

See README.md in this directory for usage, the verdict tiers, and how to add a showcase.
"""
