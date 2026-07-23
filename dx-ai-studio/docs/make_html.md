# Building the DX-AI-Studio User Manual

This manual is built with [MkDocs](https://www.mkdocs.org/) + the Material theme.
Everything is self-contained under `docs/` and uses **relative paths**, so it builds
after a fresh clone on any host.

## Install the build tools

Use a virtual environment (do not install into system Python):

```bash
cd dx-ai-studio/docs
python3 -m venv .venv-docs
source .venv-docs/bin/activate
pip install -r requirements-docs.txt
```

## Build the site

```bash
cd dx-ai-studio/docs
mkdocs build --strict     # writes HTML to ./site/ ; --strict fails on broken links/nav
```

## Live preview

```bash
mkdocs serve              # http://127.0.0.1:8000
```

## PDF

PDF export is gated behind an env var so a plain `mkdocs build --strict` verifies the
content without the PDF renderer (whose internal warnings otherwise trip `--strict`).
Build the PDF explicitly:

```bash
ENABLE_PDF_EXPORT=1 mkdocs build     # → site/DX-AI-Studio-User-Manual.pdf
```

## Notes

- `docs_dir: source`, `site_dir: site` — generated HTML never touches the developer
  docs (`docs/architecture.md`, `docs/development.md`, `docs/testing.md`).
- Screenshots live under `source/resources/` and are referenced relatively.
- The logo/favicon is `source/img/deepx-logo.svg` (copied from the studio's own assets).
