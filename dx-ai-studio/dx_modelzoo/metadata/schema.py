"""ModelZoo metadata schema constants."""

SCHEMA_VERSION = "2.0"

SOURCE_STATUS = {
    "provided",
    "not_provided",
    "benchmark_required",
    "metadata_pending",
    "artifact_unavailable",
    "source_error",
    "stale_cache",
    "suspect",
}

ARTIFACT_IDS = {"onnx", "qlite_dxnn", "qlite_json", "qpro_dxnn", "qpro_json"}
