"""Talk to a Traintrackr board over the local network."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import TypeAlias
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from traintrackr.color import encode_frame, normalise_color
from traintrackr.map import BoardMap, Led, load_board

HOST_ENV = "TRAINTRACKR_HOST"
BOARD_ENV = "TRAINTRACKR_BOARD"

ColorValue: TypeAlias = tuple[float, float, float] | list[float] | float
GetColor: TypeAlias = Callable[[Led], ColorValue]

_dotenv_loaded = False


def find_env_file() -> Path | None:
    """Find the shared repo-root ``.env`` file."""
    candidates: list[Path] = [Path.cwd() / ".env"]
    for parent in Path(__file__).resolve().parents:
        candidates.append(parent / ".env")

    seen: set[Path] = set()
    for path in candidates:
        path = path.resolve()
        if path in seen:
            continue
        seen.add(path)
        if path.is_file():
            return path
    return None


def load_dotenv(path: Path | None = None) -> Path | None:
    """Load ``KEY=VALUE`` pairs from ``.env`` without overriding real env vars.

    The file at the repository root is shared by every language. Returns the
    path that was read, or ``None`` if none was found.
    """
    global _dotenv_loaded
    env_path = path if path is not None else find_env_file()
    if env_path is None:
        _dotenv_loaded = True
        return None

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value

    _dotenv_loaded = True
    return env_path


def _ensure_dotenv() -> None:
    if not _dotenv_loaded:
        load_dotenv()


def default_host() -> str | None:
    """Return ``TRAINTRACKR_HOST``, or ``None`` if it is unset."""
    _ensure_dotenv()
    value = os.environ.get(HOST_ENV, "").strip()
    return value or None


def default_board() -> str:
    """Return ``TRAINTRACKR_BOARD``, or ``tfl6`` if it is unset."""
    _ensure_dotenv()
    value = os.environ.get(BOARD_ENV, "").strip()
    return value or "tfl6"


class Board:
    """A named LED map plus the host that displays it."""

    def __init__(
        self,
        host: str | None = None,
        name: str | Path | None = None,
        *,
        timeout: float = 10.0,
    ) -> None:
        resolved_host = host if host is not None else default_host()
        if not resolved_host:
            raise ValueError(
                f"host is required (pass it or set {HOST_ENV})"
            )
        resolved_name: str | Path = (
            name if name is not None else default_board()
        )
        self.host = resolved_host.rstrip("/")
        if "://" in self.host:
            raise ValueError("host should be a hostname or IP, not a URL")
        self._map = load_board(resolved_name)
        self.timeout = timeout

    @property
    def id(self) -> str:
        return self._map.id

    @property
    def name(self) -> str:
        return self._map.name

    @property
    def colour_space(self) -> str:
        return self._map.colour_space

    @property
    def x_max(self) -> float:
        return self._map.x_max

    @property
    def y_max(self) -> float:
        return self._map.y_max

    @property
    def leds(self) -> tuple[Led, ...]:
        return self._map.leds

    @property
    def map(self) -> BoardMap:
        return self._map

    def line_color(self, name: str) -> tuple[int, int, int] | int:
        """Return the palette colour for one line name."""
        return self._map.line_color(name)

    def render(self, get_color: GetColor) -> list[tuple[int, int, int]]:
        """Call ``get_color`` once per LED and normalise each result."""
        return [normalise_color(get_color(led)) for led in self.leds]

    def encode_frame(
        self,
        colors: list[ColorValue] | tuple[ColorValue, ...],
        *,
        add_noise: bool = False,
    ) -> str:
        """Encode colours with this board's colour space."""
        return encode_frame(
            colors,
            colour_space=self.colour_space,
            add_noise=add_noise,
        )

    def send(self, payload: str) -> None:
        """Send a ``pixels-v5`` payload with a GET request."""
        # Commas must stay literal in the query string.
        url = f"http://{self.host}/send-data?data={quote(payload, safe=',')}"
        request = Request(url, method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                if getattr(response, "status", 200) >= 400:
                    raise HTTPError(
                        url,
                        response.status,
                        getattr(response, "reason", ""),
                        response.headers,
                        None,
                    )
        except HTTPError:
            raise
        except URLError as error:
            raise ConnectionError(
                f"could not reach board at {self.host!r}: {error.reason}"
            ) from error

    def update(self, get_color: GetColor, *, add_noise: bool = False) -> str:
        """Render, encode, and send one frame. Return the payload sent."""
        colors = self.render(get_color)
        payload = self.encode_frame(colors, add_noise=add_noise)
        self.send(payload)
        return payload
