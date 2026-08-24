# Python Build & Dependency Tool

A lightweight command-line utility for analyzing Python projects, identifying imported dependencies, installing missing packages, and packaging applications into standalone executables.

The goal is simple: reduce the repetitive setup involved in taking a Python script from source code to a runnable application without turning the project into another elaborate configuration ritual.

## Features

* **Automatic dependency detection**

  * Parses Python source files using the AST module.
  * Identifies imported modules without executing the target source code.
  * Includes mappings for common cases where Python import names differ from PyPI package names.

* **Dependency installation**

  * Detects packages that are unavailable in the current Python environment.
  * Installs missing dependencies through `pip`.

* **Executable generation**

  * Uses [PyInstaller](https://pyinstaller.org/) to package Python applications.
  * Supports both CLI and GUI-oriented applications.
  * Supports custom application icons.

* **Dry-run mode**

  * Preview dependency installation and build operations without modifying the environment.

* **Multiple source files**

  * Analyze and build individual Python files or multiple targets.

## Requirements

* Python 3.8+
* `pip`
* `PyInstaller`

Install PyInstaller with:

```bash
python -m pip install pyinstaller
```

## Usage

Run the tool against a Python file:

```bash
python install.py main.py
```

The tool will inspect the source file, determine its dependencies, install missing packages, and prepare the requested build.

### Interactive Mode

Running the tool without a target launches its interactive workflow:

```bash
python install.py
```

### Dry Run

To inspect what the tool intends to do without installing dependencies or creating an executable:

```bash
python install.py main.py --dry-run
```

### Build a CLI Application

```bash
python install.py main.py --exe --cli
```

### Build a GUI Application

```bash
python install.py main.py --exe --gui
```

### Custom Icon

```bash
python install.py main.py --exe --icon app.ico
```

## How It Works

The tool follows a straightforward pipeline:

```text
Python Source
     │
     ▼
AST Analysis
     │
     ▼
Import Detection
     │
     ▼
Dependency Mapping
     │
     ▼
Dependency Verification
     │
     ▼
Missing Packages ──► pip
     │
     ▼
PyInstaller
     │
     ▼
Standalone Executable
```

Python source files are parsed with the standard-library `ast` module rather than executed during dependency discovery. This allows the tool to inspect imports while avoiding unnecessary execution of the target application.

## Import Mapping

Python import names and PyPI distribution names do not always match.

For example:

| Import    | PyPI Package     |
| --------- | ---------------- |
| `cv2`     | `opencv-python`  |
| `PIL`     | `Pillow`         |
| `bs4`     | `beautifulsoup4` |
| `sklearn` | `scikit-learn`   |

The tool maintains mappings for known cases such as these.

## Build Output

When executable generation is enabled, PyInstaller handles the final packaging process.

Typical output:

```text
build/
dist/
    application.exe
application.spec
```

The exact output depends on the selected PyInstaller options and the target application.

## Project Structure

```text
Python-Build-and-Dependency-Tool/
├── install.py
├── README.md
├── LICENSE
└── .gitignore
```

## Design Philosophy

The project intentionally keeps its implementation small.

Rather than attempting to replace Python's entire packaging ecosystem, it focuses on automating a few common tasks:

1. Discover dependencies.
2. Install missing packages.
3. Build the application.
4. Produce a distributable executable.

The project is currently experimental and should be considered a lightweight build utility rather than a replacement for established package managers or build systems.

## Limitations

Dependency discovery through static imports has inherent limitations.

The tool may not detect dependencies introduced through:

* Dynamic imports
* Plugin systems
* Runtime-generated module names
* External configuration
* Optional dependencies
* Dependencies imported indirectly by another package

Import names also cannot always be reliably converted into PyPI distribution names. The mapping table therefore covers known exceptions rather than attempting to solve package-name resolution universally.

## Roadmap

Planned improvements include:

* [ ] `pyproject.toml` support
* [ ] Explicit dependency declarations
* [ ] Improved standard-library detection
* [ ] Better local-module detection
* [ ] Dependency version handling
* [ ] Virtual-environment management
* [ ] Dependency locking
* [ ] Improved build configuration
* [ ] Automated tests
* [ ] CI/CD integration
* [ ] Package the tool itself as a proper CLI
* [ ] Publish releases through PyPI

## Contributing

Contributions are welcome.

Before submitting a change:

1. Keep the implementation focused.
2. Avoid introducing unnecessary dependencies.
3. Test changes against both simple and multi-file Python projects.
4. Document new CLI options and behavior.
5. Keep security implications in mind when modifying dependency installation.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [`LICENSE`](LICENSE) for the complete license text.
