"""Verify the install ZIP and import its runtime alone with inert SDK mocks."""
import subprocess
import re
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
FOLDER = 'UltimateVaultHunterDeathtrapBoost'
ARCHIVE = ROOT / 'dist' / (FOLDER + '_folder_install.zip')
EXPECTED = {FOLDER + '/' + name for name in ('__init__.py', 'pyproject.toml', 'README.txt')}
VERSION = re.search(r'^version\s*=\s*"([^"]+)"',
                    (ROOT / 'sdk_mods' / FOLDER / 'pyproject.toml').read_text(), re.M).group(1)
SMOKE = '''
import runpy, sys, types
def forbidden(*args, **kwargs):
    raise AssertionError('runtime import unexpectedly accessed game state')
base = types.ModuleType('mods_base')
base.ButtonOption = lambda *args, **kwargs: kwargs
base.CoopSupport = types.SimpleNamespace(ClientSide='client')
base.Game = types.SimpleNamespace(BL2='bl2')
base.get_pc = forbidden
registered = []
base.build_mod = lambda **kwargs: registered.append(kwargs)
sdk = types.ModuleType('unrealsdk')
sdk.logging = types.SimpleNamespace(info=forbidden)
sdk.find_object = sdk.find_all = sdk.find_enum = sdk.load_package = sdk.construct_object = forbidden
sys.modules['mods_base'] = base
sys.modules['unrealsdk'] = sdk
runpy.run_path(sys.argv[1])
assert len(registered) == 1
assert registered[0]['version'] == sys.argv[2]
assert registered[0]['on_disable'].__name__ == 'shutdown'
assert len(registered[0]['options']) == 23
print('PASS: isolated packaged runtime import; no game access or scaffolding')
'''

with ZipFile(ARCHIVE) as archive:
    assert len(archive.namelist()) == len(EXPECTED)
    assert set(archive.namelist()) == EXPECTED, archive.namelist()
    assert archive.testzip() is None
    for name in EXPECTED:
        assert archive.read(name) == (ROOT / 'sdk_mods' / name).read_bytes(), name
    compile(archive.read(FOLDER + '/__init__.py'), FOLDER + '/__init__.py', 'exec')
    with tempfile.TemporaryDirectory(prefix='uvh_package_check_', dir=ROOT / 'dist') as temporary:
        archive.extractall(temporary)
        subprocess.run([sys.executable, '-I', '-c', SMOKE,
                        str(Path(temporary) / FOLDER / '__init__.py'), VERSION],
                       cwd=temporary, check=True)

print('PASS: ZIP integrity, exact single-folder layout and source match')
