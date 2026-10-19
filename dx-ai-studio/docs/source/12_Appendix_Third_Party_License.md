# Third-Party License Notice

DX-AI-Studio is a GUI over the DEEPX SDK. The models and sample data it lets you browse,
download, compile, and run come from third parties and carry **their own licenses** — the
studio does not grant you any rights to them.

## Sample models

Models surfaced in **DX Model Zoo** and used by **DX App** / **DX Compiler** (as `.dxnn`
or ONNX) are supplied as evaluation / development examples. Availability in Studio does
**not** itself grant commercial-deployment rights. They originate from different
projects with different terms (including copyleft and non-commercial licenses);
restrictions and attribution obligations must be checked for the selected model.
Per-model license terms are shown in **DX Model Zoo's detail view** —
check them before any commercial use. For production, obtain a proper license from the
model's authors, or bring your own commercially licensed / proprietary model.  

## Sample data

Sample images and videos are from public academic / open-source datasets (e.g. ImageNet —
non-commercial research only) or AI-generated. They are for **evaluation and demonstration
only**. You are responsible for identifying each sample's source and complying with its
terms, and must not redistribute or use them commercially without the copyright holder's
permission.  

## Bundled software & fonts

The local UI includes fonts and JavaScript assets for offline rendering. External AI
providers, downloads and AWS operations still need their own network access and terms.

**Fonts with accompanying SIL Open Font License 1.1 notices** — paths below are relative
to `shared/static/fonts/`:

| Font | Shipped notice | Copyright named in the notice |
|------|----------------|-------------------------------|
| Inter | `LICENSE-Inter.txt` | The Inter Project Authors |
| Noto Sans SC / TC | `LICENSE-NotoSansSC.txt`, `LICENSE-NotoSansTC.txt` | Adobe; reserved font name “Source” |
| Pretendard / Pretendard JP | `LICENSE-Pretendard.txt`, `LICENSE-PretendardJP.txt` | Kil Hyung-jin |

CJK UI fonts are supplied as subsets. Other bundled font families include JetBrains
Mono, Noto Sans and Noto Sans Mono. Before redistribution, retain the applicable font
notices supplied with your distribution and check the upstream terms for each family.

**JavaScript assets**

| Asset | Component / license information |
|-------|---------------------------------|
| `shared/static/vendor/chart.umd.min.js` | The header identifies **MiniChart**, a lightweight Chart.js-compatible canvas engine, not an upstream Chart.js bundle. |
| `shared/static/vendor/mermaid.min.js` | Mermaid package metadata declares MIT; the bundle also contains dependency-specific notices, including DOMPurify's Apache-2.0 / MPL-2.0 notice. Preserve those notices. |
| `dx_compiler/static/js/dagre.min.js` | The graph-layout bundle contains Chris Pettitt's copyright and MIT permission text, and bundled graphlib / lodash code. |

MiniChart's Chart.js-compatible API does not mean that upstream Chart.js is bundled or
that its license applies to MiniChart. For redistribution, consult your distribution's
notices and obtain any additional component terms from its distributor.

For example, before redistributing a model demo, check its Model Zoo **license / source**
fields and upstream terms, then preserve the relevant software / font notices with
your package. A model license is not a substitute for the bundled UI assets' licenses.

## Disclaimer

DEEPX provides these third-party models and datasets "as-is" for convenience and is not
responsible for issues arising from their unauthorized or commercial use. By using these
samples you assume all liability for license compliance.
