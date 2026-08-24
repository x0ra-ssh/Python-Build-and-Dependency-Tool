import argparse
import ast
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

# Mapping import names to PyPI package names
PACKAGE_MAP = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "bs4": "beautifulsoup4",
    "yaml": "PyYAML",
    "sklearn": "scikit-learn",
    "wx": "wxPython",
    "fitz": "PyMuPDF",
    "crypto": "pycryptodome",
    "serial": "pyserial",
    "customtkinter": "customtkinter",
}

# Frameworks that trigger --noconsole build mode
GUI_FRAMEWORKS = {
    "tkinter", "PyQt5", "PyQt6", "PySide2", "PySide6", 
    "wx", "customtkinter", "kivy", "pygame", "flet",
}


def get_stdlib_modules() -> set[str]:
    """Returns standard library module names."""
    if sys.version_info >= (3, 10):
        return set(sys.stdlib_module_names)
    return set(sys.builtin_module_names)


def resolve_targets(targets: list[str]) -> set[Path]:
    """Resolves input paths into a set of Python file paths."""
    py_files = set()
    for target in targets:
        path = Path(target)
        if path.is_file() and path.suffix == ".py":
            py_files.add(path.resolve())
        elif path.is_dir():
            py_files.update(path.rglob("*.py"))
        else:
            print(f"[!] Warning: '{target}' is not a valid .py file or directory.")
    return py_files


def extract_imports(file_path: Path) -> set[str]:
    """Extracts top-level import module names using AST."""
    imports = set()
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
    except Exception as e:
        print(f"[!] AST Error in '{file_path}': {e}")
    return imports


def install_packages(modules: set[str], dry_run: bool = False) -> None:
    """Installs missing third-party packages via pip."""
    stdlib = get_stdlib_modules()
    missing_packages = set()

    for mod in sorted(modules):
        if mod in stdlib or mod.startswith("_"):
            continue

        pypi_name = PACKAGE_MAP.get(mod, mod)
        if importlib.util.find_spec(mod) is None:
            missing_packages.add(pypi_name)
        else:
            print(f" [✓] '{mod}' is installed.")

    if not missing_packages:
        print("\nAll required dependencies are satisfied!")
        return

    print(f"\nMissing packages: {', '.join(sorted(missing_packages))}")
    if dry_run:
        print("[Dry Run] Skipping package installation.")
        return

    print("Installing missing dependencies...\n")
    cmd = [sys.executable, "-m", "pip", "install"] + sorted(list(missing_packages))
    subprocess.check_call(cmd)


def build_exe(file_path: Path, imports: set[str], force_gui: bool = False, force_cli: bool = False, icon: str = None) -> None:
    """Compiles script into a single executable via PyInstaller."""
    if importlib.util.find_spec("PyInstaller") is None:
        print("\nPyInstaller is required for building binaries. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    has_gui = any(mod in GUI_FRAMEWORKS for mod in imports)
    is_gui = True if force_gui else (False if force_cli else has_gui)

    mode_str = "GUI (--noconsole)" if is_gui else "CLI/Console (--console)"
    print(f"\nBuilding executable for '{file_path.name}' [Mode: {mode_str}]...")

    cmd = [sys.executable, "-m", "PyInstaller", "--onefile"]
    cmd.append("--noconsole" if is_gui else "--console")

    if icon:
        cmd.extend(["--icon", icon])

    cmd.append(str(file_path))

    try:
        subprocess.check_call(cmd)
        dist_dir = Path("dist").resolve()
        print(f"\n[✓] Executable built successfully!")
        print(f"    Location: {dist_dir}")
    except subprocess.CalledProcessError as e:
        print(f"\n[!] PyInstaller build failed: {e}")


def interactive_menu():
    """Interactive CLI menu when run without flags."""
    print("=" * 50)
    print("        PYTHON BUILD & DEPENDENCY TOOL        ")
    print("=" * 50)
    print("1. Scan & Install Dependencies")
    print("2. Test Scan (Dry Run - No Installation)")
    print("3. Build .EXE (Auto-Detect GUI/CLI)")
    print("4. Build .EXE (Force CLI/Console Mode)")
    print("5. Build .EXE (Force GUI/No Console Mode)")
    print("6. Exit")
    print("=" * 50)

    choice = input("\nSelect an option (1-6): ").strip()
    if choice == "6":
        sys.exit(0)

    target = input("Enter target file or directory path (default: current dir): ").strip()
    target_path = [target] if target else ["."]
    py_files = resolve_targets(target_path)

    if not py_files:
        print("No valid Python files found.")
        return

    all_imports = set()
    for f in py_files:
        all_imports.update(extract_imports(f))

    if choice == "1":
        install_packages(all_imports)
    elif choice == "2":
        install_packages(all_imports, dry_run=True)
    elif choice in ["3", "4", "5"]:
        install_packages(all_imports)
        force_gui = choice == "5"
        force_cli = choice == "4"
        for f in py_files:
            build_exe(f, extract_imports(f), force_gui=force_gui, force_cli=force_cli)


def main():
    parser = argparse.ArgumentParser(
        description="Scan dependencies and compile Python scripts into binaries.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py                              Launch interactive menu
  python install.py main.py                      Scan & install dependencies for main.py
  python install.py ./src                        Scan & install dependencies recursively
  python install.py main.py --exe                Scan dependencies & compile to .exe
  python install.py net_mapper.py --exe --cli    Compile TUI/CLI app explicitly with console
  python install.py gui.py --exe --icon logo.ico Compile GUI app with a custom icon
        """
    )
    parser.add_argument("targets", nargs="*", default=[], help="Python file(s) or directory to process")
    parser.add_argument("--dry-run", action="store_true", help="Check dependencies without installing")
    parser.add_argument("--exe", action="store_true", help="Compile script(s) into a standalone .exe")
    parser.add_argument("--gui", action="store_true", help="Force GUI mode (hides terminal window)")
    parser.add_argument("--cli", action="store_true", help="Force CLI mode (shows terminal window)")
    parser.add_argument("--icon", type=str, default=None, help="Path to .ico file for binary")

    args = parser.parse_args()

    # Launch menu if no targets or flags are provided
    if not args.targets and not sys.argv[1:]:
        interactive_menu()
        return

    py_files = resolve_targets(args.targets if args.targets else ["."])
    if not py_files:
        print("No valid Python files found.")
        sys.exit(1)

    all_imports = set()
    for file_path in py_files:
        print(f"Scanning '{file_path.name}'...")
        all_imports.update(extract_imports(file_path))

    install_packages(all_imports, dry_run=args.dry_run)

    if args.exe:
        for file_path in py_files:
            build_exe(file_path, extract_imports(file_path), force_gui=args.gui, force_cli=args.cli, icon=args.icon)


if __name__ == "__main__":
    main()