#!/usr/bin/env -S uv run
"""Colour each LED from its position on the board."""

from __future__ import annotations

from traintrackr import Board, Led
from traintrackr.cli import parse_board_args
from traintrackr.client import default_board


def main(host: str, board: str | None = None, *, noise: bool = False) -> None:
    board = Board(host, board if board is not None else default_board())

    def get_color(led: Led) -> tuple[float, float, float]:
        return (led.x / board.x_max * 255, led.y / board.y_max * 255, 0)

    payload = board.update(get_color, add_noise=noise)
    print(board.frame_url(payload))
    print(f"sent {payload.count(',')} colours to {host}")


if __name__ == "__main__":
    args = parse_board_args(__doc__, noise=True)
    main(args.host, args.board, noise=args.noise)
