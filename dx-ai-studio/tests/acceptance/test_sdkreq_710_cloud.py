"""SDKREQ-710 [DX Cloud] AWS Compiler and Greengrass — DX Cloud inside a real ./launcher.sh studio.

DX Cloud talks to AWS through the studio server (boto3 and the user's AWS CLI profile). The UI checks run
against a fake AWS account: the page's /cloud/api/aws/* calls are answered by FakeAws below, so they run
on any board and never create, bill or delete anything. What the real server says without boto3 is
checked against the real server. A real AWS round trip (read-only calls) runs only when a usable AWS
profile and boto3 are present.
"""
from __future__ import annotations

import json
import re
from urllib.parse import parse_qs, urlparse

from tests.acceptance.conftest import http_get, module_frame, wait_home
from tests.acceptance.hardware import need, probe

NOW = "2026-10-16T09:30:00+00:00"
PREFIX = "models/mobilenet-20261016-093000/"


class FakeAws:
    """A small, stateful stand-in for the AWS account behind /cloud/api/aws/*."""

    def __init__(self, subscribed=True, stacks=True):
        self.subscribed = subscribed
        self.stacks = [] if not stacks else [
            {"name": "dx-cloud-qa", "kind": "compiler", "ready": True, "status": "CREATE_COMPLETE",
             "bucket": "dx-models-qa", "created": NOW, "deletable": True},
            {"name": "dx-gg-qa", "kind": "greengrass", "ready": True, "status": "CREATE_COMPLETE",
             "bucket": "dx-gg-qa", "created": NOW, "deletable": True}]
        self.posts: list[tuple[str, object]] = []
        self.compiled = False

    def reply(self, path: str, query: dict, method: str, body):
        if method == "POST":
            self.posts.append((path, body))
        if path == "status":
            return {"boto3": True, "profiles": ["dev"], "default_region": "ap-northeast-2", "install_hint": ""}
        if path == "regions":
            return {"regions": [{"code": "ap-northeast-2", "name": "Asia Pacific (Seoul)"},
                                {"code": "us-east-1", "name": "US East (N. Virginia)"}]}
        if path == "identity":
            return {"account": "123456789012", "arn": "arn:aws:iam::123456789012:user/qa"}
        if path == "subscription":
            return {"templates": [
                {"id": "compiler", "label": "DEEPX Compiler Solution", "subscribed": self.subscribed, "ami_id": "ami-0qa",
                 "marketplace": "https://aws.amazon.com/marketplace/pp/prodview-compiler"},
                {"id": "greengrass", "label": "DEEPX Greengrass Solution", "subscribed": self.subscribed,
                 "marketplace": "https://aws.amazon.com/marketplace/pp/prodview-greengrass"}]}
        if path == "stacks" and method == "GET":
            return {"stacks": self.stacks}
        if path == "stacks" and method == "POST":
            self.stacks.append({"name": body["name"], "kind": body["template"], "ready": False,
                                "status": "CREATE_IN_PROGRESS", "bucket": "dx-new", "created": NOW, "deletable": False})
            return {"name": body["name"], "bucket": "dx-new"}
        if path == "stacks/progress":
            for s in self.stacks:
                if s["name"] == query.get("name"):
                    s.update(ready=s["status"] != "DELETE_IN_PROGRESS", status="CREATE_COMPLETE", deletable=True)
            return {"name": query.get("name"), "status": "CREATE_COMPLETE",
                    "events": [{"time": NOW, "resource": "ModelBucket", "status": "CREATE_COMPLETE", "reason": ""}]}
        if path == "stacks/delete":
            self.stacks = [s for s in self.stacks if s["name"] != body["name"]]
            return {"name": body["name"], "bucket": "dx-models-qa"}
        if path == "compile" and method == "POST":
            self.compiled = True
            return {"region": "ap-northeast-2", "stack": "dx-cloud-qa", "prefix": PREFIX}
        if path == "compile/status":
            return {"state": "succeeded", "dxnn": PREFIX + "mobilenet.dxnn", "links": {
                "execution": "https://console.aws.amazon.com/states", "logs": "https://console.aws.amazon.com/cloudwatch",
                "s3": "https://s3.console.aws.amazon.com/s3"}}
        if path == "compile/log":
            return {"steps": [{"name": "Upload", "status": "succeeded", "time": NOW, "count": 1, "detail": ""},
                              {"name": "Compile", "status": "succeeded", "time": NOW, "count": 1, "detail": ""}],
                    "lines": [{"stream": "stdout", "text": "dxcom: compiling mobilenet.onnx"},
                              {"stream": "stdout", "text": "dxcom: done mobilenet.dxnn"}],
                    "instance_id": "i-0qa", "execution": {"status": "SUCCEEDED"}}
        if path == "compile/jobs":
            jobs = [{"model": "mobilenet", "prefix": PREFIX, "uploaded": NOW, "state": "succeeded",
                     "dxnn": PREFIX + "mobilenet.dxnn", "dxnn_size": 4_200_000}]
            return {"jobs": jobs}
        if path == "greengrass/devices":
            return {"thing_group": "dx-gg-qa-group", "deployment": {"status": "COMPLETED"},
                    "devices": [{"name": "board-01", "status": "HEALTHY", "last_update": NOW}]}
        if path == "greengrass/components":
            return {"components": [{"name": "com.deepx.dxrt", "version": "3.5.0", "state": "RUNNING"}]}
        if path == "greengrass/install-script":
            return {"script": f"#!/bin/sh\n# provision {body['thing']}\n", "filename": f"install-{body['thing']}.sh"}
        return None

    def route(self, route):
        req = route.request
        url = urlparse(req.url)
        path = url.path.split("/api/aws/", 1)[1]
        if path == "compile/download":
            route.fulfill(status=200, body=b"DXNN-QA", headers={
                "Content-Type": "application/octet-stream",
                "Content-Disposition": 'attachment; filename="mobilenet.dxnn"'})
            return
        body = None
        if req.method == "POST":
            ctype = req.headers.get("content-type", "")
            body = json.loads(req.post_data or "{}") if "json" in ctype else {"multipart": True}
        query = {k: v[0] for k, v in parse_qs(url.query).items()}
        out = self.reply(path, query, req.method, body)
        if out is None:
            route.fulfill(status=404, content_type="application/json", body=json.dumps({"error": f"no fake for {path}"}))
        else:
            route.fulfill(status=200, content_type="application/json", body=json.dumps(out))


def _cloud(pages, aws=None, lang="en"):
    page = pages.new(None, lang=lang)
    if aws is not None:
        page.route("**/cloud/api/aws/**", aws.route)
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    wait_home(page)
    page.locator('#studioGrid .orbital-card[data-app="edge"]').click()
    page.wait_for_function("() => DXLauncher.currentApp === 'edge' && location.pathname.startsWith('/cloud')")
    return page, module_frame(page, "edge", ready="#edgeSetup")


def _state(frame, step_id):
    return frame.locator(f"#{step_id}").evaluate("e => e.closest('.dx-step').dataset.state")


def test_entry_from_home_shows_both_solutions_and_the_status_bar(pages):
    page, frame = _cloud(pages, FakeAws())
    assert page.evaluate("() => DXLauncher.APP_PATHS.edge") == "/cloud/"
    tabs = [t.strip() for t in frame.locator(".edge-tab").all_inner_texts()]
    assert tabs == ["DEEPX Compiler Solution", "DEEPX Greengrass Solution"], tabs
    for chip in ("Profile", "Region", "Account", "Subs", "Stacks"):
        frame.locator(f"#edgeChip{chip}").wait_for(state="attached")
    frame.wait_for_function("() => document.getElementById('edgeChipAccountVal').textContent === '123456789012'",
                            timeout=15000)


def test_setup_is_a_numbered_flow_that_unlocks_step_by_step(pages):
    page, frame = _cloud(pages, FakeAws())
    dots = frame.locator("#edgePanel-compiler .dx-step-dot, #edgeSetup .dx-step-dot").all_inner_texts()
    assert [d.strip() for d in dots] == ["1", "2", "3", "4"], dots
    frame.wait_for_function("() => document.getElementById('edgeStep1State').textContent.trim() === 'Done'",
                            timeout=15000)
    assert _state(frame, "edgeStep2State-compiler") == "done"
    assert _state(frame, "edgeStep3State-compiler") == "done"
    assert _state(frame, "edgeStep4State-compiler") in ("todo", "done")
    frame.locator("#edgeTab-greengrass").click()
    gg = [d.strip() for d in frame.locator("#edgePanel-greengrass .dx-step-dot").all_inner_texts()]
    assert gg == ["2", "3", "4-1", "4-2"], gg


def test_aws_status_names_the_profile_and_region_and_without_boto3_says_how_to_install_it(pages, studio):
    st = json.loads(http_get(studio.base + "/cloud/api/aws/status", headers={"Sec-Fetch-Dest": "empty"})[2])
    assert set(st) >= {"boto3", "profiles", "default_region"}, st
    assert st["default_region"]
    page, frame = _cloud(pages, FakeAws())
    frame.wait_for_function("() => [...document.getElementById('edgeProfile').options].some(o => o.value === 'dev')",
                            timeout=15000)
    assert "us-east-1" in frame.locator("#edgeRegion").inner_text()
    assert "arn:aws:iam::123456789012:user/qa" in frame.locator("#edgeIdentity").inner_text()
    if not st["boto3"]:                     # the real server on a studio without the aws extra
        page2, real = _cloud(pages)
        real.locator("#edgeBoto3Missing").wait_for(state="visible", timeout=15000)
        assert "boto3" in real.locator("#edgeBoto3Missing").inner_text()
        assert real.locator("#edgeGuide").evaluate("d => d.open")
        assert real.locator("#edgeStart-compiler").is_disabled()


def test_marketplace_subscription_is_checked_per_solution(pages):
    page, frame = _cloud(pages, FakeAws(subscribed=False, stacks=False))
    subs = frame.locator("#edgeSubs-compiler")
    subs.locator(".badge").first.wait_for(timeout=15000)
    assert "Not subscribed" in subs.inner_text()
    assert subs.locator("a", has_text="Subscribe on Marketplace").get_attribute("href").startswith("https://aws.amazon.com/marketplace")
    assert _state(frame, "edgeStep2State-compiler") == "todo"
    page2, frame2 = _cloud(pages, FakeAws(subscribed=True))
    frame2.locator("#edgeSubs-compiler .badge", has_text="Subscribed").wait_for(timeout=15000)


def test_a_compiler_stack_is_created_and_deleted_only_after_typing_its_name(pages):
    aws = FakeAws(stacks=False)
    page, frame = _cloud(pages, aws)
    frame.wait_for_function("() => document.getElementById('edgeStep2State-compiler').textContent.trim() === 'Done'",
                            timeout=15000)
    frame.locator("#edgeStackName-compiler").fill("dx-cloud-accept")
    frame.locator("#edgeDeploy-compiler").click()
    frame.locator("#edgeStackEvents-compiler li").first.wait_for(timeout=15000)
    created = [b for p, b in aws.posts if p == "stacks"]
    assert created and created[0]["template"] == "compiler" and created[0]["name"] == "dx-cloud-accept", aws.posts
    row = frame.locator("#edgeStackList-compiler li", has_text="dx-cloud-accept")
    row.locator("button", has_text="Delete").wait_for(timeout=15000)
    row.locator("button", has_text="Delete").click()
    frame.locator("#edgeDeleteDialog[open]").wait_for(timeout=10000)
    assert frame.locator("#edgeDeleteOk").is_disabled()
    frame.locator("#edgeDeleteConfirm").fill("dx-cloud-accep")
    assert frame.locator("#edgeDeleteOk").is_disabled()
    frame.locator("#edgeDeleteConfirm").fill("dx-cloud-accept")
    frame.locator("#edgeDeleteOk").click()
    frame.wait_for_function("() => !document.querySelector('#edgeDeleteDialog[open]')")
    deleted = [b for p, b in aws.posts if p == "stacks/delete"]
    assert deleted and deleted[0]["confirm"] == "dx-cloud-accept", aws.posts


def test_cloud_compile_uploads_the_model_and_shows_the_workflow_log(pages, tmp_path):
    aws = FakeAws()
    page, frame = _cloud(pages, aws)
    onnx, cfg = tmp_path / "mobilenet.onnx", tmp_path / "mobilenet.json"
    onnx.write_bytes(b"\x08\x07fake-onnx")
    cfg.write_text("{}")
    frame.wait_for_function("() => document.getElementById('edgeStack-compiler').value === 'dx-cloud-qa'", timeout=15000)
    frame.locator("#edgeOnnx-compiler").set_input_files(str(onnx))
    frame.locator("#edgeJson-compiler").set_input_files(str(cfg))
    frame.locator("#edgeStart-compiler").click()
    frame.wait_for_function("(p) => document.getElementById('edgeJobPrefix-compiler').textContent === p", arg=PREFIX,
                            timeout=15000)
    frame.wait_for_function("() => /done mobilenet.dxnn/.test(document.getElementById('edgeLogOut-compiler').textContent)",
                            timeout=20000)
    assert frame.locator("#edgeLogSteps-compiler li").count() >= 2
    frame.locator("#edgeDownload-compiler").wait_for(state="visible", timeout=20000)
    assert "compile/download" in frame.locator("#edgeDownload-compiler").get_attribute("href")
    assert frame.locator("#edgeSave-compiler").is_visible()
    assert any(p == "compile" for p, _ in aws.posts)


def test_the_job_list_shows_every_compile_and_downloads_its_dxnn(pages):
    page, frame = _cloud(pages, FakeAws())
    row = frame.locator("#edgeJobRows-compiler tr", has_text="mobilenet")
    row.wait_for(timeout=20000)
    assert "succeeded" in row.inner_text().lower()
    with page.expect_download(timeout=20000) as dl:
        row.locator("a[href*='compile/download']").click()
    assert dl.value.suggested_filename.endswith(".dxnn")


def test_greengrass_tab_lists_devices_and_generates_an_install_script(pages):
    aws = FakeAws()
    page, frame = _cloud(pages, aws)
    frame.locator("#edgeTab-greengrass").click()
    frame.locator("#edgePanel-greengrass").wait_for(state="visible")
    frame.locator("#edgeDevRows tr", has_text="board-01").wait_for(timeout=20000)
    assert "HEALTHY" in frame.locator("#edgeDevRows").inner_text()
    assert frame.locator("#edgeDevGroup").inner_text() == "dx-gg-qa-group"
    frame.locator("#edgeThing").fill("board-02")
    frame.locator("#edgeRegGen").click()
    frame.locator("#edgeRegOut").wait_for(state="visible", timeout=10000)
    assert "board-02" in frame.locator("#edgeScript").inner_text()


def test_aws_cli_setup_guide_and_the_console_guide_page(pages):
    page, frame = _cloud(pages, FakeAws())
    frame.locator("#edgeGuide").evaluate("d => d.open = true")
    guide = frame.locator("#edgeGuide").inner_text()
    for step in ("Install AWS CLI v2", "Configure credentials", "Verify", "Required permissions"):
        assert step in guide, step
    links = frame.locator('a[href^="guide#"]').evaluate_all("els => els.map(e => e.getAttribute('href'))")
    assert {"guide#compiler", "guide#greengrass"} <= set(links), links
    frame.locator('a[href="guide#compiler"]').click()
    frame.wait_for_url(re.compile(r"/cloud/guide"), timeout=15000)
    frame.locator("#guideMain").wait_for(timeout=15000)
    frame.wait_for_function("() => document.querySelectorAll('#guideMain img').length > 0 &&"
                            " document.getElementById('guideMain').innerText.length > 500", timeout=15000)


def test_the_tutorial_guides_through_dx_cloud_without_pressing_aws_buttons(pages):
    page, frame = _cloud(pages, FakeAws())
    frame.locator("#dxToolbarTutorial").click()
    frame.locator(".dxt-toc.open").wait_for(timeout=10000)
    frame.locator(".dxt-toc-btn-start").click()
    frame.locator(".dxt-tooltip.active").wait_for(timeout=10000)


def test_the_aws_partner_and_qualified_software_badges_show(pages):
    page, frame = _cloud(pages, FakeAws())
    imgs = frame.locator(".edge-badge-art img:visible")
    imgs.first.wait_for(timeout=15000)
    alts = set(imgs.evaluate_all("els => els.map(e => e.alt)"))
    assert {"AWS Partner", "AWS Qualified Software"} <= alts, alts
    assert frame.evaluate("() => [...document.querySelectorAll('.edge-badge-art img')].filter(i => i.offsetParent)"
                          ".every(i => i.complete && i.naturalWidth > 0)")


def test_a_real_aws_account_answers_read_only_calls(studio):
    need("aws")
    q = "?region=ap-northeast-2"
    for path in ("identity", "subscription", "stacks"):
        status, _, body = http_get(studio.base + f"/cloud/api/aws/{path}{q}", timeout=60,
                                   headers={"Sec-Fetch-Dest": "empty"})
        assert status == 200, (path, status, body[:300])
    assert probe("aws")[0]
