"""Sheet preflight. Refuse code generation on missing values or broken references."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = {
    'games': ('id','name','campaign_min_level','campaign_max_level','engine_family','original_content_from_owned_install','melty_loader_status','steam_install_key','chronological_order','completed_campaign_required'),
    'vault_hunters': ('id','display_name','source_game','role','signature_action_reference','core_style','requires_content','original_skill_trees','new_branch_id','playable_host_status','native_objects'),
    'expanded_skills': ('id','vault_hunter','branch_id','branch_name','skill_name','skill_kind','unlock_level','max_rank','stat','bonus_per_rank','prerequisite','design_status'),
    'systems': ('id','host_hook','protocol','behavior','status'),
}

def load_sheets(root=ROOT):
    return {name: json.loads((Path(root)/'sheets'/f'{name}.json').read_text(encoding='utf-8')) for name in REQUIRED}

def inspect(sheets):
    errors=[]
    for name,required in REQUIRED.items():
        rows=sheets.get(name, [])
        if not isinstance(rows,list) or not rows: errors.append(f'{name}: sheet must be nonempty');continue
        ids=set()
        for idx,row in enumerate(rows):
            if not isinstance(row,dict): errors.append(f'{name}[{idx}]: not a row');continue
            for field in required:
                if field not in row or row[field] is None or row[field] == '' or row[field] == []:
                    errors.append(f'{name}[{idx}].{field}: empty or missing')
            if row.get('id') in ids: errors.append(f'{name}[{idx}].id: duplicate {row.get("id")}')
            ids.add(row.get('id'))
    game_ids={g['id'] for g in sheets['games']}
    hunters={h['id']:h for h in sheets['vault_hunters']}
    skills={s['id']:s for s in sheets['expanded_skills']}
    for h in hunters.values():
        if h['source_game'] not in game_ids:errors.append(f'{h["id"]}: unknown source game')
        if h['new_branch_id'] not in {s['branch_id'] for s in skills.values()}:errors.append(f'{h["id"]}: unresolved branch')
    for s in skills.values():
        if s['vault_hunter'] not in hunters:errors.append(f'{s["id"]}: unknown hunter')
        elif s['branch_id'] != hunters[s['vault_hunter']]['new_branch_id']: errors.append(f'{s["id"]}: wrong branch')
        if s['prerequisite'] != 'none' and s['prerequisite'] not in skills:errors.append(f'{s["id"]}: invalid prerequisite')
        if not (1<=s['unlock_level']<=300):errors.append(f'{s["id"]}: invalid level')
        if not (1<=s['max_rank']<=10):errors.append(f'{s["id"]}: invalid max rank')
        if not (0 < s['bonus_per_rank'] <= 1):errors.append(f'{s["id"]}: invalid bonus')
    order=sorted(sheets['games'],key=lambda g:g['chronological_order'])
    if [x['chronological_order'] for x in order]!=list(range(1,len(order)+1)):errors.append('game order has gaps')
    for i,g in enumerate(order):
        if g['campaign_min_level'] != (1 if i==0 else order[i-1]['campaign_max_level']+1):errors.append(f'{g["id"]}: level range not contiguous')
        if g['campaign_max_level'] != 60*(i+1):errors.append(f'{g["id"]}: unexpected milestone')
        if g['completed_campaign_required'] != ('none' if i==0 else order[i-1]['id']):errors.append(f'{g["id"]}: incorrect gate')
    if order[-1]['campaign_max_level']!=300: errors.append('max player/weapon level must be 300')
    if len(hunters)!=26:errors.append('expected 26 hunters including both Borderlands 4 DLC hunters')
    return errors

def require_clean(sheets):
    errors=inspect(sheets)
    if errors: raise ValueError('Preflight failed:\n'+'\n'.join(errors))
    return sheets

if __name__=='__main__':
    sheets=load_sheets()
    errors=inspect(sheets)
    if errors:
        print('Preflight FAILED:\n'+'\n'.join(errors));raise SystemExit(1)
    print(f'Preflight PASS: {len(sheets["games"])} campaigns, {len(sheets["vault_hunters"])} hunters, {len(sheets["expanded_skills"])} expansion skills, {len(sheets["systems"])} systems.')
