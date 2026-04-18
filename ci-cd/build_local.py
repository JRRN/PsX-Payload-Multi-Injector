import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".build_local"

if platform.system() == "Windows":
    PYTHON = VENV / "Scripts" / "python.exe"
else:
    PYTHON = VENV / "bin" / "python3"


def run(cmd, check=True):
    print(f"→ {cmd}")
    return subprocess.run(cmd, shell=True, check=check)


def ensure_venv():
    if not PYTHON.exists():
        print("No virtualenv found. Creating .build_local...")
        run(f"{sys.executable} -m venv {VENV}")
        run(f"\"{PYTHON}\" -m pip install --upgrade pip")
    else:
        print("Using existing virtualenv.")


def ensure_pip():
    try:
        run(f"\"{PYTHON}\" -m pip --version")
    except Exception:
        print("pip missing. Bootstrapping ensurepip...")
        run(f"\"{PYTHON}\" -m ensurepip --upgrade")


def ensure_pyside6():
    print("Checking for PySide6...")
    result = subprocess.run([str(PYTHON), "-c", "import PySide6"], capture_output=True)
    if result.returncode == 0:
        print("PySide6 OK.")
        return

    print("ERROR: PySide6 missing after installing requirements.")
    if result.stderr:
        print(result.stderr.decode(errors="ignore"))
    sys.exit(1)


def ensure_pyinstaller():
    try:
        run(f"\"{PYTHON}\" -m PyInstaller --version")
    except Exception:
        print("Installing PyInstaller...")
        run(f"\"{PYTHON}\" -m pip install pyinstaller")


def install_requirements():
    print("Installing requirements.txt...")
    run(f"\"{PYTHON}\" -m pip install -r requirements.txt")


def get_version():
    cmd = f"\"{PYTHON}\" -c \"from src.models.version import __version__; print(__version__)\""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    version = result.stdout.strip()
    if not version:
        print("ERROR: Could not read version.")
        sys.exit(1)
    return version


def generate_spec(version):
    system = platform.system()

    icon = ""
    if (ROOT / "src/assets/logo.ico").exists():
        icon = str(ROOT / "src/assets/logo.ico")

    spec_dir = ROOT / "build"
    spec_dir.mkdir(exist_ok=True)

    spec_file = spec_dir / f"PS_MultiInjector-{version}.spec"

    print("Generating optimized .spec...")

    spec_content = f"""
# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_submodules

ROOT = r"{ROOT}"
hiddenimports = collect_submodules('src')
block_cipher = None

a = Analysis(
    [os.path.join(ROOT, 'src', 'main.py')],
    pathex=[os.path.join(ROOT, 'src')],
    binaries=[],
    datas=[
        (os.path.join(ROOT, 'src/assets/logo.png'), 'assets'),
        (os.path.join(ROOT, 'src/lang'), 'lang'),
        (os.path.join(ROOT, 'src/assets/logo.ico'), 'assets'),
    ],
    hiddenimports=hiddenimports,
    hookspath=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='PS_MultiInjector',
    icon=r"{icon}",
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='PS_MultiInjector-{version}-dist'
)
"""

    spec_file.write_text(spec_content)
    print(f"Spec file created: {spec_file}")
    return spec_file


def build_from_spec(spec_file):
    run(f"\"{PYTHON}\" -m PyInstaller \"{spec_file}\"")


def cleanup_venv():
    import shutil

    if VENV.exists():
        print("Cleaning virtualenv .build_local...")
        try:
            shutil.rmtree(VENV)
            print("Virtualenv removed.")
        except Exception as e:
            print(f"ERROR removing virtualenv: {e}")
    else:
        print("No virtualenv to clean.")


def main():
    os.chdir(ROOT)

    ensure_venv()
    ensure_pip()
    install_requirements()
    ensure_pyside6()
    ensure_pyinstaller()

    version = get_version()
    print(f"Building version {version}...")

    spec_file = generate_spec(version)
    build_from_spec(spec_file)

    print(f"Build complete. Check dist/PS_MultiInjector-{version}-dist")

    cleanup_venv()


if __name__ == "__main__":
    main()
