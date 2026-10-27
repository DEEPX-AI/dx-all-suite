# Kubernetes Quickstart

> Kubernetes가 처음이라면 [Kubernetes 입문 가이드](07_Kubernetes_Beginner_Guide_kor.md)를 먼저 보세요. 교실 비유와 직접 해보는 예제로 각 구성 요소를 설명합니다.

DEEPX DX-M1 NPU를 Kubernetes native 리소스로 사용합니다. Pod spec에
`deepx.ai/dx-m1: 1`을 선언하면 scheduler가 NPU 노드에 Pod를 배치하고, device
node와 runtime library가 자동으로 주입됩니다.

## Architecture

```
host (NPU 노드별)             k3s cluster
─────────────────────        ─────────────────────────────────────────
dx-runtime/install.sh   ──►  driver (dxrt-driver-dkms) + firmware + dxrtd
containerd CDI 활성화        (enable_cdi=true, cdi_spec_dirs에 /etc/cdi 포함)

Helm: dx-npu ──► NodeFeatureRule (PCI 1ff4 → deepx.ai/dx-m1.present)
              └► device-plugin DaemonSet → deepx.ai/dx-m1 리소스 광고
                   ├─ /etc/cdi/deepx.json 생성 (device node + libs + dxcli)
                   ├─ NFD feature file 생성 → fw/driver 버전 노드 라벨
                   └─ deepx_npu_* Prometheus metrics 제공 (:9400)
Pod가 deepx.ai/dx-m1: 1 요청 → containerd가 /dev/dxrtN + runtime libs 주입
```

구성 요소 (검증된 NVIDIA 스택 구성을 동일하게 적용):

| 구성 요소 | 역할 |
|---|---|
| [dx-k8s-device-plugin](https://github.com/DEEPX-AI/dx-k8s-device-plugin) | `deepx.ai/dx-m1` 리소스 등록, health check, Pod 할당 |
| CDI spec (plugin이 생성) | `/dev/dxrtN`, runtime libs, `dxcli`를 container에 주입 |
| NFD 연동 | 노드 라벨: 장착 여부, count, product, firmware/driver 버전 |
| `dx-npu` Helm chart | 위 구성 요소 전체의 원커맨드 설치/업그레이드 |

## 사전 준비

0. **클러스터 도구.** Kubernetes 클러스터와 `kubectl`, `helm`이 이미 있다면 건너뛰세요.

    ```bash
    # k3s — 바이너리 하나로 된 Kubernetes. kubectl도 함께 설치됨
    curl -sfL https://get.k3s.io | sh -

    # sudo 없이 kubectl 쓰기
    mkdir -p ~/.kube
    sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
    sudo chown "$USER" ~/.kube/config
    # KUBECONFIG가 없으면 k3s의 kubectl은 /etc/rancher/k3s/k3s.yaml(root 전용)을 읽음
    echo 'export KUBECONFIG=~/.kube/config' >> ~/.bashrc
    export KUBECONFIG=~/.kube/config

    # helm
    curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

    # jq — 이 문서의 확인 명령에서만 사용
    sudo apt-get install -y jq

    kubectl get nodes      # STATUS가 Ready
    helm version
    ```

    vanilla Kubernetes라면 kubectl은 [공식 가이드](https://kubernetes.io/docs/tasks/tools/),
    helm은 [helm.sh](https://helm.sh/docs/intro/install/)를 따르세요.

1. **각 NPU 노드** — host driver, firmware, runtime 설치:

    ```bash
    cd dx-runtime && ./install.sh --runtime-only
    dxcli -s   # NPU 목록이 표시되어야 함
    # NPU Pod는 자체 dxrtd를 실행; 같은 카드에 host dxrtd가 있으면 Pod가 멈춤
    sudo systemctl disable --now dxrt.service
    ```

    device plugin은 카드 하나를 Pod 하나에 할당하고, 그 Pod가 자체 `dxrtd`를
    실행합니다. NPU 노드에서는 host `dxrt.service`를 중지해 두세요 — 한 카드에
    `dxrtd` 두 개가 동작하면 Pod 내부 추론이 종료되지 않습니다. 이 경우 해당 노드의
    NPU는 Kubernetes 전용이 되며, 서비스가 꺼진 동안 `dxrtd`가 필요한 host 앱은
    실행되지 않습니다.

    CDI spec이 host의 `libdxrt.so.3`, `libonnxruntime.so.1`을 모든 NPU Pod에
    마운트하므로, 노드의 DX-RT와 Pod image의 DX-RT는 같은 build여야 합니다(host와
    image에서 각각 `dxcli --version`으로 확인). 다르면 `undefined symbol` 오류로
    실패합니다.

2. **containerd CDI 활성화.** containerd 2.x는 CDI가 기본으로 켜져 있어서(`enable_cdi =
   true`, spec dir `/etc/cdi`, `/var/run/cdi`) 할 일이 없습니다. 버전만 확인하세요:

    ```bash
    sudo k3s ctr version | grep -m1 Version    # v2.x → 완료
    ```

    containerd 1.7만 CDI를 켜야 합니다. k3s에서 CDI 몇 줄만 넣은 `config.toml.tmpl`을
    **새로 만들면 안 됩니다** — k3s는 template을 자기가 생성한 설정 *대신* 쓰기 때문에
    나머지 containerd 설정이 전부 사라집니다. 생성된 파일을 복사한 뒤 덧붙이세요:

    ```bash
    cd /var/lib/rancher/k3s/agent/etc/containerd
    sudo cp config.toml config.toml.tmpl
    sudo tee -a config.toml.tmpl <<'EOF'
    [plugins."io.containerd.grpc.v1.cri".cdi]
      enable_cdi = true
      cdi_spec_dirs = ["/etc/cdi", "/var/run/cdi"]
    EOF
    sudo systemctl restart k3s
    ```

    어느 쪽이든 아래 smoke test로 확인됩니다. Pod 안에 `/dev/dxrt0`가 보이면 CDI가
    동작하는 것입니다.

## 설치

```bash
helm install dx-npu oci://ghcr.io/deepx-ai/charts/dx-npu \
  -n dx-system --create-namespace --set nfd.enabled=true
```

cluster에 node-feature-discovery가 이미 있다면 기본값(`nfd.enabled=false`)을
유지합니다.

NPU 스케줄링 가능 여부와 라벨 확인:

```bash
kubectl get node -o json | jq '.items[].status.allocatable' | grep deepx.ai/dx-m1
kubectl get node --show-labels | grep -o 'deepx.ai[^,]*'
# deepx.ai/dx-m1.present=true, .count, .product, .fw-version, .driver-version
```

## Workload 실행

Smoke test (thin image — 모든 것이 CDI로 주입됨):

```bash
kubectl apply -f deploy/k8s/samples/test-pod.yaml
kubectl logs -f dx-m1-test
# Pod 내부에서 /dev/dxrt0 및 `dxcli -s` 전체 device status 출력
```

Suite runtime image로 실제 추론 실행. init container가 모델 하나를 emptyDir로
받아오고, `dxrun`이 NPU 시간·latency·FPS를 출력합니다:

```bash
kubectl apply -f deploy/k8s/samples/inference-pod.yaml
kubectl wait --for=jsonpath='{.status.phase}'=Succeeded pod/dx-m1-inference --timeout=300s
kubectl logs dx-m1-inference -c inference
```

어떤 Pod든 리소스 요청만 추가하면 NPU Pod가 됩니다:

```yaml
resources:
  limits:
    deepx.ai/dx-m1: 1
```

## Metrics

device plugin은 `:9400`에서 Prometheus metrics를 제공합니다 (headless Service
`dx-npu-metrics`): `deepx_npu_up`, `deepx_npu_device_healthy`, per-core
`deepx_npu_core_{temperature_celsius,voltage_millivolts,clock_mhz}`.
prometheus-operator가 있다면 `metrics.serviceMonitor.enabled=true`를 설정하세요.

## Troubleshooting

| 증상 | 원인 / 해결 |
|---|---|
| allocatable에 `deepx.ai/dx-m1` 없음 | device plugin Pod 미구동 — `kubectl get pods -n dx-system` 및 노드의 `deepx.ai/dx-m1.present=true` 라벨 확인 |
| `deepx.ai/*` 노드 라벨 없음 | NFD 미설치 — `nfd.enabled=true` 설정 또는 NFD 설치; NFD 없이 쓰려면 수동 라벨: `kubectl label node <n> deepx.ai/dx-m1.present=true` |
| Pod는 스케줄됐지만 `/dev/dxrt*` 없음 | containerd CDI 비활성 — config.toml.tmpl 수정 후 k3s 재시작 |
| host에서 `dxcli`가 device를 못 찾음 | driver/firmware 미설치 — `dx-runtime/install.sh` 재실행, device init 실패 시 cold boot |
| device unhealthy 보고 | sysfs에는 있으나 `dxcli -s`에 없음 — 대부분 host 전원 재인가 필요 |
| 추론 Pod가 `Running`에 머물고 `dxrun`이 종료되지 않음 | 노드에서 host `dxrt.service`가 동작 중 — `sudo systemctl disable --now dxrt.service` (사전 준비 1단계) |
| Pod에서 `dxrun: symbol lookup error: undefined symbol` | 노드 DX-RT와 Pod image DX-RT가 다름 — CDI가 host `libdxrt.so.3`를 마운트하므로 노드와 image에 같은 DX-RT build 설치 |
| pod에서 `dxcli` 실행 시 `GLIBC_2.xx not found` | Pod image의 glibc가 CDI로 주입되는 host DX-RT보다 낮음 — base를 `ubuntu:24.04` 이상으로 (아래 note 참고) |

!!! note "host DX-RT가 요구하는 glibc"
    CDI는 node의 `dxcli`와 `libdxrt.so.3`를 Pod에 마운트하므로, Pod image에는 해당 바이너리가 빌드된 glibc 이상이 있어야 합니다.

    - prebuilt `libdxrt-bin` 패키지: glibc ≥ 2.27
    - node에서 소스 빌드한 DX-RT: node의 glibc를 따름 (예: Ubuntu 24.04 빌드는 `GLIBC_2.38`)

    실제 요구 버전은 node에서 `objdump -T /usr/local/bin/dxcli /usr/local/lib/libdxrt.so.3 | grep -o 'GLIBC_[0-9.]*' | sort -uV | tail -1`로 확인하십시오.

전체 chart values와 상세 내용: `deploy/k8s/README.md`.
