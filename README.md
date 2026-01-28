# simple-scan-MVP

A single-file barcode scanner script for Windows 11 that uses your webcam to scan common 1D/2D barcodes, copies the scanned value to the clipboard, and shows a GUI with scan history.

## Features
- Auto-selects the default webcam, with an option to choose another camera.
- Scans common 1D/2D barcode types via `pyzbar`.
- Copies every scan to the clipboard (manual paste).
- Shows barcode type + scan history with timestamps.
- Draws a bounding box around detected barcodes.
- Beep, on-screen, and console feedback on every scan.

## Install
```bash
pip install opencv-python pyzbar pillow pyperclip
```

> **Note for Windows:** `pyzbar` depends on the ZBar library. If you see an error like `Unable to find zbar`, install the ZBar DLL and make sure it is on your PATH. Many users grab the Windows ZBar binary from the ZBar releases page and place the DLL next to `barcode_scanner.py`.

## Run
```bash
python barcode_scanner.py
```

## Usage tips
- Use the **Cooldown (seconds)** control to avoid repeated rapid scans.
- The scan history table supports selecting a row and clicking **Copy Selected**.
- If multiple webcams are connected, pick a camera from the **Camera** dropdown.
