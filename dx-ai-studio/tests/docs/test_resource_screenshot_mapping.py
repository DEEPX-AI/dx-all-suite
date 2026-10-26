import hashlib
from pathlib import Path


RESOURCE_DIR = Path(__file__).resolve().parents[2] / "docs" / "source" / "resources"

EXPECTED_SHA256 = {
    "stream.png": "d9f6862c6bd4bdbd4495bc5d539c0bb738b7adad4fa93544867e534f18ef90c1",
    "modelzoo-detail.png": "db348954a4dc10478c6a7e261c85b851ef27f2954940d909ac91327677e20718",
    "app.png": "379f2275f2a758dbf938e59a5103a2604e1efbfe90ca6379265cffa5096041fa",
    "tutorial.png": "6f36ce6a9ef720e1d64113650beb707ed8cb0611b470004b3c653c236187c29f",
    "compiler.png": "6ad217a8aa5df5c95dc7a1902904d4b8855ea84f2ab012701a438f30f8207dac",
    "hub.png": "12a3e06932c884fb494930d079479a724045f0fbdbe6501ce1dc07ca271b7c63",
    "about.png": "59ff30bfc4599688372869f08ecbbf8584a860d83d9cc1ceda076af9a5a7243b",
}


def test_resources_match_documented_screen_mapping():
    actual = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in RESOURCE_DIR.glob("*.png")
        if path.name in EXPECTED_SHA256
    }

    assert actual == EXPECTED_SHA256
