#!/usr/bin/env -S uv run
"""Colour each LED with its first line's palette colour."""

from __future__ import annotations

import argparse

from traintrackr import Board, Led
from traintrackr.client import BOARD_ENV, HOST_ENV, default_board, default_host


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "host",
        nargs="?",
        default=default_host(),
        help=f"board hostname or IP (or set {HOST_ENV})",
    )
    parser.add_argument(
        "--board",
        default=default_board(),
        help=f"board id or path (default: {default_board()}, or set {BOARD_ENV})",
    )
    parser.add_argument(
        "--noise",
        action="store_true",
        help="dither colours that fall between RGB565 levels",
    )
    args = parser.parse_args()
    if not args.host:
        parser.error(f"host is required (pass it or set {HOST_ENV})")

    board = Board(args.host, args.board)

    def get_color(led: Led) -> tuple[float, float, float] | int:
        return board.line_color(led.line[0])

    payload = board.update(get_color, add_noise=args.noise)
    print(f"sent {payload.count(',')} colours to {args.host}")


if __name__ == "__main__":
    main()
