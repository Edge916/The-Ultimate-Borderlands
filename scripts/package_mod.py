"""Build installable BL2 PythonSDK folder ZIP from current source."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "sdk_mods" / "UltimateVaultHunterDeathtrapBoost"
OUT = ROOT / "dist" / "UltimateVaultHunterDeathtrapBoost_folder_install.zip"
OUT.parent.mkdir(exist_ok=True)
with ZipFile(OUT, "w", ZIP_DEFLATED) as archive:
    for name in ("__init__.py", "pyproject.toml", "README.txt"):
        path = FOLDER / name
        assert path.is_file(), f"Missing {path}"
        archive.write(path, f"UltimateVaultHunterDeathtrapBoost/{name}")
print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
