# Validation

## Public baseline

Repository: `dexter02-crypt/qr-camera-reader`

Baseline `main`:

`c96be3e3e29cd6b4122031c5b0e6a1aa75d77024`

GitHub Actions run `36765698334` completed successfully on that exact commit.

The historical hosted workflow had one job:

- Ubuntu / Python 3.12

The baseline source suite contained 22 tests.

## Release-candidate coverage

The release candidate contains **23 tests**, including a release-version identity check.

Coverage includes:

- actual two-code decoding from the synthetic fixture
- blank-image negative behavior
- input preservation
- repeated-payload deduplication
- bounded session storage and reset
- truncated-payload exclusion from unique identity counting
- escaped controls and Unicode display behavior
- rejection of partial undecoded results
- rejection of invalid QR corner coordinates
- explicit long-payload truncation
- image read/export behavior
- no-overwrite guarantees
- metadata collision handling
- output symlink refusal
- invalid frame and image rejection
- rejection of non-integer/network camera sources
- failed-camera cleanup
- processing-exception camera/window cleanup
- bounded one-frame camera-loop behavior using mocks
- display-header input preservation
- real CLI demo/export behavior
- release version identity

The release-candidate GitHub Actions workflow expands validation to Python 3.11–3.14 on both Ubuntu and macOS.

Fresh branch, pull-request and final-main CI evidence is required before release.

## Synthetic demonstration

`examples/two-codes.png` is a synthetic fixture.

The real OpenCV decoder recovers:

- `KEDBYTE-DEMO-ONE`
- `https://example.invalid/not-opened`

The `.invalid` domain is deliberately non-routable.

The application does not open the decoded URL.

## Camera boundary

Automated tests exercise camera failure, cleanup and bounded-loop behavior using mocks.

Those tests do not establish successful access to physical camera hardware.

## Mac local evidence

On the maintainer Mac, `setup.sh` succeeded with Python 3.14.6, OpenCV 4.13.0 and NumPy 2.3.5.

The 23-test release-candidate suite passed.

The synthetic CLI demo successfully decoded the two expected fixture payloads:

- `KEDBYTE-DEMO-ONE`
- `https://example.invalid/not-opened`

A bounded physical-camera command using camera index 0 and `--max-frames 180` returned cleanly to the shell without a reported application error.

The terminal record does not independently establish what was visible in the GUI or whether a live QR payload was decoded. Therefore the hardware result establishes only bounded camera access/loop execution, not real-world decoding accuracy.

## Scope boundaries

The project makes no measured field precision/recall claim.

It is QR-only, not a universal barcode reader.

Decoded content is untrusted data. A successfully decoded link is not automatically safe.

Image decoding uses native OpenCV code and is not a hostile-file sandbox.
