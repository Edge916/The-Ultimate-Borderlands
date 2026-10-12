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
sdk.find_object = sdk.find_all = sdk.find_enum = sdk.find_class = sdk.load_package = sdk.construct_object = forbidden
sys.modules['mods_base'] = base
sys.modules['unrealsdk'] = sdk
scope = runpy.run_path(sys.argv[1])
assert len(registered) == 1
assert registered[0]['version'] == sys.argv[2]
assert registered[0]['on_disable'].__name__ == 'shutdown'
assert len(registered[0]['options']) == 25
assert registered[0]['name'] == 'UVH v0.2.19 - RELATIONSHIP CLASS METADATA'
assert scope['_CR_PATH'] == 'WillowGame.SkillEffectManager:ActivateSkill'
assert scope['_CR_IDENT'] == 'UVH_ACTIVATION_READER_V18_PRE'
assert '[UVH-ACTIVATION] ' in scope['_cr_emit'].__code__.co_consts
assert scope['_RM_PATH'] == 'WillowGame.SkillEffectManager:ActivateSkill'
assert scope['_RM_IDENT'] == 'UVH_RELATION_METADATA_V19_PRE'
assert '[UVH-REL-META] ' in scope['_rm_record'].__code__.co_consts
assert scope['_RM_CAPS'] == (112, 96, 14000, 14000)
assert not scope['_rm_accepting'] and scope['_rm_pending'] is None
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
