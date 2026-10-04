import asyncio
import gc
from inspect import isawaitable
from weakref import ref
from unittest.mock import AsyncMock, Mock, PropertyMock

import pytest

from scrapling.core._types import Any, Optional
from scrapling.engines._browsers import _network
from scrapling.engines._browsers._network import NetworkRecorder, NetworkRequest
from scrapling.engines.toolbelt.custom import Response


class Context:
    def __init__(self):
        self.listeners: dict[str, list[Any]] = {}

    def on(self, event, listener):
        self.listeners.setdefault(event, []).append(listener)

    def remove_listener(self, event, listener):
        self.listeners[event].remove(listener)

    def emit(self, event, value=None):
        tasks = []
        for listener in self.listeners.get(event, []).copy():
            result = listener(value)
            if isawaitable(result):
                tasks.append(asyncio.ensure_future(result))
        return tasks


def request(
    url="https://example.test/api",
    method="GET",
    resource_type="fetch",
    status: Optional[int] = 200,
    body=b'{"ok":true}',
    asynchronous=False,
):
    make = AsyncMock if asynchronous else Mock
    native = Mock(url=url, method=method, resource_type=resource_type)
    native.headers = {"cookie": "session=1"}
    native.all_headers = make(return_value=native.headers.copy())
    native.post_data_buffer = None
    native.existing_response = None
    if status is not None:
        response = Mock(url=url, status=status, status_text="OK", request=native)
        response.headers = {"content-type": "application/json", "content-length": str(len(body))}
        response.all_headers = make(return_value=response.headers.copy())
        response.body = make(return_value=body)
        native.existing_response = response
    return native


def recorder(max_requests=1000, asynchronous=False):
    network = NetworkRecorder(enabled=True, max_requests=max_requests, asynchronous=asynchronous)
    context = Context()
    network._attach(context)
    return network, context


async def finish(context, native):
    await asyncio.gather(*context.emit("requestfinished", native))


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_only_completed_responses_are_saved(asynchronous):
    network, context = recorder(asynchronous=asynchronous)
    native = request(asynchronous=asynchronous)
    assert set(context.listeners) == {"requestfinished", "close"}
    context.emit("request", native)
    context.emit("response", native.existing_response)
    context.emit("requestfailed", request(status=None, asynchronous=asynchronous))
    assert network.search() == [] and network.last_id == 0
    native.all_headers.assert_not_called()
    native.existing_response.body.assert_not_called()
    await finish(context, request(status=None, asynchronous=asynchronous))
    assert network.search() == []
    await finish(context, native)
    record = network.get(1)
    assert isinstance(record, NetworkRequest) and not hasattr(record, "request")
    assert not hasattr(record, "state") and not hasattr(record, "failure")
    assert record.id == 1 and record.url == native.url and record.method == "GET"
    assert record.resource_type == "fetch" and record.status == 200
    assert record.response.json() == {"ok": True}
    assert "body_note" not in record.response.meta


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_saved_response_has_final_request_data_and_survives_close(asynchronous):
    network, context = recorder(asynchronous=asynchronous)
    native = request(asynchronous=asynchronous)
    original_url = native.url
    context.emit("request", native)
    native.url, native.method = "https://example.test/overridden", "POST"
    native.headers = {"x-overridden": "yes", "content-type": "text/plain"}
    native.post_data_buffer = b"overridden"
    native.all_headers.return_value = native.headers.copy()
    native.existing_response.url = native.url
    await finish(context, native)
    record = network.get(1)
    assert record is not None
    assert record.url == native.url and record.response.url == native.url and record.method == "POST"
    assert record.request_body == b"overridden"
    assert record.request_headers == record.response.request_headers == native.headers
    assert record.response_headers == record.response.headers == native.existing_response.headers
    assert network.search(url_pattern=original_url) == [] and network.search(method="POST") == [record]
    native.headers["x-overridden"] = "changed"
    native.existing_response.headers["content-type"] = "changed"
    assert record.request_headers["x-overridden"] == "yes"
    assert record.response_headers["content-type"] == "application/json"
    native.all_headers.assert_called_once_with()
    native.existing_response.all_headers.assert_called_once_with()
    native.existing_response.body.assert_called_once_with()
    context.emit("close")
    network._detach()
    native.all_headers.side_effect = RuntimeError("Browser closed")
    native.existing_response.all_headers.side_effect = RuntimeError("Browser closed")
    native.existing_response.body.side_effect = RuntimeError("Browser closed")
    assert record.response.json() == {"ok": True}
    assert network.get(1) is record and network.search() == [record]
    native.existing_response.body.assert_called_once_with()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("outcome", ["saved", "oversized", "unreadable", "invalid_charset", "non_text"])
async def test_recording_skips_fetch_log_without_muting_normal_responses(monkeypatch, asynchronous, outcome):
    logger = Mock()
    monkeypatch.setattr("scrapling.engines.toolbelt.custom.log", logger)
    network, context = recorder(asynchronous=asynchronous)
    native = request(asynchronous=asynchronous)
    if outcome == "oversized":
        monkeypatch.setattr(_network, "MAX_BODY_BYTES", 4)
    elif outcome == "unreadable":
        native.existing_response.body.side_effect = RuntimeError("Body missing")
    elif outcome == "invalid_charset":
        native.existing_response.headers["content-type"] = "application/json; charset=bogus"
    elif outcome == "non_text":
        native.existing_response.headers["content-type"] = "application/octet-stream"
    await finish(context, native)
    record = network.get(1)
    assert record is not None
    assert (
        record.response.meta
        == {
            "saved": {},
            "oversized": {"body_note": "too large; not saved."},
            "unreadable": {"body_note": "Body missing"},
            "invalid_charset": {},
            "non_text": {"body_note": "Non-text body; not saved."},
        }[outcome]
    )
    logger.info.assert_not_called()
    response = Response(
        url="https://example.test/page",
        content=b"page",
        status=200,
        reason="OK",
        cookies={},
        headers={},
        request_headers={},
    )
    assert response.body == b"page"
    logger.info.assert_called_once_with("Fetched (200) <GET https://example.test/page> (referer: None)")


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_oversized_response_keeps_headers_without_reading_body(monkeypatch, asynchronous):
    monkeypatch.setattr(_network, "MAX_BODY_BYTES", 4)
    network, context = recorder(asynchronous=asynchronous)
    native = request(body=b"large", asynchronous=asynchronous)
    await finish(context, native)
    record = network.get(1)
    assert record is not None
    assert record.status == 200 and record.response.meta == {"body_note": "too large; not saved."}
    assert record.response.body == b"" and record.response.headers["content-length"] == "5"
    native.existing_response.body.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("message", ["Body was removed", ""])
async def test_unreadable_response_keeps_headers_and_reports_unavailable(asynchronous, message):
    network, context = recorder(asynchronous=asynchronous)
    native = request(asynchronous=asynchronous)
    native.existing_response.body.side_effect = RuntimeError(message)
    await finish(context, native)
    record = network.get(1)
    assert record is not None
    assert record.status == 200
    assert record.response.meta == {"body_note": message or "could not be saved."}
    assert record.response.body == b"" and record.response.headers == native.existing_response.headers


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_non_text_records_keep_metadata_without_using_body_budget(monkeypatch, asynchronous):
    monkeypatch.setattr(_network, "MAX_TOTAL_BODY_BYTES", 8)
    network, context = recorder(asynchronous=asynchronous)
    await finish(context, request(body=b"1234", asynchronous=asynchronous))
    for request_id, content_type in enumerate(("application/octet-stream", "application/x-custom", None), start=2):
        native = request(
            url=f"https://example.test/binary/{request_id}",
            method="POST",
            resource_type="image",
            status=206,
            body=b"\x00\xffbinary",
            asynchronous=asynchronous,
        )
        native.post_data_buffer = b"submitted"
        response = native.existing_response
        response.headers = {"x-saved": "yes"}
        if content_type is not None:
            response.headers["content-type"] = content_type
        response.all_headers.return_value = response.headers.copy()
        response.body.side_effect = AssertionError("Non-text body must not be read")
        await finish(context, native)
        record = network.get(request_id)
        assert record is not None
        assert record.url == native.url and record.method == "POST" and record.status == 206
        assert record.resource_type == "image" and record.request_body == b"submitted"
        assert record.request_headers == native.headers and record.response_headers == response.headers
        assert record.response.body == b"" and record.response.meta == {"body_note": "Non-text body; not saved."}
        response.body.assert_not_called()
    await finish(context, request(body=b"5678", asynchronous=asynchronous))
    assert [record.id for record in network.search()] == [1, 2, 3, 4, 5]
    assert [record.response.body for record in network.search()] == [b"1234", b"", b"", b"", b"5678"]
    assert network.dropped_count == 0
    await finish(context, request(body=b"9", asynchronous=asynchronous))
    assert [record.id for record in network.search()] == [2, 3, 4, 5, 6]
    assert network.get(1) is None and network.dropped_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_total_body_budget_evicts_oldest_records_and_clear_releases_budget(monkeypatch, asynchronous):
    monkeypatch.setattr(_network, "MAX_TOTAL_BODY_BYTES", 7)
    network, context = recorder(asynchronous=asynchronous)
    for body in (b"one", b"two", b"three"):
        await finish(context, request(body=body, asynchronous=asynchronous))
    assert [record.id for record in network.search()] == [3]
    record = network.get(3)
    assert record is not None
    assert network.dropped_count == 2 and record.response.body == b"three"
    network.clear()
    assert network.dropped_count == 0 and network.last_id == 3 and not network.search()
    for _ in range(2):
        await finish(context, request(body=b"new", asynchronous=asynchronous))
    assert [record.id for record in network.search()] == [4, 5] and network.dropped_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_count_eviction_releases_saved_body_budget(monkeypatch, asynchronous):
    monkeypatch.setattr(_network, "MAX_TOTAL_BODY_BYTES", 5)
    network, context = recorder(max_requests=1, asynchronous=asynchronous)
    for _ in range(3):
        await finish(context, request(body=b"new", asynchronous=asynchronous))
    assert [record.id for record in network.search()] == [3]
    record = network.get(3)
    assert record is not None
    assert record.response.body == b"new" and network.dropped_count == 2
    network.clear()
    await finish(context, request(body=b"new", asynchronous=asynchronous))
    assert [record.id for record in network.search()] == [4] and network.dropped_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("change", ["clear", "detach", "reattach"])
@pytest.mark.parametrize("started", [False, True])
async def test_late_callback_cannot_publish_after_clear_or_detach(change, started):
    network, context = recorder(asynchronous=True)
    reading, release = asyncio.Event(), asyncio.Event()

    async def body():
        reading.set()
        await release.wait()
        return b"old"

    native = request(asynchronous=True)
    native.existing_response.body.side_effect = body
    tasks = context.emit("requestfinished", native)
    try:
        if started:
            await asyncio.wait_for(reading.wait(), timeout=2)
        if change == "clear":
            network.clear()
        else:
            network._detach(context)
            if change == "reattach":
                network._attach(context)
        release.set()
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=2)
        assert network.search() == [] and network.last_id == 0
        if change != "detach":
            await finish(context, request(body=b"new", asynchronous=True))
            record = network.get(1)
            assert record is not None
            assert record.response.body == b"new"
    finally:
        release.set()
        await asyncio.gather(*tasks)
        network._detach()


@pytest.mark.asyncio
async def test_records_are_published_in_save_order_without_waiting_for_other_bodies():
    network, context = recorder(asynchronous=True)
    reading, release = asyncio.Event(), asyncio.Event()

    async def body():
        reading.set()
        await release.wait()
        return b"first"

    first = request(asynchronous=True)
    first.existing_response.body.side_effect = body
    tasks = context.emit("requestfinished", first)
    try:
        await asyncio.wait_for(reading.wait(), timeout=2)
        assert network.search() == [] and network.get(1) is None
        await finish(context, request(body=b"second", asynchronous=True))
        record = network.get(1)
        assert record is not None
        assert record.response.body == b"second"
        release.set()
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=2)
        assert [record.response.body for record in network.search()] == [b"second", b"first"]
    finally:
        release.set()
        await asyncio.gather(*tasks)


def test_context_lifecycle_keeps_history_and_removes_only_owned_listeners():
    network, first = recorder()
    second, external = Context(), Mock()
    first.on("requestfinished", external)
    network._attach(first)
    network._attach(second)
    assert len(first.listeners["requestfinished"]) == 2 and len(first.listeners["close"]) == 1
    first.emit("requestfinished", request(status=201))
    second.emit("requestfinished", request())
    network._detach(first)
    first.emit("requestfinished", request())
    second.emit("requestfinished", request())
    assert network.last_id == 3
    assert first.listeners["requestfinished"] == [external] and not first.listeners["close"]
    second.emit("close")
    assert not any(second.listeners.values()) and not network._contexts
    record = network.get(1)
    assert record is not None
    assert record.status == 201
    network._attach(first)
    first.emit("requestfinished", request())
    network._detach()
    network._detach()
    assert network.enabled and len(network.search()) == 4
    assert first.listeners["requestfinished"] == [external] and not first.listeners["close"]
    external.assert_called()


def test_search_filters_include_completed_http_errors():
    network, context = recorder()
    for native in (
        request(url="https://example.test/page", resource_type="document"),
        request(url="https://example.test/api", method="POST", status=503),
        request(url="https://example.test/missing", resource_type="document", status=404),
        request(url="https://example.test/api", resource_type="xhr"),
    ):
        context.emit("requestfinished", native)
    assert [record.id for record in network.search(include_static=False)] == [2, 3, 4]
    assert [record.id for record in network.search(after_id=2, limit=1)] == [3]
    assert [record.id for record in network.search(url_pattern="/api$", method="post", status=503)] == [2]
    assert [record.id for record in network.search(resource_type="xhr")] == [4]
    assert network.get(100) is None and network.search(url_pattern="absent") == []


@pytest.mark.parametrize("options", [{"limit": 0}, {"after_id": -1}, {"url_pattern": "["}])
def test_invalid_filters_raise_value_error(options):
    with pytest.raises(ValueError):
        NetworkRecorder().search(**options)


def test_disabled_recorder_never_attaches():
    network, context = NetworkRecorder(), Mock()
    network._attach(context)
    network._detach(context)
    network._detach()
    assert not context.mock_calls and not network.search() and network.last_id == 0
    with pytest.raises(ValueError, match="greater than zero"):
        NetworkRecorder(max_requests=0)


def test_partial_listener_setup_failure_does_not_leave_capture_attached():
    network, context = NetworkRecorder(enabled=True), Mock()
    context.on.side_effect = [None, RuntimeError("Context closed")]
    network._attach(context)
    assert not network._contexts
    assert context.remove_listener.call_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("outcome", ["finished", "body_error", "headers_error", "conversion_error", "unfinished"])
async def test_native_handles_are_not_kept_in_history(asynchronous, outcome):
    network, context = recorder(asynchronous=asynchronous)
    native = request(asynchronous=asynchronous)
    native_ref, response_ref = ref(native), ref(native.existing_response)
    if outcome == "body_error":
        native.existing_response.body.side_effect = RuntimeError("Body missing")
    elif outcome == "headers_error":
        native.existing_response.all_headers.side_effect = RuntimeError("Headers missing")
    elif outcome == "conversion_error":
        type(native.existing_response).status_text = PropertyMock(side_effect=RuntimeError("Response missing"))
    if outcome != "unfinished":
        await finish(context, native)
    else:
        context.emit("request", native)
    if outcome in {"unfinished", "conversion_error"}:
        assert network.search() == []
    else:
        record = network.get(1)
        assert record is not None
        assert record.status == 200
        assert record.response.meta.get("body_note") == ("Body missing" if outcome == "body_error" else None)
    del native
    gc.collect()
    assert native_ref() is None and response_ref() is None


@pytest.mark.parametrize("change", ["clear", "detach", "reattach"])
def test_sync_conversion_cannot_restore_history_after_reentrant_reset(change):
    network, context = recorder()
    native = request(body=b"old")

    def body():
        assert network.search() == [] and network.get(1) is None
        if change == "clear":
            network.clear()
        else:
            network._detach(context)
            if change == "reattach":
                network._attach(context)
        if change != "detach":
            context.emit("requestfinished", request(body=b"new"))
        return b"old"

    native.existing_response.body.side_effect = body
    context.emit("requestfinished", native)
    expected = [] if change == "detach" else [b"new"]
    assert [record.response.body for record in network.search()] == expected
    assert network.last_id == len(expected)


@pytest.mark.asyncio
async def test_cancelled_conversion_publishes_nothing_and_later_requests_still_save():
    network, context = recorder(asynchronous=True)
    reading, release = asyncio.Event(), asyncio.Event()

    async def body():
        reading.set()
        await release.wait()
        return b"cancelled"

    native = request(asynchronous=True)
    native.existing_response.body.side_effect = body
    tasks = context.emit("requestfinished", native)
    try:
        await asyncio.wait_for(reading.wait(), timeout=2)
        tasks[0].cancel()
        with pytest.raises(asyncio.CancelledError):
            await tasks[0]
        assert network.search() == [] and network.last_id == 0
        await finish(context, request(body=b"saved", asynchronous=True))
        record = network.get(1)
        assert record is not None
        assert record.response.body == b"saved"
    finally:
        release.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        network._detach()


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("budget", ["count", "body", "both"])
async def test_exact_storage_boundaries_keep_records_until_exceeded(monkeypatch, asynchronous, budget):
    monkeypatch.setattr(_network, "MAX_BODY_BYTES", 4)
    monkeypatch.setattr(_network, "MAX_TOTAL_BODY_BYTES", 100 if budget == "count" else 8)
    network, context = recorder(max_requests=3 if budget == "body" else 2, asynchronous=asynchronous)
    for body in (b"1111", b"2222"):
        await finish(context, request(body=body, asynchronous=asynchronous))
    assert [record.response.body for record in network.search()] == [b"1111", b"2222"]
    assert network.dropped_count == 0
    await finish(context, request(body=b"3", asynchronous=asynchronous))
    assert [record.response.body for record in network.search()] == [b"2222", b"3"]
    assert network.get(1) is None and network.dropped_count == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("attribute", ["resource_type", "post_data_buffer"])
async def test_unreadable_request_metadata_is_omitted_and_native_handles_are_released(asynchronous, attribute):
    network, context = recorder(asynchronous=asynchronous)
    native = request(asynchronous=asynchronous)
    native_ref, response_ref = ref(native), ref(native.existing_response)
    setattr(type(native), attribute, PropertyMock(side_effect=RuntimeError("Request metadata missing")))
    await finish(context, native)
    assert network.search() == []
    del native
    gc.collect()
    assert native_ref() is None and response_ref() is None
    await finish(context, request(body=b"next", asynchronous=asynchronous))
    assert [record.response.body for record in network.search()] == [b"next"]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_detach_ignores_removed_listener_errors_and_rejects_stale_callbacks(asynchronous):
    network, context = recorder(asynchronous=asynchronous)
    context.remove_listener = Mock(side_effect=RuntimeError("Context already closed"))
    network._detach(context)
    await finish(context, request(asynchronous=asynchronous))
    assert network.search() == [] and network.last_id == 0
    context.remove_listener.assert_any_call("requestfinished", context.listeners["requestfinished"][0])
    context.remove_listener.assert_any_call("close", context.listeners["close"][0])


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize(
    "body,expected,encoding",
    [
        ("café €".encode(), "café €", "utf-8"),
        (b"caf\xe9 \xa4", "café €", "iso-8859-15"),
        (b"\xc3\xa9", "é", "utf-8"),
    ],
)
async def test_saved_native_bytes_and_text_encoding_remain_valid_after_detach(asynchronous, body, expected, encoding):
    network, context = recorder(asynchronous=asynchronous)
    native = request(body=body, asynchronous=asynchronous)
    content_type = "text/plain; charset=iso-8859-15"
    native.existing_response.headers["content-type"] = content_type
    native.existing_response.all_headers.return_value = native.existing_response.headers.copy()
    await finish(context, native)
    network._detach()
    record = network.get(1)
    assert record is not None
    assert record.response.body == body
    assert record.response_headers["content-type"] == content_type
    assert record.response.encoding == encoding
    assert record.response.get_all_text().strip() == expected
    assert "body_note" not in record.response.meta
