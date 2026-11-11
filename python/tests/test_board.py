"""Board rendering, frame encoding, and HTTP send."""

from __future__ import annotations

from io import BytesIO
from urllib.error import HTTPError, URLError

import pytest

from traintrackr import Board, encode_frame


def test_encode_frame_guide_example():
    payload = encode_frame([(255, 0, 0), 0, (0, 255, 0), (0, 0, 255)])
    assert payload == "pixels-v5,f800,0,7e0,1f"
    assert " " not in payload


def test_encode_frame_brightness_and_length():
    board = Board("192.168.1.50", "tfl6")
    colors = board.render(lambda led: led.y / board.y_max * 255)
    payload = board.encode_frame(colors)
    assert payload.startswith("pixels-v5,")
    assert " " not in payload
    assert "\n" not in payload
    assert len(payload.split(",")) == 374  # prefix + 373 LEDs


def test_render_line_colors():
    board = Board("127.0.0.1", "tfl6")
    colors = board.render(lambda led: board.line_color(led.line[0]))
    amersham = next(led for led in board.leds if led.station == "Amersham")
    assert colors[amersham.led - 1] == board.line_color("metropolitan")


def test_send_uses_get_and_keeps_commas(monkeypatch):
    board = Board("192.168.1.50", "tfl6")
    seen: dict[str, object] = {}

    class FakeResponse(BytesIO):
        status = 200
        reason = "OK"
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout=None):
        seen["url"] = request.full_url
        seen["method"] = request.get_method()
        seen["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr("traintrackr.client.urlopen", fake_urlopen)
    payload = "pixels-v5,f800,0,7e0,1f"
    board.send(payload)
    assert seen["method"] == "GET"
    assert seen["timeout"] == board.timeout
    assert seen["url"] == "http://192.168.1.50/send-data?data=pixels-v5,f800,0,7e0,1f"


def test_update_renders_encodes_and_sends(monkeypatch):
    board = Board("10.0.0.8", "tfl6")
    sent: list[str] = []

    class FakeResponse(BytesIO):
        status = 200
        reason = "OK"
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout=None):
        sent.append(request.full_url)
        return FakeResponse()

    monkeypatch.setattr("traintrackr.client.urlopen", fake_urlopen)
    payload = board.update(lambda led: (255, 0, 0) if led.led == 1 else 0)
    assert payload.startswith("pixels-v5,f800,")
    assert payload.endswith(",0")
    assert len(payload.split(",")) == 374
    assert sent == [f"http://10.0.0.8/send-data?data={payload}"]


def test_send_http_error(monkeypatch):
    board = Board("192.168.1.50", "tfl6")

    def fake_urlopen(request, timeout=None):
        raise HTTPError(
            request.full_url,
            500,
            "Server Error",
            hdrs=None,
            fp=None,
        )

    monkeypatch.setattr("traintrackr.client.urlopen", fake_urlopen)
    with pytest.raises(HTTPError):
        board.send("pixels-v5,0")


def test_send_connection_error(monkeypatch):
    board = Board("192.168.1.50", "tfl6")

    def fake_urlopen(request, timeout=None):
        raise URLError("timed out")

    monkeypatch.setattr("traintrackr.client.urlopen", fake_urlopen)
    with pytest.raises(ConnectionError, match="192.168.1.50"):
        board.send("pixels-v5,0")
