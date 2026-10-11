"""Atomic, versioned *sidecar* saves; does NOT modify any real Borderlands save files."""
from __future__ import annotations
import json, hashlib, os, tempfile
from pathlib import Path
from .progression import HunterState
SAVE_VERSION=1

def save_state(path:Path,state:HunterState):
    state.validate()
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    obj={'hunter_id':state.hunter_id,'level':state.level,'experience':state.experience,
         'money':state.money,'eridium':state.eridium,'completed_campaigns':sorted(state.completed_campaigns),
         'unlocked_locations':sorted(state.unlocked_locations),'skills':state.skills,
         'equipment_refs':state.equipment_refs}
    payload=json.dumps(obj,sort_keys=True,separators=(',',':'))
    data={'version':SAVE_VERSION,'sha256':hashlib.sha256(payload.encode()).hexdigest(),'data':obj}
    fd,tmp=tempfile.mkstemp(prefix='.uvh-',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:
            json.dump(data,f,indent=2,sort_keys=True);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def load_state(path:Path)->HunterState:
    blob=json.loads(Path(path).read_text(encoding='utf-8'))
    if blob.get('version')!=SAVE_VERSION:raise ValueError('Unsupported save version')
    payload=json.dumps(blob['data'],sort_keys=True,separators=(',',':'))
    if hashlib.sha256(payload.encode()).hexdigest()!=blob['sha256']:raise ValueError('Save checksum mismatch')
    obj=blob['data']
    obj['completed_campaigns']=set(obj['completed_campaigns'])
    obj['unlocked_locations']=set(obj['unlocked_locations'])
    return HunterState(**obj).validate()
