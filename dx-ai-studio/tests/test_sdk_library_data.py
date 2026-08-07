import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "launcher" / "static" / "sdk-library-data.json"
SUPPORTED_LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW")


def load_data():
    assert DATA_PATH.exists()
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def assert_i18n_label(value, path):
    assert isinstance(value, dict), f"{path} must be an i18n map"
    for lang in SUPPORTED_LANGS:
        assert lang in value, f"{path} missing {lang}"
        assert isinstance(value[lang], str) and value[lang].strip(), f"{path}.{lang} must be text"


def test_sdk_library_drawers_have_required_shape():
    data = load_data()
    assert isinstance(data.get("drawers"), list)
    assert data["drawers"], "drawers must not be empty"
    for drawer in data["drawers"]:
        for key in ("id", "label", "icon", "color", "sections"):
            assert key in drawer, f"drawer missing {key}"
        assert_i18n_label(drawer["label"], f"drawer[{drawer['id']}].label")
        assert isinstance(drawer["sections"], list) and drawer["sections"]


def test_sdk_library_sections_have_i18n_labels_and_files():
    data = load_data()
    for drawer in data["drawers"]:
        for section in drawer["sections"]:
            for key in ("id", "label", "icon", "files"):
                assert key in section, f"section missing {key}"
            assert_i18n_label(section["label"], f"section[{section['id']}].label")
            assert isinstance(section["files"], list)
            for file_info in section["files"]:
                assert "path" in file_info
                assert "title" in file_info


def test_registered_sdk_library_pdfs_are_packaged():
    data = load_data()
    missing = []
    for drawer in data["drawers"]:
        for section in drawer["sections"]:
            for file_info in section["files"]:
                if file_info.get("type") != "pdf":
                    continue
                pdf_path = ROOT / "launcher" / "static" / file_info["path"]
                if not pdf_path.is_file():
                    missing.append(file_info["path"])
    assert missing == []


def _suggest_relocation(suite_root, rel):
    """On drift, find a same-named real file elsewhere in the suite to hint the new path.

    is_file() skips broken mkdocs `--8<--` snippet symlinks; internal/build dirs are
    excluded so the hint points at a real, user-facing doc."""
    name = Path(rel).name
    skip = {".git", ".venv", "node_modules", "__pycache__", "superpowers", "build"}
    hits = []
    for cand in suite_root.rglob(name):
        if not cand.is_file() or set(cand.parts) & skip:
            continue
        hits.append(str(cand.relative_to(suite_root)))
        if len(hits) >= 3:
            break
    return hits


def test_registered_sdk_library_markdown_paths_exist_on_disk():
    data = load_data()
    suite_root = ROOT.parent
    missing = []
    for drawer in data["drawers"]:
        for section in drawer["sections"]:
            for file_info in section["files"]:
                path = file_info.get("path", "")
                if file_info.get("type") == "pdf" or path.startswith("pdfs/"):
                    continue
                if not (suite_root / path).is_file():
                    missing.append(path)
    if missing:
        # Submodule doc reorganizations (e.g. docs/ -> docs/source/, file renumbering)
        # break these hardcoded registry paths. Point at the likely new location so the
        # sdk-library-data.json fix is quick.
        lines = []
        for rel in missing:
            hits = _suggest_relocation(suite_root, rel)
            lines.append(
                "  " + rel
                + ("  -> maybe: " + ", ".join(hits) if hits else "  (no same-named file — doc removed?)")
            )
        raise AssertionError(
            "sdk-library-data.json registers %d markdown path(s) that no longer exist on "
            "disk (likely a submodule doc move/rename):\n%s" % (len(missing), "\n".join(lines))
        )
