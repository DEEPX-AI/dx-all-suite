"""브라우저 응답용 모델 payload sanitize."""

import copy
from urllib.parse import urlparse

from dx_modelzoo.metadata.artifacts import INTERNAL_HOSTS


def _is_internal_url(url):
    hostname = (urlparse(str(url)).hostname or "").lower()
    return hostname in INTERNAL_HOSTS


def sanitize_browser_model(model):
    safe = copy.deepcopy(model)
    artifacts = safe.get("artifacts")
    if not isinstance(artifacts, dict):
        return safe

    for artifact in artifacts.values():
        if not isinstance(artifact, dict):
            continue
        url = artifact.get("remote_url")
        if url and _is_internal_url(url):
            artifact.pop("remote_url", None)
            artifact["source_status"] = artifact.get("source_status") or "artifact_unavailable"
    return safe
