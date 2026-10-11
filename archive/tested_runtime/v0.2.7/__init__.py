"""UVH: manual Deathtrap boost, opt-in inert node test and loading diagnostics.

No automatic gameplay changes. The optional trace observes native calls without
blocking or overriding them. Node insertion writes shared definitions only on an
explicit menu button; keep a backed-up Gaige save and never buy the test node.
"""
import math
from mods_base import ButtonOption, CoopSupport, Game, build_mod, get_pc
from unrealsdk import logging

TAG = '[UVH-BOOST]'
EXTRA_SECONDS = 15.0
EXPECTED_DEFAULT = 60.0
MAX_DURATION = 180.0
_record = None


def log(message):
    logging.info('{} {}'.format(TAG, message))


def read(obj, field):
    try:
        return getattr(obj, field)
    except Exception:
        return None


def name(obj):
    return str(read(obj, 'Name') or '')


def finite_num(value):
    return type(value) in (float, int) and math.isfinite(value)


def near(a, b):
    return finite_num(a) and finite_num(b) and math.isclose(a, b, rel_tol=0, abs_tol=0.05)


def signature(skill):
    # Names sometimes get reused by UE; activation time distinguishes each summon.
    return (name(skill), read(skill, 'ActivatedTime'), name(read(skill, 'SkillInstigator')))


def find_live():
    """Return (skill, action, pc) for our own active Deathtrap or (None, ...)."""
    pc = get_pc(possibly_loading=True)
    if pc is None:
        log('No local controller. Load Gaige into a map.')
        return None, None, None
    if name(read(pc, 'PlayerClass')) != 'CharClass_Mechromancer':
        log('Not Gaige. No gameplay changes.')
        return None, None, pc
    action = read(read(pc, 'Pawn'), 'MyActionSkill')
    if name(read(action, 'Class')) != 'DeathtrapActionSkill':
        log('Deathtrap is not summoned. Summon first.')
        return None, action, pc
    try:
        manager = pc.GetSkillManager()
        skills = read(manager, 'ActiveSkills')
        count = len(skills)
    except Exception as exc:
        log('Could not access ActiveSkills ({})'.format(type(exc).__name__))
        return None, action, pc
    for i in range(min(count, 64)):
        try:
            skill = skills[i]
            if name(read(skill, 'Definition')) != 'Skill_DeathTrap':
                continue
            instigator = read(skill, 'SkillInstigator')
            if name(instigator) != name(pc) or not name(pc):
                log('Deathtrap skill owner did not match player controller; aborting.')
                return None, action, pc
            return skill, action, pc
        except Exception as exc:
            log('Could not read ActiveSkills[{}] ({})'.format(i, type(exc).__name__))
    log('No active Skill_DeathTrap instance found.')
    return None, action, pc


def display(skill):
    log('Skill={} | Grade={} | Duration={} | Base={} | ActivatedTime={} | modifiers={}'.format(
        name(skill), read(skill, 'Grade'), read(skill, 'Duration'),
        read(skill, 'DurationBaseValue'), read(skill, 'ActivatedTime'),
        _modifier_count(skill)))


def _modifier_count(skill):
    stack = read(skill, 'DurationModifierStack')
    if stack is None:
        return 'unavailable'
    try:
        return len(stack)
    except Exception:
        return 'unavailable'


def inspect(_option=None):
    log('BEGIN inspect v0.1.1')
    try:
        skill, _action, _pc = find_live()
        if skill is not None:
            display(skill)
            if _record is not None:
                log('Last test record: {} -> {} on {}'.format(
                    _record['before'], _record['after'], _record['sig']))
            else:
                log('No duration change recorded in this session.')
    except Exception as exc:
        log('ERROR inspect: {}: {}'.format(type(exc).__name__, str(exc)[:130]))
    finally:
        log('END inspect')


def apply(_option=None):
    global _record
    log('BEGIN experimental +15 seconds (live skill instance only)')
    try:
        skill, _action, _pc = find_live()
        if skill is None:
            return
        sig = signature(skill)
        if _record is not None:
            if sig == _record['sig']:
                log('NOT APPLIED: Already tested on this summon; prevents stacking.')
                display(skill)
                return
            log('Previous summon ended. Clearing stale duration record.')
            _record = None

        current = read(skill, 'Duration')
        base = read(skill, 'DurationBaseValue')
        modifier_count = _modifier_count(skill)
        display(skill)
        if not near(current, EXPECTED_DEFAULT) or not near(base, EXPECTED_DEFAULT):
            log('NOT APPLIED: Expected unmodified Duration and DurationBaseValue ~= 60.0.')
            return
        if modifier_count != 0:
            log('NOT APPLIED: Skill has duration modifiers or modifiers inaccessible.')
            return
        after = current + EXTRA_SECONDS
        if after > MAX_DURATION:
            log('NOT APPLIED: requested Duration exceeds safety limit.')
            return
        try:
            skill.Duration = float(after)
        except Exception as exc:
            log('WRITE REJECTED: {}: {}'.format(type(exc).__name__, str(exc)[:110]))
            return
        observed = read(skill, 'Duration')
        if not near(observed, after):
            log('WRITE NOT VERIFIED: expected {}, got {}; attempting rollback.'.format(after, observed))
            try:
                skill.Duration = current
            except Exception as rollback_exc:
                log('WARNING rollback failed: {}'.format(type(rollback_exc).__name__))
            return
        _record = {'sig': sig, 'before': current, 'after': after}
        log('WRITE VERIFIED: live Skill_DeathTrap.Duration {} -> {}'.format(current, observed))
        log('DurationBaseValue left unchanged. A successful write does not yet prove longer in-game lifespan.')
        log('No shared definitions, tree points, cooldown pools or saves changed.')
    except Exception as exc:
        log('ERROR apply: {}: {}'.format(type(exc).__name__, str(exc)[:130]))
    finally:
        log('END apply')


def restore(_option=None):
    global _record
    log('BEGIN restore live duration')
    try:
        if _record is None:
            log('Nothing to restore; no successful modification recorded.')
            return
        skill, _action, _pc = find_live()
        if skill is None or signature(skill) != _record['sig']:
            log('Original Deathtrap summon is no longer active. No other skill touched.')
            _record = None
            return
        current = read(skill, 'Duration')
        if not near(current, _record['after']):
            log('NOT RESTORED: current Duration {} changed independently; avoiding overwrite.'.format(current))
            _record = None
            return
        before = _record['before']
        skill.Duration = before
        checked = read(skill, 'Duration')
        if near(checked, before):
            log('RESTORED: live Skill_DeathTrap.Duration {} -> {}'.format(current, checked))
            _record = None
        else:
            log('RESTORE READBACK MISMATCH: got {}'.format(checked))
    except Exception as exc:
        log('ERROR restore: {}: {}'.format(type(exc).__name__, str(exc)[:130]))
    finally:
        log('END restore')




def _tree_info(val):
    if val is None:
        return '<none>'
    if type(val) in (str, int, bool, float):
        return repr(val)[:160]
    label = name(val)
    clazz = name(read(val, 'Class'))
    if label:
        return '{} [{}]'.format(label[:75], clazz[:75] or type(val).__name__)
    try:
        return '<{} len={}>'.format(type(val).__name__, len(val))
    except Exception:
        return '<{}>'.format(type(val).__name__)


def _tree_fields(label, obj):
    if obj is None:
        log('[UVH-TREE] {} unavailable'.format(label))
        return
    tokens = ('skill', 'tree', 'train', 'point', 'branch', 'grade', 'purchase', 'unlock', 'node')
    try:
        fields = sorted(set(k for k in dir(obj) if not k.startswith('_')
                            and any(t in k.lower() for t in tokens)))
    except Exception as exc:
        log('[UVH-TREE] {} names ERROR {}'.format(label, type(exc).__name__))
        return
    log('[UVH-TREE] {} matching names ({}): {}'.format(
        label, len(fields), ', '.join(fields[:85]) or '<none>'))
    for key in fields[:80]:
        try:
            val = getattr(obj, key)
            if callable(val):
                continue
            log('[UVH-TREE] {}.{} = {}'.format(label, key, _tree_info(val)))
            # Sample a few referenced tree/branch structs, without walking the entire graph.
            if any(x in key.lower() for x in ('tree', 'branch', 'node')) and not isinstance(val, (str, bytes)):
                if isinstance(val, (tuple, list)):
                    for i, entry in enumerate(val[:3]):
                        log('[UVH-TREE] {}.{}[{}] = {}'.format(label, key, i, _tree_info(entry)))
        except Exception as exc:
            log('[UVH-TREE] {}.{} READ ERROR {}'.format(label, key, type(exc).__name__))


def inspect_native_tree(_option=None):
    """Inspect native Gaige skill-tree access, never spend or mutate points."""
    log('[UVH-TREE] BEGIN v0.1.2 native tree/skill-point inspection (READ ONLY)')
    try:
        pc = get_pc(possibly_loading=True)
        if pc is None:
            log('[UVH-TREE] No player controller; load Gaige and retry.')
            return
        cls = read(pc, 'PlayerClass')
        if name(cls) != 'CharClass_Mechromancer':
            log('[UVH-TREE] Current class {} is not Gaige; skipping.'.format(name(cls)))
            return
        pri = read(pc, 'PlayerReplicationInfo')
        log('[UVH-TREE] Class={} SkillTreePath={}'.format(name(cls), _tree_info(read(cls, 'SkillTreePath'))))
        log('[UVH-TREE] GeneralSkillPoints={} SpecialistSkillPoints={}'.format(
            _tree_info(read(pri, 'GeneralSkillPoints')),
            _tree_info(read(pri, 'SpecialistSkillPoints'))))
        _tree_fields('PlayerClass', cls)
        _tree_fields('PlayerReplicationInfo', pri)
        _tree_fields('PlayerController', pc)
        try:
            import unrealsdk
            trees = unrealsdk.find_all('SkillTreeDefinition', exact=False)
            log('[UVH-TREE] Loaded SkillTreeDefinition count={}'.format(len(trees)))
            for i, tree in enumerate(trees):
                if i >= 16:
                    break
                log('[UVH-TREE] loadedTree[{}] = {}'.format(i, _tree_info(tree)))
                if 'mechro' in name(tree).lower() or 'gaige' in name(tree).lower():
                    _tree_fields('GaigeSkillTree', tree)
        except Exception as exc:
            log('[UVH-TREE] find_all SkillTreeDefinition ERROR {}: {}'.format(
                type(exc).__name__, str(exc)[:100]))
        log('[UVH-TREE] FINISHED; no new skill, point spending, save, or native UI modification.')
    except Exception as exc:
        log('[UVH-TREE] ERROR {}: {}'.format(type(exc).__name__, str(exc)[:120]))
    finally:
        log('[UVH-TREE] END')



# Native skill branches referenced by BL2 skill-tree patch mods.  We only inspect
# these objects (and their original packages); no asset or save property writes.
def _find_native(path, types=('Object',)):
    import unrealsdk
    for kind in types:
        try:
            obj = unrealsdk.find_object(kind, path)
            if obj is not None:
                return obj, kind
        except Exception:
            pass
    return None, None


def _native_describe(obj):
    if obj is None:
        return '<missing>'
    try:
        return '{} | {}'.format(_tree_info(obj), str(obj)[:190])
    except Exception:
        return _tree_info(obj)


def _read_tiers(label, obj):
    fields = ('Branches', 'Tiers', 'Skills', 'SkillTreeBranches', 'Layout',
              'RequiredPoints', 'PointsToUnlockNextTier', 'bCellIsOccupied',
              'SkillDefinition', 'SkillTree', 'SkillName', 'SkillDescription')
    for field in fields:
        value = read(obj, field)
        if value is None:
            continue
        log('[UVH-NODES] {}.{} = {}'.format(label, field, _native_describe(value)))
        if isinstance(value, (str, bytes)):
            continue
        try:
            count = len(value)
        except Exception:
            continue
        log('[UVH-NODES] {}.{} length={}'.format(label, field, count))
        for i in range(min(count, 7)):
            try:
                item = value[i]
                log('[UVH-NODES] {}.{}[{}] = {}'.format(label, field, i, _native_describe(item)))
                for nested in ('Skills', 'PointsToUnlockNextTier', 'bCellIsOccupied',
                               'SkillDefinition', 'SkillName'):
                    v = read(item, nested)
                    if v is not None:
                        log('[UVH-NODES] {}.{}[{}].{} = {}'.format(
                            label, field, i, nested, _native_describe(v)))
                        if nested in ('Skills', 'bCellIsOccupied'):
                            try:
                                for j in range(min(len(v), 4)):
                                    log('[UVH-NODES] {}.{}[{}].{}[{}] = {}'.format(
                                        label, field, i, nested, j, _native_describe(v[j])))
                            except Exception:
                                pass
            except Exception as exc:
                log('[UVH-NODES] {}.{}[{}] inspect failed {}'.format(
                    label, field, i, type(exc).__name__))


def inspect_native_branch_assets(_option=None):
    # Non-mutating asset/package check for Gaige native tree branches.
    log('[UVH-NODES] BEGIN v0.1.3 locate native Gaige tree/branches (NO SKILL EDITS)')
    try:
        pc = get_pc(possibly_loading=True)
        if pc is None or name(read(pc, 'PlayerClass')) != 'CharClass_Mechromancer':
            log('[UVH-NODES] Gaige not loaded; abort.')
            return
        import unrealsdk
        stream = read(read(pc, 'PlayerClass'), 'SkillTreePath')
        log('[UVH-NODES] PlayerClass.SkillTreePath = {}'.format(repr(stream)))
        objects = (
            ('TreeFromClass', stream, ('SkillTreeDefinition', 'Object')),
            ('BranchFriends', 'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_BestFriendsForever', ('Object',)),
            ('BranchTrouble', 'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble', ('Object',)),
            ('BranchChaos', 'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_OrderedChaos', ('Object',)),
            ('LayoutTrouble', 'GD_Tulip_Mechromancer_Skills.SkillTrees.Layout_LittleBigTrouble', ('Object',)),
        )
        for label, path, kinds in objects:
            if not isinstance(path, str) or not path:
                continue
            obj, kind = _find_native(path, kinds)
            log('[UVH-NODES] BEFORE {} {} => {}'.format(label, path, _native_describe(obj)))
        # The streaming package alone was not enough in prior trials.  Test the
        # distinct package used by native BL2 Gaige branch modders.
        pkg = 'GD_Tulip_Mechromancer_Skills'
        try:
            result = unrealsdk.load_package(pkg)
            log('[UVH-NODES] load_package({}) returned {} (None may be normal; verify objects below)'.format(
                pkg, _native_describe(result)))
        except Exception as exc:
            log('[UVH-NODES] load_package({}) raised {}: {}'.format(
                pkg, type(exc).__name__, str(exc)[:130]))
        resolved = 0
        for label, path, kinds in objects:
            if not isinstance(path, str) or not path:
                continue
            obj, kind = _find_native(path, kinds)
            log('[UVH-NODES] AFTER {} [{}] {} => {}'.format(
                label, kind or '-', path, _native_describe(obj)))
            if obj is not None:
                resolved += 1
                _read_tiers(label, obj)
        for class_kind in ('SkillTreeDefinition', 'SkillTreeBranchDefinition', 'SkillTreeBranchLayoutDefinition'):
            try:
                matches = unrealsdk.find_all(class_kind, exact=False)
                matches = [x for x in matches if name(x).lower().find('default__') != 0]
                log('[UVH-NODES] loaded {} count (non-default) = {}'.format(class_kind, len(matches)))
                for obj in matches[:12]:
                    log('[UVH-NODES] loaded {} => {}'.format(class_kind, _native_describe(obj)))
            except Exception as exc:
                log('[UVH-NODES] scan {} => {} {}'.format(class_kind, type(exc).__name__, str(exc)[:90]))
        log('[UVH-NODES] RESOLVED {} of 5 asset paths (0 is a diagnostic result, not a crash)'.format(resolved))
        log('[UVH-NODES] READ ONLY: no skill grade, points, HUD, save, or skill duration changed.')
    except Exception as exc:
        log('[UVH-NODES] ERROR {}: {}'.format(type(exc).__name__, str(exc)[:150]))
    finally:
        log('[UVH-NODES] END')



# Stage for a new, genuinely native skill-tree node: inspect object metadata,
# branch layout, and the SDK object creation API WITHOUT creating or modifying.
def inspect_node_blueprint(_option=None):
    log('[UVH-NODEPREP] BEGIN v0.1.5 inspect prerequisites for a NEW skill (read only)')
    try:
        pc = get_pc(possibly_loading=True)
        if pc is None or name(read(pc, 'PlayerClass')) != 'CharClass_Mechromancer':
            log('[UVH-NODEPREP] Load Gaige in a map first.')
            return
        import unrealsdk
        pairs = (
            ('LittleBigTrouble', 'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble',
             'GD_Tulip_Mechromancer_Skills.SkillTrees.Layout_LittleBigTrouble'),
            ('BestFriendsForever', 'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_BestFriendsForever',
             'GD_Tulip_Mechromancer_Skills.SkillTrees.Layout_BestFriendsForever'),
        )
        for branch_name, branch_path, layout_path in pairs:
            branch, _ = _find_native(branch_path, ('SkillTreeBranchDefinition', 'Object'))
            layout, _ = _find_native(layout_path, ('SkillTreeBranchLayoutDefinition', 'Object'))
            log('[UVH-NODEPREP] {}: branch={} layout={}'.format(
                branch_name, _native_describe(branch), _native_describe(layout)))
            if branch is None or layout is None:
                continue
            tiers = read(branch, 'Tiers')
            occupied_tiers = read(layout, 'Tiers')
            if tiers is None or occupied_tiers is None:
                log('[UVH-NODEPREP] {} missing Tiers properties'.format(branch_name))
                continue
            n = min(6, len(tiers), len(occupied_tiers))
            for i in range(n):
                try:
                    skills = read(tiers[i], 'Skills')
                    cells = read(occupied_tiers[i], 'bCellIsOccupied')
                    if skills is None or cells is None:
                        continue
                    contents = [name(s) for s in skills]
                    layout_slots = [bool(x) for x in cells]
                    log('[UVH-NODEPREP] {} tier={} skills={} cells={} (read-only)'.format(
                        branch_name, i, contents, layout_slots))
                    if len(layout_slots) == 3 and sum(layout_slots) == len(contents):
                        mapping = []
                        idx = 0
                        for col, used in enumerate(layout_slots):
                            mapping.append('{}:{}'.format(col, contents[idx] if used else '<empty>'))
                            if used:
                                idx += 1
                        log('[UVH-NODEPREP] {} tier={} map {}'.format(branch_name, i, ', '.join(mapping)))
                    else:
                        log('[UVH-NODEPREP] WARN tier={} skill count != occupied slots'.format(i))
                except Exception as exc:
                    log('[UVH-NODEPREP] Tier {} error {}: {}'.format(i, type(exc).__name__, str(exc)[:90]))
        # Compare a multi-rank native skill and a one-point skill to see which
        # minimum fields a separately created Deathtrap Overclock would need.
        samples = (
            ('multi-rank MorePep', 'GD_Tulip_Mechromancer_Skills.LittleBigTrouble.MorePep'),
            ('one-point ExplosiveClap', 'GD_Tulip_Mechromancer_Skills.BestFriendsForever.ExplosiveClap'),
        )
        for label, path in samples:
            obj, kind = _find_native(path, ('SkillDefinition', 'Object'))
            log('[UVH-NODEPREP] SAMPLE {} => {} (lookup kind {})'.format(label, _native_describe(obj), kind))
            if obj is None:
                continue
            try:
                keys = [k for k in dir(obj) if not k.startswith('_') and any(
                    needle in k.lower() for needle in (
                        'skill', 'icon', 'grade', 'effect', 'present', 'cost',
                        'point', 'description', 'name', 'dependency', 'unlock'))]
                log('[UVH-NODEPREP] SAMPLE {} fields={}'.format(label, ','.join(sorted(set(keys))[:90])))
            except Exception as exc:
                log('[UVH-NODEPREP] SAMPLE field listing failed {}'.format(type(exc).__name__))
            for attr in ('SkillName', 'SkillDescription', 'MaxGrade', 'DefaultStartingGrade',
                         'bSubjectToGradeRules', 'SkillIcon', 'SkillEffectDefinitions',
                         'SkillEffectPresentations', 'bCanBeDeactivated'):
                val = read(obj, attr)
                if val is None:
                    log('[UVH-NODEPREP] SAMPLE {}.{} = <not exposed>'.format(label,attr))
                else:
                    try:
                        length = len(val)
                        extra = ' length={}'.format(length)
                    except Exception:
                        extra = ''
                    log('[UVH-NODEPREP] SAMPLE {}.{} = {}{}'.format(
                        label,attr,_native_describe(val)[:170],extra))
        # Inspect, but NEVER invoke, object creation in this release.
        creator = getattr(unrealsdk, 'construct_object', None)
        log('[UVH-NODEPREP] SDK construct_object available={}'.format(callable(creator)))
        if callable(creator):
            try:
                import inspect
                log('[UVH-NODEPREP] SDK construct_object signature={}'.format(inspect.signature(creator)))
            except Exception as exc:
                log('[UVH-NODEPREP] SDK construct_object signature unavailable {}'.format(type(exc).__name__))
            log('[UVH-NODEPREP] SDK construct_object docs={}'.format(
                (getattr(creator, '__doc__', None) or '<none>')[:300].replace('\n', ' ')))
        log('[UVH-NODEPREP] FINISHED READ ONLY: no tree, layout, skills, points, or save mutated.')
    except Exception as exc:
        log('[UVH-NODEPREP] ERROR {}: {}'.format(type(exc).__name__,str(exc)[:160]))
    finally:
        log('[UVH-NODEPREP] END')



# v0.1.6: EXPERIMENTAL native skill node creation and branch insert.
# No save changes or point spending are performed by this mod.
# The new skill is intentionally inert until native UI/purchase handling is proven.
_uvh_node_state = None


def _node_first_tier():
    """Only use this exact verified Gaige branch and its unused middle column."""
    branch_path = 'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble'
    layout_path = 'GD_Tulip_Mechromancer_Skills.SkillTrees.Layout_LittleBigTrouble'
    branch, _ = _find_native(branch_path, ('SkillTreeBranchDefinition', 'Object'))
    layout, _ = _find_native(layout_path, ('SkillTreeBranchLayoutDefinition', 'Object'))
    if branch is None or layout is None:
        log('[UVH-NEWNODE] Missing assets: branch={} layout={}'.format(
            _native_describe(branch), _native_describe(layout)))
        return None
    try:
        btier = branch.Tiers[0]
        ltier = layout.Tiers[0]
        originals = [x for x in btier.Skills]
        occupied = [bool(x) for x in ltier.bCellIsOccupied]
        if [name(x) for x in originals] != ['MorePep', 'Myelin'] or occupied != [True, False, True]:
            log('[UVH-NEWNODE] First tier is not in expected pristine state; no writes.')
            return None
        return branch, layout, btier, ltier, originals, occupied
    except Exception as exc:
        log('[UVH-NEWNODE] Cannot inspect first tier: {}: {}'.format(type(exc).__name__, str(exc)[:110]))
        return None


def _node_has_exact_contents(btier, ltier, new):
    try:
        skills = [x for x in btier.Skills]
        flags = [bool(x) for x in ltier.bCellIsOccupied]
        return (len(skills) == 3 and
                name(skills[0]) == 'MorePep' and skills[1] == new and
                name(skills[2]) == 'Myelin' and flags == [True, True, True])
    except Exception:
        return False


def _node_set_array(owner, prop, values):
    """Try property array assignment; then element-level mutation if supported."""
    try:
        setattr(owner, prop, list(values))
        if list(getattr(owner, prop)) == list(values):
            return True, 'assign'
    except Exception as exc:
        log('[UVH-NEWNODE] {} assignment unsupported: {}: {}'.format(prop, type(exc).__name__, str(exc)[:90]))
    arr = read(owner, prop)
    if arr is None:
        return False, 'missing'
    try:
        arr[:] = list(values)
        if list(read(owner, prop)) == list(values):
            return True, 'slice'
    except Exception as exc:
        log('[UVH-NEWNODE] {} slice unsupported: {}'.format(prop, type(exc).__name__))
    try:
        # Useful for WrappedArray implementations supporting clear/extend.
        arr.clear()
        arr.extend(list(values))
        if list(read(owner, prop)) == list(values):
            return True, 'clear+extend'
    except Exception as exc:
        log('[UVH-NEWNODE] {} list methods unsupported: {}'.format(prop, type(exc).__name__))
    return False, 'unsupported'


def _node_restore_snapshot(record):
    """Restore both native branch and layout arrays and verify the readback."""
    btier, ltier = record['btier'], record['ltier']
    old_skills, old_cells = record['skills'], record['cells']
    success_skills, how_skills = _node_set_array(btier, 'Skills', old_skills)
    success_cells, how_cells = _node_set_array(ltier, 'bCellIsOccupied', old_cells)
    try:
        observed = [name(x) for x in btier.Skills]
        flags = [bool(x) for x in ltier.bCellIsOccupied]
        success = (success_skills and success_cells and
                   observed == ['MorePep', 'Myelin'] and flags == [True, False, True])
    except Exception:
        success = False
        observed, flags = '<cannot read>', '<cannot read>'
    log('[UVH-NEWNODE] RESTORE result={} skills={} cells={} (methods {}, {})'.format(
        success, observed, flags, how_skills, how_cells))
    if not success:
        log('[UVH-NEWNODE] SAFETY: Exit BL2 WITHOUT SAVING and restart before playing.')
    return success


def _node_make_candidate(branch):
    import unrealsdk
    template, _ = _find_native(
        'GD_Tulip_Mechromancer_Skills.LittleBigTrouble.MorePep', ('SkillDefinition', 'Object'))
    if template is None:
        log('[UVH-NEWNODE] Existing MorePep template missing.')
        return None
    # Creating inside a known UObject guarantees a valid Unreal outer even if
    # this SDK version does not expose UObject.Outer. Does NOT overwrite template.
    outer = read(template, 'Outer') or branch
    for path in (
        'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble.UVH_DeathtrapOverclock',
        'GD_Tulip_Mechromancer_Skills.LittleBigTrouble.UVH_DeathtrapOverclock',
    ):
        existing, _ = _find_native(path, ('Object',))
        if existing is not None:
            log('[UVH-NEWNODE] Candidate name already exists; restart before another test. No overwrite.')
            return None
    try:
        obj = unrealsdk.construct_object('SkillDefinition', outer, 'UVH_DeathtrapOverclock')
    except Exception as exc:
        log('[UVH-NEWNODE] construct_object FAILED {}: {}'.format(type(exc).__name__, str(exc)[:170]))
        return None
    if (obj is None or name(read(obj, 'Class')) != 'SkillDefinition'
            or name(obj) != 'UVH_DeathtrapOverclock' or obj == template):
        log('[UVH-NEWNODE] Candidate construction did not return SkillDefinition.')
        return None
    # Never copy another active skill's gameplay effects or activation actions.
    for attr in ('SkillEffectDefinitions', 'SkillActivationActions', 'SkillDeactivationActions'):
        val = read(obj, attr)
        try:
            if val is None or len(val) != 0:
                log('[UVH-NEWNODE] ABORT: candidate {} is missing or nonempty'.format(attr))
                return None
        except Exception:
            log('[UVH-NEWNODE] ABORT: cannot verify empty {}'.format(attr))
            return None
    requested = (
        ('SkillName', 'Deathtrap Overclock'),
        ('SkillDescription', 'Prototype: Extends Deathtrap duration by 15 seconds. (Not active in this node test.)'),
        ('MaxGrade', 1),
        ('DefaultStartingGrade', 0),
        ('bSubjectToGradeRules', True),
    )
    for prop, val in requested:
        try:
            setattr(obj, prop, val)
            if read(obj, prop) != val:
                log('[UVH-NEWNODE] {} readback mismatch; abort.'.format(prop))
                return None
        except Exception as exc:
            log('[UVH-NEWNODE] {} write failed {}: {}'.format(prop, type(exc).__name__, str(exc)[:95]))
            return None
    try:
        obj.SkillIcon = template.SkillIcon  # temporary built-in icon, not custom art
    except Exception as exc:
        log('[UVH-NEWNODE] Icon binding failed {}, continuing with no icon.'.format(type(exc).__name__))
    log('[UVH-NEWNODE] NEW SkillDefinition created: {} | max rank={} | effects=0'.format(
        _native_describe(obj), read(obj, 'MaxGrade')))
    return obj


def add_overclock_node(_option=None):
    global _uvh_node_state
    log('[UVH-NEWNODE] BEGIN v0.2.1 EARLY MENU node insertion (NO POINT SPENDING)')
    record = None
    try:
        if _init_armed or _init_hooks:
            log('[UVH-NEWNODE] NOT INSERTED: initialization experiment is armed; use its CANCEL button first.')
            return
        try:
            pc = get_pc(possibly_loading=True)
        except Exception:
            pc = None
        if pc is not None and read(pc, 'Pawn') is not None:
            log('[UVH-NEWNODE] NOT INSERTED: character already loaded. Return to the MAIN MENU and try there.')
            return
        log('[UVH-NEWNODE] Menu preflight: controller={} class={} pawn={}'.format(
            name(pc) or '<none>', name(read(pc, 'PlayerClass')) or '<none>',
            name(read(pc, 'Pawn')) or '<none>'))
        # The exact Gaige branch may not be in memory on the main menu.
        # Load its data package before accessing it, without changing saves.
        import unrealsdk
        try:
            pkg = unrealsdk.load_package('GD_Tulip_Mechromancer_Skills')
            log('[UVH-NEWNODE] load_package completed; returned {} (None is not necessarily failure)'.format(
                _tree_info(pkg)))
        except Exception as exc:
            log('[UVH-NEWNODE] load_package raised {}: {}'.format(type(exc).__name__, str(exc)[:140]))
        if _uvh_node_state is not None:
            log('[UVH-NEWNODE] Already inserted this session; will not stack.')
            return
        objects = _node_first_tier()
        if objects is None:
            log('[UVH-NEWNODE] Gaige skill assets unavailable at main menu or unexpected layout; no changes made.')
            return
        branch, layout, btier, ltier, originals, occupied = objects
        new = _node_make_candidate(branch)
        if new is None:
            return
        record = dict(btier=btier, ltier=ltier, skills=originals, cells=occupied, node=new)
        wanted = [originals[0], new, originals[1]]
        s_ok, s_method = _node_set_array(btier, 'Skills', wanted)
        l_ok, l_method = _node_set_array(ltier, 'bCellIsOccupied', [True, True, True])
        # Confirm through a fresh native lookup too, not just the local struct proxy.
        re_branch, _ = _find_native(
            'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble',
            ('SkillTreeBranchDefinition', 'Object'))
        re_layout, _ = _find_native(
            'GD_Tulip_Mechromancer_Skills.SkillTrees.Layout_LittleBigTrouble',
            ('SkillTreeBranchLayoutDefinition', 'Object'))
        observed_live = (re_branch is not None and re_layout is not None and
                         _node_has_exact_contents(re_branch.Tiers[0], re_layout.Tiers[0], new))
        if not s_ok or not l_ok or not _node_has_exact_contents(btier, ltier, new) or not observed_live:
            log('[UVH-NEWNODE] INSERT NOT VERIFIED: skills={}, layout={}; rolling back.'.format(s_ok, l_ok))
            _node_restore_snapshot(record)
            return
        _uvh_node_state = record
        log('[UVH-NEWNODE] INSERT VERIFIED: Tier0=[MorePep, DeathtrapOverclock, Myelin]')
        log('[UVH-NEWNODE] Layout.Tier0=[True, True, True] (methods {}, {})'.format(s_method,l_method))
        log('[UVH-NEWNODE] Visual test only! DO NOT BUY the new node. 15s bonus still via manual button.')
        log('[UVH-NEWNODE] Now load Gaige via CONTINUE (do not buy node); inspect Skills tab.')
    except Exception as exc:
        log('[UVH-NEWNODE] ERROR {}: {}'.format(type(exc).__name__, str(exc)[:160]))
        if record is not None and _uvh_node_state is None:
            _node_restore_snapshot(record)
    finally:
        log('[UVH-NEWNODE] END')


def remove_overclock_node(_option=None):
    global _uvh_node_state
    log('[UVH-NEWNODE] BEGIN remove prototype node')
    try:
        if _uvh_node_state is None:
            log('[UVH-NEWNODE] Nothing added by this mod session.')
            return
        record = _uvh_node_state
        if 'init_tree' in record:
            cancel_init_node()
            return
        if not _node_has_exact_contents(record['btier'], record['ltier'], record['node']):
            log('[UVH-NEWNODE] Other modifications detected; will not overwrite them. Restart game.')
            return
        if _node_restore_snapshot(record):
            _uvh_node_state = None
            log('[UVH-NEWNODE] Prototype node removed; original tree restored.')
    except Exception as exc:
        log('[UVH-NEWNODE] Removal ERROR {}: {}'.format(type(exc).__name__, str(exc)[:160]))
    finally:
        log('[UVH-NEWNODE] END remove')


def check_overclock_preload(_option=None):
    """Read-only comparison of the *current* native branch with the insertion snapshot."""
    log('[UVH-PRELOAD] BEGIN check current tree state (READ ONLY)')
    try:
        try:
            pc = get_pc(possibly_loading=True)
        except Exception:
            pc = None
        log('[UVH-PRELOAD] Controller={} class={} pawn={}'.format(
            name(pc) or '<none>', name(read(pc, 'PlayerClass')) or '<none>',
            name(read(pc, 'Pawn')) or '<none>'))
        branch, _ = _find_native(
            'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble',
            ('SkillTreeBranchDefinition','Object'))
        layout, _ = _find_native(
            'GD_Tulip_Mechromancer_Skills.SkillTrees.Layout_LittleBigTrouble',
            ('SkillTreeBranchLayoutDefinition','Object'))
        if branch is None or layout is None:
            log('[UVH-PRELOAD] Branch/layout not loaded in current world; no writes.')
            return
        skills = list(branch.Tiers[0].Skills)
        cells = [bool(x) for x in layout.Tiers[0].bCellIsOccupied]
        log('[UVH-PRELOAD] CURRENT branch={} skills={} layout={}'.format(
            _native_describe(branch), [name(x) for x in skills], cells))
        if _uvh_node_state is not None:
            record = _uvh_node_state
            log('[UVH-PRELOAD] State saved: current branch is same object={} node still in current tree={}'.format(
                branch == record['btier'] or branch.Tiers[0] == record['btier'],
                len(skills) == 3 and skills[1] == record['node']))
        else:
            log('[UVH-PRELOAD] No node inserted by this mod session.')
        # Check the streaming tree too, but never attempt to edit it.
        try:
            obj, _ = _find_native(
                'GD_Tulip_Mechro_Streaming.SkillTree.SkillTree_Mechromancer',
                ('SkillTreeDefinition','Object'))
            log('[UVH-PRELOAD] Top-level streaming SkillTreeDefinition = {}'.format(_native_describe(obj)))
        except Exception as exc:
            log('[UVH-PRELOAD] Top-level inspection {}: {}'.format(type(exc).__name__,str(exc)[:100]))
    except Exception as exc:
        log('[UVH-PRELOAD] ERROR {}: {}'.format(type(exc).__name__,str(exc)[:160]))
    finally:
        log('[UVH-PRELOAD] END')

# v0.1.8 diagnostics never load packages, construct skills, call native gameplay
# functions, or write UObject/struct properties. SDK _path_name is a metadata API.
_DIAG_PATHS = (
    ('StreamingTree', 'SkillTreeDefinition',
     'GD_Tulip_Mechro_Streaming.SkillTree.SkillTree_Mechromancer'),
    ('TroubleBranch', 'SkillTreeBranchDefinition',
     'GD_Tulip_Mechromancer_Skills.SkillTrees.Branch_LittleBigTrouble'),
    ('TroubleLayout', 'SkillTreeBranchLayoutDefinition',
     'GD_Tulip_Mechromancer_Skills.SkillTrees.Layout_LittleBigTrouble'),
    ('MorePep', 'SkillDefinition',
     'GD_Tulip_Mechromancer_Skills.LittleBigTrouble.MorePep'),
)
_trace_hooks = []
_trace_hits = {}
_trace_events = 0
_trace_busy = False
_TRACE_EVENT_LIMIT = 24
_TRACE_FUNCTION_LIMIT = 8


def _diag_path(obj):
    try:
        return obj._path_name()
    except Exception:
        return str(obj)[:220] if obj is not None else '<missing>'


def _diag_refs(label, obj):
    """Inspect bounded tree references, including SDK WrappedArray values."""
    if obj is None:
        return
    try:
        fields = sorted(k for k in dir(obj) if not k.startswith('_') and
                        any(t in k.lower() for t in ('skilltree', 'branch', 'layout')))
        for key in fields[:16]:
            val = read(obj, key)
            if callable(val):
                continue
            log('[UVH-LOAD] {}.{} = {}'.format(label, key, _native_describe(val)))
            if val is None or isinstance(val, (str, bytes)):
                continue
            try:
                for i in range(min(len(val), 4)):
                    entry = val[i]
                    log('[UVH-LOAD] {}.{}[{}] = {}'.format(
                        label, key, i, _native_describe(entry)))
                    for ref in ('Branch', 'Layout', 'SkillTree', 'SkillTreeDefinition'):
                        nested = read(entry, ref)
                        if nested is not None and not callable(nested):
                            log('[UVH-LOAD] {}.{}[{}].{} = {}'.format(
                                label, key, i, ref, _native_describe(nested)))
            except (TypeError, AttributeError):
                pass
    except Exception as exc:
        log('[UVH-LOAD] {} reference inspection ERROR {}'.format(label, type(exc).__name__))


def _diag_state(label):
    try:
        pc = get_pc(possibly_loading=True)
    except Exception:
        pc = None
    log('[UVH-LOAD] STAGE {} controller={} class={} pawn={}'.format(
        label, name(pc) or '<none>', name(read(pc, 'PlayerClass')) or '<none>',
        name(read(pc, 'Pawn')) or '<none>'))
    for title, kind, path in _DIAG_PATHS:
        obj, found_kind = _find_native(path, (kind, 'Object'))
        log('[UVH-LOAD] {} found={} via={} object={}'.format(
            title, obj is not None, found_kind or '-', _native_describe(obj)))
        if title in ('TroubleBranch', 'TroubleLayout') and obj is not None:
            try:
                tier = obj.Tiers[0]
                if title == 'TroubleBranch':
                    values = [name(x) for x in tier.Skills]
                else:
                    values = [bool(x) for x in tier.bCellIsOccupied]
                log('[UVH-LOAD] {} Tier0={}'.format(title, values))
            except Exception as exc:
                log('[UVH-LOAD] {} Tier0 unreadable: {}'.format(title, type(exc).__name__))


def _diag_dump_live(label, obj, depth=3, budget=None, ancestors=()):
    """Bounded field/sequence inspection; never call a reflected function."""
    if obj is None:
        log('[UVH-LIVE] {} unavailable'.format(label))
        return
    if budget is None:
        budget = [120]
    if budget[0] <= 0:
        return
    path = _diag_path(obj) if name(read(obj, 'Class')) else None
    kind = name(read(obj, 'Class'))
    if kind.endswith('PlayerController') or kind in ('WorldInfo', 'SkillDefinition', 'SkillTreeDefinition',
                                   'SkillTreeBranchDefinition', 'SkillTreeBranchLayoutDefinition',
                                   'Class', 'ScriptStruct'):
        log('[UVH-LIVE] {} asset/type reference={}'.format(label, path))
        return
    if path is not None and path in ancestors:
        return
    if path is not None:
        ancestors = ancestors + (path,)
    try:
        fields = [key for key in dir(obj) if not key.startswith('_')]
        # Prioritize native tree data over metadata when the budget is exhausted.
        fields.sort(key=lambda key: (not any(t in key.lower() for t in
                    ('branch', 'tier', 'skill', 'root', 'node', 'definition', 'layout')), key))
        log('[UVH-LIVE] {} object={} fields={}'.format(
            label, _native_describe(obj), ', '.join(fields[:80])[:1800]))
        for key in fields:
            if budget[0] <= 0:
                break
            try:
                value = getattr(obj, key)
            except Exception as exc:
                budget[0] -= 1
                log('[UVH-LIVE] {}.{} READ ERROR {}'.format(label, key, type(exc).__name__))
                continue
            if callable(value):
                continue
            budget[0] -= 1
            log('[UVH-LIVE] {}.{} = {}'.format(label, key, _native_describe(value)))
            if depth <= 0 or value is None or isinstance(value, (str, bytes, bool, int, float)):
                continue
            # Report backlinks but never traverse the controller/world or type graph.
            if key.lower() in ('class', 'outer', 'owner', 'controller', 'playercontroller',
                                'world', 'parent', 'instigator', 'skilltreelisteners') or key.startswith('VfTable_'):
                continue
            try:
                count = len(value)
            except (TypeError, AttributeError):
                _diag_dump_live(label + '.' + key, value, depth - 1, budget, ancestors)
                continue
            log('[UVH-LIVE] {}.{} count={}'.format(label, key, count))
            for i in range(min(count, 4)):
                if budget[0] <= 0:
                    break
                budget[0] -= 1
                entry = value[i]
                child_label = '{}.{}[{}]'.format(label, key, i)
                log('[UVH-LIVE] {} = {}'.format(child_label, _native_describe(entry)))
                if entry is not None and not isinstance(entry, (str, bytes, bool, int, float)):
                    _diag_dump_live(child_label, entry, depth - 1, budget, ancestors)
    except Exception as exc:
        log('[UVH-LIVE] {} inspection ERROR {}'.format(label, type(exc).__name__))


def _diag_player_tree(pc):
    tree = read(pc, 'PlayerSkillTree')
    log('[UVH-LIVE] PlayerSkillTree = {}'.format(_native_describe(tree)))
    if name(read(pc, 'PlayerClass')) != 'CharClass_Mechromancer' or tree is None:
        log('[UVH-LIVE] No live Gaige player tree to inspect; no writes.')
        return
    if name(read(tree, 'Class')) != 'PlayerSkillTree':
        log('[UVH-LIVE] Unexpected player tree class; skipping traversal.')
        return
    _diag_dump_live('PlayerSkillTree', tree)


def inspect_tree_loading(_option=None):
    """Manual read-only snapshot; safe even when Gaige assets are not loaded."""
    log('[UVH-LOAD] BEGIN v0.2.1 loading snapshot (READ ONLY; no package loads)')
    try:
        import unrealsdk
        _diag_state('manual snapshot')
        try:
            pc = get_pc(possibly_loading=True)
        except Exception:
            pc = None
        _diag_refs('PlayerClass', read(pc, 'PlayerClass'))
        _diag_refs('PlayerController', pc)
        _diag_player_tree(pc)
        for kind in ('SkillTreeDefinition', 'SkillTreeBranchDefinition',
                     'SkillTreeBranchLayoutDefinition'):
            total, relevant = 0, 0
            try:
                for obj in unrealsdk.find_all(kind, exact=False):
                    if name(obj).lower().startswith('default__'):
                        continue
                    total += 1
                    path = _diag_path(obj)
                    if not any(t in path.lower() for t in ('tulip', 'mechro', 'gaige')):
                        continue
                    relevant += 1
                    if relevant <= 8:
                        log('[UVH-LOAD] Loaded {} path={}'.format(kind, path))
                        _diag_refs(kind, obj)
                log('[UVH-LOAD] {} total={} GaigeMatches={}'.format(kind, total, relevant))
            except Exception as exc:
                log('[UVH-LOAD] {} scan ERROR {}'.format(kind, type(exc).__name__))
    except Exception as exc:
        log('[UVH-LOAD] Snapshot ERROR {}: {}'.format(type(exc).__name__, str(exc)[:120]))
    finally:
        log('[UVH-LOAD] END snapshot; no points, definitions or saves changed')


def _trace_hook_path(func):
    """Accept canonical Class:Function and the dot-form metadata fallback."""
    path = _diag_path(func)
    separator = ':' if ':' in path else '.'
    owner, sep, method = path.rpartition(separator)
    # Exclude state/nested paths and objects outside WillowGame.
    if (not sep or not owner.startswith('WillowGame.') or owner.count('.') != 1
            or ':' in owner or method != name(func)):
        return None
    return owner + ':' + method


def _trace_candidates():
    """Only hook functions discovered in live metadata, never guessed paths."""
    import unrealsdk
    found = set()
    scanned, relevant = 0, 0
    for func in unrealsdk.find_all('Function', exact=False):
        scanned += 1
        owner = name(read(func, 'Outer')).lower()
        method = name(func).lower()
        if 'skilltree' not in owner and 'skilltree' not in method:
            continue
        relevant += 1
        if relevant <= 24:
            log('[UVH-TRACE] Raw function path={} owner={} method={}'.format(
                _diag_path(func), owner, method))
        if not any(t in method for t in ('init', 'setup', 'populate', 'create',
                                        'start', 'load', 'refresh', 'show')):
            continue
        path = _trace_hook_path(func)
        if path is not None:
            found.add(path)
    log('[UVH-TRACE] Function scan total={} treeMatches={} usable={}'.format(
        scanned, relevant, len(found)))
    return sorted(found, key=lambda path: ('init' not in path.rsplit(':', 1)[-1].lower(), path))


def stop_tree_trace(_option=None):
    """Remove only this mod's observers; retain failures for a retry."""
    global _trace_hooks
    if not _trace_hooks:
        log('[UVH-TRACE] No observers active.')
        return
    import unrealsdk
    pending = []
    for path, phase, identifier in _trace_hooks:
        try:
            unrealsdk.hooks.remove_hook(path, phase, identifier)
            if unrealsdk.hooks.has_hook(path, phase, identifier):
                pending.append((path, phase, identifier))
        except Exception as exc:
            pending.append((path, phase, identifier))
            log('[UVH-TRACE] Removal ERROR {}: {}'.format(path, type(exc).__name__))
    _trace_hooks = pending
    log('[UVH-TRACE] STOP remaining={}; events={}'.format(len(pending), _trace_events))
    if pending:
        log('[UVH-TRACE] Restart BL2 to clear remaining read-only observers.')


def _trace_callback(path, phase):
    def observe(obj, args, ret, func):
        global _trace_events, _trace_busy
        if _trace_busy or _trace_events >= _TRACE_EVENT_LIMIT:
            return None
        key = (path, phase)
        if _trace_hits.get(key, 0) >= 2:
            return None
        _trace_hits[key] = _trace_hits.get(key, 0) + 1
        _trace_events += 1
        _trace_busy = True
        try:
            log('[UVH-TRACE] EVENT {} {} {} owner={}'.format(
                _trace_events, phase, path, _native_describe(obj)))
            _diag_state('{} {}'.format(phase, path))
            _diag_refs('CallOwner', obj)
            _diag_refs('CallArgs', args)
            if _trace_events == _TRACE_EVENT_LIMIT:
                log('[UVH-TRACE] Event limit reached; further events ignored. Use STOP TRACE.')
        except Exception as exc:
            log('[UVH-TRACE] Observer ERROR {}'.format(type(exc).__name__))
        finally:
            _trace_busy = False
        # Never Block, override a return, invoke func, or write args/obj.
        return None
    return observe


def start_tree_trace(_option=None):
    global _trace_events
    log('[UVH-TRACE] BEGIN explicit read-only initialization trace')
    if _skillstate_context is not None or _skillstate_hooks:
        log('[UVH-TRACE] Stop the focused skill-state trace first.')
        return
    if _trace_hooks:
        log('[UVH-TRACE] Already active; use STOP TRACE before restarting.')
        return
    try:
        import unrealsdk
        candidates = _trace_candidates()
        log('[UVH-TRACE] Discovered candidates={}'.format(len(candidates)))
        for path in candidates[:20]:
            log('[UVH-TRACE] Candidate {}'.format(path))
        _trace_events = 0
        _trace_hits.clear()
        for path in candidates[:_TRACE_FUNCTION_LIMIT]:
            for label, phase in (('PRE', unrealsdk.hooks.Type.PRE),
                                 ('POST', unrealsdk.hooks.Type.POST)):
                identifier = 'UVH_v020_loading_' + label
                if unrealsdk.hooks.add_hook(path, phase, identifier, _trace_callback(path, label)):
                    _trace_hooks.append((path, phase, identifier))
        log('[UVH-TRACE] Active observers={}; event limit={}'.format(
            len(_trace_hooks), _TRACE_EVENT_LIMIT))
        if not _trace_hooks:
            log('[UVH-TRACE] No usable initialization functions loaded. Take snapshots at menu and in Gaige map.')
    except Exception as exc:
        log('[UVH-TRACE] Setup ERROR {}: {}'.format(type(exc).__name__, str(exc)[:120]))
        stop_tree_trace()


# v0.2.1: retain the observed Initialize path and verify solo using both rosters.
# No hooks are installed automatically. Arming permits one Gaige initialization.
_INIT_PATH = 'WillowGame.PlayerSkillTree:Initialize'
_INIT_TREE_PATH = 'GD_Tulip_Mechro_Streaming.SkillTree.SkillTree_Mechromancer'
_init_hooks = []
_init_armed = False
_init_consumed = False
_init_target = None


def _init_remove_hooks():
    global _init_hooks
    import unrealsdk
    pending = []
    for phase, identifier in _init_hooks:
        try:
            unrealsdk.hooks.remove_hook(_INIT_PATH, phase, identifier)
            if unrealsdk.hooks.has_hook(_INIT_PATH, phase, identifier):
                pending.append((phase, identifier))
        except Exception as exc:
            pending.append((phase, identifier))
            log('[UVH-INITNODE] Hook removal ERROR {}'.format(type(exc).__name__))
    _init_hooks = pending
    log('[UVH-INITNODE] Observers remaining={}'.format(len(pending)))
    if pending:
        log('[UVH-INITNODE] Restart BL2 to clear remaining observers; insertion is disarmed.')


def _init_rollback(record):
    """Restore native snapshots; the engine-built player cache needs a restart."""
    global _uvh_node_state
    try:
        if (list(record['btier'].Skills) != record['owned_skills']
                or list(record['ltier'].bCellIsOccupied) != record['owned_cells']):
            log('[UVH-INITNODE] Native arrays changed independently; refusing rollback overwrite. Restart BL2.')
            return False
    except Exception:
        log('[UVH-INITNODE] Cannot verify rollback ownership; snapshot retained. Restart BL2.')
        return False
    if _node_restore_snapshot(record):
        if _uvh_node_state is record:
            _uvh_node_state = None
        log('[UVH-INITNODE] NATIVE ARRAYS RESTORED. Restart BL2 to clear any player/UI cache.')
        return True
    record['restore_failed'] = True
    try:
        record['owned_skills'] = list(record['btier'].Skills)
        record['owned_cells'] = list(record['ltier'].bCellIsOccupied)
    except Exception:
        pass
    log('[UVH-INITNODE] Rollback failed; snapshot retained. Do not continue playing; restart BL2.')
    return False


def _init_solo_session(pc):
    """Read SDK enum and two player rosters; unknown/loading state never permits writes."""
    try:
        import unrealsdk
        from mods_base import ENGINE
        world = pc.WorldInfo
        mode = world.NetMode
        if not isinstance(mode, int) or isinstance(mode, bool):
            raise ValueError('NetMode is unavailable or not an integer enum')
        modes = unrealsdk.find_enum('ENetMode')
        if mode == modes.NM_Standalone:
            role = 'standalone'
        elif mode == modes.NM_ListenServer:
            role = 'listen_host'
        else:
            log('[UVH-INITNODE] ABORT: unsupported session NetMode={}; no writes.'.format(mode))
            return False
        # mods_base uses GamePlayers.Actor for get_pc; SDK networking uses GRI.PRIArray
        # as the join/leave roster. A host role alone does not establish solo play.
        local_players = ENGINE.GamePlayers
        local_count = len(local_players)
        own_pri = pc.PlayerReplicationInfo
        roster = world.GRI.PRIArray
        roster_count = len(roster)
        local_matches = local_count == 1 and local_players[0].Actor == pc
        roster_matches = (own_pri is not None and roster_count == 1
                          and roster[0] == own_pri and own_pri.Owner == pc)
        log('[UVH-INITNODE] SESSION role={} local_players={} roster_players={} local_matches={} roster_matches={}'.format(
            role, local_count, roster_count, local_matches, roster_matches))
        if not local_matches or not roster_matches:
            log('[UVH-INITNODE] ABORT: exactly one owned local/roster player not verified; no writes.')
            return False
        return True
    except Exception as exc:
        log('[UVH-INITNODE] ABORT: session evidence unavailable {}: {}; no writes.'.format(
            type(exc).__name__, str(exc)[:160]))
        return False


def _init_pre(obj, args, ret, func):
    global _init_armed, _init_consumed, _init_target, _uvh_node_state
    if not _init_armed:
        return None
    record = None
    try:
        pc = get_pc(possibly_loading=True)
        if name(read(pc, 'PlayerClass')) != 'CharClass_Mechromancer':
            log('[UVH-INITNODE] Ignoring initialization for another class; no writes.')
            return None
        _init_armed = False
        _init_consumed = True
        _init_target = obj
        net_mode = read(read(pc, 'WorldInfo'), 'NetMode')
        log('[UVH-INITNODE] PRE Gaige initialization: net_mode={} pawn={}'.format(
            net_mode, name(read(pc, 'Pawn')) or '<none>'))
        if not _init_solo_session(pc):
            return None
        tree_def = read(args, 'SkillTreeDef')
        if (name(read(obj, 'Class')) != 'PlayerSkillTree' or read(obj, 'Outer') != pc
                or read(pc, 'Pawn') is not None or len(obj.Branches) != 0
                or name(read(tree_def, 'Class')) != 'SkillTreeDefinition'
                or _diag_path(tree_def) != _INIT_TREE_PATH):
            log('[UVH-INITNODE] ABORT: unexpected owner, initialization state or SkillTreeDef={}; no writes.'.format(
                _native_describe(tree_def)))
            return None
        if _uvh_node_state is not None:
            log('[UVH-INITNODE] ABORT: another node test is already recorded; no writes.')
            return None
        objects = _node_first_tier()
        if objects is None:
            log('[UVH-INITNODE] ABORT: native tier unavailable/unexpected at Initialize; no writes.')
            return None
        branch, layout, btier, ltier, originals, occupied = objects
        template, _ = _find_native(
            'GD_Tulip_Mechromancer_Skills.LittleBigTrouble.MorePep', ('SkillDefinition',))
        if (name(read(branch, 'Class')) != 'SkillTreeBranchDefinition'
                or name(read(layout, 'Class')) != 'SkillTreeBranchLayoutDefinition'
                or read(branch, 'Layout') != layout or len(branch.Tiers) != 6
                or len(layout.Tiers) != 6 or originals[0] != template):
            log('[UVH-INITNODE] ABORT: branch/layout identity or six-tier shape mismatch; no writes.')
            return None
        node = _node_make_candidate(branch)
        if node is None:
            return None
        record = dict(branch=branch, layout=layout, btier=btier, ltier=ltier,
                      skills=originals, cells=occupied, node=node,
                      init_tree=obj, restore_failed=False,
                      owned_skills=list(originals), owned_cells=list(occupied))
        # Keep the rollback snapshot before the first shared-definition write.
        _uvh_node_state = record
        skills_ok, _ = _node_set_array(btier, 'Skills', [originals[0], node, originals[1]])
        record['owned_skills'] = list(btier.Skills)
        cells_ok, _ = _node_set_array(ltier, 'bCellIsOccupied', [True, True, True])
        record['owned_cells'] = list(ltier.bCellIsOccupied)
        if not skills_ok or not cells_ok or not _node_has_exact_contents(branch.Tiers[0], layout.Tiers[0], node):
            log('[UVH-INITNODE] INSERT NOT VERIFIED; rolling native arrays back.')
            _init_rollback(record)
            return None
        log('[UVH-INITNODE] PRE INSERT VERIFIED before native PlayerSkillTree.Initialize; node is inert, grade 0.')
    except Exception as exc:
        log('[UVH-INITNODE] PRE ERROR {}: {}'.format(type(exc).__name__, str(exc)[:120]))
        _init_armed = False
        if record is not None:
            _init_rollback(record)
    # Let the engine build the player tree normally. Never call func or edit args.
    return None


def inspect_init_node(_option=None):
    """Read the native patch and runtime registration without spending points."""
    log('[UVH-INITNODE] BEGIN current result (READ ONLY)')
    try:
        log('[UVH-INITNODE] armed={} consumed={} hooks={}'.format(
            _init_armed, _init_consumed, len(_init_hooks)))
        record = _uvh_node_state
        if record is None or 'init_tree' not in record:
            log('[UVH-INITNODE] No initialization insertion recorded.')
            pc = get_pc(possibly_loading=True)
            if name(read(pc, 'PlayerClass')) == 'CharClass_Mechromancer':
                _init_solo_session(pc)  # Useful if the PRE roster was not yet available.
            return False
        pc = get_pc(possibly_loading=True)
        tree = record['init_tree']
        if (name(read(pc, 'PlayerClass')) != 'CharClass_Mechromancer'
                or read(tree, 'Outer') != pc):
            log('[UVH-INITNODE] Original Gaige tree is no longer owned by current controller; no traversal.')
            return False
        if not _init_solo_session(pc):
            log('[UVH-INITNODE] Current session no longer verifies solo; cancel and restart BL2.')
            return False
        native_ok = _node_has_exact_contents(record['branch'].Tiers[0], record['layout'].Tiers[0], record['node'])
        skills = read(tree, 'Skills')
        if skills is None or len(skills) > 256:
            log('[UVH-INITNODE] Runtime Skills array unavailable/unexpected. UI visibility unverified.')
            return False
        definitions = []
        matches = []
        for entry in skills:
            definition = read(entry, 'Definition')
            definitions.append(definition)
            if definition == record['node']:
                matches.append(entry)
        runtime_ok = (len(matches) == 1 and all(old in definitions for old in record['skills']))
        log('[UVH-INITNODE] RESULT native={} runtime_node_count={} original_skills_present={} total_runtime_skills={}'.format(
            native_ok, len(matches), all(old in definitions for old in record['skills']), len(skills)))
        for entry in matches:
            _diag_dump_live('OverclockRuntimeEntry', entry, depth=1, budget=[24])
        for branch_entry in read(tree, 'Branches') or ():
            if read(branch_entry, 'Definition') == record['branch']:
                indices = read(branch_entry, 'TierIndices')
                if indices is not None and len(indices):
                    _diag_dump_live('TroubleRuntimeTier0', tree.Tiers[indices[0]], depth=1, budget=[32])
                break
        log('[UVH-INITNODE] Data readback is not proof of visibility. Inspect Little Big Trouble; DO NOT BUY NODE.')
        return native_ok and runtime_ok
    except Exception as exc:
        log('[UVH-INITNODE] Result inspection ERROR {}: {}'.format(type(exc).__name__, str(exc)[:120]))
        return False
    finally:
        log('[UVH-INITNODE] END current result')


def _init_post(obj, args, ret, func):
    global _init_target
    if obj != _init_target:
        return None
    try:
        if _uvh_node_state is not None and read(_uvh_node_state.get('init_tree'), 'Outer') is not None:
            verified = inspect_init_node()
            if not verified:
                log('[UVH-INITNODE] Runtime node not verified; restore native arrays and restart before playing.')
                _init_rollback(_uvh_node_state)
    except Exception as exc:
        log('[UVH-INITNODE] POST ERROR {}'.format(type(exc).__name__))
    finally:
        _init_target = None
        _init_remove_hooks()
    return None


def arm_init_node(_option=None):
    global _init_armed
    log('[UVH-INITNODE] BEGIN arm ONE inert Gaige initialization experiment')
    try:
        pc = get_pc(possibly_loading=True)
        if read(pc, 'Pawn') is not None or read(pc, 'PlayerSkillTree') is not None:
            log('[UVH-INITNODE] NOT ARMED: return to main menu before loading Gaige.')
            return
        if _init_consumed or _uvh_node_state is not None:
            log('[UVH-INITNODE] NOT ARMED: restart BL2 for each experiment; a test/state already exists.')
            return
        if _init_hooks:
            log('[UVH-INITNODE] Already armed or observers need removal; use CANCEL.')
            return
        import unrealsdk
        for label, phase, callback in (
            ('PRE', unrealsdk.hooks.Type.PRE, _init_pre),
            ('POST', unrealsdk.hooks.Type.POST_UNCONDITIONAL, _init_post),
        ):
            identifier = 'UVH_v021_init_node_' + label
            if not unrealsdk.hooks.add_hook(_INIT_PATH, phase, identifier, callback):
                raise RuntimeError('Observer identifier already registered')
            _init_hooks.append((phase, identifier))
        _init_armed = True
        log('[UVH-INITNODE] ARMED. Continue as backed-up Gaige SOLO; inspect Skills, never buy the node.')
        log('[UVH-INITNODE] No assets modified while arming. Native arrays and player cache require rollback/restart after test.')
    except Exception as exc:
        _init_armed = False
        log('[UVH-INITNODE] Arming ERROR {}: {}'.format(type(exc).__name__, str(exc)[:120]))
        _init_remove_hooks()


def cancel_init_node(_option=None):
    global _init_armed
    stop_skillstate_trace()
    stop_ui_trace()
    stop_upgrade_trace()
    _init_armed = False
    _init_remove_hooks()
    record = _uvh_node_state
    if record is not None and 'init_tree' in record:
        _init_rollback(record)
        log('[UVH-INITNODE] Restart BL2 now to discard the cached prototype tree. Do not buy the node.')
    else:
        log('[UVH-INITNODE] DISARMED; no initialization patch to restore.')


def _purchase_scalar(value):
    """Expose SDK IntFlag members without treating len(enum) as its value."""
    from enum import Enum
    if isinstance(value, Enum):
        return '{}.{} (value={})'.format(type(value).__name__, value.name or '<unnamed>', value.value)[:160]
    return _tree_info(value)


def _purchase_constraint_details(definition):
    """Bounded metadata/field reads; never evaluate a constraint or copy it."""
    label = name(definition)
    log('[UVH-PURCHASE] {}.LockedSkillDetailStr={}'.format(
        label, _purchase_scalar(read(definition, 'LockedSkillDetailStr'))))
    constraints = read(definition, 'SkillConstraints')
    try:
        if constraints is None:
            log('[UVH-PURCHASE] {} constraint details unavailable.'.format(label))
            return
        count = len(constraints)
        for index in range(min(count, 4)):
            constraint = constraints[index]
            struct_type = read(constraint, '_type')
            if (name(read(struct_type, 'Class')) != 'ScriptStruct'
                    or name(struct_type) != 'SkillConstraintData'):
                log('[UVH-PURCHASE] {}.SkillConstraints[{}] unverified struct type {}; not traversed.'.format(
                    label, index, name(struct_type) or '<unavailable>'))
                continue
            log('[UVH-PURCHASE] {}.SkillConstraints[{}] struct=SkillConstraintData'.format(label, index))
            try:
                for i, prop in enumerate(struct_type._properties()):
                    if i >= 8:
                        log('[UVH-PURCHASE] Constraint fields capped at 8.')
                        break
                    field = name(prop)
                    if not field or not field.isidentifier() or field.startswith('_'):
                        continue
                    value = read(constraint, field)
                    if callable(value):
                        continue
                    log('[UVH-PURCHASE] CONSTRAINT {}[{}].{} type={} value={}'.format(
                        label, index, field, name(read(prop, 'Class')), _purchase_scalar(value)))
            except Exception as exc:
                log('[UVH-PURCHASE] Constraint fields unavailable {}[{}]: {}'.format(label, index, type(exc).__name__))
        if count > 4:
            log('[UVH-PURCHASE] Constraints capped at 4 per definition.')
    except Exception as exc:
        log('[UVH-PURCHASE] Constraint details unavailable {}: {}'.format(label, type(exc).__name__))


def _purchase_function_metadata():
    """Discover UFunction metadata; never invoke, hook or alter a game function."""
    import unrealsdk
    priorities = ('CanUpgradeSkill', 'Flash_SetSkillPointProperties',
                  'Flash_SetSkillPointProperties_AS', 'GetSkillUpgradeCost',
                  'GetSkillState', 'GetSkillGradeByDef', 'GetSkillDescriptionForGrade',
                  'GetSkillGrade', 'GetSkillPointsSpentInTree')
    owners = ('PlayerSkillTree', 'WillowPlayerController', 'SkillTreeGFxObject')
    found = {}
    scanned = 0
    for func in unrealsdk.find_all('Function', exact=False):
        if scanned >= 30000:
            log('[UVH-PURCHASE] Metadata scan capped at 30000 objects; discovery may be incomplete.')
            break
        scanned += 1
        if (name(read(func, 'Class')) != 'Function'
                or name(read(func, 'Outer')) not in owners):
            continue
        method = name(func)
        if ('skill' not in method.lower() or not any(word in method.lower() for word in
                ('grade', 'upgrade', 'cost', 'state', 'point', 'save', 'reset', 'train', 'purchase'))):
            continue
        path = _trace_hook_path(func)
        if path is not None and path.rsplit(':', 1)[0].rsplit('.', 1)[-1] == name(read(func, 'Outer')):
            found[path] = func
    def order(path):
        method = path.rsplit(':', 1)[-1]
        return (priorities.index(method) if method in priorities else len(priorities), path)
    paths = sorted(found, key=order)
    log('[UVH-PURCHASE] Metadata scanned={} discovered={} detailed_limit=12'.format(scanned, len(paths)))
    for path in paths[:32]:
        log('[UVH-PURCHASE] DISCOVERED {}'.format(path))
    for path in paths[:12]:
        func = found[path]
        log('[UVH-PURCHASE] FUNCTION {} flags={} num_params={} params_size={} return_offset={}'.format(
            path, read(func, 'FunctionFlags'), read(func, 'NumParams'),
            read(func, 'ParamsSize'), read(func, 'ReturnValueOffset')))
        try:
            # SDK reflection iterator, not a BoundFunction/native gameplay call.
            for i, prop in enumerate(func._properties()):
                if i >= 16:
                    log('[UVH-PURCHASE] Function fields capped at 16; signature may be incomplete.')
                    break
                log('[UVH-PURCHASE] FIELD {}.{} type={} flags={} offset={} array_dim={} object_class={} struct={} enum={} inner_type={}'.format(
                    path, name(prop), name(read(prop, 'Class')), read(prop, 'PropertyFlags'),
                    read(prop, 'Offset_Internal'), read(prop, 'ArrayDim'),
                    name(read(prop, 'PropertyClass')) or '-', name(read(prop, 'Struct')) or '-',
                    name(read(prop, 'Enum')) or '-', name(read(read(prop, 'Inner'), 'Class')) or '-'))
        except Exception as exc:
            log('[UVH-PURCHASE] Metadata fields unavailable for {}: {}'.format(path, type(exc).__name__))
    log('[UVH-PURCHASE] Raw flags/fields are metadata, not a verified callable signature or purchase eligibility.')


def inspect_overclock_purchase(_option=None):
    """Explicit read-only snapshot of the current owned node and purchase metadata."""
    log('[UVH-PURCHASE] BEGIN v0.2.7 snapshot (READ ONLY; DO NOT BUY)')
    try:
        pc = get_pc(possibly_loading=True)
        record = _uvh_node_state
        if (name(read(pc, 'PlayerClass')) != 'CharClass_Mechromancer'
                or read(pc, 'Pawn') is None or record is None or 'init_tree' not in record):
            log('[UVH-PURCHASE] NOT INSPECTED: load Gaige after ARM with an active inert node record.')
            return False
        tree = record['init_tree']
        if (name(read(tree, 'Class')) != 'PlayerSkillTree' or read(tree, 'Outer') != pc
                or read(pc, 'PlayerSkillTree') != tree or not _init_solo_session(pc)):
            log('[UVH-PURCHASE] NOT INSPECTED: current tree ownership/session not verified.')
            return False
        if not _node_has_exact_contents(record['branch'].Tiers[0], record['layout'].Tiers[0], record['node']):
            log('[UVH-PURCHASE] NOT INSPECTED: native patch no longer matches; cancel and restart.')
            return False
        skills = tree.Skills
        if len(skills) > 256:
            log('[UVH-PURCHASE] NOT INSPECTED: unexpected runtime Skills size.')
            return False
        definitions = [read(entry, 'Definition') for entry in skills]
        matches = [entry for entry in skills if read(entry, 'Definition') == record['node']]
        if len(matches) != 1 or not all(original in definitions for original in record['skills']):
            log('[UVH-PURCHASE] NOT INSPECTED: candidate/original registration mismatch.')
            return False
        entry = matches[0]
        index = read(entry, 'Index')
        tier_index = read(entry, 'ParentTierIndex')
        if (read(entry, 'Owner') != tree or type(index) is not int or not 0 <= index < len(skills)
                or read(skills[index], 'Definition') != record['node']
                or type(tier_index) is not int or len(tree.Tiers) > 64
                or not 0 <= tier_index < len(tree.Tiers)):
            log('[UVH-PURCHASE] NOT INSPECTED: runtime entry owner/index/tier mismatch.')
            return False
        branches = tree.Branches
        if len(branches) > 16:
            log('[UVH-PURCHASE] NOT INSPECTED: unexpected runtime Branches size.')
            return False
        target_branches = [branch for branch in branches if read(branch, 'Definition') == record['branch']]
        if (len(target_branches) != 1 or len(target_branches[0].TierIndices) == 0
                or target_branches[0].TierIndices[0] != tier_index):
            log('[UVH-PURCHASE] NOT INSPECTED: candidate not registered in the target first tier.')
            return False
        tier = tree.Tiers[tier_index]
        if read(tier, 'TierNumber') != 0:
            log('[UVH-PURCHASE] NOT INSPECTED: unexpected target tier number.')
            return False
        pri = read(pc, 'PlayerReplicationInfo')
        for label, owner in (('PRI', pri), ('Controller', pc)):
            for field in ('GeneralSkillPoints', 'SpecialistSkillPoints'):
                log('[UVH-PURCHASE] {}.{}={}'.format(label, field, _tree_info(read(owner, field))))
        grade = read(entry, 'Grade')
        log('[UVH-PURCHASE] NODE rank={} max_rank={} starting_rank={} index={} tier={} unlocked={} unlock_points={}'.format(
            grade, read(record['node'], 'MaxGrade'), read(record['node'], 'DefaultStartingGrade'),
            index, tier_index, read(tier, 'bUnlocked'), read(tier, 'BranchPointsToUnlockTier')))
        for definition in [record['node']] + record['skills']:
            runtime_entries = [item for item in skills if read(item, 'Definition') == definition]
            log('[UVH-PURCHASE] DEFINITION {} runtime_count={} ranks={} max_rank={} skill_type={} skill_class={} grade_rules={}'.format(
                name(definition), len(runtime_entries), [read(item, 'Grade') for item in runtime_entries],
                read(definition, 'MaxGrade'), _purchase_scalar(read(definition, 'SkillType')),
                name(read(definition, 'SkillClass')) or '<none/unavailable>', read(definition, 'bSubjectToGradeRules')))
            for field in ('SkillConstraints', 'SkillEffectDefinitions', 'SkillActivationActions', 'SkillDeactivationActions'):
                value = read(definition, field)
                try:
                    count = len(value) if value is not None else '<unavailable>'
                except Exception:
                    count = '<unavailable>'
                log('[UVH-PURCHASE] {}.{} count={}'.format(name(definition), field, count))
            _purchase_constraint_details(definition)
        if type(grade) is not int or grade != 0:
            log('[UVH-PURCHASE] UNEXPECTED RANK: stop test; native-array restore does not refund points or restore a save.')
        _purchase_function_metadata()
        log('[UVH-PURCHASE] Snapshot complete. Actual point cost/purchase behavior unverified; DO NOT BUY. Cancel and restart after test.')
        return True
    except Exception as exc:
        log('[UVH-PURCHASE] Snapshot ERROR {}: {}'.format(type(exc).__name__, str(exc)[:160]))
        return False
    finally:
        log('[UVH-PURCHASE] END snapshot; no points, grades, definitions, durations or saves written by this button.')


_UPGRADE_PATHS = ('WillowGame.SkillTreeGFxObject:CanUpgradeSkill',
                  'WillowGame.WillowPlayerController:GetSkillUpgradeCost')
_UPGRADE_EVENT_LIMIT = 24
_UPGRADE_CALLBACK_LIMIT = 2048
_UPGRADE_SECONDS = 90.0  # Checked on the next observed call; no background timer.
_upgrade_hooks = []
_upgrade_context = None
_upgrade_results = []
_upgrade_hits = {}
_upgrade_callbacks = 0
_upgrade_skipped = 0
_upgrade_busy = False


def _upgrade_metadata():
    """Require the two loaded descriptors observed in v0.2.3; never call them."""
    import unrealsdk
    found = {}
    for index, func in enumerate(unrealsdk.find_all('Function', exact=False)):
        if index >= 30000:
            raise ValueError('function discovery exceeds 30000 objects')
        path = _trace_hook_path(func)
        if path not in _UPGRADE_PATHS:
            continue
        if (path in found or name(read(func, 'Class')) != 'Function'
                or name(read(func, 'Outer')) != path.split(':')[0].split('.')[-1]):
            raise ValueError('duplicate or foreign function descriptor')
        expected = (1, 1, 0) if path == _UPGRADE_PATHS[0] else (2, 8, 4)
        if tuple(read(func, field) for field in ('NumParams', 'ParamsSize', 'ReturnValueOffset')) != expected:
            raise ValueError('unexpected signature metadata for ' + path)
        fields = {}
        for field_index, prop in enumerate(func._properties()):
            if field_index >= 16:
                raise ValueError('function fields exceed 16')
            field = name(prop)
            if field in fields:
                raise ValueError('duplicate field metadata')
            fields[field] = prop
        required = {'ReturnValue': ('ByteProperty', 1408, 0)} if path == _UPGRADE_PATHS[0] else {
            'Skill': ('ObjectProperty', 128, 0), 'ReturnValue': ('IntProperty', 1408, 4)}
        for field, spec in required.items():
            prop = fields.get(field)
            actual = (name(read(prop, 'Class')), read(prop, 'PropertyFlags'), read(prop, 'Offset_Internal'))
            if actual != spec or read(prop, 'ArrayDim') != 1:
                raise ValueError('unexpected parameter metadata ' + path + '.' + field)
        if any(read(prop, 'PropertyFlags') != 0 for field, prop in fields.items() if field not in required):
            raise ValueError('unexpected additional parameter flags')
        if path == _UPGRADE_PATHS[0]:
            if name(read(fields['ReturnValue'], 'Enum')) != 'ESkillTreeFailureReason':
                raise ValueError('unverified failure-reason enum descriptor')
        elif name(read(fields['Skill'], 'PropertyClass')) != 'SkillDefinition':
            raise ValueError('unverified cost skill parameter class')
        found[path] = func
    if len(found) != 2:
        raise ValueError('both observed upgrade functions must be loaded')


def _upgrade_state(context):
    """Quiet bounded reads of this exact solo tree; exceptions end observation."""
    from mods_base import ENGINE
    pc, tree, record = context['pc'], context['tree'], context['record']
    if (get_pc(possibly_loading=True) != pc or _uvh_node_state is not record
            or name(read(pc, 'Class')) != 'WillowPlayerController'
            or name(read(pc, 'PlayerClass')) != 'CharClass_Mechromancer'
            or read(pc, 'Pawn') != context['pawn'] or context['pawn'] is None
            or read(pc, 'PlayerSkillTree') != tree or read(tree, 'Outer') != pc
            or name(read(tree, 'Class')) != 'PlayerSkillTree' or record['init_tree'] != tree):
        raise ValueError('current Gaige/controller/pawn/tree ownership changed or unavailable')
    world, pri = pc.WorldInfo, pc.PlayerReplicationInfo
    mode = world.NetMode
    locals_, roster = ENGINE.GamePlayers, world.GRI.PRIArray
    if (world != context['world'] or pri != context['pri']
            or not isinstance(mode, int) or isinstance(mode, bool) or mode not in context['modes']
            or len(locals_) != 1 or locals_[0].Actor != pc
            or len(roster) != 1 or roster[0] != pri or pri.Owner != pc):
        raise ValueError('solo session/roster ownership changed or unavailable')
    originals, node = record['skills'], record['node']
    if (len(originals) != 2 or context['definitions'] != (node, originals[0], originals[1])
            or name(node) != 'UVH_DeathtrapOverclock'
            or not _node_has_exact_contents(record['branch'].Tiers[0], record['layout'].Tiers[0], node)
            or list(record['branch'].Tiers[0].Skills) != [originals[0], node, originals[1]]
            or read(node, 'MaxGrade') != 1 or read(node, 'DefaultStartingGrade') != 0
            or read(node, 'bSubjectToGradeRules') is not True):
        raise ValueError('owned native patch/candidate changed or unavailable')
    for field in ('SkillEffectDefinitions', 'SkillActivationActions', 'SkillDeactivationActions'):
        if len(getattr(node, field)) != 0:
            raise ValueError('candidate is no longer verified inert')
    skills, tiers, branches = tree.Skills, tree.Tiers, tree.Branches
    if not (3 <= len(skills) <= 256 and 1 <= len(tiers) <= 64 and 1 <= len(branches) <= 16):
        raise ValueError('runtime arrays have unexpected sizes')
    target = [branch for branch in branches if read(branch, 'Definition') == record['branch']]
    if len(target) != 1 or not 1 <= len(target[0].TierIndices) <= 16:
        raise ValueError('target runtime branch unavailable')
    tier_index = target[0].TierIndices[0]
    if type(tier_index) is not int or not 0 <= tier_index < len(tiers):
        raise ValueError('target tier index unavailable')
    tier = tiers[tier_index]
    if read(tier, 'TierNumber') != 0 or not 3 <= len(tier.SkillIndices) <= 16:
        raise ValueError('first runtime tier unavailable')
    grades, indices = [], []
    for definition in context['definitions']:
        if name(read(definition, 'Class')) != 'SkillDefinition':
            raise ValueError('unverified skill definition class')
        entries = [entry for entry in skills if read(entry, 'Definition') == definition]
        if len(entries) != 1:
            raise ValueError('candidate/original registration is not unique')
        entry = entries[0]
        index, grade = read(entry, 'Index'), read(entry, 'Grade')
        if (read(entry, 'Owner') != tree or type(index) is not int or not 0 <= index < len(skills)
                or read(skills[index], 'Definition') != definition
                or read(entry, 'ParentTierIndex') != tier_index or index not in tier.SkillIndices
                or type(grade) is not int or grade < 0):
            raise ValueError('skill owner/index/tier/rank unavailable')
        grades.append(grade)
        indices.append(index)
    points = (read(pri, 'GeneralSkillPoints'), read(pri, 'SpecialistSkillPoints'))
    if grades[0] != 0 or any(type(value) is not int or value < 0 for value in points):
        raise ValueError('candidate rank must be zero and both PRI point fields known')
    state = (points, tuple(grades), tuple(indices), tier_index)
    if context.get('baseline') is not None and state != context['baseline']:
        raise ValueError('points/ranks/runtime indices changed; no refund or repair attempted')
    return state


def stop_upgrade_trace(_option=None):
    """Clear capture first, then retry removal of only our registered observers."""
    global _upgrade_context, _upgrade_hooks
    import unrealsdk
    context = _upgrade_context
    _upgrade_context = None  # Any callback left after removal failure is inert.
    if context is not None:
        try:
            state = _upgrade_state(context)
            log('[UVH-UPGRADE] FINAL points={} ranks={} unchanged_from_start=True'.format(state[0], state[1]))
        except Exception as exc:
            log('[UVH-UPGRADE] FINAL UNVERIFIED {}: {}; no refund or repair.'.format(
                type(exc).__name__, str(exc)[:180]))
    pending = []
    for path, phase, ident in _upgrade_hooks:
        try:
            unrealsdk.hooks.remove_hook(path, phase, ident)
            if unrealsdk.hooks.has_hook(path, phase, ident):
                pending.append((path, phase, ident))
        except Exception as exc:
            pending.append((path, phase, ident))
            log('[UVH-UPGRADE] Removal ERROR {}: {}'.format(path, type(exc).__name__))
    _upgrade_hooks = pending
    log('[UVH-UPGRADE] STOP remaining={} captured={} callbacks={} skipped={}'.format(
        len(pending), len(_upgrade_results), _upgrade_callbacks, _upgrade_skipped))
    for path in _UPGRADE_PATHS:
        for definition in ('UVH_DeathtrapOverclock', 'MorePep', 'Myelin'):
            values = [result[2] for result in _upgrade_results if result[:2] == (path, definition)]
            log('[UVH-UPGRADE] SUMMARY {} {} results={}'.format(path.rsplit(':', 1)[-1], definition, values))
    log('[UVH-UPGRADE] Missing results mean NOT OBSERVED; no purchase/effect/persistence conclusion. Cancel and restart.')
    return not pending


def _upgrade_callback(path):
    def observe(obj, args, ret, func):
        global _upgrade_busy, _upgrade_callbacks, _upgrade_skipped
        context = _upgrade_context
        if context is None or _upgrade_busy:
            return None
        _upgrade_busy = True
        try:
            import time
            _upgrade_callbacks += 1
            if (_upgrade_callbacks >= _UPGRADE_CALLBACK_LIMIT
                    or time.monotonic() - context['started'] >= _UPGRADE_SECONDS):
                log('[UVH-UPGRADE] LIMIT callback/time bound reached (time checked on calls).')
                stop_upgrade_trace()
                return None
            _upgrade_state(context)
            rollover = None
            if path == _UPGRADE_PATHS[0]:
                if name(read(obj, 'Class')) != 'SkillTreeGFxObject' or read(obj, 'WPCOwner') != context['pc']:
                    if _upgrade_skipped < 6:
                        log('[UVH-UPGRADE] IGNORED UI class={} owner_matches={} current={} rollover={}'.format(
                            name(read(obj, 'Class')), read(obj, 'WPCOwner') == context['pc'],
                            name(read(obj, 'CurrentSkill')), name(read(obj, 'CurrentSkill_Rollover'))))
                    _upgrade_skipped += 1
                    return None
                definition = read(obj, 'CurrentSkill')
                rollover = read(obj, 'CurrentSkill_Rollover')
            else:
                if obj != context['pc']:
                    if _upgrade_skipped < 6:
                        log('[UVH-UPGRADE] IGNORED cost controller ownership mismatch.')
                    _upgrade_skipped += 1
                    return None
                definition = read(args, 'Skill')
            if definition not in context['definitions']:
                if _upgrade_skipped < 6:
                    log('[UVH-UPGRADE] IGNORED {} unverified/other selection={} rollover={}'.format(
                        path.rsplit(':', 1)[-1], name(definition) or '<unavailable>', name(rollover) or '<unavailable>'))
                _upgrade_skipped += 1
                return None
            if path == _UPGRADE_PATHS[0]:
                if not isinstance(ret, context['failure_enum']) or ret not in context['failure_enum'].__members__.values():
                    raise ValueError('unverified failure-reason return: ' + _purchase_scalar(ret))
                value = _purchase_scalar(ret)  # Actual POST ret; never args.ReturnValue or bool(ret).
            else:
                if type(ret) is not int or ret < 0:
                    raise ValueError('unverified point-cost return: ' + _purchase_scalar(ret))
                value = str(ret)
            key = (path, name(definition), value)
            if _upgrade_hits.get(key, 0) >= 2:
                _upgrade_skipped += 1
                return None
            _upgrade_hits[key] = _upgrade_hits.get(key, 0) + 1
            _upgrade_results.append(key)
            log('[UVH-UPGRADE] RESULT {} skill={} return={} rollover={} baseline_points={} baseline_ranks={}'.format(
                path, name(definition), value, name(rollover) or '<unavailable>',
                context['baseline'][0], context['baseline'][1]))
            if len(_upgrade_results) >= _UPGRADE_EVENT_LIMIT:
                log('[UVH-UPGRADE] LIMIT captured event bound reached.')
                stop_upgrade_trace()
        except Exception as exc:
            log('[UVH-UPGRADE] ABORT {}: {}'.format(type(exc).__name__, str(exc)[:180]))
            stop_upgrade_trace()
        finally:
            _upgrade_busy = False
        return None  # POST observer never blocks, overrides, invokes or edits the native call.
    return observe


def start_upgrade_trace(_option=None):
    global _upgrade_context, _upgrade_results, _upgrade_hits, _upgrade_callbacks, _upgrade_skipped
    import unrealsdk
    import time
    from enum import Enum
    if (_upgrade_context is not None or _upgrade_hooks or _trace_hooks or _init_hooks or _init_armed
            or _ui_context is not None or _ui_hooks or _skillstate_context is not None or _skillstate_hooks):
        log('[UVH-UPGRADE] NOT STARTED: stop existing observers; initialization must be complete.')
        return False
    try:
        pc, record = get_pc(possibly_loading=True), _uvh_node_state
        if record is None or 'init_tree' not in record or len(record['skills']) != 2:
            raise ValueError('load Gaige after ARM with an owned inert node')
        modes = unrealsdk.find_enum('ENetMode')
        failure_enum = unrealsdk.find_enum('ESkillTreeFailureReason')
        if (not isinstance(failure_enum, type) or not issubclass(failure_enum, Enum)
                or failure_enum.__name__ != 'ESkillTreeFailureReason'):
            raise ValueError('failure-reason enum type unavailable')
        context = dict(pc=pc, tree=record['init_tree'], record=record, pawn=read(pc, 'Pawn'),
                       world=read(pc, 'WorldInfo'), pri=read(pc, 'PlayerReplicationInfo'),
                       modes=(modes.NM_Standalone, modes.NM_ListenServer), failure_enum=failure_enum,
                       definitions=(record['node'], record['skills'][0], record['skills'][1]),
                       started=time.monotonic())
        context['baseline'] = _upgrade_state(context)
        _upgrade_metadata()
        _upgrade_results, _upgrade_hits = [], {}
        _upgrade_callbacks, _upgrade_skipped = 0, 0
        for path in _UPGRADE_PATHS:
            phase, ident = unrealsdk.hooks.Type.POST, 'UVH_UPGRADE_' + path.rsplit(':', 1)[-1]
            if unrealsdk.hooks.has_hook(path, phase, ident):
                raise ValueError('observer identifier already exists; not owned or removed')
            if not unrealsdk.hooks.add_hook(path, phase, ident, _upgrade_callback(path)):
                raise ValueError('observer registration refused')
            _upgrade_hooks.append((path, phase, ident))
        _upgrade_context = context  # Both registrations and every preflight check passed.
        log('[UVH-UPGRADE] START v0.2.7 POST observers=2 points={} ranks={} READ ONLY; DO NOT BUY.'.format(
            context['baseline'][0], context['baseline'][1]))
        log('[UVH-UPGRADE] Highlight Overclock/More Pep/Myelin; CurrentSkill identifies the query, rollover is separate.')
        return True
    except Exception as exc:
        log('[UVH-UPGRADE] NOT STARTED {}: {}'.format(type(exc).__name__, str(exc)[:180]))
        if _upgrade_hooks:
            stop_upgrade_trace()
        return False


_UI_FUNCTION_LIMIT = 10
_UI_EVENT_LIMIT = 48
_UI_CALLBACK_LIMIT = 2048
_UI_SECONDS = 90.0  # Expiry checked on calls; always use STOP even if no calls occur.
_ui_hooks = []
_ui_context = None
_ui_results = []
_ui_hits = {}
_ui_callbacks = 0
_ui_skipped = 0
_ui_busy = False


def _ui_candidates():
    """Only loaded, canonical SkillTreeGFxObject functions; no guessed hook paths."""
    import unrealsdk
    found = {}
    tokens = ('nav', 'rollover', 'select', 'inputkey', 'infobox', 'init', 'refresh',
              'skillpointproperties', 'initialskilldata', 'skilldescription', 'skillicon')
    # All names below were discovered in v0.2.5; priority never invents a path.
    # Six missed helpers + Init and the three live navigation anchors fit ten.
    preferred = ('PostNav', 'Navigate', 'HandleInputKey', 'UpdateInfoBox',
                 'Flash_SetSkillPointProperties', 'Flash_SetSkillPointProperties_AS',
                 'Init', 'Nav_Down', 'Nav_Left', 'Nav_Right', 'extInitTree',
                 'Nav_Up', 'Nav_Back', 'Flash_SendInitialSkillData')
    priorities = {method: index for index, method in enumerate(preferred)}
    scanned = 0
    for index, func in enumerate(unrealsdk.find_all('Function', exact=False)):
        if index >= 30000:
            raise ValueError('UI discovery exceeds 30000 function objects')
        scanned += 1
        method_lower = name(func).lower()
        if (name(read(func, 'Class')) != 'Function'
                or name(read(func, 'Outer')) != 'SkillTreeGFxObject'
                or 'artifact' in method_lower or 'equip' in method_lower
                or not any(token in method_lower for token in tokens)):
            continue
        path = _trace_hook_path(func)
        if path is None or path.split(':')[0] != 'WillowGame.SkillTreeGFxObject':
            continue
        if path in found:
            raise ValueError('duplicate UI function descriptor: ' + path)
        found[path] = func
    def order(path):
        method = path.rsplit(':', 1)[-1]
        return priorities.get(method, len(preferred)), path
    paths = sorted(found, key=order)
    log('[UVH-UI] DISCOVERY scanned={} candidates={} function_limit={}'.format(scanned, len(paths), _UI_FUNCTION_LIMIT))
    for path in paths[:24]:
        log('[UVH-UI] CANDIDATE {}'.format(path))
    for path in paths[:_UI_FUNCTION_LIMIT]:
        func = found[path]
        log('[UVH-UI] SELECTED {}'.format(path))
        fields = []
        # Read descriptors only. Never infer/call a signature or read args/ret.
        for index, prop in enumerate(func._properties()):
            if index >= 8:
                fields.append('<fields capped at 8>')
                break
            fields.append('{}:{}:flags={}'.format(name(prop), name(read(prop, 'Class')), read(prop, 'PropertyFlags')))
        log('[UVH-UI] METADATA {} params={} size={} return_offset={} fields={}'.format(
            path, read(func, 'NumParams'), read(func, 'ParamsSize'), read(func, 'ReturnValueOffset'), fields))
    return paths[:_UI_FUNCTION_LIMIT]


def _ui_view(context, ui):
    """Read selection only from an exact UI owned by the guarded local Gaige."""
    if name(read(ui, 'Class')) != 'SkillTreeGFxObject' or read(ui, 'WPCOwner') != context['pc']:
        return None
    skills = context['tree'].Skills
    if not 3 <= len(skills) <= 256:
        raise ValueError('runtime skill size changed during UI read')
    def selected(field):
        definition = read(ui, field)
        if definition is None:
            return '<none/unavailable>'
        if name(read(definition, 'Class')) != 'SkillDefinition':
            return '<unverified>'
        matches = [entry for entry in skills if read(entry, 'Definition') == definition]
        if len(matches) != 1:
            return '<unverified>'
        entry = matches[0]
        index = read(entry, 'Index')
        if (read(entry, 'Owner') != context['tree'] or type(index) is not int
                or not 0 <= index < len(skills) or read(skills[index], 'Definition') != definition):
            return '<unverified>'
        return name(definition)
    current, rollover = selected('CurrentSkill'), selected('CurrentSkill_Rollover')
    ui_points = read(ui, 'NumSkillPoints')
    if type(ui_points) is not int or ui_points < 0:
        ui_points = '<unavailable>'
    unlocked = read(context['tree'].Tiers[context['baseline'][3]], 'bUnlocked')
    if type(unlocked) is not bool:
        unlocked = '<unavailable>'
    return current, rollover, ui_points, unlocked


def _ui_inventory(context, stage):
    """Bounded direct owned-UI snapshots at START/STOP, even with zero callbacks."""
    import unrealsdk
    _upgrade_state(context)
    scanned, owned = 0, 0
    for index, ui in enumerate(unrealsdk.find_all('SkillTreeGFxObject', exact=True)):
        if index >= 32:
            raise ValueError('UI object inventory exceeds 32')
        scanned += 1
        view = _ui_view(context, ui)
        if view is None:
            continue
        owned += 1
        if owned <= 4:
            log('[UVH-UI] SNAPSHOT {} object={} current={} rollover={} ui_points={} tier_unlocked={}'.format(
                stage, _diag_path(ui), *view))
    log('[UVH-UI] INVENTORY {} scanned={} owned={} printed_limit=4'.format(stage, scanned, owned))


def stop_ui_trace(_option=None):
    """Clear capture, verify final state/owned UI and remove only our hooks."""
    global _ui_context, _ui_hooks
    import unrealsdk
    context = _ui_context
    _ui_context = None
    if context is not None:
        try:
            state = _upgrade_state(context)
            log('[UVH-UI] FINAL points={} ranks={} unchanged_from_start=True'.format(state[0], state[1]))
            _ui_inventory(context, 'STOP')
        except Exception as exc:
            log('[UVH-UI] FINAL UNVERIFIED {}: {}'.format(type(exc).__name__, str(exc)[:180]))
    pending = []
    for path, phase, ident in _ui_hooks:
        try:
            unrealsdk.hooks.remove_hook(path, phase, ident)
            if unrealsdk.hooks.has_hook(path, phase, ident):
                pending.append((path, phase, ident))
        except Exception as exc:
            pending.append((path, phase, ident))
            log('[UVH-UI] Removal ERROR {}: {}'.format(path, type(exc).__name__))
    _ui_hooks = pending
    log('[UVH-UI] STOP remaining={} captured={} callbacks={} skipped={}'.format(
        len(pending), len(_ui_results), _ui_callbacks, _ui_skipped))
    paths = sorted({result[0] for result in _ui_results})
    for path in paths:
        log('[UVH-UI] SUMMARY {} events={}'.format(path, sum(result[0] == path for result in _ui_results)))
    log('[UVH-UI] Selection snapshots/events are not eligibility or cost. DO NOT BUY; cancel and restart.')
    return not pending


def _ui_callback(path, phase):
    def observe(obj, args, ret, func):
        global _ui_busy, _ui_callbacks, _ui_skipped
        context = _ui_context
        if context is None or _ui_busy:
            return None
        _ui_busy = True
        try:
            import time
            _ui_callbacks += 1
            if (_ui_callbacks >= _UI_CALLBACK_LIMIT or time.monotonic() - context['started'] >= _UI_SECONDS):
                log('[UVH-UI] LIMIT callback/time bound reached (time checked on calls).')
                stop_ui_trace()
                return None
            _upgrade_state(context)
            view = _ui_view(context, obj)
            if view is None:
                if _ui_skipped < 4:
                    log('[UVH-UI] IGNORED {} {} unverified UI class/owner.'.format(phase, path))
                _ui_skipped += 1
                return None
            key = (path, phase) + view
            if _ui_hits.get(key, 0) >= 2:
                _ui_skipped += 1
                return None
            _ui_hits[key] = _ui_hits.get(key, 0) + 1
            _ui_results.append(key)
            log('[UVH-UI] EVENT {} {} {} object={} current={} rollover={} ui_points={} tier_unlocked={}'.format(
                len(_ui_results), phase, path, _diag_path(obj), *view))
            if len(_ui_results) >= _UI_EVENT_LIMIT:
                log('[UVH-UI] LIMIT event bound reached.')
                stop_ui_trace()
        except Exception as exc:
            log('[UVH-UI] ABORT {}: {}'.format(type(exc).__name__, str(exc)[:180]))
            stop_ui_trace()
        finally:
            _ui_busy = False
        return None  # No args/ret reads, native invocation, writes, block or override.
    return observe


def start_ui_trace(_option=None):
    global _ui_context, _ui_results, _ui_hits, _ui_callbacks, _ui_skipped
    import unrealsdk
    import time
    if (_ui_context is not None or _ui_hooks or _upgrade_context is not None or _upgrade_hooks
            or _trace_hooks or _init_hooks or _init_armed or _skillstate_context is not None or _skillstate_hooks):
        log('[UVH-UI] NOT STARTED: stop other observers; initialization must be complete.')
        return False
    try:
        pc, record = get_pc(possibly_loading=True), _uvh_node_state
        if record is None or 'init_tree' not in record or len(record['skills']) != 2:
            raise ValueError('ARM at main menu, then Continue as Gaige with the owned inert node')
        modes = unrealsdk.find_enum('ENetMode')
        context = dict(pc=pc, tree=record['init_tree'], record=record, pawn=read(pc, 'Pawn'),
                       world=read(pc, 'WorldInfo'), pri=read(pc, 'PlayerReplicationInfo'),
                       modes=(modes.NM_Standalone, modes.NM_ListenServer),
                       definitions=(record['node'], record['skills'][0], record['skills'][1]),
                       started=time.monotonic())
        context['baseline'] = _upgrade_state(context)
        paths = _ui_candidates()
        if not paths:
            raise ValueError('no verified UI navigation/refresh function metadata loaded')
        _ui_results, _ui_hits = [], {}
        _ui_callbacks, _ui_skipped = 0, 0
        _ui_inventory(context, 'START')
        for path in paths:
            for label, phase in (('PRE', unrealsdk.hooks.Type.PRE),
                                 ('POST_ANY', unrealsdk.hooks.Type.POST_UNCONDITIONAL)):
                ident = 'UVH_UI_' + label + '_' + path.rsplit(':', 1)[-1]
                if unrealsdk.hooks.has_hook(path, phase, ident):
                    raise ValueError('UI observer identifier already exists; not owned')
                if not unrealsdk.hooks.add_hook(path, phase, ident, _ui_callback(path, label)):
                    raise ValueError('UI observer registration refused')
                _ui_hooks.append((path, phase, ident))
        _ui_context = context
        log('[UVH-UI] START v0.2.7 functions={} observers={} points={} ranks={} READ ONLY; DO NOT BUY.'.format(
            len(paths), len(_ui_hooks), context['baseline'][0], context['baseline'][1]))
        log('[UVH-UI] Open Skills, hover/navigate Overclock/More Pep/Myelin, then button 8 STOP and button 3 CANCEL.')
        return True
    except Exception as exc:
        log('[UVH-UI] NOT STARTED {}: {}'.format(type(exc).__name__, str(exc)[:180]))
        if _ui_hooks:
            stop_ui_trace()
        return False


_SKILLSTATE_PATHS = ('WillowGame.PlayerSkillTree:GetSkillState',
                     'WillowGame.SkillTreeGFxObject:GetSkillDescriptionForGrade',
                     'WillowGame.SkillTreeGFxObject:UpdateInfoBox')
_SKILLSTATE_EVENT_LIMIT = 48
_SKILLSTATE_CALLBACK_LIMIT = 2048
_SKILLSTATE_SECONDS = 90.0  # Checked on callbacks; always press STOP.
_skillstate_hooks = []
_skillstate_context = None
_skillstate_results = []
_skillstate_hits = {}
_skillstate_counts = {}
_skillstate_callbacks = 0
_skillstate_skipped = 0
_skillstate_busy = False


def _skillstate_metadata():
    """Verify loaded input/return descriptors; never read locals or out values."""
    import unrealsdk
    signatures = ((3, 28, 24), (6, 32, 20), (0, 0, 65535))
    schemas = (
        {'SkillDef': ('ObjectProperty', 128, 0),
         'OutSkillState': ('StructProperty', 384, 4), 'ReturnValue': ('BoolProperty', 1408, 24)},
        {'SkillDef': ('ObjectProperty', 128, 0), 'Grade': ('IntProperty', 128, 4),
         'GradeModifier': ('IntProperty', 128, 8), 'PlayerOwner': ('ObjectProperty', 128, 12),
         'bIncludeHTML': ('BoolProperty', 128, 16), 'ReturnValue': ('StrProperty', 4195712, 20)},
        {})
    found = {}
    for index, func in enumerate(unrealsdk.find_all('Function', exact=False)):
        if index >= 30000:
            raise ValueError('skill-state discovery exceeds 30000 functions')
        path = _trace_hook_path(func)
        if path not in _SKILLSTATE_PATHS:
            continue
        if (path in found or name(read(func, 'Class')) != 'Function'
                or name(read(func, 'Outer')) != path.split(':')[0].split('.')[-1]):
            raise ValueError('duplicate or foreign skill-state function descriptor')
        slot = _SKILLSTATE_PATHS.index(path)
        if tuple(read(func, field) for field in ('NumParams', 'ParamsSize', 'ReturnValueOffset')) != signatures[slot]:
            raise ValueError('unexpected signature metadata: ' + path)
        fields = {}
        for field_index, prop in enumerate(func._properties()):
            if field_index >= 16 or name(prop) in fields:
                raise ValueError('too many or duplicate function fields')
            fields[name(prop)] = prop
        for field, spec in schemas[slot].items():
            prop = fields.get(field)
            actual = (name(read(prop, 'Class')), read(prop, 'PropertyFlags'), read(prop, 'Offset_Internal'))
            if actual != spec or read(prop, 'ArrayDim') != 1:
                raise ValueError('unexpected parameter metadata: ' + path + '.' + field)
        for field, prop in fields.items():
            flags = read(prop, 'PropertyFlags')
            if type(flags) is not int or (field not in schemas[slot] and flags & 0x580):
                raise ValueError('unverified additional parameter flags: ' + path)
        if slot in (0, 1) and name(read(fields['SkillDef'], 'PropertyClass')) != 'SkillDefinition':
            raise ValueError('unverified skill input class')
        if slot == 1 and name(read(fields['PlayerOwner'], 'PropertyClass')) != 'WillowPlayerController':
            raise ValueError('unverified description player input class')
        if slot == 0:
            struct = read(fields['OutSkillState'], 'Struct')
            if name(read(struct, 'Class')) != 'ScriptStruct' or name(struct) != 'SkillTreeSkillStateData':
                raise ValueError('unverified native skill-state struct descriptor')
            for field_index, prop in enumerate(struct._properties()):
                if field_index >= 12:
                    log('[UVH-STATE] STRUCT metadata capped at 12 fields.')
                    break
                log('[UVH-STATE] STRUCT {} type={} flags={} offset={} array_dim={}'.format(
                    name(prop), name(read(prop, 'Class')), read(prop, 'PropertyFlags'),
                    read(prop, 'Offset_Internal'), read(prop, 'ArrayDim')))
        log('[UVH-STATE] METADATA {} signature={} fields={}'.format(
            path, signatures[slot], [(field, name(read(prop, 'Class')), read(prop, 'PropertyFlags'))
                                    for field, prop in fields.items()]))
        found[path] = func
    if set(found) != set(_SKILLSTATE_PATHS):
        raise ValueError('all three focused functions must be loaded and verified')
    return found


def stop_skillstate_trace(_option=None):
    """Clear capture before final verification and owned-hook removal/retry."""
    global _skillstate_context, _skillstate_hooks
    import unrealsdk
    context = _skillstate_context
    _skillstate_context = None
    if context is not None:
        try:
            state = _upgrade_state(context)
            log('[UVH-STATE] FINAL points={} ranks={} unchanged_from_start=True'.format(state[0], state[1]))
        except Exception as exc:
            log('[UVH-STATE] FINAL UNVERIFIED {}: {}; no refund/repair.'.format(type(exc).__name__, str(exc)[:180]))
    pending = []
    for path, phase, ident in _skillstate_hooks:
        try:
            unrealsdk.hooks.remove_hook(path, phase, ident)
            if unrealsdk.hooks.has_hook(path, phase, ident):
                pending.append((path, phase, ident))
        except Exception as exc:
            pending.append((path, phase, ident))
            log('[UVH-STATE] Removal ERROR {}: {}'.format(path, type(exc).__name__))
    _skillstate_hooks = pending
    log('[UVH-STATE] STOP remaining={} captured={} callbacks={} skipped={}'.format(
        len(pending), len(_skillstate_results), _skillstate_callbacks, _skillstate_skipped))
    for path in _SKILLSTATE_PATHS:
        for label in ('UVH_DeathtrapOverclock', 'MorePep', 'Myelin'):
            count = sum(row[:2] == (path, label) for row in _skillstate_results)
            log('[UVH-STATE] SUMMARY {} skill={} captures={} {}'.format(
                path.rsplit(':', 1)[-1], label, count, 'OBSERVED' if count else 'NOT OBSERVED'))
    log('[UVH-STATE] Query Boolean is not eligibility. OutSkillState/locals were NOT read. DO NOT BUY; cancel/restart.')
    return not pending


def _skillstate_emit(path, definition, detail):
    """Reserve four captures per path/target; unrelated traffic uses no events."""
    global _skillstate_skipped
    label = name(definition)
    bucket, key = (path, label), (path, label, detail)
    if _skillstate_counts.get(bucket, 0) >= 4 or _skillstate_hits.get(key, 0) >= 2:
        _skillstate_skipped += 1
        return
    _skillstate_counts[bucket] = _skillstate_counts.get(bucket, 0) + 1
    _skillstate_hits[key] = _skillstate_hits.get(key, 0) + 1
    _skillstate_results.append(key)
    log('[UVH-STATE] RESULT {} skill={} detail={}'.format(path, label, detail))
    if len(_skillstate_results) >= _SKILLSTATE_EVENT_LIMIT:
        log('[UVH-STATE] LIMIT event bound reached.')
        stop_skillstate_trace()


def _skillstate_callback(path):
    def observe(obj, args, ret, func):
        global _skillstate_busy, _skillstate_callbacks, _skillstate_skipped
        context = _skillstate_context
        if context is None or _skillstate_busy:
            return None
        _skillstate_busy = True
        try:
            import time
            _skillstate_callbacks += 1
            if (_skillstate_callbacks >= _SKILLSTATE_CALLBACK_LIMIT
                    or time.monotonic() - context['started'] >= _SKILLSTATE_SECONDS):
                log('[UVH-STATE] LIMIT callback/time bound reached (time checked on calls).')
                stop_skillstate_trace()
                return None
            _upgrade_state(context)
            if path == _SKILLSTATE_PATHS[0]:
                if obj != context['tree']:
                    _skillstate_skipped += 1
                    return None  # No args/ret reads for a foreign tree.
                view = None
            else:
                view = _ui_view(context, obj)
                if view is None:
                    _skillstate_skipped += 1
                    return None  # Ownership checked before inputs/return text.
            if path == _SKILLSTATE_PATHS[2]:
                definition = read(obj, 'CurrentSkill_Rollover')
                if definition not in context['definitions']:
                    definition = read(obj, 'CurrentSkill')
                if definition not in context['definitions']:
                    _skillstate_skipped += 1
                    return None
                _skillstate_emit(path, definition, ('UI_VIEW',) + view)
                return None  # Zero-param UpdateInfoBox: never read args, ret or locals.
            if read(args, '_type') != context['functions'][path]:
                raise ValueError('hook input struct does not match verified function')
            definition = read(args, 'SkillDef')
            if definition not in context['definitions']:
                _skillstate_skipped += 1
                return None  # Never read out/return values for unrelated skills.
            if path == _SKILLSTATE_PATHS[0]:
                if type(ret) is not bool:
                    raise ValueError('unverified GetSkillState Boolean return')
                _skillstate_emit(path, definition, ('QUERY_RETURN', ret))
                # Hook args are copied inputs. OutSkillState is NOT a final output.
            else:
                if read(args, 'PlayerOwner') != context['pc']:
                    _skillstate_skipped += 1
                    return None
                grade, modifier, html = (read(args, field) for field in ('Grade', 'GradeModifier', 'bIncludeHTML'))
                if (type(grade) is not int or not 0 <= grade <= 128
                        or type(modifier) is not int or not -128 <= modifier <= 128
                        or type(html) is not bool or type(ret) is not str):
                    raise ValueError('unverified grade-description input/return types or bounds')
                if name(definition) not in view[:2]:
                    _skillstate_skipped += 1
                    return None
                _skillstate_emit(path, definition, ('DESCRIPTION', grade, modifier, html,
                                                   len(ret), ret[:512], view))
        except Exception as exc:
            log('[UVH-STATE] ABORT {}: {}'.format(type(exc).__name__, str(exc)[:180]))
            stop_skillstate_trace()
        finally:
            _skillstate_busy = False
        return None  # Never invoke, write, block, override or return the query result.
    return observe


def start_skillstate_trace(_option=None):
    global _skillstate_context, _skillstate_results, _skillstate_hits, _skillstate_counts
    global _skillstate_callbacks, _skillstate_skipped
    import unrealsdk
    import time
    if (_skillstate_context is not None or _skillstate_hooks or _ui_context is not None or _ui_hooks
            or _upgrade_context is not None or _upgrade_hooks or _trace_hooks or _init_hooks or _init_armed):
        log('[UVH-STATE] NOT STARTED: stop other observers; initialization must be complete.')
        return False
    try:
        pc, record = get_pc(possibly_loading=True), _uvh_node_state
        if record is None or 'init_tree' not in record or len(record['skills']) != 2:
            raise ValueError('ARM before Continue as Gaige with the owned inert node')
        modes = unrealsdk.find_enum('ENetMode')
        context = dict(pc=pc, tree=record['init_tree'], record=record, pawn=read(pc, 'Pawn'),
                       world=read(pc, 'WorldInfo'), pri=read(pc, 'PlayerReplicationInfo'),
                       modes=(modes.NM_Standalone, modes.NM_ListenServer),
                       definitions=(record['node'], record['skills'][0], record['skills'][1]),
                       started=time.monotonic())
        context['baseline'] = _upgrade_state(context)
        context['functions'] = _skillstate_metadata()
        _skillstate_results, _skillstate_hits, _skillstate_counts = [], {}, {}
        _skillstate_callbacks, _skillstate_skipped = 0, 0
        for path in _SKILLSTATE_PATHS:
            phase, ident = unrealsdk.hooks.Type.POST, 'UVH_STATE_' + path.rsplit(':', 1)[-1]
            if unrealsdk.hooks.has_hook(path, phase, ident):
                raise ValueError('focused observer identifier already exists; not owned')
            if not unrealsdk.hooks.add_hook(path, phase, ident, _skillstate_callback(path)):
                raise ValueError('focused observer registration refused')
            _skillstate_hooks.append((path, phase, ident))
        _skillstate_context = context
        log('[UVH-STATE] START v0.2.7 POST observers=3 points={} ranks={} READ ONLY; DO NOT BUY.'.format(
            context['baseline'][0], context['baseline'][1]))
        log('[UVH-STATE] Four captures per function/skill; inputs/actual ret only. No OutSkillState or locals reads.')
        log('[UVH-STATE] Highlight all three; button 10 STOP, button 3 CANCEL, fully exit.')
        return True
    except Exception as exc:
        log('[UVH-STATE] NOT STARTED {}: {}'.format(type(exc).__name__, str(exc)[:180]))
        if _skillstate_hooks:
            stop_skillstate_trace()
        return False


def shutdown():
    stop_tree_trace()
    cancel_init_node()


build_mod(
    name='UVH v0.2.7 - OVERCLOCK FOCUSED STATE TRACE',
    author='Borderlands Ultimate prototype',
    description=('Opt-in focused native query/description observation with the established inert insertion test. '
                 'Explicitly arm on backed-up solo Gaige; no point spending. Restore and restart after test.'),
    version='0.2.7',
    supported_games=Game.BL2,
    coop_support=CoopSupport.ClientSide,
    options=[
        ButtonOption('uvh_init_node_arm', display_name='1 - ARM ONE GAIGE INIT NODE TEST (SOLO / INERT)', on_press=arm_init_node),
        ButtonOption('uvh_init_node_check', display_name='2 - CHECK INIT NODE RESULT (READ ONLY)', on_press=inspect_init_node),
        ButtonOption('uvh_init_node_cancel', display_name='3 - CANCEL / RESTORE NATIVE ARRAYS (THEN RESTART)', on_press=cancel_init_node),
        ButtonOption('uvh_purchase_snapshot', display_name='4 - INSPECT OVERCLOCK PURCHASE DATA (READ ONLY)', on_press=inspect_overclock_purchase),
        ButtonOption('uvh_upgrade_start', display_name='5 - START UPGRADE OBSERVERS (READ ONLY; DO NOT BUY)', on_press=start_upgrade_trace),
        ButtonOption('uvh_upgrade_stop', display_name='6 - STOP / REPORT UPGRADE OBSERVERS', on_press=stop_upgrade_trace),
        ButtonOption('uvh_ui_start', display_name='7 - START CORE SKILL UI TRACE (READ ONLY; DO NOT BUY)', on_press=start_ui_trace),
        ButtonOption('uvh_ui_stop', display_name='8 - STOP / REPORT UI TRACE + SNAPSHOT (READ ONLY)', on_press=stop_ui_trace),
        ButtonOption('uvh_state_start', display_name='9 - START FOCUSED STATE TRACE (READ ONLY; DO NOT BUY)', on_press=start_skillstate_trace),
        ButtonOption('uvh_state_stop', display_name='10 - STOP / REPORT FOCUSED STATE TRACE', on_press=stop_skillstate_trace),
        ButtonOption('uvh_loading_snapshot', display_name='Diagnostic - SNAPSHOT TREE LOADING (READ ONLY)', on_press=inspect_tree_loading),
        ButtonOption('uvh_loading_trace_start', display_name='Diagnostic - START TREE INIT TRACE (READ ONLY)', on_press=start_tree_trace),
        ButtonOption('uvh_loading_trace_stop', display_name='Diagnostic - STOP TREE INIT TRACE', on_press=stop_tree_trace),
        ButtonOption('uvh_insert_node_early', display_name='Legacy - INSERT INERT NODE AT MAIN MENU', on_press=add_overclock_node),
        ButtonOption('uvh_verify_node_early', display_name='Legacy - CHECK CURRENT NODE STATE (READ ONLY)', on_press=check_overclock_preload),
        ButtonOption('uvh_remove_node_early', display_name='Legacy - REMOVE NODE (if not purchased)', on_press=remove_overclock_node),
        ButtonOption('uvh_boost_inspect', display_name='Inspect live Deathtrap duration', on_press=inspect),
        ButtonOption('uvh_boost_apply', display_name='Apply +15s (working manual prototype)', on_press=apply),
        ButtonOption('uvh_boost_restore', display_name='Restore original duration', on_press=restore),
    ],
    auto_enable=True,
    on_disable=shutdown,
)
