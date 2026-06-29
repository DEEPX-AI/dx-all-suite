# SPDX-License-Identifier: Apache-2.0
"""dx_transcripts — shared session-parsing & transcript-rendering library.

Common to (1) the session-sentinel DONE-line transcript generation baked into
every agent's CLAUDE.md/AGENTS.md, and (2) the e2e harness + analyzer. Holds the
per-CLI session parsers, the shared session model, and the transcript renderer.
"""
