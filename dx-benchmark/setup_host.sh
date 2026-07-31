#!/usr/bin/env bash
# dx-benchmark host provisioning — one-time, requires sudo/root.
# Usage: sudo ./setup_host.sh [username]
#
# Configures:
#   0. System dependencies (time, jq, ffmpeg, curl, tar) via apt
#   1. Passwordless sudo for dxrt.service restart (crash recovery)
#   2. Passwordless sudo for dmesg (kernel log collection on incidents)
#   3. Passwordless sudo for journalctl (dxrt service log collection on incidents)
#   4. Passwordless sudo for lspci -vv (PCIe LnkCap/LnkSta capture — host_health)
#   5. systemd-journal group membership (journal access without sudo)
#   6. video group membership (vcgencmd power/throttle capture — Raspberry Pi only)
#
# Data (models/videos) needs no sudo — use ./setup_data.sh for that.
set -euo pipefail

SUDOERS_FILE="/etc/sudoers.d/benchmark-dxrt"

# ── Determine target user ─────────────────────────────────────────────────
TARGET_USER="${1:-${SUDO_USER:-}}"

if [[ -z "${TARGET_USER}" ]]; then
    echo "ERROR: Cannot determine target user."
    echo "Usage: sudo $0 [username]"
    exit 1
fi

# Verify user exists
if ! id "${TARGET_USER}" &>/dev/null; then
    echo "ERROR: User '${TARGET_USER}' does not exist on this system."
    exit 1
fi

# ── Must run as root ──────────────────────────────────────────────────────
if [[ "$(id -u)" -ne 0 ]]; then
    echo "ERROR: This script must be run with sudo (or as root)."
    echo "Usage: sudo $0 [username]"
    exit 1
fi

echo "[setup] Target user: ${TARGET_USER}"

# ── Ensure benchmark system dependencies ──────────────────────────────────
# CLIs the benchmark & setup_data.sh rely on: GNU time (CPU%/RSS in every
# run_model & gst run), jq (model download), ffmpeg/ffprobe (E2E frame
# counting), curl + tar (data download).
#
# What matters is that the TOOLS are present — NOT that apt succeeds. So we:
#   1. detect which are missing (by the binary the benchmark actually invokes),
#   2. apt-install ONLY the missing ones (skip apt entirely when none missing),
#   3. never abort on an apt error unrelated to our tools — a pre-existing
#      broken dpkg state (e.g. a failing DKMS build) or a deliberately held
#      package (e.g. a vendor MPP ffmpeg) must NOT block the sudoers/group
#      provisioning below.
# A hard failure is raised only if a required binary is still absent afterward.
# >>> bench-deps (self-test extracts this block by these markers) >>>
TIME_BIN="${TIME_BIN:-/usr/bin/time}"   # GNU time path (override if non-standard)
BENCH_TOOL_BINS=("${TIME_BIN}" jq ffprobe curl tar)
declare -A BENCH_BIN_PKG=(
    ["${TIME_BIN}"]=time [jq]=jq [ffprobe]=ffmpeg [curl]=curl [tar]=tar
)
_have() { command -v "$1" >/dev/null 2>&1; }

_missing_pkgs=()
for _bin in "${BENCH_TOOL_BINS[@]}"; do
    _have "${_bin}" || _missing_pkgs+=("${BENCH_BIN_PKG[${_bin}]}")
done

if ((${#_missing_pkgs[@]} == 0)); then
    echo "[setup] All system dependencies already present — skipping apt."
elif command -v apt-get >/dev/null 2>&1; then
    echo "[setup] Installing missing dependencies: ${_missing_pkgs[*]}"
    # '|| true' / '|| echo': an unrelated broken or held dpkg state must not
    # abort this script (set -e). Tools are re-verified by binary just below.
    apt-get update -qq || true
    apt-get install -y "${_missing_pkgs[@]}" || \
        echo "[setup] WARNING: apt reported an error — verifying tools directly (an unrelated broken/held package state does not affect these tools)."
else
    echo "[setup] Non-apt system detected — install these manually (package names may vary):"
    echo "        GNU time, jq, ffmpeg (provides ffprobe), curl, tar"
    echo "        e.g.  dnf install time jq ffmpeg curl tar   |   pacman -S time jq ffmpeg curl tar"
fi

_still_missing=()
for _bin in "${BENCH_TOOL_BINS[@]}"; do
    _have "${_bin}" || _still_missing+=("${_bin}")
done
if ((${#_still_missing[@]})); then
    echo "ERROR: required benchmark tools still missing after setup: ${_still_missing[*]}"
    echo "       Install them manually, then re-run this script."
    exit 1
fi
echo "[setup] System dependencies ready."
# <<< bench-deps <<<

# ── Resolve command paths ─────────────────────────────────────────────────
SYSTEMCTL_BIN="$(command -v systemctl 2>/dev/null || echo /usr/bin/systemctl)"
DMESG_BIN="$(command -v dmesg 2>/dev/null || echo /usr/bin/dmesg)"
JOURNALCTL_BIN="$(command -v journalctl 2>/dev/null || echo /usr/bin/journalctl)"
LSPCI_BIN="$(command -v lspci 2>/dev/null || echo /usr/bin/lspci)"

# ── Install sudoers rules ─────────────────────────────────────────────────
# The lspci rule matches env_fingerprint's exact call: sudo -n lspci -vv -s <bdf>
SUDOERS_CONTENT="# Benchmark automation: passwordless sudo for dxrt crash recovery and incident log collection
${TARGET_USER} ALL=(ALL) NOPASSWD: ${SYSTEMCTL_BIN} restart dxrt.service
${TARGET_USER} ALL=(ALL) NOPASSWD: ${DMESG_BIN} --time-format=iso -T
${TARGET_USER} ALL=(ALL) NOPASSWD: ${JOURNALCTL_BIN} -u dxrt.service *
${TARGET_USER} ALL=(ALL) NOPASSWD: ${LSPCI_BIN} -vv -s *"

# Check if already fully configured (older installs lack the lspci rule → rewrite)
if [[ -f "${SUDOERS_FILE}" ]] && \
   grep -qF "restart dxrt.service" "${SUDOERS_FILE}" && \
   grep -qF "${DMESG_BIN}" "${SUDOERS_FILE}" && \
   grep -qF "${JOURNALCTL_BIN}" "${SUDOERS_FILE}" && \
   grep -qF "${LSPCI_BIN} -vv -s" "${SUDOERS_FILE}"; then
    echo "[setup] Sudoers rules already configured. Skipping."
else
    echo "${SUDOERS_CONTENT}" > "${SUDOERS_FILE}"
    chmod 0440 "${SUDOERS_FILE}"

    # Validate with visudo — rollback on failure
    if visudo -cf "${SUDOERS_FILE}" &>/dev/null; then
        echo "[setup] Sudoers rules installed: ${SUDOERS_FILE}"
        echo "        - systemctl restart dxrt.service"
        echo "        - dmesg (kernel log for incident collection)"
        echo "        - journalctl (service log for incident collection)"
        echo "        - lspci -vv (PCIe LnkCap/LnkSta for host_health)"
    else
        echo "ERROR: Sudoers validation failed. Removing broken file."
        rm -f "${SUDOERS_FILE}"
        exit 1
    fi
fi

# ── Add user to systemd-journal group (journal access without sudo) ───────
if getent group systemd-journal &>/dev/null; then
    if id -nG "${TARGET_USER}" | grep -qw systemd-journal; then
        echo "[setup] User '${TARGET_USER}' already in systemd-journal group."
    else
        usermod -aG systemd-journal "${TARGET_USER}"
        echo "[setup] Added '${TARGET_USER}' to systemd-journal group."
        echo "        (re-login required for group to take effect)"
    fi
else
    echo "[setup] systemd-journal group not found. Skipping group membership."
fi

# ── video group for vcgencmd (Raspberry Pi power/throttle capture) ────────
# host_health reads `vcgencmd get_throttled` / `pmic_read_adc` without sudo;
# on Raspberry Pi OS that requires membership in the 'video' group.
if command -v vcgencmd &>/dev/null; then
    if getent group video &>/dev/null; then
        if id -nG "${TARGET_USER}" | grep -qw video; then
            echo "[setup] User '${TARGET_USER}' already in video group (vcgencmd OK)."
        else
            usermod -aG video "${TARGET_USER}"
            echo "[setup] Added '${TARGET_USER}' to video group for vcgencmd."
            echo "        (re-login required for group to take effect)"
        fi
    else
        echo "[setup] video group not found. Skipping vcgencmd group membership."
    fi
else
    echo "[setup] vcgencmd not present (not a Raspberry Pi). Skipping video group."
fi

# ── Verify passwordless sudo works ────────────────────────────────────────
echo ""
echo "[setup] Verifying passwordless sudo ..."

# Test dmesg
if sudo -n -u "${TARGET_USER}" -- sudo -n "${DMESG_BIN}" --version &>/dev/null 2>&1; then
    echo "  sudo -n dmesg          — OK"
else
    echo "  sudo -n dmesg          — installed (cannot verify as ${TARGET_USER})"
fi

# Test journalctl
if sudo -n -u "${TARGET_USER}" -- sudo -n "${JOURNALCTL_BIN}" --version &>/dev/null 2>&1; then
    echo "  sudo -n journalctl     — OK"
else
    echo "  sudo -n journalctl     — installed (cannot verify as ${TARGET_USER})"
fi

# Test lspci (host_health LnkSta capture)
if sudo -n -u "${TARGET_USER}" -- sudo -n "${LSPCI_BIN}" -vv -s 00:00.0 &>/dev/null 2>&1; then
    echo "  sudo -n lspci -vv -s   — OK"
else
    echo "  sudo -n lspci -vv -s   — installed (cannot verify as ${TARGET_USER})"
fi

# Test vcgencmd (Raspberry Pi only; group takes effect after re-login)
if command -v vcgencmd &>/dev/null; then
    if sudo -n -u "${TARGET_USER}" -- vcgencmd get_throttled &>/dev/null 2>&1; then
        echo "  vcgencmd get_throttled — OK"
    else
        echo "  vcgencmd get_throttled — group added (re-login required to verify)"
    fi
fi

# Test systemctl
echo "  sudo -n systemctl restart dxrt.service — rule installed"

# ── Summary ───────────────────────────────────────────────────────────────
echo ""
echo "=== Setup Complete ==="
echo "  User:  ${TARGET_USER}"
echo "  Rule:  ${SUDOERS_FILE}"
echo "  Group: systemd-journal"
echo ""
echo "  Passwordless sudo enabled for:"
echo "    - systemctl restart dxrt.service  (crash recovery)"
echo "    - dmesg                           (kernel log collection)"
echo "    - journalctl                      (service log collection)"
echo "    - lspci -vv -s                    (PCIe LnkCap/LnkSta capture)"
if command -v vcgencmd &>/dev/null; then
    echo "  Group membership: video (vcgencmd power/throttle capture)"
fi
echo ""
echo "To remove this configuration later:"
echo "  sudo rm ${SUDOERS_FILE}"
