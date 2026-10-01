# qr-camera-reader 0.1.0

QR Camera Reader is a small local OpenCV utility for decoding QR codes from trusted images and live camera frames.

Decoded links and messages are displayed as data only. The application does not automatically open URLs, execute decoded payloads, upload camera frames, or record live sessions.

## Highlights

- Detects and decodes multiple QR codes in one image or frame.
- Draws QR boundaries and displays escaped payload previews.
- Caps per-frame results at 32.
- Caps complete decoded payloads at 2,048 characters.
- Uses a bounded 512-entry in-memory unique-payload session set.
- Explicit image/demo commands can export PNG and JSON results without overwriting existing files.
- Camera mode does not write video, decoded payloads, or session counters to disk.

## Existing public validation

Public `main` commit `c96be3e3e29cd6b4122031c5b0e6a1aa75d77024` passed GitHub Actions run `36765698334`.

That historical workflow contained one hosted job:

- Ubuntu / Python 3.12

The existing source suite contained 22 tests.

## Release-candidate validation

The release candidate adds a program-version identity regression, bringing the suite to 23 tests.

The hosted workflow expands to:

- Ubuntu / Python 3.11
- Ubuntu / Python 3.12
- Ubuntu / Python 3.13
- Ubuntu / Python 3.14
- macOS / Python 3.11
- macOS / Python 3.12
- macOS / Python 3.13
- macOS / Python 3.14

Release publication requires all eight jobs to pass on the final `main` commit.

A maintainer Mac local setup succeeded with Python 3.14.6, OpenCV 4.13.0 and NumPy 2.3.5. The 23-test release-candidate suite passed, and the synthetic demo decoded both expected QR payloads.

A bounded camera-index-0 smoke command using `--max-frames 180` returned to the shell without a reported application error. The terminal record does not independently show the visual preview contents or a live QR decode, so this is treated as camera-access/loop evidence rather than an accuracy result.

## Scope

This is a QR reader, not a universal barcode reader.

Successful decoding does not establish that a URL, message, or other decoded payload is trustworthy.

Synthetic test fixtures demonstrate known cases only and are not an accuracy benchmark.

The application is intended for trusted local image input rather than hostile-file sandboxing.
