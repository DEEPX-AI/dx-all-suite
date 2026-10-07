# DEEPX Container Images (GHCR)

Prebuilt DEEPX All Suite images, published to GitHub Container Registry by
[`.github/workflows/ghcr-release.yml`](../.github/workflows/ghcr-release.yml).
Pull one instead of building the suite yourself.

All images are based on **Ubuntu 24.04**.

> Commands below target the upstream **DEEPX-AI** organization. The registry path is
> written `deepx-ai` in lowercase because GHCR rejects uppercase repository names
> (`docker pull ghcr.io/DEEPX-AI/…` fails with *repository name must be lowercase*); the
> release workflow lowercases `github.repository_owner` for the same reason. If you work
> from a fork, substitute your own account name, also lowercased.

## Images and tags

| Image | Immutable tags | Moving tags | Platforms |
|---|---|---|---|
| `ghcr.io/deepx-ai/dx-runtime` | `v<ver>-rt`, `v<ver>-rt-app`, `v<ver>-rt-stream`, `v<ver>-rt-app-stream`, `v<ver>` | `rt`, `rt-app`, `rt-stream`, `rt-app-stream`, `latest` | `linux/amd64`, `linux/arm64` |
| `ghcr.io/deepx-ai/dx-compiler` | `v<ver>` | `latest` | `linux/amd64` **only** |
| `ghcr.io/deepx-ai/dx-modelzoo` | `v<mz-ver>` | `latest` | `linux/amd64` **only** |

The three components version independently, so their tags do not match each other:
`dx-modelzoo` carries its own version while `dx-runtime` and `dx-compiler` carry theirs.
`v<ver>` below stands for whichever release you are pulling — the GHCR package page
lists the tags that actually exist.

On `dx-runtime`, the bare `v<ver>` and `latest` tags both point at the **`rt-app-stream`**
(full) variant — but they are not equivalent: `v<ver>` names one release and therefore never
moves, while `latest` is repointed at the newest release every time one is published.

You will also see per-architecture tags in the GHCR tag list (`v<ver>-rt-amd64`,
`v<ver>-rt-app-arm64`, `v<mz-ver>-amd64`, …). These are build intermediates that the release
workflow pushes before merging them into the multi-arch manifests above, and nothing deletes
them afterwards. **They are not supported tags — ignore them** and use the manifest tags from
the table, which resolve to the right architecture on their own.

### Tag policy

- **Immutable** (`v<ver>-rt-app`, `v<ver>`, `v<mz-ver>`, …) — every tag carrying a version
  number is pinned to that release and is never republished. **Use these in production and in
  CI**, so a new release cannot change what your deployment runs.
- **Moving** (`latest`, `rt`, `rt-app`, `rt-stream`, `rt-app-stream`) — repointed to the
  newest release on every release run. Convenient for trying things out; do not pin a
  deployment to them.

## Which `dx-runtime` variant?

`dx-runtime` ships four variants, built as separate stages of
[`Dockerfile.dx-runtime`](./Dockerfile.dx-runtime).

| Variant | Contains | Size | Use when |
|---|---|---|---|
| `rt` | DX-RT runtime core only (`dxrtd`, `dxrt-cli`, `dx_engine`) | 2.41 GB | You are building your own app on top, or you only need the NPU service / CLI. Smallest base. |
| `rt-app` | `rt` + **dx_app** (standalone Python/C++ inference apps) | 5.28 GB | Standalone inference — the usual choice for running models. |
| `rt-stream` | `rt` + **dx_stream** (GStreamer pipeline plugins) | 4.37 GB | GStreamer video-analytics pipelines only, without dx_app. |
| `rt-app-stream` | `rt` + dx_app + dx_stream (**= `latest`**) | 5.63 GB | You want everything, or you are not sure yet. |

Sizes are `docker images` values from a local `linux/amd64` Ubuntu 24.04 build on a
containerd-backed image store. A classic overlay2 Docker reports the smaller unpacked size
instead — `docker image inspect -f '{{.Size}}'` gives 0.71 / 1.49 / 1.22 / 1.58 GB for the
four rows above — so treat these as an upper bound. Either way they do not add up: all four
variants share the `rt` base layers, and `rt-app-stream` is built on top of `rt-app`, so a
host holding all four stores about 7.6 GB rather than the 17.7 GB the column sums to.

## Pull

```bash
# Full runtime, newest release
docker pull ghcr.io/deepx-ai/dx-runtime:rt-app-stream

# Full runtime, pinned to one release (recommended for production and CI)
docker pull ghcr.io/deepx-ai/dx-runtime:v<ver>-rt-app-stream

# Minimal runtime core
docker pull ghcr.io/deepx-ai/dx-runtime:rt

# Compiler — amd64 only
docker pull ghcr.io/deepx-ai/dx-compiler:latest

# ModelZoo
docker pull ghcr.io/deepx-ai/dx-modelzoo:latest
```

`dx-runtime` is a multi-arch manifest, so Docker picks `amd64` or `arm64` automatically.
**`dx-compiler` and `dx-modelzoo` are `linux/amd64` only** — the archive step downloads x86_64
binaries only ([`docker_build.sh`](../docker_build.sh) `arch_check "amd64 x86_64"`), so the
release workflow does not build an arm64 compiler at all. On an arm64 host you must compile
models elsewhere (or under emulation, which is unsupported).

## Run `dx-runtime` (NPU passthrough)

The NPU needs device access plus host IPC. Minimal working command:

```bash
docker run --rm -it \
    --privileged --ipc=host --pid=host \
    -v /dev:/dev \
    --entrypoint bash \
    ghcr.io/deepx-ai/dx-runtime:rt-app-stream
```

Verify the NPU is visible from inside the container in one shot:

```bash
docker run --rm \
    --privileged --ipc=host --pid=host \
    -v /dev:/dev \
    --entrypoint dxrt-cli \
    ghcr.io/deepx-ai/dx-runtime:rt --status
```

Expected output starts with `DXRT v…` and lists `Device 0: M1`, its RT/PCIe driver and FW
versions, and per-NPU clock/temperature. If instead no device is listed, the host NPU driver
is not loaded — see
[FAQ / Troubleshooting](../docs/source/05_FAQ_Troubleshooting_Guide.md).

### The default entrypoint is `dxrtd`

`ENTRYPOINT` is `/usr/local/bin/dxrtd`, the DX-RT service. `docker run <image>` with no
override therefore starts the service in the foreground — that is the intended way to run
it. Use `--entrypoint bash` (as above) when you want a shell instead.

**`dxrtd` must run in exactly one place** — the host *or* one container, not both. If your
host already runs `dxrtd` (`pgrep -a dxrtd`), start the container with `--entrypoint bash`
and let it use the host service through `--ipc=host --pid=host`.

### Full option set

Each option below comes from the `dx-runtime` service in
[`docker-compose.yml`](./docker-compose.yml), with its purpose as commented there. This is not
the complete service definition: it omits `-v /var/run/docker.sock:/var/run/docker.sock`
(compose uses it so one container can drive another's CLI — not needed here, and handing a
container the Docker socket is worth doing deliberately rather than by default) and the
`TIMEZONE_MOUNT` mount, which compose uses to pass through `/etc/timezone` on Debian/Ubuntu
hosts.

| Option | Why |
|---|---|
| `--privileged`, `-v /dev:/dev`, `--device /dev:/dev` | NPU / GPU / USB camera device access |
| `--ipc=host` | NPU IPC |
| `--pid=host` | PID sharing for the DX-RT service |
| `-it` (`tty` + `stdin_open`) | NPU |
| `--network=host` | `network_mode: "host"` |
| `-v /etc/machine-id:/etc/machine-id:ro`<br>`-v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket`<br>`-v /run/dbus:/run/dbus`<br>`-v /var/lib/dbus:/var/lib/dbus` | NPU D-Bus |
| `-v /lib/modules:/lib/modules` | GPU |
| `-v /lib/udev/rules.d:/lib/udev/rules.d` | Auto-detect devices (USB camera) |
| `-e DISPLAY`, `-e XDG_RUNTIME_DIR`, `-v /tmp/.X11-unix:/tmp/.X11-unix`, `-v $HOME/.Xauthority:/root/.Xauthority` | X11 forwarding (GUI demos) |
| `-v /etc/localtime:/etc/localtime:ro` | Host timezone |
| `-v <host dir>:/deepx/workspace` | Your models / data (`DOCKER_VOLUME_PATH`, default `/deepx/workspace`) |
| `-e PYTHONUNBUFFERED=1` | Unbuffered Python output |

As one command:

```bash
docker run --rm -it \
    --privileged --ipc=host --pid=host --network=host \
    --device /dev:/dev \
    -v /dev:/dev \
    -v /lib/modules:/lib/modules \
    -v /lib/udev/rules.d:/lib/udev/rules.d \
    -v /etc/machine-id:/etc/machine-id:ro \
    -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket \
    -v /run/dbus:/run/dbus \
    -v /var/lib/dbus:/var/lib/dbus \
    -v /etc/localtime:/etc/localtime:ro \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$HOME/.Xauthority:/root/.Xauthority" \
    -e DISPLAY="$DISPLAY" \
    -e XDG_RUNTIME_DIR="$XDG_RUNTIME_DIR" \
    -e PYTHONUNBUFFERED=1 \
    -v "$PWD/workspace:/deepx/workspace" \
    --entrypoint bash \
    ghcr.io/deepx-ai/dx-runtime:rt-app-stream
```

Inside the container, `dx_app` lives at `/deepx/dx-runtime/dx_app` (prebuilt binaries under
`bin/`), `dx_stream` at `/deepx/dx-runtime/dx_stream`, and the walkthrough scripts at
`/deepx/getting-started/`.

> **Python needs the venv.** `dx_engine` is installed in `/venv-dxnn`, not in the system
> Python. An interactive shell activates it for you (the image appends
> `source /venv-dxnn/bin/activate` to `/root/.bashrc`), so the `-it --entrypoint bash` command
> above just works. A **non-interactive** command does not read `.bashrc` and will fail even on
> `rt-app-stream`: `bash -c 'python …'` gives `python: command not found` (the `python` name
> comes from the venv), and `bash -c 'python3 …'` reaches `/usr/bin/python3` and gives
> `ModuleNotFoundError: No module named 'dx_engine'`. Activate it explicitly in that case:
> ```bash
> docker run --rm --privileged --ipc=host --pid=host -v /dev:/dev \
>     --entrypoint bash ghcr.io/deepx-ai/dx-runtime:rt-app-stream \
>     -c 'source /venv-dxnn/bin/activate && python -c "import dx_engine; print(dx_engine.__name__)"'
> ```

To fetch assets and run a first example, follow
[Running Your First NPU Model](../docs/source/03_Running_Your_First_NPU_Model.md).

## Run `dx-compiler`

`linux/amd64` only. Its entrypoint is `init-workspace.sh`, which fixes workspace ownership and
then `exec`s the command you pass. Its default `CMD` is `tail -f /dev/null`, so omitting a
command leaves the container idling rather than failing — pass `bash` (as below) when you want
a shell, or your own command to run one-shot.

```bash
docker run --rm -it \
    --privileged --network=host \
    --cap-add=SYS_ADMIN \
    --security-opt apparmor=unconfined \
    -e HOST_UID="$(id -u)" -e HOST_GID="$(id -g)" \
    -v /dev:/dev \
    -v /etc/machine-id:/etc/machine-id:ro \
    -v /var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket \
    -v /run/dbus:/run/dbus \
    -v /var/lib/dbus:/var/lib/dbus \
    -v "/run/user/$(id -u)/bus:/run/user/$(id -u)/bus" \
    -e DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus" \
    -v /etc/localtime:/etc/localtime:ro \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -e DISPLAY="$DISPLAY" \
    -e PYTHONUNBUFFERED=1 \
    -v "$PWD/workspace:/deepx/workspace" \
    ghcr.io/deepx-ai/dx-compiler:latest bash
```

`--privileged`, `--cap-add=SYS_ADMIN`, `--security-opt apparmor=unconfined`, `/dev`, and the
D-Bus mounts are the full set the `dx-compiler` service in
[`docker-compose.yml`](./docker-compose.yml) uses for FUSE (DX-Tron); the X11 mounts are for
the DX-Tron GUI. They are listed explicitly to mirror the compose service — on current Docker
`--privileged` already implies both `SYS_ADMIN` and an unconfined AppArmor profile, so the two
matter only if you drop `--privileged`. If compilation fails with
`[ResourceError]: Insufficient shared memory (shm)`, add `--shm-size=256m` (the same note is
in the compose file).

> **Do not drop `-e HOST_UID` / `-e HOST_GID` — they are required for *pulled* images.**
> `HOST_UID` is a runtime `ENV` baked into the image from a build arg
> (`Dockerfile.dx-compiler` `ENV HOST_UID=${HOST_UID:-1000}`, fed by `docker_build.sh`'s
> `HOST_UID=$(id -u)`), and the entrypoint runs `chown -R "$HOST_UID:$HOST_GID"` over your
> mounted workspace. So a GHCR image carries **the CI runner's uid**, which has nothing to do
> with yours: without these two variables the container silently re-owns your workspace files
> to that uid. `docker-compose.yml` gets away with passing them at *build* time only because
> it builds locally, where the baked uid already equals the host's — a prebuilt image has no
> such guarantee. Setting them to `$(id -u)`/`$(id -g)` keeps your files yours.
>
> If your uid differs from the image's baked uid, the container user still *is* the baked uid,
> so it reaches your workspace through its passwordless `sudo` rather than by direct
> ownership. Building locally (see below) avoids the mismatch entirely.

For compiler usage itself, see
[Setting Up Environment](../docs/source/02_Setting_Up_Environment.md).

## Run `dx-modelzoo`

Same NPU options as `dx-runtime`. Its entrypoint is also `dxrtd`, but the compose file
overrides it to `sleep infinity` so it reuses the `dx-runtime` container's DX-RT service
instead of starting a second one. Do the same when a `dx-runtime` container is already
running `dxrtd`:

```bash
docker run --rm -it \
    --privileged --ipc=host --pid=host --network=host \
    -v /dev:/dev \
    -v "$PWD/workspace:/deepx/workspace" \
    --entrypoint bash \
    ghcr.io/deepx-ai/dx-modelzoo:latest
```

`dx_modelzoo` is pip-installed into `/venv-dxnn`, so `import dx_modelzoo` works out of
the box (activate the venv first in a non-interactive shell). `torch` is the CPU build:
the `[cpu]` extra alone does not prevent the CUDA wheels, so the image installs torch
from the PyTorch CPU index first. For GPU inference install the `gpu` extra in the
running container — `cd /deepx/dx-modelzoo && pip install -e ".[gpu]"` — which pulls the
nvidia runtime wheels on demand instead of baking several GB into every pull.

## Build locally instead

If you cannot pull from GHCR, build the same images from this repository:

```bash
# Full runtime (default variant) -> dx-runtime:ubuntu-24.04
./docker_build.sh --target=dx-runtime --ubuntu_version=24.04

# A specific variant -> dx-runtime:ubuntu-24.04-rt-app
./docker_build.sh --target=dx-runtime --ubuntu_version=24.04 --variant=rt-app

./docker_build.sh --target=dx-compiler --ubuntu_version=24.04
./docker_build.sh --target=dx-modelzoo --ubuntu_version=24.04
```

`--variant` accepts `rt`, `rt-app`, `rt-stream`, `rt-app-stream`. Notes:

- Omitting `--variant` builds the full `rt-app-stream` image with **no** tag suffix
  (`dx-runtime:ubuntu-24.04`). Non-default variants get a `-<variant>` suffix.
- `--variant` is only valid with `--target=dx-runtime`.
- `--variant` cannot be combined with `--nvidia_gpu` (that overlay hardcodes its own image
  tag, which would drop the variant suffix).
- Building several variants in a row? Pass `--skip-archive` after the first build to reuse
  the source tarballs.

`./docker_build.sh --help` lists every option.

## Smoke-test an image

[`smoke_test.sh`](./smoke_test.sh) checks a *local* image (it never pulls) with
import / file-existence / plugin-registration probes. No NPU required.

```bash
docker/smoke_test.sh <image_ref> <component> [variant]
#   component : runtime | compiler | modelzoo
#   variant   : rt | rt-app | rt-stream | rt-app-stream   (runtime only, default rt-app-stream)

docker pull ghcr.io/deepx-ai/dx-runtime:rt-app
docker/smoke_test.sh ghcr.io/deepx-ai/dx-runtime:rt-app runtime rt-app
```

Exit codes: `0` all checks passed, `1` a check failed or the image is not present locally,
`2` usage error.

## Related documentation

- [Setting Up Environment](../docs/source/02_Setting_Up_Environment.md) — local and Docker installation
- [Running Your First NPU Model](../docs/source/03_Running_Your_First_NPU_Model.md)
- [Version Compatibility](../docs/source/04_Version_Compatibility.md) — SDK / driver / firmware matrix
- [FAQ & Troubleshooting](../docs/source/05_FAQ_Troubleshooting_Guide.md) — X11 and environment conflicts
