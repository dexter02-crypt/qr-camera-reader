# Design

The core calls OpenCV `detectAndDecodeMulti`, accepts finite in-frame quadrilaterals and nonempty decoded values, bounds result/payload sizes, and displays escaped previews. It never passes payload data to a shell, network client, browser or interpreter. The fixture is generated with the build-time `qrcode` library, not a runtime dependency. Actual decoding is tested on the fixture. The session deduplicator is separate from the native decoder so its capacity/reset behavior is directly testable.

Local image/metadata export is explicit and no-overwrite. Camera access is limited to a local integer device index. Independent core functions allow image processing to be tested without opening a device.
