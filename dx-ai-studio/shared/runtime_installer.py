"""Studio-owned staging and privileged installation of verified runtime artifacts."""
from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Callable, Optional
from urllib.parse import urlparse

from shared.paths import STUDIO_ROOT
from shared.runtime_profile import RuntimeArtifact, RuntimeDefinition


DEFAULT_ARTIFACT_CACHE_DIR = STUDIO_ROOT / "var" / "runtime" / "artifacts"
ArtifactFetcher = Callable[[str], bytes]
CommandRunner = Callable[[tuple[str, ...]], bool]
ContractValidator = Callable[[RuntimeDefinition], bool]


class ExternalArtifactInstaller:
    """Install only immutable, digest-verified packages staged in Studio storage.

    ``authorized`` is intentionally explicit: callers must collect user consent before
    an external ``sudo -n dpkg -i`` command can run.  The installer never writes to a
    runtime source checkout and does not treat a failed privileged command as success.
    """

    def __init__(
        self,
        *,
        cache_dir: Path = DEFAULT_ARTIFACT_CACHE_DIR,
        fetcher: Optional[ArtifactFetcher] = None,
        command_runner: Optional[CommandRunner] = None,
        validator: Optional[ContractValidator] = None,
        authorized: bool = False,
    ) -> None:
        self.cache_dir = Path(cache_dir)
        self.fetcher = fetcher or self._fetch
        self.command_runner = command_runner or self._run_privileged_command
        self.validator = validator or (lambda _definition: False)
        self.authorized = authorized
        self.last_error = ""
        self._staged: dict[tuple[str, str], tuple[Path, Path]] = {}

    @staticmethod
    def _fetch(uri: str) -> bytes:
        with urllib.request.urlopen(uri, timeout=60) as response:
            return response.read()

    @staticmethod
    def _run_privileged_command(command: tuple[str, ...]) -> bool:
        try:
            result = subprocess.run(command, check=False, timeout=300)
        except (OSError, subprocess.SubprocessError):
            return False
        return result.returncode == 0

    @staticmethod
    def _artifact_filename(artifact: RuntimeArtifact) -> str:
        name = Path(urlparse(artifact.uri).path).name or "artifact.deb"
        return "{}-{}".format(artifact.sha256[:16], name)

    @staticmethod
    def _has_expected_digest(path: Path, expected: str) -> bool:
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            return False
        return digest == expected.lower()

    def _stage(self, artifact: RuntimeArtifact) -> Optional[Path]:
        if not artifact.has_valid_digest:
            self.last_error = "Artifact has no valid SHA-256 digest."
            return None
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        destination = self.cache_dir / self._artifact_filename(artifact)
        if destination.is_file() and self._has_expected_digest(destination, artifact.sha256):
            return destination
        try:
            data = self.fetcher(artifact.uri)
        except Exception as exc:
            self.last_error = "Artifact download failed: {}".format(exc)
            return None
        if not isinstance(data, bytes):
            self.last_error = "Artifact downloader returned non-bytes data."
            return None
        actual = hashlib.sha256(data).hexdigest()
        if actual != artifact.sha256.lower():
            self.last_error = "Artifact digest mismatch for {}.".format(artifact.uri)
            return None

        descriptor, temporary = tempfile.mkstemp(
            prefix=".{}-".format(destination.name),
            suffix=".tmp",
            dir=str(self.cache_dir),
        )
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, destination)
        finally:
            try:
                Path(temporary).unlink()
            except FileNotFoundError:
                pass
        return destination

    @staticmethod
    def _definition_key(definition: RuntimeDefinition) -> tuple[str, str]:
        return definition.version, definition.architecture

    def verify_artifact(self, definition: RuntimeDefinition) -> bool:
        """Stage both package artifacts and check their exact manifest digests."""
        runtime_path = self._stage(definition.runtime)
        driver_path = self._stage(definition.driver)
        if runtime_path is None or driver_path is None:
            self._staged.pop(self._definition_key(definition), None)
            return False
        self._staged[self._definition_key(definition)] = (runtime_path, driver_path)
        self.last_error = ""
        return True

    def staged_paths(self, definition: RuntimeDefinition) -> tuple[Path, Path]:
        """Return runtime and driver package paths only after successful verification."""
        return self._staged.get(self._definition_key(definition), ())

    def install(self, definition: RuntimeDefinition) -> bool:
        """Run the explicitly authorized external package command using staged bytes."""
        if not self.authorized:
            self.last_error = "Privileged installation requires explicit authorization."
            return False
        if not self.verify_artifact(definition):
            return False
        paths = self.staged_paths(definition)
        if len(paths) != 2:
            self.last_error = "Verified runtime artifacts are unavailable."
            return False
        command = ("sudo", "-n", "dpkg", "-i", *(str(path) for path in paths))
        if not self.command_runner(command):
            self.last_error = "Privileged package installation failed."
            return False
        self.last_error = ""
        return True

    def validate(self, definition: RuntimeDefinition) -> bool:
        """Delegate activation proof to the complete App/Stream contract validator."""
        try:
            valid = bool(self.validator(definition))
        except Exception as exc:
            self.last_error = "Runtime contract validation failed: {}".format(exc)
            return False
        if not valid:
            self.last_error = "Runtime contract validation failed for {}.".format(definition.version)
        return valid
