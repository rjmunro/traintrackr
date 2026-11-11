# Traintrackr

Code for drawing frames on Traintrackr LED boards and sending them over the local network.

The frame format is described in [traintrackr-LAN-Guide.md](traintrackr-LAN-Guide.md). Turn LAN access on in the board's settings before sending.

## Repository

- [boards/](boards/README.md) holds one folder per board. Each folder has the LED map and a description of that board's size, colour space, and line colours. Every language reads this data.
- [python/](python/README.md) is the Python library. A callback returns a colour for each LED, and the library sends the frame.

Node and other languages will use the same `boards/` data.
