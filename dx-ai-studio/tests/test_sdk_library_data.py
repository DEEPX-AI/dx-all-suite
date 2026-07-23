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
    assert missing == []
