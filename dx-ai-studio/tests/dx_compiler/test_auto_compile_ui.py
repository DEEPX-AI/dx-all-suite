import pathlib
from tests.i18n_markup import assert_translatable

H = (pathlib.Path(__file__).resolve().parents[2] / "dx_compiler" / "templates" / "index.html").read_text()


def test_two_auto_compile_buttons_and_picker():
    for el in (
        'id="auto-compile-noninteractive"',
        'id="auto-compile-interactive"',
        'id="agentic-agent-select"',
        'id="agentic-model-input"',
    ):
        assert el in H, el


def test_agentic_has_llm_model_and_effort_pickers():
    """Mirror dx_agent_dev console: agentic compile exposes Model + Effort selectors."""
    for el in (
        'id="agentic-model-select"',       # LLM/coding model picker
        'id="agentic-effort-control"',     # reasoning-effort wrapper (hidden until populated)
        'id="agentic-effort-select"',      # effort picker
        'id="agentic-model-quality-hint"', # low-quality-model warning box
    ):
        assert el in H, el


def test_agentic_labels_six_langs():
    seg = H.split('id="agentic-compile"', 1)[1][:4000]
    assert_translatable(
        seg, "dx_compiler/static/js/compiler-i18n.js", "agentic-compile"
    )
