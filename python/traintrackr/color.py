"""RGB565 colour conversion for a pixels-v5 frame.

Channels are 8-bit, from 0 to 255. RGB565 keeps 5 bits of red, 6 of green,
and 5 of blue. The hex form drops leading zeros, and black is ``0``.
"""

from __future__ import annotations


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


def rgb_to_rgb565(red: float, green: float, blue: float) -> str:
    """Encode an 8-bit RGB colour as an RGB565 hex string.

    Full red, green, blue, and white match the LAN guide. Orange uses the
    guide's 5-6-5 example: red 31, green 32, and blue 0, which is 8-bit
    ``(248, 128, 0)``.

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
    >>> rgb_to_rgb565(248, 128, 0)
    'fc00'
    """
    red = clamp_channel(red)
    green = clamp_channel(green)
    blue = clamp_channel(blue)
    value = ((red >> 3) << 11) | ((green >> 2) << 5) | (blue >> 3)
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


def encode_rgb565(color: tuple[float, float, float] | list[float] | float) -> str:
    """Encode one callback colour as an RGB565 hex value.

    A single number is black-and-white brightness. ``128`` is the grey
    ``(128, 128, 128)``.

    >>> encode_rgb565((255, 0, 0))
    'f800'
    >>> encode_rgb565(255)
    'ffff'
    >>> encode_rgb565(128)
    '8410'
    >>> encode_rgb565(0)
    '0'
    """
    red, green, blue = normalise_color(color)
    return rgb_to_rgb565(red, green, blue)
