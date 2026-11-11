"""Load a Traintrackr board description and its LED map."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import yaml

KNOWN_COLOUR_SPACES = frozenset({"rgb565", "greyscale"})


@dataclass(frozen=True)
class Led:
    """One LED on a board, from a row of ``leds.csv``."""

    led: int
    station: str
    line: tuple[str, ...]
    naptan_id: str
    x: float
    y: float


@dataclass(frozen=True)
class BoardMap:
    """A named board: size, colour space, line palette, and LEDs."""

    id: str
    name: str
    colour_space: str
    x_max: float
    y_max: float
    lines: Mapping[str, tuple[int, int, int] | int]
    leds: tuple[Led, ...]

    def line_color(self, name: str) -> tuple[int, int, int] | int:
        """Return the palette colour for one line name.

        >>> from traintrackr.map import load_board
        >>> board = load_board("tfl6")
        >>> board.line_color("central")
        (227, 32, 23)
        >>> board.line_color("missing")
        Traceback (most recent call last):
        ...
        KeyError: 'missing'
        """
        return self.lines[name]


def find_board_dir(name: str | Path) -> Path:
    """Find a board directory by short name or by full path.

    A path that already contains ``board.yaml`` is used as-is. Otherwise
    ``name`` is treated as a board id: prefer a copy next to this module
    (the pip-installed layout), then walk up looking for ``boards/<name>``.
    """
    path = Path(name)
    if (path / "board.yaml").is_file():
        return path.resolve()

    board_id = str(name)
    packaged = Path(__file__).resolve().parent / "boards" / board_id
    candidates = [packaged]
    for parent in Path(__file__).resolve().parents:
        candidates.append(parent / "boards" / board_id)

    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen:
            continue
        seen.add(candidate)
        if (candidate / "board.yaml").is_file():
            return candidate

    raise FileNotFoundError(
        f"board {name!r} not found under a boards/ directory"
    )


def load_board(name: str | Path = "tfl6") -> BoardMap:
    """Load a board by short name or by path to a board directory."""
    board_dir = find_board_dir(name)
    board_id = board_dir.name
    with (board_dir / "board.yaml").open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, dict):
        raise ValueError(f"{board_dir / 'board.yaml'} must be a mapping")

    try:
        display_name = raw["name"]
        colour_space = raw["colour_space"]
        x_max = float(raw["x_max"])
        y_max = float(raw["y_max"])
        map_name = raw["map"]
        lines_raw = raw["lines"]
    except KeyError as error:
        raise ValueError(
            f"{board_dir / 'board.yaml'} is missing {error.args[0]!r}"
        ) from error

    if colour_space not in KNOWN_COLOUR_SPACES:
        known = ", ".join(sorted(KNOWN_COLOUR_SPACES))
        raise ValueError(
            f"unknown colour_space {colour_space!r}; expected one of {known}"
        )
    if not isinstance(lines_raw, dict) or not lines_raw:
        raise ValueError("lines must be a non-empty mapping")

    lines = {
        str(line_name): _parse_line_color(line_name, color, colour_space)
        for line_name, color in lines_raw.items()
    }

    map_path = board_dir / map_name
    if not map_path.is_file():
        raise FileNotFoundError(f"map file not found: {map_path}")

    leds = _load_leds(map_path, lines)
    return BoardMap(
        id=board_id,
        name=str(display_name),
        colour_space=colour_space,
        x_max=x_max,
        y_max=y_max,
        lines=lines,
        leds=leds,
    )


def _parse_line_color(
    line_name: str,
    color: object,
    colour_space: str,
) -> tuple[int, int, int] | int:
    if colour_space == "greyscale":
        if isinstance(color, bool) or not isinstance(color, (int, float)):
            raise ValueError(
                f"line {line_name!r} must be a brightness for greyscale"
            )
        return max(0, min(255, round(color)))

    if not isinstance(color, (list, tuple)) or len(color) != 3:
        raise ValueError(
            f"line {line_name!r} must be an RGB triple for {colour_space}"
        )
    return tuple(max(0, min(255, round(channel))) for channel in color)


def _load_leds(
    map_path: Path,
    lines: Mapping[str, tuple[int, int, int] | int],
) -> tuple[Led, ...]:
    with map_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected = {
            "led",
            "station",
            "lines",
            "naptan_id",
            "x_mm",
            "y_mm_from_top",
        }
        if reader.fieldnames is None or set(reader.fieldnames) != expected:
            raise ValueError(
                f"{map_path} must have columns {', '.join(sorted(expected))}"
            )

        leds: list[Led] = []
        for row in reader:
            line = tuple(part for part in row["lines"].split() if part)
            if not line:
                raise ValueError(
                    f"{map_path} LED {row['led']} has no line names"
                )
            missing = [name for name in line if name not in lines]
            if missing:
                raise ValueError(
                    f"{map_path} LED {row['led']} uses unknown line "
                    f"{missing[0]!r}"
                )
            leds.append(
                Led(
                    led=int(row["led"]),
                    station=row["station"],
                    line=line,
                    naptan_id=row["naptan_id"],
                    x=float(row["x_mm"]),
                    y=float(row["y_mm_from_top"]),
                )
            )

    if not leds:
        raise ValueError(f"{map_path} has no LED rows")

    numbers = [led.led for led in leds]
    if numbers != list(range(1, len(leds) + 1)):
        raise ValueError(
            f"{map_path} LED numbers must be 1 through {len(leds)} with no gaps"
        )
    return tuple(leds)
