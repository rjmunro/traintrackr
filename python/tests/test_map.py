"""Load the shared tfl6 board description."""

from __future__ import annotations

from traintrackr import load_board


def test_tfl6_profile():
    board = load_board("tfl6")
    assert board.id == "tfl6"
    assert board.name == "London Underground"
    assert board.colour_space == "rgb565"
    assert board.x_max == 385
    assert board.y_max == 282


def test_tfl6_led_count_and_order():
    board = load_board("tfl6")
    assert len(board.leds) == 373
    assert [led.led for led in board.leds] == list(range(1, 374))


def test_tfl6_every_led_has_line_and_naptan():
    board = load_board("tfl6")
    for led in board.leds:
        assert led.line
        assert led.naptan_id
        assert all(name in board.lines for name in led.line)


def test_tfl6_line_palette():
    board = load_board("tfl6")
    assert board.line_color("bakerloo") == (179, 99, 5)
    assert board.line_color("central") == (227, 32, 23)
    assert board.line_color("northern") == (255, 255, 255)
    assert board.line_color("elizabeth") == (105, 80, 161)
    assert set(board.lines) == {
        "bakerloo",
        "central",
        "circle",
        "district",
        "hammersmith-city",
        "jubilee",
        "metropolitan",
        "northern",
        "piccadilly",
        "victoria",
        "waterloo-city",
        "dlr",
        "elizabeth",
    }


def test_tfl6_shared_naptans():
    board = load_board("tfl6")
    by_naptan: dict[str, list] = {}
    for led in board.leds:
        by_naptan.setdefault(led.naptan_id, []).append(led)

    euston = by_naptan["940GZZLUEUS"]
    assert {led.led for led in euston} == {167, 231}
    assert {led.station for led in euston} == {
        "Euston",
        "Euston (via Charing Cross)",
    }

    kennington = by_naptan["940GZZLUKNG"]
    assert {led.led for led in kennington} == {172, 314}
    assert {led.station for led in kennington} == {
        "Kennington",
        "Kennington (via Charing Cross / to Battersea)",
    }


def test_tfl6_fields_from_csv():
    board = load_board("tfl6")
    first = board.leds[0]
    assert first.station == "Amersham"
    assert first.line == ("metropolitan",)
    assert first.naptan_id == "940GZZLUAMS"
    assert first.x == 42
    assert first.y == 35

    multi = next(led for led in board.leds if led.led == 90)
    assert multi.station == "Liverpool Street"
    assert multi.line == (
        "central",
        "circle",
        "hammersmith-city",
        "metropolitan",
    )
