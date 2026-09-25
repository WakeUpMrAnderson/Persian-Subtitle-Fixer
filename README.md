# Persian Subtitle Fixer

[![CI](https://github.com/WakeUpMrAnderson/Persian-Subtitle-Fixer/actions/workflows/ci.yaml/badge.svg)](https://github.com/WakeUpMrAnderson/Persian-Subtitle-Fixer/actions/workflows/ci.yaml)
[![Release](https://github.com/WakeUpMrAnderson/Persian-Subtitle-Fixer/actions/workflows/release.yaml/badge.svg)](https://github.com/WakeUpMrAnderson/Persian-Subtitle-Fixer/actions/workflows/release.yaml)

A simple, cross-platform application for fixing Persian and Arabic subtitle encoding issues that cause gibberish text in media players.

## Features

- ✅ **Drag & Drop Interface** - Easy to use GUI
- ✅ **Multi-file Support** - Process multiple subtitles at once
- ✅ **Format Support** - SRT, srt, and ASS formats
- ✅ **Encoding Fix** - Automatically detects and fixes encoding issues
- ✅ **Cross-platform** - Available for Windows, Linux, and macOS

## Download

Get the latest release for your platform from the [Releases page](https://github.com/WakeUpMrAnderson/Persian-Subtitle-Fixer/releases).

### Installation

#### Windows
1. Download `PersianSubtitleFixer-Windows-{version}.zip`
2. Extract the archive
3. Run `PersianSubtitleFixer.exe`

#### macOS
1. Download `PersianSubtitleFixer-macOS-{version}.dmg` (recommended)
2. Open the DMG and drag the app to Applications
3. Right-click → Open (first time only, to bypass Gatekeeper)

#### Linux
1. Download `PersianSubtitleFixer-Linux-{version}.zip`
2. Extract the archive
3. Make executable: `chmod +x PersianSubtitleFixer`
4. Run: `./PersianSubtitleFixer`

## Usage

1. Launch the application
2. Drag and drop your subtitle files onto the window
3. Files are automatically processed and fixed
4. Fixed files are saved with corrected encoding

**Note:** Only UTF-8 or ANSI encoded files are supported. Other encodings may cause issues.

## Development

### Requirements

- Python 3.11+
- uv (recommended) or pip
- PyQt5

### Setup

```bash
# Clone the repository
git clone https://github.com/WakeUpMrAnderson/Persian-Subtitle-Fixer.git
cd Persian-Subtitle-Fixer

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Install development dependencies
uv pip install pytest ruff pyinstaller
```

### Running Tests

```bash
# Run linting
ruff check .

# Run test suite
pytest -v
```

### Building

```bash
# Build with PyInstaller
pyinstaller --clean PersianSubtitleFixer.spec
```

The executable will be in `dist/PersianSubtitleFixer/`.

## CI/CD

This project uses GitHub Actions for continuous integration and automated releases:

- **CI Workflow** - Runs on every push/PR to main
  - Linting with ruff
  - Test suite with pytest
  
- **Release Workflow** - Runs on tag push (v*)
  - Runs tests first (must pass)
  - Builds for Windows, Linux, macOS
  - Creates GitHub release with artifacts
  - Generates SHA256 checksums

## Contributing

Contributions are welcome! Please ensure:
- All tests pass (`pytest -v`)
- Code passes linting (`ruff check .`)
- Commits follow conventional commit format

## Todo List

- [ ] Rework UI widgets tree
- [ ] Fix issue with incompatible file encodings (UTF-16, etc.)
- [x] Reduce executable size (optimized to ~36 MB compressed)
- [ ] Add folder support to drag & drop
- [ ] Add output log for failed files tracking
- [x] Add automated testing and CI/CD
- [x] Multi-platform builds

## License

This project is open source. See LICENSE file for details.

## Acknowledgments

Built with Python and PyQt5.
