# Kubernetes 입문 가이드 — DX-M1 NPU로 배우기

Kubernetes를 처음 접하는 분을 위한 문서입니다. 어려운 용어는 **유치원 교실**에 빗대어
먼저 설명하고, 그 다음 실제 명령으로 직접 확인해 봅니다.

설치 절차만 필요하다면 [Kubernetes Quickstart](06_Kubernetes_Quickstart_kor.md)를 보세요.

---

## 1부. 그림으로 이해하기

### 유치원 하나를 떠올려 보세요

```
유치원 (Cluster)
│
├─ 원장 선생님 (Scheduler)      "이 아이는 어느 교실로 보낼까?"
│
├─ 교실 A (Node)                문패: 특별 블록 1개
│    ├─ 반장 (Device Plugin)
│    ├─ 특별 블록 (DX-M1) 🧩
│    └─ 아이 (Pod) 🙋
│
└─ 교실 B (Node)                문패: 특별 블록 없음
     └─ 아이 (Pod) 🙂
```

| 유치원에서는 | Kubernetes에서는 | 하는 일 |
|---|---|---|
| 유치원 전체 | **Cluster** | 컴퓨터 여러 대를 하나처럼 묶은 것 |
| 교실 | **Node** | 컴퓨터 한 대 |
| 아이 | **Pod** | 실행되는 프로그램 하나 (컨테이너를 감싼 상자) |
| 원장 선생님 | **Scheduler** | 아이를 어느 교실에 보낼지 정함 |
| 특별 블록 | **DX-M1 NPU** | AI 추론을 빠르게 하는 카드 |

### 아이가 "특별 블록 주세요!" 하고 손을 들어요

아이가 특별 블록을 갖고 놀고 싶으면 **손을 들어야** 합니다. Pod 설계도(YAML)에 이렇게 씁니다:

```yaml
resources:
  limits:
    deepx.ai/dx-m1: 1     # "특별 블록 1개 주세요!"
```

원장 선생님은 손 든 아이를 **특별 블록이 남아 있는 교실**로만 보냅니다.
블록이 없는 교실(교실 B)로는 절대 보내지 않습니다.

### 그런데 원장 선생님은 블록이 어디 있는지 어떻게 알까요?

혼자서는 모릅니다. 그래서 도와주는 친구들이 있습니다.

**🧑‍🏫 반장 = Device Plugin** (`dx-k8s-device-plugin`)

블록이 있는 교실마다 반장이 한 명씩 있습니다. 반장은 원장 선생님께 계속 보고합니다:
"우리 반에 특별 블록 1개 있어요! 지금 멀쩡해요!"

블록이 고장 나면 반장이 바로 "고장 났어요!" 하고 보고합니다. 그러면 원장 선생님은
그 교실로 아이를 보내지 않습니다. 모든 블록 교실에 반장이 한 명씩 있게 해주는 규칙을
**DaemonSet**이라고 부릅니다.

**🏷️ 문패 = NFD (Node Feature Discovery) Label**

교실 문에 붙은 이름표입니다. "특별 블록 있음 · 1개 · 버전 v2.7.6" 처럼 적혀 있습니다.
아이(또는 부모님)가 "버전 v2.7.6 블록이 있는 교실로만 보내 주세요"라고 고를 수 있습니다.
이걸 **nodeSelector**라고 합니다.

**🚚 배달 도우미 = CDI (Container Device Interface)**

아이가 교실에 들어가면, 도우미가 블록과 **블록 사용 설명서**(드라이버 라이브러리)를
아이 책상 위에 직접 갖다 놓습니다. 아이는 가방에 아무것도 챙겨 올 필요가 없습니다.
그래서 컨테이너 이미지에 DEEPX 런타임을 넣지 않아도 NPU를 쓸 수 있습니다.

**📦 교실 꾸미기 상자 = Helm Chart** (`dx-npu`)

반장, 문패 규칙, 건강 기록장을 하나하나 설치하려면 번거롭습니다. 그래서 전부 한 상자에
담아 두었습니다. 상자를 한 번 열면(`helm install`) 모든 교실이 한꺼번에 준비됩니다.

**🩺 보건 선생님 = Prometheus**, **📊 게시판 = Grafana**

보건 선생님은 30초마다 블록의 체온(온도), 맥박(클럭), 건강 상태를 재서 기록장에 씁니다.
게시판(Grafana)은 그 기록을 그래프로 그려 벽에 붙여 둡니다. 밤새 블록이 아팠다면
아침에 게시판만 보면 바로 알 수 있습니다.

### 한 장으로 정리

```
아이(Pod)가 손을 듦          "deepx.ai/dx-m1: 1 주세요"
        │
        ▼
원장 선생님(Scheduler)       반장이 보고한 목록을 보고 블록 남은 교실 선택
        │                    (문패로 버전도 고를 수 있음)
        ▼
배달 도우미(CDI)             /dev/dxrt0 + 런타임 라이브러리 + dxcli 를 책상에 배달
        │
        ▼
아이가 블록으로 놀기          AI 추론 실행
        │
        ▼
보건 선생님(Prometheus)      온도·상태를 기록 → 게시판(Grafana)에 그래프
```

### 꼭 기억할 약속 3가지

1. **손을 안 들면 블록을 못 받아요.** `deepx.ai/dx-m1`을 요청하지 않은 Pod에는 NPU가 들어가지 않습니다.
2. **블록 하나는 한 아이만.** 카드 한 장은 한 Pod가 독점합니다. 다른 아이는 줄을 서서 기다립니다(`Pending`).
3. **블록은 반장이 있어야 보여요.** Device Plugin이 멈추면 원장 선생님 눈에 블록이 사라집니다.

---

## 2부. 직접 해보기

아래 예제는 DX-M1이 장착된 k3s 노드에서 실제로 실행한 결과입니다.
`dx-npu` chart가 이미 설치되어 있다고 가정합니다. 아직이라면 [Quickstart](06_Kubernetes_Quickstart_kor.md)의
**0단계(k3s·kubectl·helm 설치)** 부터 따라 하세요.

> 출력이 요약되어 보이면 `kubectl logs` 앞에 `rtk proxy`를 붙여 원문을 확인하세요
> (rtk를 쓰는 환경에만 해당).

### 예제 1. 우리 교실에 블록이 있나요?

```bash
kubectl get node -o json | jq '.items[].status.allocatable | with_entries(select(.key|test("deepx")))'
```
```json
{ "deepx.ai/dx-m1": "1" }
```
원장 선생님이 "이 교실엔 특별 블록 1개가 있다"고 알고 있다는 뜻입니다.

문패도 보겠습니다:
```bash
kubectl get node -o json | jq '.items[].metadata.labels | with_entries(select(.key|test("deepx")))'
```
```json
{
  "deepx.ai/dx-m1.count": "1",
  "deepx.ai/dx-m1.driver-version": "v2.5.1",
  "deepx.ai/dx-m1.fw-version": "v2.7.6",
  "deepx.ai/dx-m1.pcie-driver-version": "v2.4.1",
  "deepx.ai/dx-m1.present": "true",
  "deepx.ai/dx-m1.product": "M1"
}
```

### 예제 2. 손 들고 블록 받기

```bash
kubectl apply -f deploy/k8s/samples/test-pod.yaml
kubectl wait --for=jsonpath='{.status.phase}'=Running pod/dx-m1-test --timeout=120s
kubectl logs dx-m1-test
```
```
=== /dev/dxrt* ===
crw-rw-rw- 1 root root 507, 0 ... /dev/dxrt0
=== dxcli -s ===
DXRT v3.4.2
 * Device 0: M1, Accelerator type
 ...
NPU 0: voltage 750 mV, clock 1000 MHz, temperature 43'C
```
이 Pod는 그냥 `ubuntu:24.04` 이미지입니다. DEEPX 소프트웨어를 하나도 안 넣었는데
블록(`/dev/dxrt0`)과 `dxcli`가 들어 있습니다. **배달 도우미(CDI)** 가 갖다 준 것입니다.

```bash
kubectl delete pod dx-m1-test
```

### 예제 3. 손을 안 들면?

같은 Pod에서 `deepx.ai/dx-m1: 1` 줄만 빼고 띄워 봅니다.

```bash
sed '/deepx.ai\/dx-m1: 1/d; /resources:/d; /limits:/d' deploy/k8s/samples/test-pod.yaml \
  | sed 's/name: dx-m1-test/name: dx-m1-norequest/' | kubectl apply -f -
kubectl wait --for=jsonpath='{.status.phase}'=Running pod/dx-m1-norequest --timeout=120s
kubectl logs dx-m1-norequest
```
```
=== /dev/dxrt* ===
no NPU injected
```
**약속 1번**입니다. 손을 안 들었으니 블록을 못 받았습니다.

```bash
kubectl delete pod dx-m1-norequest
```

### 예제 4. 블록보다 많이 달라고 하면?

교실에는 블록이 1개뿐인데 2개를 달라고 해봅니다.

```bash
kubectl run greedy --image=ubuntu:24.04 --restart=Never \
  --overrides='{"spec":{"containers":[{"name":"greedy","image":"ubuntu:24.04","command":["sleep","60"],"resources":{"limits":{"deepx.ai/dx-m1":"2"}}}]}}'
kubectl get pod greedy
kubectl describe pod greedy | tail -3
```
```
NAME     READY   STATUS    RESTARTS   AGE
greedy   0/1     Pending   0          8s

0/1 nodes are available: 1 Insufficient deepx.ai/dx-m1.
```
`Pending` = 줄 서서 기다리는 중. 원장 선생님이 "블록이 모자라요(`Insufficient`)"라고 답했습니다.
**약속 2번**입니다. NPU도 CPU·메모리처럼 개수를 세서 나눠 줍니다.

```bash
kubectl delete pod greedy
```

### 예제 5. 원하는 버전이 있는 교실만 고르기

문패를 보고 교실을 고릅니다. 펌웨어 `v2.7.6`이 있는 노드에서만 실행되게 해봅니다.

```yaml
# fw-pick.yaml
apiVersion: v1
kind: Pod
metadata:
  name: fw-pick
spec:
  restartPolicy: Never
  nodeSelector:
    deepx.ai/dx-m1.fw-version: "v2.7.6"   # 이 문패가 붙은 교실로만
  containers:
    - name: c
      image: ubuntu:24.04
      command: ["sleep", "30"]
      resources:
        limits:
          deepx.ai/dx-m1: 1
```
```bash
kubectl apply -f fw-pick.yaml
kubectl get pod fw-pick          # → ContainerCreating / Running
```
버전을 `"v9.9.9"`처럼 없는 값으로 바꾸면:
```
0/1 nodes are available: 1 node(s) didn't match Pod's node affinity/selector.
```
그런 문패가 붙은 교실이 없어서 `Pending`입니다. 노드가 여러 대이고 펌웨어 버전이 섞여 있을 때,
**특정 버전에서만 검증된 모델**을 안전하게 배치하는 방법입니다.

```bash
kubectl delete pod fw-pick
```

### 예제 6. 블록으로 진짜 놀기 (AI 추론)

```bash
kubectl apply -f deploy/k8s/samples/inference-pod.yaml
kubectl wait --for=jsonpath='{.status.phase}'=Succeeded pod/dx-m1-inference --timeout=300s
kubectl logs dx-m1-inference -c inference | grep -E "NPU Processing|Latency|FPS" | tail -3
```
```
  - NPU Processing Time  : 18.107 ms
  - Latency              : 26.783 ms
  - FPS                  : 34.04
```
이 Pod는 두 단계로 움직입니다.

1. **준비 도우미(initContainer)** 가 모델 파일(YoloV7)을 먼저 받아 옵니다.
2. 아이(메인 컨테이너)가 `dxrtd`를 켜고 `dxrun`으로 추론을 돌려 속도를 알려 줍니다.

> 왜 `dxrtd`를 Pod 안에서 켜나요? DEEPX 런타임은 자기 도우미 프로그램(`dxrtd`)과
> 소켓으로 대화하는데, 그 소켓은 컨테이너 밖으로 나가지 않습니다. 그래서 Pod마다 하나씩
> 켭니다. 블록을 그 Pod가 혼자 쓰므로 서로 부딪히지 않습니다.

> 이미지가 아직 레지스트리에 없다면 먼저 로컬에서 만들어 넣어야 합니다.
> 방법은 `deploy/k8s/samples/inference-pod.yaml` 맨 위 주석에 있습니다.

```bash
kubectl delete pod dx-m1-inference
```

### 예제 7. 반장이 잠깐 자리를 비우면?

```bash
kubectl delete pod -n dx-system -l app.kubernetes.io/component=device-plugin
kubectl get node -o json | jq '.items[].status.allocatable["deepx.ai/dx-m1"]'
```
잠깐 동안 `"0"`이 됩니다. 반장이 없으니 원장 선생님 눈에 블록이 사라진 것입니다(**약속 3번**).
DaemonSet이 몇 초 안에 새 반장을 데려오면 다시 `"1"`로 돌아옵니다.

문패(label)는 그대로 남아 있는 점도 보세요. 문패는 NFD가, 블록 개수 보고는 반장이 맡기 때문에
둘은 서로 따로 움직입니다.

### 예제 8. 보건 선생님 기록 보기

Prometheus가 설치되어 있다면:

```bash
kubectl port-forward -n monitoring svc/kps-kube-prometheus-stack-prometheus 9090:9090
```
브라우저에서 `http://localhost:9090` → 검색창에 입력 → **Execute**:

| 질문 | 입력할 내용 |
|---|---|
| 블록이 건강한가요? (1=건강) | `deepx_npu_device_healthy` |
| 코어별 온도는? | `deepx_npu_core_temperature_celsius` |
| 지금 나눠 줄 수 있는 블록 수는? | `kube_node_status_allocatable{resource="deepx_ai_dx_m1"}` |
| 제일 뜨거운 코어는? | `max(deepx_npu_core_temperature_celsius)` |

**Graph** 탭을 누르면 시간에 따라 어떻게 변했는지 볼 수 있습니다.
게시판(Grafana)용 대시보드는 `deploy/k8s/dashboards/dx-npu.json`에 있습니다.
Grafana의 **Dashboards → New → Import**에 붙여 넣으면 됩니다.

---

## 3부. 자주 막히는 곳

| 이런 일이 생기면 | 유치원으로 말하면 | 확인할 것 |
|---|---|---|
| Pod가 계속 `Pending` | 블록이 다 쓰이고 있거나, 원하는 문패의 교실이 없음 | `kubectl describe pod <이름>` 맨 아래 Events |
| allocatable이 `0` | 반장이 없거나, 블록이 아프다고 보고됨 | `kubectl get pods -n dx-system`, `deepx_npu_device_healthy` |
| Pod 안에 `/dev/dxrt0`가 없음 | 배달 도우미(CDI)가 일을 안 함 | containerd CDI 설정 ([Quickstart](06_Kubernetes_Quickstart_kor.md) 2단계) |
| `ImagePullBackOff` | 아이가 가방(이미지)을 못 찾음 | 이미지 이름, 레지스트리 게시 여부, 로컬 import 여부 |
| `dxrt service is not running` | 블록 도우미(`dxrtd`)를 안 켬 | Pod 명령에서 `dxrtd &`를 먼저 실행 |
| `GLIBC_2.38 not found` | 아이 책상이 너무 낡아 설명서를 못 읽음 | Pod 이미지를 `ubuntu:24.04` 이상으로 |

---

## 용어 사전

| 용어 | 한 줄 설명 |
|---|---|
| **Cluster** | 여러 컴퓨터를 하나처럼 쓰는 묶음 |
| **Node** | 그 안의 컴퓨터 한 대 |
| **Pod** | 실행 단위. 컨테이너 1개 이상을 감싼 상자 |
| **Container** | 프로그램과 필요한 파일을 담은 이동식 가방 |
| **Scheduler** | Pod를 어느 Node에 놓을지 정하는 담당자 |
| **DaemonSet** | "모든 해당 Node에 하나씩" 띄우는 규칙 |
| **Device Plugin** | 특수 하드웨어(NPU)를 Kubernetes에 알려 주는 프로그램 |
| **Extended Resource** | CPU·메모리 외에 새로 추가한 자원. 여기서는 `deepx.ai/dx-m1` |
| **Label / nodeSelector** | Node 문패 / 그 문패로 Node 고르기 |
| **NFD** | Node 하드웨어를 살펴보고 문패를 자동으로 붙이는 도구 |
| **CDI** | 컨테이너에 장치와 파일을 자동으로 넣어 주는 표준 규칙 |
| **initContainer** | 메인 컨테이너보다 먼저 실행되는 준비용 컨테이너 |
| **Helm / Chart** | Kubernetes 설치 상자 / 그 상자 하나 |
| **Prometheus / Grafana** | 숫자 기록장 / 그 기록을 그리는 게시판 |
| **Pending** | 놓을 자리가 없어 기다리는 상태 |
