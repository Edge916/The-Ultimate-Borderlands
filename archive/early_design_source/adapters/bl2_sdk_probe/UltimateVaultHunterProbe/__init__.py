"""BL2 SDK loader diagnostic only. NO new hunters playable yet.

Place this source folder inside BL2/sdk_mods after installing bl-sdk's manager.
Do not ship/publish as the promised mashup.
"""
from mods_base import build_mod, ButtonOption, CoopSupport, Game, get_pc
from unrealsdk import logging

def probe_host(_option):
    try:
        pc=get_pc(possibly_loading=True)
        if pc is None:
            logging.info('[UVH] No active local player (menu or loading).')
            return
        logging.info('[UVH] Borderlands 2 local player controller accessible: %s',str(pc.Name))
        logging.info('[UVH] Only SDK integration verified. No imported characters, skills, or co-op yet.')
    except Exception as exc:
        logging.error('[UVH] SDK probe failed: %s',str(exc))

build_mod(
    name='Ultimate Vault Hunters - Integration Probe',
    author='Community prototype',
    description='Read-only host integration diagnostic. Does NOT unlock other games\' Vault Hunters.',
    version='0.0.1',
    supported_games=Game.BL2,
    coop_support=CoopSupport.ClientSide,
    options=[ButtonOption('probe_host',display_name='Check host integration',on_press=probe_host)],
    auto_enable=True,
)
