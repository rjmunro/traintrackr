# Boards

Each board is a folder. The folder name is the id a library loads, for example `tfl6`.

```
boards/tfl6/leds.csv
boards/tfl6/board.yaml
```

The CSV is the LED table. The YAML describes the board and names the CSV. The rows are not copied into the YAML. Add another board by adding another folder with these two files. A new colour space is the only change that needs library code.

## leds.csv

The header is:

```
led,station,lines,naptan_id,x_mm,y_mm_from_top
```

- `led` is the LED number. `1` is the first value in a frame. Numbers are unique. `tfl6` uses 1 through 373 with no gaps.
- `station` is the name drawn for that LED.
- `lines` is one or more line names, separated by spaces. `district hammersmith-city` is District and Hammersmith & City. The first name is the default line colour.
- `naptan_id` is the stop code. London uses a NaPTAN id. Another city puts its own stop id in this column.
- `x_mm` and `y_mm_from_top` are the position in millimetres from the top-left. `y` grows downward. A value may be fractional.

One station can be two LEDs. Those LEDs share a stop id, and the second name can describe the branch. On `tfl6`, LED 167 `Euston` and LED 231 `Euston (via Charing Cross)` both use `940GZZLUEUS`. LED 172 `Kennington` and LED 314 `Kennington (via Charing Cross / to Battersea)` both use `940GZZLUKNG`.

## board.yaml

```yaml
name: London Underground
colour_space: rgb565
x_max: 385
y_max: 282
map: leds.csv
lines:
  bakerloo: [179, 99, 5] # B36305
  northern: [255, 255, 255]
```

- `name` is the label for the board.
- `colour_space` selects how a colour becomes wire data.
  - `rgb565` is the `pixels-v5` format in the LAN guide. A palette entry is `[red, green, blue]`, each channel 0–255. A callback can return that kind of tuple, or a single brightness. A brightness `n` is sent as the grey `(n, n, n)`.
  - `greyscale` is for a board that only has brightness. A palette entry is then one number from 0–255, and a callback number is that brightness directly.
- `x_max` and `y_max` are the board's coordinate space, in the same units as the CSV. They are not recomputed from the rows. `tfl6` is 385 by 282.
- `map` is the CSV filename in this folder.
- `lines` is the palette, keyed by the names used in the CSV. Every name in the CSV has an entry. Northern is white on `tfl6` so those LEDs show; the printed colour is black.

`rgb565` values in the guide: full red is `f800`, green is `7e0`, blue is `1f`, white is `ffff`, and off is `0`.
