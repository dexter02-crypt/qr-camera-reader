# Validation

22 tests passed with zero skips in Linux CPython 3.13.5 / OpenCV 4.13.0 / NumPy 2.3.5. See `test-output.txt`. Actual synthetic image operations and CLI exports were executed. Camera and GUI error/cleanup paths use mocks; no camera was accessed. The example PNG is actual program output from a synthetic fixture, not a photograph or generated accuracy claim.

Fresh native dependency installation on macOS, live camera operation, remote GitHub Actions, and measured field accuracy remain unverified. The shared IO test methods run independently in each project; their repetition is not additional distinct feature coverage.
