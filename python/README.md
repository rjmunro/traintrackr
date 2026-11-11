# traintrackr

Python library for painting a Traintrackr board. You write a function that colours one LED. The library loads that board's map, calls the function once per LED, and sends the frame over the local network.

Turn LAN access on in the board's settings first. The wire format is described in [the LAN guide](../traintrackr-LAN-Guide.md).

## Colour one frame

```python
from traintrackr import Board, Led

board = Board("192.168.1.50", "tfl6")

def get_color(led: Led) -> tuple[float, float, float]:
    return (led.x / board.x_max * 255, led.y / board.y_max * 255, 0)

board.update(get_color)
```

`Board(host, name="tfl6")` loads `boards/<name>/`. The name defaults to `tfl6`. Pass a full path to a board directory instead when the map is not in the shared `boards/` tree.

If you omit them, `Board` reads `TRAINTRACKR_HOST` and `TRAINTRACKR_BOARD` from the environment:

```bash
export TRAINTRACKR_HOST=192.168.1.50
export TRAINTRACKR_BOARD=tfl6
```

```python
board = Board()  # uses the environment
```

### The LED

| Field | Meaning |
| --- | --- |
| `led` | LED number. `1` is the first value in the frame. |
| `station` | Station name. |
| `line` | Tuple of line names. `led.line[0]` is the usual choice. |
| `naptan_id` | Stop code. Two LEDs can share one when a station is drawn twice. |
| `x`, `y` | Position in millimetres. `y` is measured from the top. |

### What to return

Return an RGB tuple, each channel 0–255, or a single number for black-and-white brightness. Floats are rounded and clamped.

On an `rgb565` board a number `n` is sent as the grey `(n, n, n)`. `0` and `(0, 0, 0)` turn the LED off. Every LED needs a value; the frame cannot leave a gap in the middle. One frame can mix tuples and numbers.

Line colours come from the board description:

```python
def get_color(led: Led) -> tuple[float, float, float]:
    return board.line_color(led.line[0])
```

Brightness from position:

```python
def get_color(led: Led) -> float:
    return led.y / board.y_max * 255
```

`board.x_max`, `board.y_max`, and `board.line_color` belong to the loaded board. An unknown line name raises `KeyError`.

## Sending

`update` renders, encodes, and sends. The steps are also available on their own:

- `render(get_color)` returns one `(r, g, b)` per LED, in LED order. A brightness number is expanded first.
- `encode_frame(colors)` returns the `pixels-v5,...` payload for an `rgb565` board.
- `send(payload)` requests `http://<host>/send-data?data=...`.

For `rgb565`, full red `(255, 0, 0)` is `f800`, green `7e0`, blue `1f`, and white `ffff`. A brightness of `128` is `8410`.

## Examples

```bash
python examples/gradient.py 192.168.1.50
python examples/lines.py 192.168.1.50
```

Both take a board host, or read `TRAINTRACKR_HOST` if you omit it. Pass `--board` for another board id or path (or set `TRAINTRACKR_BOARD`), and `--noise` to dither.

## Board data

Maps, sizes, colour spaces, and palettes live in [`../boards`](../boards/README.md). `tfl6` uses `colour_space: rgb565`. A later greyscale board would use `colour_space: greyscale`, and its palette entries would be single brightness numbers.
