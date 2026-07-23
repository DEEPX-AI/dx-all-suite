"""브라우저 노출용 모델 메타데이터 sanitize 테스트."""


def test_sanitize_browser_model_removes_internal_remote_urls():
    from dx_modelzoo.metadata.sanitize import sanitize_browser_model

    model = {
        "id": "x",
        "artifacts": {
            "onnx": {
                "remote_url": "https://modelzoo-api.devops.dpx.ai/file.onnx",
            }
        },
    }

    safe = sanitize_browser_model(model)

    assert safe["artifacts"]["onnx"].get("remote_url") is None
    assert safe["artifacts"]["onnx"]["source_status"] == "artifact_unavailable"
    assert model["artifacts"]["onnx"]["remote_url"].startswith("https://modelzoo-api")


def test_sanitize_browser_model_keeps_public_urls():
    from dx_modelzoo.metadata.sanitize import sanitize_browser_model

    model = {
        "id": "x",
        "artifacts": {
            "onnx": {
                "remote_url": "https://sdk.deepx.ai/file.onnx",
            }
        },
    }

    safe = sanitize_browser_model(model)

    assert safe["artifacts"]["onnx"]["remote_url"] == "https://sdk.deepx.ai/file.onnx"
