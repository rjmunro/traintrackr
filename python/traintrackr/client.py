"""Talk to a Traintrackr board over the local network."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TypeAlias
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from traintrackr.color import encode_frame, normalise_color
from traintrackr.map import BoardMap, Led, load_board

ColorValue: TypeAlias = tuple[float, float, float] | list[float] | float
GetColor: TypeAlias = Callable[[Led], ColorValue]


class Board:
    """A named LED map plus the host that displays it."""

    def __init__(
        self,
        host: str,
        name: str | Path = "tfl6",
        *,
        timeout: float = 10.0,
    ) -> None:
        self.host = host.rstrip("/")
        if "://" in self.host:
            raise ValueError("host should be a hostname or IP, not a URL")
        self._map = load_board(name)
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
