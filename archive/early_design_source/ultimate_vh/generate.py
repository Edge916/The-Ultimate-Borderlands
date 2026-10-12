"""Generate one immutable Python model instance per JSON sheet row."""
from __future__ import annotations
from pathlib import Path
from .preflight import load_sheets, require_clean, ROOT

TYPES={
    'games':'GameRecord',
    'vault_hunters':'VaultHunterRecord',
    'expanded_skills':'SkillRecord',
    'systems':'SystemRecord',
}

def generate(root=ROOT):
    sheets=require_clean(load_sheets(root))
    root=Path(root)
    dest=root/'generated'/'sheet_records.py'
    body=['# AUTO-GENERATED. Edit sheets/*.json, not this file.',
          'from dataclasses import dataclass',
          '',
          '@dataclass(frozen=True)',
          'class GameRecord:',
          '    id: str; name: str; campaign_min_level: int; campaign_max_level: int',
          '    engine_family: str; original_content_from_owned_install: bool',
          '    melty_loader_status: str; steam_install_key: str; chronological_order: int; completed_campaign_required: str',
          '',
          '@dataclass(frozen=True)',
          'class VaultHunterRecord:',
          '    id: str; display_name: str; source_game: str; role: str; signature_action_reference: str',
          '    core_style: str; requires_content: str; original_skill_trees: str; new_branch_id: str',
          '    playable_host_status: str; native_objects: str',
          '',
          '@dataclass(frozen=True)',
          'class SkillRecord:',
          '    id: str; vault_hunter: str; branch_id: str; branch_name: str; skill_name: str',
          '    skill_kind: str; unlock_level: int; max_rank: int; stat: str; bonus_per_rank: float',
          '    prerequisite: str; design_status: str',
          '',
          '@dataclass(frozen=True)',
          'class SystemRecord:',
          '    id: str; host_hook: str; protocol: str; behavior: str; status: str',
          '']
    for sheet,rows in sheets.items():
        body.append(f'{sheet.upper()} = (')
        for row in rows:
            args=', '.join(f'{k}={v!r}' for k,v in row.items())
            body.append(f'    {TYPES[sheet]}({args}),')
        body.append(')')
        body.append('')
    dest.parent.mkdir(exist_ok=True)
    dest.write_text('\n'.join(body), encoding='utf-8')
    return dest

if __name__=='__main__':
    print(generate())
