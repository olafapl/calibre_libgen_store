# A Library Genesis Store for Calibre

## Installation

1. Download  [the latest release](/releases/latest).
1. Open Calibre and navigate to "Preferences" > "Advanced" > "Plugins", click "Load plugin from
   file", and select the ZIP file downloaded in the previous step.

## Development

### Requirements

- Python 3.7+
- [Poetry](https://python-poetry.org/)
- Calibre 5.0.1+

### Setup

Run `poetry install` to install dependencies and (optionally) download Calibre's Python source code
to `calibre/`
with `poetry run download_calibre_src`.

### Available scripts

```sh
# Run all (unit) tests located in tests/
poetry run test

# Download Calibre's Python source code and place it in calibre/
# Makes development easier by enabling proper IntelliSense
poetry run download_calibre_src

# Create a release ZIP file and place it in dist/
poetry run create_release
```

## License

This project is MIT licensed.
