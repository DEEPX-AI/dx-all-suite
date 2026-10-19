## 인벤토리 개수 — 여기에 쓰지 않는다

sub-project 의 모델 수, 예제 수, element/플러그인 수는 **이 파일에 적지 않으며**
추가해서도 안 된다. 그 숫자는 sub-project 안에서 관리되고 그쪽이 바뀌면 함께 바뀐다.
여기에 커밋된 사본은 "그 repo 가 그때 어떤 상태였는지"의 스냅샷일 뿐이라 조용히 낡는다
(직전 사본은 dx_stream element 를 13개라고 했지만 실제 트리는 16개였고, dx_app 모델을
353개라고 했지만 registry 에는 498행이 있었다).

대신 해당 파일을 직접 읽는다 — 아래는 각각 명령 한 줄이다:

| 무엇 | 정의된 위치 | 세는 법 (경로는 suite 루트 기준 — dx-runtime checkout 안에서는 `dx-runtime/` 접두사를 뺀다) |
|---|---|---|
| dx_app — 모델 | `dx-runtime/dx_app/config/model_registry.json` | `jq 'length' dx-runtime/dx_app/config/model_registry.json` (registry 행) · `jq -r '.[].dxnn_file' dx-runtime/dx_app/config/model_registry.json \| sort -u \| wc -l` (published 모델 — 여러 행이 같은 `.dxnn` 을 공유하면 한 모델) |
| dx_app — AI task | `dx-runtime/dx_app/src/python_example/` | `ls -d dx-runtime/dx_app/src/python_example/*/ \| grep -v '/common/$' \| wc -l` |
| dx_app — 특정 task 의 예제 | `dx-runtime/dx_app/src/python_example/<task>/<family>/<variant>/` | `find dx-runtime/dx_app/src/python_example/<task> -mindepth 2 -maxdepth 2 -type d \| wc -l` |
| dx_app — task별 모델 | 같은 registry | `jq -r '.[].add_model_task' dx-runtime/dx_app/config/model_registry.json \| sort \| uniq -c` |
| dx_stream — 모델 | `dx-runtime/dx_stream/model_list.json` | `jq '.models \| length' dx-runtime/dx_stream/model_list.json` |
| dx_stream — element / 플러그인 | `dx-runtime/dx_stream/gst-dxstream-plugin/src/` | `ls dx-runtime/dx_stream/gst-dxstream-plugin/src/gst-dx*.cpp \| wc -l` |
| dx_stream — 파이프라인 예제 | `dx-runtime/dx_stream/dx_stream/pipelines/` | `ls -d dx-runtime/dx_stream/dx_stream/pipelines/*/ \| wc -l` |
| dx-modelzoo — 모델 | `dx-modelzoo/src/dx_modelzoo/models/<domain>/<task>/<family>/<Model>.yaml` | `find dx-modelzoo/src/dx_modelzoo/models -name '*.yaml' ! -name template.yaml \| wc -l` (staging 제외하려면 `-not -path '*/staging/*'` 추가) |

sub-project 자신의 KB 는 자기 숫자를 적어도 된다 — 그 숫자를 정의하는 파일 바로 옆에
있기 때문이다. 이 레벨은 적지 않는다.
