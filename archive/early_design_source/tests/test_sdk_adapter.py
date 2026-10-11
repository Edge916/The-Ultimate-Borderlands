"""An import contract test, NOT a test inside Borderlands 2."""
from __future__ import annotations
import importlib.util, types, sys, unittest
from pathlib import Path
from unittest.mock import patch

class AdapterContractTests(unittest.TestCase):
    def test_probe_registers_without_native_game(self):
        sent={}
        fake_mods=types.ModuleType('mods_base')
        fake_mods.build_mod=lambda **kwargs: sent.update(kwargs)
        fake_mods.ButtonOption=lambda *a,**kw: ('ButtonOption',a,kw)
        fake_mods.CoopSupport=types.SimpleNamespace(ClientSide='ClientSide')
        fake_mods.Game=types.SimpleNamespace(BL2='BL2')
        fake_mods.get_pc=lambda possibly_loading=False: types.SimpleNamespace(Name='TestController')
        fake_sdk=types.ModuleType('unrealsdk')
        entries=[]
        fake_sdk.logging=types.SimpleNamespace(info=lambda *args: entries.append(('info',args)),error=lambda *args: entries.append(('error',args)))
        source=Path(__file__).resolve().parent.parent/'adapters'/'bl2_sdk_probe'/'UltimateVaultHunterProbe'/'__init__.py'
        spec=importlib.util.spec_from_file_location('probe_mod',source)
        mod=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'mods_base':fake_mods,'unrealsdk':fake_sdk}):
            spec.loader.exec_module(mod)
            self.assertEqual(sent['supported_games'],'BL2')
            self.assertEqual(sent['coop_support'],'ClientSide')
            mod.probe_host(None)
        self.assertTrue(any(entry[0]=='info' for entry in entries))

if __name__=='__main__':unittest.main()
