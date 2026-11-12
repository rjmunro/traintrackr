# Traintrackr device setup guide

Ensure your board is on firmware **3.1.21** or later. You can check this on the device page of the Traintrackr website.

## Turn on LAN access

1. Put your board into setup mode (press the setup button so all LEDs come on).
2. Connect to the board's Wi‑Fi (`traintrackr`).
3. Go to [http://192.168.4.1](http://192.168.4.1) and click **Configure Wi‑Fi**.
4. Enter your Wi‑Fi network and password.
5. Do not change Access Key, layout ID, or environment ID.
6. Change **Enable LAN** to `1`, save, and wait for the board to reconnect to your home Wi‑Fi.
7. Find the board's IP address on your home network (router device list, or your usual network tools).

## Point this repo at the board

Copy the shared env template and set the host and board type:

```bash
cp .env.example .env
```

```bash
TRAINTRACKR_HOST=192.168.1.50
TRAINTRACKR_BOARD=tfl6
```

Replace `192.168.1.50` with the IP from step 7. Set `TRAINTRACKR_BOARD` to your board type (SKU), for example `tfl6`.

## Check that it works

On the same Wi‑Fi as the board, open this in a browser (or any GET client). LED 1 should go red, LED 2 off, LED 3 green, LED 4 blue:

```
http://<board IP>/send-data?data=pixels-v5,f800,0,7e0,1f
```

Or from the Python package:

```bash
cd python
./examples/lines.py
```

`uv` installs the project environment the first time the script runs.

The frame format is described in [traintrackr-LAN-Guide.md](traintrackr-LAN-Guide.md). To try the same API without hardware, run the [simulator](sim/README.md) and set `TRAINTRACKR_HOST=127.0.0.1:8765`.
