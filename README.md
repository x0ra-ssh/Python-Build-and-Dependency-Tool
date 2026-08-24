# Python Build & Dependency Tool

A lightweight Python utility for **dependency discovery, package installation, and executable generation**.

The tool analyzes Python source code using the Abstract Syntax Tree (AST), identifies imported modules, resolves common Python-to-PyPI naming differences, installs missing dependencies, and optionally packages Python applications into standalone executables using PyInstaller.

It is intentionally small, transparent, and command-line oriented.

## Features

* **AST-based dependency scanning**

  * Inspects Python source without executing it.
  * Detects `import` and `from ... import ...` statements.
  * Recursively processes Python files inside directories.

* **Automatic dependency installation**

  * Ignores Python standard-library modules.
  * Detects unavailable third-party imports.
  * Maps common import names to their corresponding PyPI packages.
  * Installs missing packages through the active Python environment.

* **Executable generation**

  * Uses PyInstaller to create standalone executables.
  * Supports single-file builds with `--onefile`.
  * Automatically detects common GUI frameworks.
  * Supports explicit CLI or GUI build modes.
  * Supports custom application icons.

* **Dry-run mode**

  * Inspect missing dependencies without installing anything.

* **Interactive mode**

  * Provides a simple menu-driven workflow when launched without arguments.

## Requirements

* Python 3.10+
* `pip`
* Internet access when dependencies need to be installed

PyInstaller is installed automatically when an executable build is requested and PyInstaller is not already available.

## Installation

Clone the repository:

```bash
git clone https://github.com/x0ra-ssh/Python-Build-and-Dependency-Tool.git
cd Python-Build-and-Dependency-Tool
```

No additional installation is required to run the tool directly.

## Usage

### Interactive Mode

Run the tool without arguments:

```bash
python install.py
```

The interactive menu provides options to:

1. Scan and install dependencies
2. Perform a dry dependency scan
3. Build an executable with automatic GUI/CLI detection
4. Build an executable in CLI mode
5. Build an executable in GUI mode
6. Exit

### Scan a Python File

```bash
python install.py app.py
```

The tool analyzes the specified file and installs missing dependencies.

### Scan a Directory

```bash
python install.py ./src
```

All `.py` files inside the directory and its subdirectories are analyzed.

### Dry Run

To inspect dependencies without installing them:

```bash
python install.py app.py --dry-run
```

This is useful for previewing what the tool considers missing before allowing it to modify the environment.

## Building Executables

### Automatic Mode

```bash
python install.py app.py --exe
```

The tool determines whether the application appears to be GUI-oriented based on imported frameworks.

### CLI / Console Mode

```bash
python install.py app.py --exe --cli
```

The generated application retains its console window.

### GUI Mode

```bash
python install.py app.py --exe --gui
```

The generated application is built with PyInstaller's `--noconsole` option.

### Custom Icon

```bash
python install.py app.py --exe --icon logo.ico
```

The supplied `.ico` file is passed to PyInstaller during the build.

## Dependency Detection

The tool parses source files using Python's `ast` module.

For example:

```python
import requests
import cv2
from PIL import Image
```

The scanner extracts the top-level modules:

```text
requests
cv2
PIL
```

Standard-library modules are excluded automatically.

For imports where the Python module name differs from the PyPI distribution name, the tool maintains an internal mapping.

### Current Mappings

| Python Import   | PyPI Package     |
| --------------- | ---------------- |
| `cv2`           | `opencv-python`  |
| `PIL`           | `Pillow`         |
| `bs4`           | `beautifulsoup4` |
| `yaml`          | `PyYAML`         |
| `sklearn`       | `scikit-learn`   |
| `wx`            | `wxPython`       |
| `fitz`          | `PyMuPDF`        |
| `crypto`        | `pycryptodome`   |
| `serial`        | `pyserial`       |
| `customtkinter` | `customtkinter`  |

## Build Process

When executable generation is requested, the workflow is:

```text
Python Source
      │
      ▼
   AST Scan
      │
      ▼
Import Detection
      │
      ▼
Standard Library Filtering
      │
      ▼
Dependency Mapping
      │
      ▼
Missing Dependency Detection
      │
      ▼
     pip
      │
      ▼
   PyInstaller
      │
      ▼
Standalone Executable
```

PyInstaller is invoked through the active Python interpreter:

```bash
python -m PyInstaller
```

This keeps the build process tied to the Python environment in which the tool is being executed.

## GUI Detection

The tool recognizes several common GUI frameworks, including:

* Tkinter
* PyQt5
* PyQt6
* PySide2
* PySide6
* wxPython
* CustomTkinter
* Kivy
* Pygame
* Flet

If one of these frameworks is detected, the tool can automatically select PyInstaller's GUI/no-console mode.

CLI and GUI behavior can also be explicitly overridden with:

```bash
--cli
```

or:

```bash
--gui
```

## Output

PyInstaller normally produces its build artifacts in:

```text
build/
dist/
```

The resulting standalone executable is placed inside the `dist/` directory.

The executable can then be distributed independently of the original Python source environment, subject to PyInstaller's platform-specific packaging requirements.

## Limitations

Dependency discovery is based on static import analysis and therefore cannot identify every possible runtime dependency.

The scanner may not detect dependencies introduced through:

* Dynamic imports
* Plugin systems
* Runtime-generated module names
* External configuration
* Optional dependencies
* Packages imported indirectly by another dependency

Import names also do not always correspond directly to PyPI distribution names. The built-in mapping therefore covers known exceptions rather than attempting to infer every possible package name.

The tool should currently be considered a **lightweight build utility**, not a replacement for established Python packaging systems.

## Project Structure

```text
Python-Build-and-Dependency-Tool/
├── install.py
├── README.md
├── LICENSE
└── .gitignore
```

## Roadmap

* [ ] Improve local-module detection
* [ ] Expand import-to-PyPI mappings
* [ ] Add explicit dependency configuration
* [ ] Add `pyproject.toml` support
* [ ] Add dependency version handling
* [ ] Add virtual-environment management
* [ ] Add dependency locking
* [ ] Improve build configuration
* [ ] Add automated tests
* [ ] Add CI/CD
* [ ] Package the tool as an installable CLI
* [ ] Publish releases through PyPI

## Contributing

Contributions are welcome.

When contributing:

1. Keep changes focused and minimal.
2. Avoid unnecessary dependencies.
3. Test against both individual Python files and directories.
4. Test dependency detection before modifying installation behavior.
5. Document new command-line options.
6. Consider the security implications of automatically installing packages.

## License

This project is licensed under the **GNU General Public License v3.0**.

See [`LICENSE`](LICENSE) for the full license text.
