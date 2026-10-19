## Inventory Counts — Never Written Here

How many models, examples, elements or plugins a sub-project has is **not stated
in this file**, and must not be added to it. Those numbers live in the sub-project
and change with it; a copy committed here is a snapshot of whatever that repo
happened to be at the time, and it silently goes stale (the previous copy claimed
13 dx_stream elements when the tree had 16, and 353 dx_app models when the
registry had 498).

Read the owning file instead — each of these is one command:

| Question | Where it is defined | How to count (paths are from the suite root — drop the `dx-runtime/` prefix inside a dx-runtime checkout) |
|---|---|---|
| dx_app — models | `dx-runtime/dx_app/config/model_registry.json` | `jq 'length' dx-runtime/dx_app/config/model_registry.json` (registry rows) · `jq -r '.[].dxnn_file' dx-runtime/dx_app/config/model_registry.json \| sort -u \| wc -l` (published models — rows can share a `.dxnn`, and that is one model) |
| dx_app — AI tasks | `dx-runtime/dx_app/src/python_example/` | `ls -d dx-runtime/dx_app/src/python_example/*/ \| grep -v '/common/$' \| wc -l` |
| dx_app — examples in one task | `dx-runtime/dx_app/src/python_example/<task>/<family>/<variant>/` | `find dx-runtime/dx_app/src/python_example/<task> -mindepth 2 -maxdepth 2 -type d \| wc -l` |
| dx_app — models per task | same registry | `jq -r '.[].add_model_task' dx-runtime/dx_app/config/model_registry.json \| sort \| uniq -c` |
| dx_stream — models | `dx-runtime/dx_stream/model_list.json` | `jq '.models \| length' dx-runtime/dx_stream/model_list.json` |
| dx_stream — elements / plugins | `dx-runtime/dx_stream/gst-dxstream-plugin/src/` | `ls dx-runtime/dx_stream/gst-dxstream-plugin/src/gst-dx*.cpp \| wc -l` |
| dx_stream — pipeline examples | `dx-runtime/dx_stream/dx_stream/pipelines/` | `ls -d dx-runtime/dx_stream/dx_stream/pipelines/*/ \| wc -l` |
| dx-modelzoo — models | `dx-modelzoo/src/dx_modelzoo/models/<domain>/<task>/<family>/<Model>.yaml` | `find dx-modelzoo/src/dx_modelzoo/models -name '*.yaml' ! -name template.yaml \| wc -l` (add `-not -path '*/staging/*'` to exclude staging) |

A sub-project's own KB may state its own counts — it owns them and sits next to
the file that defines them. This level does not.
