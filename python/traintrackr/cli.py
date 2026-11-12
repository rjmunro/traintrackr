"""Shared CLI helpers for the example scripts."""

from __future__ import annotations

import argparse
from dataclasses import dataclass

from traintrackr.client import BOARD_ENV, HOST_ENV, default_board, default_host


@dataclass(frozen=True)
class BoardArgs:
    host: str
    board: str
    noise: bool = False


def parse_board_args(
    description: str | None = None,
    *,
    noise: bool = False,
) -> BoardArgs:
    """Parse host/board (and optional ``--noise``) from argv and the environment."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "host",
        nargs="?",
        default=default_host(),
        help=f"board hostname or IP (or set {HOST_ENV})",
    )
    parser.add_argument(
        "--board",
        default=default_board(),
        help=f"board type or path (default: {default_board()}, or set {BOARD_ENV})",
    )
    if noise:
        parser.add_argument(
            "--noise",
            action="store_true",
            help="dither colours that fall between RGB565 levels",
        )
    args = parser.parse_args()
    if not args.host:
        parser.error(f"host is required (pass it or set {HOST_ENV})")
    return BoardArgs(
        host=args.host,
        board=args.board,
        noise=bool(getattr(args, "noise", False)),
    )
