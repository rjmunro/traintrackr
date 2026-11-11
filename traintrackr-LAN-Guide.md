# Sending a frame over your local network

**Technical guide** · Using pixels-v5 format

> Before you start: LAN access must be turned on in the board's settings (alternate setup).

## Send it

Open this address in a browser on the same WiFi network, or send it with any GET request:

```
http://<board IP>/send-data?data=pixels-v5,f800,0,7e0,1f
```

Replace `<board IP>` with the board's address on your network, for example `192.168.1.50`.

## The data

The word `pixels-v5`, then one colour value per LED, all separated by commas:

```
pixels-v5,colour1,colour2,colour3,...
```

- Position is the LED number. The 1st value after `pixels-v5` is LED 1, the 2nd is LED 2, and so on. The LED numbering for your board (which number is which LED) is shown on your board's schematic.
- Each value is a colour in RGB565, written as 1 to 4 hex digits.
  - `0` means off.
  - Leading zeros can be dropped, so `07e0` and `7e0` are the same.
- To leave an LED off, put `0` in its place. Don't leave an empty gap (`,,`) or end with a comma.
- Shorter frames are allowed. If the data stops early, for example after 50 values, only LEDs 1 to 50 change.
- No spaces or line breaks. The whole thing must be one unbroken line in the address.

## Example

LED 1 red, LED 2 off, LED 3 green, LED 4 blue:

```
http://192.168.1.50/send-data?data=pixels-v5,f800,0,7e0,1f
```

## Common colours

| Colour | Full brightness | Half brightness |
| --- | --- | --- |
| Red | `f800` | `7800` |
| Green | `7e0` | `3e0` |
| Blue | `1f` | `f` |
| White | `ffff` | `7bef` |
| Yellow | `ffe0` | `7be0` |
| Orange | `fc00` | `7a00` |
| Cyan | `7ff` | `3ef` |
| Magenta / pink | `f81f` | `780f` |
| Purple | `801f` | `400f` |
| Off | `0` | |

## Making your own colour

RGB565 squeezes a normal colour into 16 bits:

| Channel | Range | Bits |
| --- | --- | --- |
| Red | 0–31 | 5 bits |
| Green | 0–63 | 6 bits |
| Blue | 0–31 | 5 bits |

The value is `(red × 2048) + (green × 32) + blue`, written in hex. For example, red 31, green 32, blue 0 gives 63,488 + 1,024 + 0 = 64,512, which is `fc00` (orange).

Most online "RGB565 converters" will turn a normal `#rrggbb` colour into this for you.

---

traintrackr · Technical guide · pixels-v5 over LAN
