"""Colour each LED from its position on the board."""

from __future__ import annotations

import argparse

from traintrackr import Board, Led


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", help="board hostname or IP address")
    parser.add_argument(
        "--board",
        default="tfl6",
        help="board id or path to a board directory (default: tfl6)",
    )
    parser.add_argument(
        "--noise",
        action="store_true",
        help="dither colours that fall between RGB565 levels",
    )
    args = parser.parse_args()

    board = Board(args.host, args.board)

    def get_color(led: Led) -> tuple[float, float, float]:
        return (led.x / board.x_max * 255, led.y / board.y_max * 255, 0)

    payload = board.update(get_color, add_noise=args.noise)
    print(f"sent {payload.count(',')} colours to {args.host}")


if __name__ == "__main__":
    main()
