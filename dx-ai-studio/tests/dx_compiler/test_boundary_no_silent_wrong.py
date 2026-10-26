"""An error is better than a silently wrong answer.

Worse than a 500 is **a wrong answer with a 200**. A 500 at least says something
went wrong; a 200 says nothing while what ran differs from what the user asked for.

The cases guarded here:

  POST /compile/{id}/calculate-exclude
      input_nodes="ab"    must not be read as nodes a and b  (set("ab") == {'a','b'})
      input_nodes=["ab"]  the intended form must not crash with a 500
      unknown node        a user input error, not a server error
  POST /compile/{id}/resume
      input_nodes of any type   must not be stored on the job as-is; it would only
                                fail much later during compilation, hard to trace
  POST /compile
      enhanced_scheme="{{{"     must not silently become None and run a plain
                                compile when DXQ was requested
"""
from __future__ import annotations

import json
import types
import urllib.error
import urllib.request
import uuid

import pytest

from tests.server_helpers import start_module_server


class _Tensor:
    def __init__(self, producer=None):
        self.producer = producer
        self.consumers = []


class _Node:
    def __init__(self, name):
        self.name = name
        self.inputs = []
        self.outputs = []


def _linear_graph(names):
    """An a -> b -> c -> d chain. Single-letter names are the point.

    The bug shows only when `set("ab")` becomes `{'a','b'}` and **looks like two real
    nodes**. With longer names, splitting into letters would surface as an
    'unknown node' error and hide the real symptom (a silent 200).
    """
    nodes = [_Node(n) for n in names]
    for prev, nxt in zip(nodes, nodes[1:]):
        t = _Tensor(producer=prev)
        t.consumers.append(nxt)
        prev.outputs.append(t)
        nxt.inputs.append(t)
    return types.SimpleNamespace(nodes=nodes)


@pytest.fixture()
def compiler_with_graph():
    """A server seeded with a job that has a graph. These routes need a job to reach."""
    server, port = start_module_server("dx_compiler")
    from dx_compiler.server import compiler_service
    job = types.SimpleNamespace(
        job_id="graphjob", status="running", paused=True,
        prepared_graph_ir=_linear_graph(["a", "b", "c", "d"]),
        pause_event=__import__("threading").Event(),
        selected_input_nodes=[], selected_output_nodes=[])
    compiler_service.jobs["graphjob"] = job
    try:
        yield f"http://127.0.0.1:{port}", job
    finally:
        compiler_service.jobs.pop("graphjob", None)
        server.shutdown()


def _post(base, path, payload):
    req = urllib.request.Request(
        base + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode())
        except json.JSONDecodeError:
            return e.code, {}


class TestNodeListsAreNotStrings:
    def test_a_string_is_not_silently_split_into_letters(self, compiler_with_graph):
        """The nastiest case: set("ab") == {'a','b'} looks like two nodes.

        No error appears. The user named one node "ab", the server would take it as
        a and b and answer 200, and nobody would notice.
        """
        base, _ = compiler_with_graph
        code, body = _post(base, "/compile/graphjob/calculate-exclude",
                           {"input_nodes": "ab"})
        assert code == 400, f"문자열이 글자로 쪼개진 채 통과했다 — {code} {body}"

    def test_the_string_message_shows_the_exact_fix(self, compiler_with_graph):
        """Without a string-specific message the error only says "give a list".

        That does not tell someone who meant one node "ab" what to type. The
        message must show `['ab']`.

        Without this contract the string branch is dead code — the list check below
        also catches strings with a 400. This pins what the branch actually does
        (show the fix), so mutation testing cannot remove it unnoticed.
        """
        base, _ = compiler_with_graph
        code, body = _post(base, "/compile/graphjob/calculate-exclude",
                           {"input_nodes": "ab"})
        assert code == 400
        assert "['ab']" in body.get("error", ""), \
            f"무엇으로 고쳐야 하는지 보여주지 않는다 — {body}"

    def test_the_correct_form_for_one_node_is_accepted(self, compiler_with_graph):
        """The correct way to name one node is `["a"]`. It must pass."""
        base, _ = compiler_with_graph
        code, body = _post(base, "/compile/graphjob/calculate-exclude",
                           {"input_nodes": ["a"]})
        assert code == 200, f"올바른 형태를 막았다 — {code} {body}"

    def test_a_node_that_does_not_exist_is_the_users_mistake_not_ours(self, compiler_with_graph):
        """An unknown node name is the user's mistake. It must be a 400.

        A 500 means our fault and does not tell the user there is something to fix.
        """
        base, _ = compiler_with_graph
        code, body = _post(base, "/compile/graphjob/calculate-exclude",
                           {"input_nodes": ["does-not-exist"]})
        assert code == 400, f"사용자 입력 오류가 {code} 로 보고됐다 — {body}"
        assert "does-not-exist" in json.dumps(body), "어느 노드가 문제인지 말하지 않는다"

    @pytest.mark.parametrize("value", ["abc", 5, {"a": 1}, [1, 2], ["a", 3]])
    def test_unusable_node_lists_are_refused(self, compiler_with_graph, value):
        base, _ = compiler_with_graph
        code, body = _post(base, "/compile/graphjob/calculate-exclude",
                           {"input_nodes": value})
        assert code == 400, f"input_nodes={value!r} 가 {code} 를 받았다 — {body}"

    def test_an_empty_selection_still_means_everything_included(self, compiler_with_graph):
        """An empty selection is valid input and must not be blocked."""
        base, _ = compiler_with_graph
        code, body = _post(base, "/compile/graphjob/calculate-exclude", {})
        assert code == 200, body
        assert body["included_count"] == 4


class TestResumeStoresOnlyUsableNodeLists:
    @pytest.mark.parametrize("value", ["abc", 5, {"a": 1}, [1, 2]])
    def test_the_resume_endpoint_refuses_what_it_cannot_use(self, compiler_with_graph, value):
        """A value of the wrong type must not be stored on the job.

        It would only fail much later during compilation, where it is hard to trace
        back to this request. Refuse it on arrival.
        """
        base, job = compiler_with_graph
        job.paused = True
        job.selected_input_nodes = ["미리-있던-값"]
        code, body = _post(base, "/compile/graphjob/resume", {"input_nodes": value})
        assert code == 400, f"input_nodes={value!r} 를 {code} 로 받았다 — {body}"
        assert job.selected_input_nodes == ["미리-있던-값"], \
            "거부해 놓고 job 에는 써 넣었다"

    def test_a_usable_selection_still_resumes(self, compiler_with_graph):
        base, job = compiler_with_graph
        job.paused = True
        code, body = _post(base, "/compile/graphjob/resume",
                           {"input_nodes": ["a"], "output_nodes": ["c"]})
        assert code == 200, body
        assert job.selected_input_nodes == ["a"]
        assert job.selected_output_nodes == ["c"]


class TestBrokenEnhancedSchemeIsNotSwallowed:
    def test_unparseable_json_is_refused_not_dropped(self):
        """If the user asked for DXQ and the JSON is broken, silently running a plain
        compile is the worst outcome: what runs differs from what was asked, unnoticed."""
        server, port = start_module_server("dx_compiler")
        try:
            boundary = uuid.uuid4().hex
            fields = {"model_path": "/tmp/a.onnx", "config_path": "/tmp/a.json",
                      "output_dir": "/tmp/o", "enhanced_scheme": "{{{"}
            body = "".join(
                f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'
                for k, v in fields.items()) + f"--{boundary}--\r\n"
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/compile", data=body.encode(),
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
            try:
                with urllib.request.urlopen(req, timeout=20) as r:
                    code = r.status
                    payload = r.read().decode()[:200]
            except urllib.error.HTTPError as e:
                code, payload = e.code, e.read().decode()[:200]
            assert code == 400, f"깨진 enhanced_scheme 이 조용히 삼켜졌다 — {code} {payload}"
        finally:
            server.shutdown()
