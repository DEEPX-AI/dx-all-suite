"""Version-aware, Studio-owned runtime profile discovery and planning.

This module deliberately distinguishes an installed DX Runtime from a source
checkout.  It reads the installed runtime root's ``release.ver`` and probes a
runtime executable; the suite checkout version is never an input to discovery.
Actual installation and activation are handled by the later bootstrap layer.
"""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Mapping, Optional, Tuple, Union

from shared.paths import DX_RUNTIME_ROOT, STUDIO_ROOT


DEFAULT_MANIFEST_PATH = STUDIO_ROOT / "config" / "runtime_profiles.json"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class ProfileState(Enum):
    """Observed state of the installed runtime relative to Studio's target."""

    MISSING = "missing"
    UNSUPPORTED = "unsupported"
    TARGET_DISCOVERED = "target_discovered"
    MIGRATION_REQUIRED = "migration_required"


class ReconciliationState(Enum):
    """Whether Studio may perform a runtime reconciliation transaction."""

    NOOP = "noop"
    RECONCILE = "reconcile"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class ContractCheck:
    """A stable, user-facing observation made while discovering a profile."""

    check_id: str
    required: str
    observed: str
    passed: bool
    remediation: str


@dataclass(frozen=True)
class RuntimeArtifact:
    """An immutable external installation artifact declared by Studio."""

    version: str
    uri: str
    sha256: str

    @property
    def has_valid_digest(self) -> bool:
        return bool(_SHA256_RE.fullmatch(self.sha256.lower()))


@dataclass(frozen=True)
class RuntimeDefinition:
    """Artifacts and compatibility facts for one runtime-version/architecture pair."""

    version: str
    architecture: str
    gstreamer_abi: str
    suite_revision: str
    runtime_revision: str
    runtime: RuntimeArtifact
    driver: RuntimeArtifact


@dataclass(frozen=True)
class RuntimeManifest:
    """Parsed, immutable Studio runtime compatibility matrix."""

    schema_version: int
    studio_version: str
    target_runtime_version: str
    definitions: Mapping[Tuple[str, str], RuntimeDefinition]

    def profile(self, version: str, architecture: str) -> RuntimeDefinition:
        key = (str(version).lstrip("v"), normalize_architecture(architecture))
        try:
            return self.definitions[key]
        except KeyError as exc:
            raise KeyError(
                "No Studio runtime artifact for version {} on {}".format(*key)
            ) from exc


@dataclass(frozen=True)
class RuntimeProfile:
    """Installed runtime observation; it is not an activation record."""

    runtime_version: Optional[str]
    architecture: str
    driver_version: Optional[str]
    runtime_root: Optional[Path]
    state: ProfileState
    observations: Tuple[ContractCheck, ...]


@dataclass(frozen=True)
class ReconciliationPlan:
    """A fail-closed decision for a later bootstrap transaction."""

    state: ReconciliationState
    target: Optional[RuntimeDefinition]
    rollback: Optional[RuntimeDefinition]
    reason: str


def normalize_architecture(value: Optional[str] = None) -> str:
    """Normalize Linux architecture spellings used by Python, dpkg, and manifests."""
    raw = (value or platform.machine() or "unknown").strip().lower()
    aliases = {
        "amd64": "x86_64",
        "x64": "x86_64",
        "x86_64": "x86_64",
        "arm64": "aarch64",
        "aarch64": "aarch64",
    }
    return aliases.get(raw, raw)


def _artifact(raw: Mapping[str, object], kind: str) -> RuntimeArtifact:
    try:
        return RuntimeArtifact(
            version=str(raw.get("version", "")),
            uri=str(raw["uri"]),
            sha256=str(raw.get("sha256", "")),
        )
    except KeyError as exc:
        raise ValueError("{} artifact is missing its URI".format(kind)) from exc


def _coerce_manifest(manifest: Union[RuntimeManifest, Mapping[str, object]]) -> RuntimeManifest:
    if isinstance(manifest, RuntimeManifest):
        return manifest

    try:
        schema_version = int(manifest["schema_version"])
        studio_version = str(manifest["studio_version"])
        target_runtime_version = str(manifest["target_runtime_version"]).lstrip("v")
        profiles = manifest["profiles"]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid runtime profile manifest header") from exc
    if schema_version != 1 or not isinstance(profiles, Mapping):
        raise ValueError("Unsupported runtime profile manifest schema")

    definitions: Dict[Tuple[str, str], RuntimeDefinition] = {}
    for version, raw_profile in profiles.items():
        if not isinstance(raw_profile, Mapping):
            raise ValueError("Invalid profile for runtime {}".format(version))
        gstreamer_abi = str(raw_profile.get("gstreamer_abi", ""))
        architectures = raw_profile.get("architectures")
        if not gstreamer_abi or not isinstance(architectures, Mapping):
            raise ValueError("Runtime {} lacks compatibility data".format(version))
        for architecture, raw_architecture in architectures.items():
            if not isinstance(raw_architecture, Mapping):
                raise ValueError("Invalid architecture profile for {}".format(version))
            normalized_architecture = normalize_architecture(str(architecture))
            definitions[(str(version).lstrip("v"), normalized_architecture)] = RuntimeDefinition(
                version=str(version).lstrip("v"),
                architecture=normalized_architecture,
                gstreamer_abi=gstreamer_abi,
                suite_revision=str(raw_profile.get("suite_revision", "")),
                runtime_revision=str(raw_profile.get("runtime_revision", "")),
                runtime=_artifact(raw_architecture.get("runtime", {}), "runtime"),
                driver=_artifact(raw_architecture.get("driver", {}), "driver"),
            )

    return RuntimeManifest(
        schema_version=schema_version,
        studio_version=studio_version,
        target_runtime_version=target_runtime_version,
        definitions=definitions,
    )


def load_runtime_manifest(path: Path = DEFAULT_MANIFEST_PATH) -> RuntimeManifest:
    """Load the Studio-owned profile matrix from a JSON file."""
    with Path(path).open(encoding="utf-8") as handle:
        return _coerce_manifest(json.load(handle))


def _installed_runtime_root() -> Path:
    """Resolve an explicitly configured installed runtime root at call time."""
    override = os.environ.get("DX_RUNTIME_ROOT")
    return Path(override) if override else DX_RUNTIME_ROOT


def _read_release_version(runtime_root: Path) -> Optional[str]:
    release_file = runtime_root / "release.ver"
    try:
        value = release_file.read_text(encoding="utf-8").strip().lstrip("v")
    except OSError:
        return None
    return value or None


def _discover_driver_version(runtime_root: Path) -> Optional[str]:
    """Best-effort driver discovery without treating source metadata as installed state."""
    override = os.environ.get("DX_DRIVER_VERSION")
    if override:
        return override.strip().lstrip("v") or None

    try:
        result = subprocess.run(
            ["modinfo", "-F", "version", "dxrt_driver"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip().lstrip("v")
    return value or None


def _normalize_package_version(value: str) -> str:
    """Convert a Debian package version to its manifest upstream-version form."""
    upstream = value.strip().lstrip("v").split(":", 1)[-1]
    base, separator, revision = upstream.rpartition("-")
    if (
        separator
        and re.fullmatch(r"\d+(?:\.\d+)+", base)
        and re.fullmatch(r"\d[0-9A-Za-z.+~]*", revision)
    ):
        return base
    return upstream


def _installed_package_versions() -> Tuple[Optional[str], Optional[str]]:
    """Read installed Debian package versions, never a source-checkout version."""
    def query(package: str) -> Optional[str]:
        try:
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Version}", package],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        if result.returncode != 0:
            return None
        value = _normalize_package_version(result.stdout)
        return value or None

    return query("libdxrt-bin") or query("libdxrt"), query("dxrt-driver-dkms")


def _definition_for_package_pair(
    manifest: RuntimeManifest,
    architecture: str,
    runtime_package_version: Optional[str],
    driver_package_version: Optional[str],
) -> Optional[RuntimeDefinition]:
    if not runtime_package_version or not driver_package_version:
        return None
    runtime_package_version = _normalize_package_version(runtime_package_version)
    driver_package_version = _normalize_package_version(driver_package_version)
    matches = [
        definition
        for definition in manifest.definitions.values()
        if definition.architecture == architecture
        and definition.runtime.version == runtime_package_version
        and definition.driver.version == driver_package_version
    ]
    return matches[0] if len(matches) == 1 else None


def _runtime_executable() -> Optional[str]:
    override = os.environ.get("DX_RUNTIME_EXECUTABLE")
    if override:
        return override if Path(override).is_file() else None
    for executable in ("dxcli", "dxrun"):
        resolved = shutil.which(executable)
        if resolved:
            return resolved
    return None


def discover_runtime_profile(
    manifest: Union[RuntimeManifest, Mapping[str, object]],
) -> RuntimeProfile:
    """Discover an installed runtime without consulting the suite checkout version.

    Debian packages install binaries and package metadata, not a suite-level
    ``release.ver``.  The default discovery path therefore maps the installed
    ``libdxrt``/``dxrt-driver-dkms`` pair to Studio's declared compatibility
    matrix.  A caller that explicitly supplies ``DX_RUNTIME_ROOT`` may use a
    bundle-provided release file instead.
    """
    matrix = _coerce_manifest(manifest)
    runtime_root = _installed_runtime_root()
    architecture = normalize_architecture()
    explicit_runtime_root = bool(os.environ.get("DX_RUNTIME_ROOT"))
    package_runtime_version, package_driver_version = _installed_package_versions()
    package_runtime_version = (
        _normalize_package_version(package_runtime_version)
        if package_runtime_version
        else None
    )
    package_driver_version = (
        _normalize_package_version(package_driver_version)
        if package_driver_version
        else None
    )
    package_definition = _definition_for_package_pair(
        matrix,
        architecture,
        package_runtime_version,
        package_driver_version,
    )
    runtime_version = (
        _read_release_version(runtime_root)
        if explicit_runtime_root
        else (package_definition.version if package_definition else None)
    )
    executable = _runtime_executable()
    if explicit_runtime_root:
        observations = [
            ContractCheck(
                check_id="runtime.release_version",
                required="installed runtime release.ver",
                observed=runtime_version or "missing",
                passed=runtime_version is not None,
                remediation="Install a Studio-declared DX Runtime profile.",
            )
        ]
    else:
        observations = [
            ContractCheck(
                check_id="runtime.package_pair",
                required="Studio-declared libdxrt and dxrt-driver-dkms package pair",
                observed="libdxrt={} dxrt-driver-dkms={}".format(
                    package_runtime_version or "missing",
                    package_driver_version or "missing",
                ),
                passed=package_definition is not None,
                remediation="Install a verified Studio runtime profile package pair.",
            )
        ]
    observations.append(
        ContractCheck(
            check_id="runtime.executable",
            required="dxcli or dxrun on PATH",
            observed=executable or "missing",
            passed=executable is not None,
            remediation="Install the declared runtime artifact and refresh PATH.",
        )
    )
    driver_version = package_driver_version or _discover_driver_version(runtime_root)

    if runtime_version is None:
        # Manifest doesn't curate this version, but a runtime may still be physically installed.
        # DX runtimes ship per-version as coherent bundles that Studio must run on regardless of
        # manifest membership, so report the detected version (release.ver, else the installed
        # package version) when a runtime executable is present — reconcile() then accepts it if
        # the App/Stream launch contracts validate.
        detected = _read_release_version(runtime_root) or package_runtime_version
        if detected and executable is not None:
            runtime_version = detected

    if runtime_version is None:
        state = ProfileState.UNSUPPORTED if package_runtime_version else ProfileState.MISSING
        resolved_root: Optional[Path] = None
    elif (runtime_version, architecture) not in matrix.definitions:
        state = ProfileState.UNSUPPORTED
        resolved_root = runtime_root
    elif runtime_version == matrix.target_runtime_version:
        state = ProfileState.TARGET_DISCOVERED
        resolved_root = runtime_root
    else:
        state = ProfileState.MIGRATION_REQUIRED
        resolved_root = runtime_root

    return RuntimeProfile(
        runtime_version=runtime_version,
        architecture=architecture,
        driver_version=driver_version,
        runtime_root=resolved_root,
        state=state,
        observations=tuple(observations),
    )


def _unsigned_reason(definition: RuntimeDefinition) -> Optional[str]:
    for kind, artifact in (("runtime", definition.runtime), ("driver", definition.driver)):
        if not artifact.has_valid_digest:
            return "Artifact digest missing or invalid for {} {}".format(
                definition.version, kind
            )
    return None


def plan_reconciliation(
    profile: RuntimeProfile,
    manifest: Union[RuntimeManifest, Mapping[str, object]],
) -> ReconciliationPlan:
    """Create a fail-closed upgrade/install plan; never execute an installer here."""
    matrix = _coerce_manifest(manifest)
    try:
        target = matrix.profile(matrix.target_runtime_version, profile.architecture)
    except KeyError as exc:
        return ReconciliationPlan(ReconciliationState.BLOCKED, None, None, str(exc))

    reason = _unsigned_reason(target)
    if reason:
        return ReconciliationPlan(ReconciliationState.BLOCKED, target, None, reason)

    if profile.runtime_version == matrix.target_runtime_version:
        return ReconciliationPlan(
            ReconciliationState.NOOP,
            target,
            target,
            "Installed runtime already matches Studio target {}.".format(target.version),
        )

    rollback = None
    if profile.runtime_version is not None:
        try:
            rollback = matrix.profile(profile.runtime_version, profile.architecture)
        except KeyError as exc:
            return ReconciliationPlan(
                ReconciliationState.BLOCKED,
                target,
                None,
                "No verified rollback profile: {}".format(exc),
            )
        reason = _unsigned_reason(rollback)
        if reason:
            return ReconciliationPlan(ReconciliationState.BLOCKED, target, rollback, reason)

    return ReconciliationPlan(
        ReconciliationState.RECONCILE,
        target,
        rollback,
        "Install Studio target runtime {} as a candidate before activation.".format(target.version),
    )