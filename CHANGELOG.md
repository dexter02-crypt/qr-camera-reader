# Changelog

## 0.1.0 — 2026-10-02

Initial public release of QR Camera Reader.

- Decodes multiple QR codes from trusted local images and camera frames.
- Keeps decoded values as data and never opens links automatically.
- Escapes displayed payload text and bounds payload/result sizes.
- Maintains a bounded in-memory unique-payload session count.
- Supports explicit PNG and JSON export without overwriting existing files.
- Includes synthetic regression fixtures, automated tests, documentation, and hosted CI.
- Keeps camera frames and live-session counters out of persistent storage.
