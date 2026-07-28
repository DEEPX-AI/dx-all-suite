import hashlib
from pathlib import Path


RESOURCE_DIR = Path(__file__).resolve().parents[2] / "docs" / "source" / "resources"

EXPECTED_SHA256 = {
    "stream.png": "6091e15daaab938a68d24e02509d69aaba26cfaa1cbded6080d4cf6482f355ad",
    "modelzoo-detail.png": "a6bc38677fd54d2463159cbdebf4836251f0b0bcbb5375a42dfa09f6a35fb8f8",
    "app.png": "66e1dc09f52663820cc41c44945b5fe478ac2e2fe23746afe6e46fab52a11f59",
    "tutorial.png": "06463981d7ca211eba73f9e8b74aaabeb2f23536e5cb21b959e6a5b189332ada",
    "compiler.png": "5b190d9687dd191b1d62dbd3e15ab3e59bd597b567bcf5d9e6876c2a2aef157f",
    "hub.png": "89dcf4c03166ed21295b265f4d086a11fa643e870b016c14d84e6e11177877ea",
    "about.png": "56b723256f8cb710c51f681a88c2c154f50626f643d6b910d12a9f4f63cea3d7",
}


def test_resources_match_documented_screen_mapping():
    actual = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in RESOURCE_DIR.glob("*.png")
        if path.name in EXPECTED_SHA256
    }

    assert actual == EXPECTED_SHA256
