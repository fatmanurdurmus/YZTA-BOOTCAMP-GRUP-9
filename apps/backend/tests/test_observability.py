from carbonpilot import observability


def test_tracing_is_disabled_without_opt_in(monkeypatch):
    monkeypatch.setattr(observability, "get_settings", lambda: type("Settings", (), {"langsmith_tracing": False, "langsmith_api_key": "key"})())
    assert observability.tracing_enabled() is False
    with observability.trace_operation("safe", thread_id="thread-1", retries=1):
        pass


def test_trace_metadata_excludes_activity_payload(monkeypatch):
    captured = {}

    class Run:
        def end(self, **kwargs):
            captured["end"] = kwargs

        def patch(self):
            captured["patched"] = True

    class Client:
        def __init__(self, **kwargs):
            pass

    monkeypatch.setattr(observability, "get_settings", lambda: type("Settings", (), {"langsmith_tracing": True, "langsmith_api_key": "key", "langsmith_project": "project"})())
    import langsmith
    from langsmith import run_trees

    class RunTree:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def post(self):
            return None

        def end(self, **kwargs):
            captured["end"] = kwargs

        def patch(self):
            captured["patched"] = True

    monkeypatch.setattr(langsmith, "Client", Client)
    monkeypatch.setattr(run_trees, "RunTree", RunTree)
    with observability.trace_operation("node", thread_id="thread-1", retries=2):
        pass
    assert captured["inputs"] == {"thread_id": "thread-1", "retries": 2}
    assert captured["patched"] is True
