"""Testable progression and skill math, not yet connected to Unreal Engine."""
from __future__ import annotations
from dataclasses import dataclass,field
from generated.sheet_records import GAMES, VAULT_HUNTERS, EXPANDED_SKILLS

GAMES_BY_ID={g.id:g for g in GAMES}
HUNTERS_BY_ID={h.id:h for h in VAULT_HUNTERS}
SKILLS_BY_ID={s.id:s for s in EXPANDED_SKILLS}
MAX_LEVEL=300

@dataclass
class HunterState:
    hunter_id: str
    level: int=1
    experience: int=0
    money: int=0
    eridium: int=0
    completed_campaigns: set[str]=field(default_factory=set)
    unlocked_locations: set[str]=field(default_factory=set)
    skills: dict[str,int]=field(default_factory=dict)
    # Opaque references only; no copied textures, items, or game binaries.
    equipment_refs: list[dict]=field(default_factory=list)

    def validate(self):
        if self.hunter_id not in HUNTERS_BY_ID:raise ValueError('Unknown hunter')
        if not 1 <= self.level <= MAX_LEVEL:raise ValueError('Invalid level')
        if self.money<0 or self.eridium<0 or self.experience<0:raise ValueError('Negative resource')
        for loc in self.unlocked_locations:
            if ':' not in loc or loc.split(':',1)[0] not in GAMES_BY_ID:raise ValueError('Invalid fast-travel reference')
        for game in self.completed_campaigns:
            if game not in GAMES_BY_ID:raise ValueError('Unknown completed campaign')
        for skill_id,rank in self.skills.items():
            skill=SKILLS_BY_ID.get(skill_id)
            if skill is None or skill.vault_hunter!=self.hunter_id:raise ValueError('Wrong skill for hunter')
            if not 0<=rank<=skill.max_rank:raise ValueError('Invalid skill rank')
            if rank and self.level<skill.unlock_level:raise ValueError('Skill unlocked too early')
            if rank and skill.prerequisite!='none' and self.skills.get(skill.prerequisite,0)<1:
                raise ValueError('Missing prerequisite')
        for ref in self.equipment_refs:
            if not {'game','object_key','level'}.issubset(ref):raise ValueError('Missing equipment reference')
            if ref['game'] not in GAMES_BY_ID or not 1<=ref['level']<=MAX_LEVEL:raise ValueError('Invalid gear reference')
        return self

    def effective_bonus(self,stat):
        self.validate()
        return round(sum(SKILLS_BY_ID[sid].bonus_per_rank*rank for sid,rank in self.skills.items() if SKILLS_BY_ID[sid].stat==stat),6)

def accessible_campaigns(completed):
    finished=set(completed)
    known=[]
    for game in sorted(GAMES, key=lambda x:x.chronological_order):
        if game.completed_campaign_required!='none' and game.completed_campaign_required not in finished:break
        known.append(game.id)
    return known

def can_fast_travel(state:HunterState, location:str)->bool:
    state.validate()
    return location in state.unlocked_locations and location.split(':',1)[0] in accessible_campaigns(state.completed_campaigns)

def loot_level(player_level:int, roll_bonus:int=0)->int:
    """Clamp drop to player level through +2. Rolls beyond cap stay at 300."""
    if not 1<=player_level<=MAX_LEVEL:raise ValueError('Invalid player level')
    if not 0<=roll_bonus<=2:raise ValueError('Only level through +2 permitted')
    return min(MAX_LEVEL,player_level+roll_bonus)

def session_compatible(states:list[HunterState], manifest_hashes:list[str])->bool:
    """Validation contract only; does not open a network connection or host a session."""
    if not states or len(states)!=len(manifest_hashes):return False
    if len(set(manifest_hashes))!=1:return False
    try:
        for s in states:s.validate()
    except ValueError:return False
    return True
