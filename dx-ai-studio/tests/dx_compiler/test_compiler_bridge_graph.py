"""compiler_bridge — symbol resolution, error masking, and graph traversal.

These are the utilities that back the compiler UI's node-selection: pick a node,
and the wizard offers everything downstream (or upstream) of it. They were lifted
out of dx_com so dx_compiler runs without it, which also means nothing upstream
tests them any more.

They walk dx_com Node objects via .inputs/.outputs/.producer/.consumers, so the
fakes below reproduce exactly that shape — no dx_com required.
"""
import pytest

from dx_compiler.core import compiler_bridge as B


class _Tensor:
    def __init__(self, producer=None, consumers=None):
        self.producer = producer
        self.consumers = consumers or []


def _run_with_timeout(fn, timeout=5.0):
    """Run fn on a daemon thread; fail (rather than hang the suite) if it spins."""
    import threading

    box = {}

    def _target():
        box["value"] = fn()

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout)
    assert not t.is_alive(), (
        f"call did not terminate within {timeout}s — the visited-set guard is gone "
        "and the traversal is looping"
    )
    return box["value"]


class _Node:
    def __init__(self, name):
        self.name = name
        self.inputs = []
        self.outputs = []


def _graph(edges):
    """Build {name: node} from ("a", "b") edges meaning a -> b."""
    names = {n for e in edges for n in e}
    nodes = {n: _Node(n) for n in names}
    for src, dst in edges:
        tensor = _Tensor(producer=nodes[src], consumers=[nodes[dst]])
        nodes[src].outputs.append(tensor)
        nodes[dst].inputs.append(tensor)
    return nodes


class TestSymbolResolution:
    def test_decode_reverses_the_encoded_path(self):
        assert B._decode(B._e("dx_com.phase")) == "dx_com.phase"

    def test_unknown_symbol_names_itself_in_the_error(self):
        with pytest.raises(KeyError, match="Unknown compiler symbol"):
            B._resolve("not_a_registered_symbol")

    def test_resolution_is_cached(self, monkeypatch):
        calls = []
        monkeypatch.setattr(B, "_CACHE", {})
        monkeypatch.setattr(B, "_REGISTRY", {"x": (B._e("json"), "dumps")})
        monkeypatch.setattr(
            B.importlib, "import_module",
            lambda p: (calls.append(p), __import__(p))[1],
        )
        first, second = B._resolve("x"), B._resolve("x")
        assert first is second
        assert len(calls) == 1, "the module must be imported once, not per call"


class TestErrorMasking:
    @pytest.mark.parametrize("exc", [
        RuntimeError("/home/user/secret/path/model.onnx failed at layer 3"),
        MemoryError("allocation of 34359738368 bytes failed"),
        KeyboardInterrupt(),
    ])
    def test_raw_exception_text_never_reaches_the_banner(self, exc):
        """The failure banner is user-facing; raw compiler exceptions carry host
        paths and internals. The detail belongs in the CLI log below it."""
        masked = B.mask_compile_error(exc)
        assert masked == B.MASKED_COMPILE_ERROR
        assert str(exc) not in masked or not str(exc)


class TestValidateTargetNodes:
    def test_returns_the_intersection_when_all_exist(self):
        nodes = _graph([("a", "b"), ("b", "c")])
        assert B.validate_target_nodes({"a", "c"}, nodes) == {"a", "c"}

    def test_missing_nodes_are_listed_sorted(self):
        """The message is shown verbatim in the wizard, so the list must be
        deterministic — an unsorted set would reorder between runs."""
        nodes = _graph([("a", "b")])
        with pytest.raises(ValueError) as err:
            B.validate_target_nodes({"a", "zeta", "alpha"}, nodes)
        assert "['alpha', 'zeta']" in str(err.value)
        assert "compile_input_nodes" in str(err.value)

    def test_empty_target_set_is_allowed(self):
        assert B.validate_target_nodes(set(), _graph([("a", "b")])) == set()


class TestCollectDownstream:
    def test_walks_transitively(self):
        nodes = _graph([("a", "b"), ("b", "c"), ("c", "d")])
        assert B.collect_downstream_nodes({"a"}, nodes) == {"b", "c", "d"}

    def test_targets_themselves_are_excluded(self):
        """The caller already has the targets; re-including them would make the
        wizard offer to exclude the very node the user just picked."""
        nodes = _graph([("a", "b"), ("b", "c")])
        assert "a" not in B.collect_downstream_nodes({"a"}, nodes)

    def test_a_node_reachable_from_two_targets_is_not_duplicated(self):
        nodes = _graph([("a", "c"), ("b", "c"), ("c", "d")])
        assert B.collect_downstream_nodes({"a", "b"}, nodes) == {"c", "d"}

    def test_a_cycle_that_excludes_the_targets_terminates(self):
        """ONNX graphs are acyclic, but a malformed one must not hang the server.

        The cycle must NOT pass back through a target: `existing_targets` alone
        would then break the loop and the `visited` set would look redundant.
        Here start -> a -> b -> a loops entirely outside the target set, so only
        `visited` can stop it — and losing that guard hangs rather than returning
        a wrong answer, which is why this runs on a joined thread.
        """
        nodes = _graph([("start", "a"), ("a", "b"), ("b", "a")])
        result = _run_with_timeout(lambda: B.collect_downstream_nodes({"start"}, nodes))
        assert result == {"a", "b"}

    def test_leaf_node_has_no_downstream(self):
        nodes = _graph([("a", "b")])
        assert B.collect_downstream_nodes({"b"}, nodes) == set()

    def test_none_and_consumerless_tensors_are_skipped(self):
        """A graph output tensor has no consumers, and a partially built node can
        carry a None slot — neither may raise."""
        nodes = _graph([("a", "b")])
        nodes["a"].outputs.append(None)
        nodes["a"].outputs.append(_Tensor(consumers=[]))
        assert B.collect_downstream_nodes({"a"}, nodes) == {"b"}


class TestCollectUpstream:
    def test_walks_transitively_backwards(self):
        nodes = _graph([("a", "b"), ("b", "c"), ("c", "d")])
        assert B.collect_upstream_nodes({"d"}, nodes) == {"a", "b", "c"}

    def test_targets_themselves_are_excluded(self):
        nodes = _graph([("a", "b")])
        assert "b" not in B.collect_upstream_nodes({"b"}, nodes)

    def test_input_node_has_no_upstream(self):
        nodes = _graph([("a", "b")])
        assert B.collect_upstream_nodes({"a"}, nodes) == set()

    def test_a_cycle_terminates(self):
        nodes = _graph([("a", "b"), ("b", "a")])
        assert B.collect_upstream_nodes({"a"}, nodes) == {"b"}

    def test_none_and_producerless_tensors_are_skipped(self):
        """A graph INPUT tensor has no producer — the common case, not an edge."""
        nodes = _graph([("a", "b")])
        nodes["b"].inputs.append(None)
        nodes["b"].inputs.append(_Tensor(producer=None))
        assert B.collect_upstream_nodes({"b"}, nodes) == {"a"}

    def test_diamond_is_fully_collected(self):
        nodes = _graph([("root", "l"), ("root", "r"), ("l", "tip"), ("r", "tip")])
        assert B.collect_upstream_nodes({"tip"}, nodes) == {"l", "r", "root"}


def test_phase_param_names_are_the_hardcoded_constants():
    """These replaced dx_com.phase.constant.Params; drift silently breaks the
    config the wizard writes."""
    assert B.get_phase_params_input_nodes() == "input_nodes"
    assert B.get_phase_params_output_nodes() == "output_nodes"
