# Building the DX-AI-Studio User Manual

This manual is built with [MkDocs](https://www.mkdocs.org/) + the Material theme.
The standalone configuration is `dx-ai-studio/docs/mkdocs.yml`, with paths relative
to that directory. Documentation tooling is separate from Studio's standard-library
web runtime; it is not a mandatory product dependency.

## Install the build tools

Use a dedicated virtual environment and a Python version supported by the current
MkDocs/Material/PDF tooling (do not install into system Python). Start at the
`dx-ai-studio/` package root:

```bash
cd /path/to/dx-ai-studio
python3 -m venv .venv-docs
.venv-docs/bin/python -m pip install \
  mkdocs mkdocs-material mkdocs-include-markdown-plugin mkdocs-to-pdf
cd docs
```

These packages provide the theme and configured `include-markdown` / `to-pdf`
plugins; Material supplies the configured PyMdown extensions. The `to-pdf` plugin
must be installed to load the configuration even when PDF output is disabled.
There is no `requirements-docs.txt`. PDF rendering may additionally require
platform-specific WeasyPrint libraries/fonts; follow the renderer's installation
guidance if it reports missing native libraries.

## Build the site

Continue in `dx-ai-studio/docs/` using the tooling environment created above:

```bash
../.venv-docs/bin/mkdocs build --strict     # HTML → ./site/
```

`--strict` treats reported MkDocs warnings as errors; review its output rather than
assuming it validates external services or every link target.

## Live preview

```bash
../.venv-docs/bin/mkdocs serve              # http://127.0.0.1:8000
```

## PDF

PDF export is gated behind an env var so a plain `mkdocs build --strict` verifies the
content without the PDF renderer (whose internal warnings otherwise trip `--strict`).
Build the PDF explicitly:

```bash
ENABLE_PDF_EXPORT=1 ../.venv-docs/bin/mkdocs build
# → ./DEEPX_DX-AI-Studio_UM_v0.1.1_OCT_2026.pdf (in docs/, not site/)
```

The configured `output_path` is `../DEEPX_DX-AI-Studio_UM_v0.1.1_OCT_2026.pdf`,
resolved from `site_dir: site`. Leave `ENABLE_PDF_EXPORT` unset for the HTML-only
strict check.

## Notes

- `docs_dir: source`, `site_dir: site` — generated HTML never touches the developer
  docs (`docs/architecture.md`, `docs/development.md`, `docs/testing.md`).
- Screenshots live under `source/resources/` and are referenced relatively.
- The logo is `source/img/deepx.png` (set in `mkdocs.yml`).
- For suite documentation, edit the same Studio originals. The suite's
  `docs/mkdocs.sh` temporarily copies `dx-ai-studio/docs/source/*.md` and `resources/`
  into `docs/source/ai-studio/` for its build, then removes that copy. Do not edit
  the temporary copy. The suite nav lives in `docs/mkdocs-template.yml` at the suite
  root; Graph Composer stays inside `05_DX_App.md`, not a separate chapter/nav entry.
