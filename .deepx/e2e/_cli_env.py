# SPDX-License-Identifier: Apache-2.0
"""Shared subprocess-env helper for agent-CLI E2E runners.

All node-based agent CLIs (claude-code, cursor, opencode, copilot — and codex
via the copilot provider) make HTTPS calls through node's TLS stack. In
corporate/proxy environments the proxy's root CA is not in node's bundled CA
store, so the CLIs fail with:

  - claude-code:        "SSL certificate verification failed" /
                        "Unable to connect to API" /
                        "proxy or corporate SSL certificate"
  - cursor / opencode:  "unable to verify the first certificate"

These failures lose whole rounds (the agent never makes an LLM call). Pointing
node at the system CA bundle (which DOES include the corporate root CA) fixes
it. Verified: with NODE_EXTRA_CA_CERTS set, the TLS handshake to api.anthropic.com
succeeds (HTTP 404); without it, "unable to verify the first certificate".
"""
from __future__ import annotations

import os
from typing import Dict, Optional

# System CA bundle that includes the corporate/proxy root CA. Overridable for
# tests and for hosts that keep the bundle elsewhere.
SYSTEM_CA_BUNDLE = os.environ.get(
    "DX_AGENT_E2E_CA_BUNDLE", "/etc/ssl/certs/ca-certificates.crt"
)


def agent_subprocess_env(extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Build the base environment for an agent-CLI subprocess.

    Starts from ``os.environ`` + ``NO_COLOR=1`` and, when the system CA bundle
    exists, injects ``NODE_EXTRA_CA_CERTS`` + appends ``--use-system-ca`` to
    ``NODE_OPTIONS`` so node-based CLIs trust the corporate root CA.

    ``extra`` (e.g. thinking-mode model overrides) is applied last so callers
    can override any key.
    """
    env: Dict[str, str] = {**os.environ, "NO_COLOR": "1"}

    if os.path.isfile(SYSTEM_CA_BUNDLE):
        # Only set if not already pointing somewhere explicit.
        env.setdefault("NODE_EXTRA_CA_CERTS", SYSTEM_CA_BUNDLE)
        node_opts = env.get("NODE_OPTIONS", "") or ""
        if "--use-system-ca" not in node_opts:
            env["NODE_OPTIONS"] = (node_opts + " --use-system-ca").strip()

    if extra:
        env.update(extra)
    return env
