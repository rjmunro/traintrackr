"""RGB565 colour conversion for a pixels-v5 frame.

Channels are 8-bit, from 0 to 255. RGB565 keeps 5 bits of red, 6 of green,
and 5 of blue. The hex form drops leading zeros, and black is ``0``.

Each channel is scaled across the full 0–255 range onto its code range, so
255 is the only exact white. By default the scaled value is rounded to the
nearest code. ``add_noise`` uses a random fraction instead, so an
in-between value can land on either neighbouring colour.
"""

from __future__ import annotations

import math
import random


def clamp_channel(value: float) -> int:
    """Round a channel into the range 0 to 255.

    >>> clamp_channel(128.4)
    128
    >>> clamp_channel(-3)
    0
    >>> clamp_channel(300)
    255
    """
    return max(0, min(255, round(value)))


def quantize_channel(value: float, levels: int, roll: float = 0.5) -> int:
    """Scale one channel onto ``levels`` codes, from 0 to ``levels - 1``.

    Red and blue use 32 levels. Green uses 64. ``roll`` is a fraction in
    ``[0, 1)``. The default ``0.5`` rounds to the nearest code. A random
    roll makes the chance of the higher code equal the fractional part of
    the scaled value. Exact codes such as 0 and 255 stay put for every
    roll.

    >>> quantize_channel(0, 32)
    0
    >>> quantize_channel(255, 32)
    31
    >>> quantize_channel(255, 32, 0.0)
    31
    >>> quantize_channel(255, 32, 0.999)
    31
    >>> quantize_channel(249, 32)
    30
    >>> quantize_channel(249, 32, 0.72)
    30
    >>> quantize_channel(249, 32, 0.73)
    31
    >>> quantize_channel(128, 32)
    16
    >>> quantize_channel(128, 64)
    32
    >>> quantize_channel(85, 64)
    21
    """
    if not 0.0 <= roll < 1.0:
        raise ValueError("roll must be from 0.0 up to but not including 1.0")
    scaled = clamp_channel(value) * (levels - 1) / 255
    return min(levels - 1, math.floor(scaled + roll))


def rgb_to_rgb565(
    red: float,
    green: float,
    blue: float,
    *,
    add_noise: bool = False,
) -> str:
    """Encode an 8-bit RGB colour as an RGB565 hex string.

    Full red, green, blue, and white match the LAN guide. The guide's
    orange ``fc00`` is the 5-6-5 value for red 31, green 32, and blue 0,
    which is 8-bit ``(255, 128, 0)`` after scaling.

    With ``add_noise``, each channel uses a random fraction instead of
    rounding to nearest. Exact ends such as black and white do not change.

    >>> rgb_to_rgb565(255, 0, 0)
    'f800'
    >>> rgb_to_rgb565(0, 255, 0)
    '7e0'
    >>> rgb_to_rgb565(0, 0, 255)
    '1f'
    >>> rgb_to_rgb565(255, 255, 255)
    'ffff'
    >>> rgb_to_rgb565(0, 0, 0)
    '0'
    >>> rgb_to_rgb565(255, 128, 0)
    'fc00'
    >>> rgb_to_rgb565(249, 253, 249)
    'f7fe'
    >>> rgb_to_rgb565(255, 255, 255, add_noise=True)
    'ffff'
    >>> rgb_to_rgb565(0, 0, 0, add_noise=True)
    '0'
    """
    if add_noise:
        red_roll = random.random()
        green_roll = random.random()
        blue_roll = random.random()
    else:
        red_roll = green_roll = blue_roll = 0.5
    red = quantize_channel(red, 32, red_roll)
    green = quantize_channel(green, 64, green_roll)
    blue = quantize_channel(blue, 32, blue_roll)
    value = (red << 11) | (green << 5) | blue
    return format(value, "x")


def normalise_color(
    color: tuple[float, float, float] | list[float] | float,
) -> tuple[int, int, int]:
    """Turn a callback result into an 8-bit RGB triple.

    A single number is black-and-white brightness: ``n`` becomes ``(n, n, n)``.

    >>> normalise_color(128)
    (128, 128, 128)
    >>> normalise_color((255, 0, 0))
    (255, 0, 0)
    >>> normalise_color([0, 255, 0])
    (0, 255, 0)
    >>> normalise_color(255.2)
    (255, 255, 255)
    >>> normalise_color((1, 2))
    Traceback (most recent call last):
    ...
    TypeError: a colour must be an RGB triple or a brightness
    >>> normalise_color("red")
    Traceback (most recent call last):
    ...
    TypeError: a colour must be an RGB triple or a brightness
    """
    if isinstance(color, bool) or isinstance(color, str):
        raise TypeError("a colour must be an RGB triple or a brightness")
    if isinstance(color, (int, float)):
        level = clamp_channel(color)
        return (level, level, level)
    if isinstance(color, (tuple, list)) and len(color) == 3:
        return (
            clamp_channel(color[0]),
            clamp_channel(color[1]),
            clamp_channel(color[2]),
        )
    raise TypeError("a colour must be an RGB triple or a brightness")


def encode_rgb565(
    color: tuple[float, float, float] | list[float] | float,
    *,
    add_noise: bool = False,
) -> str:
    """Encode one callback colour as an RGB565 hex value.

    A single number is black-and-white brightness. ``128`` is the grey
    ``(128, 128, 128)``, which rounds to ``8410``. ``add_noise`` dithers
    channels that fall between two RGB565 levels.

    >>> encode_rgb565((255, 0, 0))
    'f800'
    >>> encode_rgb565(255)
    'ffff'
    >>> encode_rgb565(128)
    '8410'
    >>> encode_rgb565(0)
    '0'
    >>> encode_rgb565((249, 253, 249))
    'f7fe'
    """
    red, green, blue = normalise_color(color)
    return rgb_to_rgb565(red, green, blue, add_noise=add_noise)
