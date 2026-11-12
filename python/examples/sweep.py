#!/usr/bin/env -S uv run
"""Sweep LEDs on from left to right, then off from left to right."""

from __future__ import annotations

import time

from traintrackr import Board, Led
from traintrackr.cli import parse_board_args
from traintrackr.client import default_board

CYCLE_S = 5.0
MIN_INTERVAL_S = 0.1


def main(host: str, board: str | None = None) -> None:
    board = Board(host, board if board is not None else default_board())
    x_max = board.x_max
    previous_start: float | None = None
    animation_started = time.perf_counter()

    def lit_at(led: Led, elapsed_s: float) -> bool:
        phase_t = elapsed_s % CYCLE_S
        if x_max <= 0:
            return phase_t < CYCLE_S / 2
        half = CYCLE_S / 2
        if phase_t < half:
            # Sweep on left → right.
            threshold = (phase_t / half) * x_max
            return led.x <= threshold
        # Sweep off left → right.
        threshold = ((phase_t - half) / half) * x_max
        return led.x > threshold

    def send_frame() -> None:
        nonlocal previous_start

        if previous_start is not None:
            wait_s = MIN_INTERVAL_S - (time.perf_counter() - previous_start)
            if wait_s > 0:
                time.sleep(wait_s)

        started = time.perf_counter()
        elapsed_s = started - animation_started

        def get_color(led: Led) -> tuple[int, int, int] | int:
            return (255, 255, 255) if lit_at(led, elapsed_s) else 0

        board.update(get_color)
        finished = time.perf_counter()
        request_ms = (finished - started) * 1000
        between_ms = (
            request_ms
            if previous_start is None
            else (started - previous_start) * 1000
        )
        lit = sum(1 for led in board.leds if lit_at(led, elapsed_s))
        print(
            f"{between_ms:.1f} ms since previous request  "
            f"({request_ms:.1f} ms HTTP, {lit} lit, t={elapsed_s % CYCLE_S:.2f}s)"
        )
        previous_start = started

    print(
        f"sweeping by x on {host} over {CYCLE_S:.0f}s cycles "
        f"at >= {MIN_INTERVAL_S * 1000:.0f} ms/frame (Ctrl+C to stop)"
    )
    try:
        while True:
            send_frame()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    args = parse_board_args(__doc__)
    main(args.host, args.board)
