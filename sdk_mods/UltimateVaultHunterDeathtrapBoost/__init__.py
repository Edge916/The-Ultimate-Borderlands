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
    stop_callback_local_reader()
    stop_deathtrap_events()
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
    log('[UVH-PURCHASE] BEGIN v0.2.11 snapshot (READ ONLY; DO NOT BUY)')
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
        log('[UVH-UPGRADE] START v0.2.11 POST observers=2 points={} ranks={} READ ONLY; DO NOT BUY.'.format(
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
        log('[UVH-UI] START v0.2.11 functions={} observers={} points={} ranks={} READ ONLY; DO NOT BUY.'.format(
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
        log('[UVH-STATE] START v0.2.11 POST observers=3 points={} ranks={} READ ONLY; DO NOT BUY.'.format(
            context['baseline'][0], context['baseline'][1]))
        log('[UVH-STATE] Four captures per function/skill; inputs/actual ret only. No OutSkillState or locals reads.')
        log('[UVH-STATE] Highlight all three; button 10 STOP, button 3 CANCEL, fully exit.')
        return True
    except Exception as exc:
        log('[UVH-STATE] NOT STARTED {}: {}'.format(type(exc).__name__, str(exc)[:180]))
        if _skillstate_hooks:
            stop_skillstate_trace()
        return False


def _presentation_metadata(definition):
    """Resolve one loaded array descriptor; no discovery or native invocation."""
    import unrealsdk
    cls = read(definition, 'Class')
    if (not isinstance(cls, unrealsdk.unreal.UClass) or name(cls) != 'SkillDefinition'):
        raise ValueError('unverified SkillDefinition class metadata')
    prop = cls._find_prop('SkillEffectPresentations')  # SDK reflection, not a game call.
    inner = read(prop, 'Inner')
    presentation_class = read(inner, 'PropertyClass')
    for field, kind in ((prop, 'ArrayProperty'), (inner, 'ObjectProperty')):
        flags, offset, dim = (read(field, attr) for attr in ('PropertyFlags', 'Offset_Internal', 'ArrayDim'))
        if (name(read(field, 'Class')) != kind or type(flags) is not int or not 0 <= flags < 2 ** 64
                or flags & 0x580 or type(offset) is not int or not 0 <= offset <= 1048576
                or type(dim) is not int or dim != 1):
            raise ValueError('unverified presentation array/inner descriptor')
    if (name(prop) != 'SkillEffectPresentations' or read(prop, 'Outer') != cls
            or not isinstance(presentation_class, unrealsdk.unreal.UClass)
            or name(presentation_class) != 'AttributePresentationDefinition'):
        raise ValueError('unverified presentation property owner/element class')
    log('[UVH-PRESENT] SCHEMA skill={} type=ArrayProperty inner=ObjectProperty element_class={} flags={} offset={}'.format(
        name(definition)[:96], name(presentation_class), read(prop, 'PropertyFlags'), read(prop, 'Offset_Internal')))
    return presentation_class


def _presentation_class_fields(cls):
    """At most 16 raw descriptors, never presentation instance values or functions."""
    seen = set()
    for index, prop in enumerate(cls._properties()):
        if index >= 16:
            log('[UVH-PRESENT] METADATA CAPPED at 16 properties; remaining fields unobserved.')
            return 'CAPPED'
        field = name(prop)
        kind = name(read(prop, 'Class'))
        flags, offset, dim = (read(prop, attr) for attr in ('PropertyFlags', 'Offset_Internal', 'ArrayDim'))
        if (not field or len(field) > 96 or field in seen or not kind.endswith('Property')
                or len(kind) > 96 or type(flags) is not int
                or not 0 <= flags < 2 ** 64 or type(offset) is not int or not 0 <= offset <= 1048576
                or type(dim) is not int or not 1 <= dim <= 128):
            raise ValueError('unverified/duplicate presentation field metadata')
        seen.add(field)
        log('[UVH-PRESENT] PROPERTY {}.{} type={} flags={} offset={} array_dim={} object_class={} struct={} enum={} inner_type={}'.format(
            name(cls), field, kind, flags, offset, dim,
            name(read(prop, 'PropertyClass'))[:96] or '-', name(read(prop, 'Struct'))[:96] or '-',
            name(read(prop, 'Enum'))[:96] or '-', name(read(read(prop, 'Inner'), 'Class'))[:96] or '-'))
    log('[UVH-PRESENT] METADATA properties={} complete=True (descriptors only).'.format(len(seen)))
    return 'COMPLETE'


def _presentation_details(context, definition, metadata):
    """Read the owned target's array/count and at most four object identities."""
    import unrealsdk
    if definition not in context['definitions'] or read(definition, 'Class') != context['skill_class']:
        raise ValueError('unverified target definition identity/class')
    cls = _presentation_metadata(definition)
    if metadata.get('class') is not None and metadata['class'] != cls:
        raise ValueError('presentation element class differs between targets')
    _upgrade_state(context)  # Recheck after metadata, before the first payload read.
    values = getattr(definition, 'SkillEffectPresentations')
    if not isinstance(values, unrealsdk.unreal.WrappedArray):
        raise ValueError('unverified presentation array wrapper')
    count = len(values)
    if not 0 <= count <= 256:
        raise ValueError('presentation array size exceeds 256; no entries read')
    shown = min(count, 4)
    log('[UVH-PRESENT] ARRAY skill={} count={} sample={} capped={}'.format(name(definition)[:96], count, shown, count > shown))
    for index in range(shown):
        _upgrade_state(context)
        entry = values[index]
        if not isinstance(entry, unrealsdk.unreal.UObject) or read(entry, 'Class') != cls:
            raise ValueError('unverified presentation reference class at index ' + str(index))
        _upgrade_state(context)
        path = entry._path_name()  # SDK object identity helper only.
        if type(path) is not str or not path or len(path) > 384:
            raise ValueError('unverified/oversized presentation object path')
        log('[UVH-PRESENT] REFERENCE skill={} index={} class={} path={!r}'.format(
            name(definition)[:96], index, name(cls), path))
    _upgrade_state(context)
    if len(values) != count or read(definition, 'Class') != context['skill_class']:
        raise ValueError('presentation array length/definition class changed during snapshot')
    if not metadata:
        metadata['class'] = cls
        try:
            metadata['status'] = _presentation_class_fields(cls)
        except Exception as exc:
            metadata['status'] = 'UNAVAILABLE'
            log('[UVH-PRESENT] METADATA UNAVAILABLE {}: {}'.format(type(exc).__name__, str(exc)[:180]))
    return (count, shown, metadata['status'])


def inspect_overclock_presentations(_option=None):
    """Explicit synchronous read-only comparison; installs no observers."""
    import unrealsdk
    log('[UVH-PRESENT] BEGIN v0.2.11 snapshot (READ ONLY; DO NOT BUY)')
    if (_init_armed or _init_hooks or _trace_hooks or _upgrade_context is not None or _upgrade_hooks
            or _ui_context is not None or _ui_hooks or _skillstate_context is not None or _skillstate_hooks):
        log('[UVH-PRESENT] NOT INSPECTED: initialization/other observers must be stopped.')
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
                       skill_class=read(record['node'], 'Class'))
        context['baseline'] = _upgrade_state(context)
        log('[UVH-PRESENT] BASELINE points={} ranks={}'.format(context['baseline'][0], context['baseline'][1]))
        metadata, verified = {}, 0
        for definition in context['definitions']:
            _upgrade_state(context)
            try:
                count, shown, status = _presentation_details(context, definition, metadata)
                verified += 1
                log('[UVH-PRESENT] SUMMARY skill={} array=VERIFIED count={} references={}/{} metadata={}'.format(
                    name(definition)[:96], count, shown, count, status))
            except Exception as exc:
                log('[UVH-PRESENT] SUMMARY skill={} array=UNAVAILABLE {}: {}'.format(
                    name(definition)[:96], type(exc).__name__, str(exc)[:180]))
            _upgrade_state(context)  # A changed state aborts, rather than proceeding to another target.
        state = _upgrade_state(context)
        log('[UVH-PRESENT] FINAL points={} ranks={} unchanged_from_start=True'.format(state[0], state[1]))
        log('[UVH-PRESENT] END verified_arrays={}/3 observers_added=0; no writes/native queries. Cancel and restart.'.format(verified))
        log('[UVH-PRESENT] Counts/references/metadata do not prove rendered text or eligibility. DO NOT BUY.')
        return verified == 3
    except Exception as exc:
        log('[UVH-PRESENT] ABORT {}: {}; no repair/refund attempted. CANCEL and exit.'.format(
            type(exc).__name__, str(exc)[:180]))
        return False


# These four StrProperty descriptors were observed in the v0.2.8 live log.
_PRESENTATION_TEXT_FIELDS = (('Description', 68), ('NoConstraintText', 80),
                             ('Prefix', 104), ('Suffix', 92))


def _presentation_text_property(cls, field):
    """Validate one allowlisted loaded descriptor before an instance read."""
    import unrealsdk
    offsets = dict(_PRESENTATION_TEXT_FIELDS)
    if (field not in offsets or not isinstance(cls, unrealsdk.unreal.UClass)
            or name(cls) != 'AttributePresentationDefinition'):
        raise ValueError('unverified presentation text class/field')
    prop = cls._find_prop(field)  # SDK reflection only, never native formatting.
    flags, offset, dim = (read(prop, attr) for attr in ('PropertyFlags', 'Offset_Internal', 'ArrayDim'))
    if (name(prop) != field or read(prop, 'Outer') != cls
            or name(read(prop, 'Class')) != 'StrProperty'
            or type(flags) is not int or flags != 4227075
            or type(offset) is not int or offset != offsets[field]
            or type(dim) is not int or dim != 1):
        raise ValueError('text descriptor differs from verified name/owner/type/flags/offset/dimension')
    return prop


def _presentation_text_reference(context, definition, cls, count, index, entry):
    """Recheck current state and membership before/after each named text read."""
    import unrealsdk
    _upgrade_state(context)
    if (definition not in context['definitions']
            or read(definition, 'Class') != context['skill_class']
            or not isinstance(entry, unrealsdk.unreal.UObject) or read(entry, 'Class') != cls):
        raise ValueError('presentation target/reference identity or class changed')
    if _presentation_metadata(definition) != cls:
        raise ValueError('presentation element class changed')
    _upgrade_state(context)  # Metadata must not change points/ranks before payload.
    values = getattr(definition, 'SkillEffectPresentations')
    if (not isinstance(values, unrealsdk.unreal.WrappedArray) or len(values) != count
            or not 0 <= index < min(count, 4) or values[index] != entry):
        raise ValueError('presentation array length/reference changed')
    _upgrade_state(context)
    if read(entry, 'Class') != cls or read(definition, 'Class') != context['skill_class']:
        raise ValueError('presentation class changed during reference check')


def _presentation_text_details(context, definition, metadata):
    """At most four references and four escaped string values per reference."""
    import unrealsdk
    _upgrade_state(context)
    if definition not in context['definitions'] or read(definition, 'Class') != context['skill_class']:
        raise ValueError('unverified target definition identity/class')
    cls = _presentation_metadata(definition)
    if metadata.get('class') is not None and metadata['class'] != cls:
        raise ValueError('presentation element class differs between targets')
    metadata['class'] = cls  # Per-call metadata identity only; no game state write.
    _upgrade_state(context)
    values = getattr(definition, 'SkillEffectPresentations')
    if not isinstance(values, unrealsdk.unreal.WrappedArray):
        raise ValueError('unverified presentation array wrapper')
    count = len(values)
    if not 0 <= count <= 256:
        raise ValueError('presentation array size exceeds 256; no entries read')
    shown, verified = min(count, 4), 0
    log('[UVH-TEXT] ARRAY skill={} count={} sample={} capped={}'.format(
        name(definition)[:96], count, shown, count > shown))
    for index in range(shown):
        _upgrade_state(context)
        entry = values[index]
        _presentation_text_reference(context, definition, cls, count, index, entry)
        path = entry._path_name()
        _presentation_text_reference(context, definition, cls, count, index, entry)
        if type(path) is not str or not path or len(path) > 384:
            raise ValueError('unverified/oversized presentation object path')
        log('[UVH-TEXT] REFERENCE skill={} index={} class={} path={!r}'.format(
            name(definition)[:96], index, name(cls), path))
        for field, _offset in _PRESENTATION_TEXT_FIELDS:
            _presentation_text_reference(context, definition, cls, count, index, entry)
            try:
                _presentation_text_property(cls, field)
                _presentation_text_reference(context, definition, cls, count, index, entry)
                value = getattr(entry, field)
                _presentation_text_reference(context, definition, cls, count, index, entry)
                if type(value) is not str:
                    raise ValueError('text payload is not an exact string')
                log('[UVH-TEXT] VALUE skill={} index={} field={} status=VERIFIED length={} clipped={} text={!r}'.format(
                    name(definition)[:96], index, field, len(value), len(value) > 512, value[:512]))
                verified += 1
            except Exception as exc:
                log('[UVH-TEXT] VALUE skill={} index={} field={} status=UNAVAILABLE {}: {!r}'.format(
                    name(definition)[:96], index, field, type(exc).__name__, str(exc)[:180]))
            # State/reference changes abort before another field, even if caught above.
            _presentation_text_reference(context, definition, cls, count, index, entry)
    _upgrade_state(context)
    current = getattr(definition, 'SkillEffectPresentations')
    if (read(definition, 'Class') != context['skill_class']
            or not isinstance(current, unrealsdk.unreal.WrappedArray) or len(current) != count):
        raise ValueError('presentation array length/definition class changed during snapshot')
    _upgrade_state(context)
    return count, shown, verified, shown * len(_PRESENTATION_TEXT_FIELDS)


def inspect_overclock_presentation_text(_option=None):
    """Explicit synchronous text comparison; no observers, evaluation or writes."""
    import unrealsdk
    log('[UVH-TEXT] BEGIN v0.2.11 snapshot (READ ONLY; DO NOT BUY)')
    if (_init_armed or _init_hooks or _trace_hooks or _upgrade_context is not None or _upgrade_hooks
            or _ui_context is not None or _ui_hooks or _skillstate_context is not None or _skillstate_hooks):
        log('[UVH-TEXT] NOT INSPECTED: initialization/other observers must be stopped.')
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
                       skill_class=read(record['node'], 'Class'))
        context['baseline'] = _upgrade_state(context)
        log('[UVH-TEXT] BASELINE points={} ranks={}'.format(context['baseline'][0], context['baseline'][1]))
        metadata, complete, total_verified, total_fields = {}, 0, 0, 0
        for definition in context['definitions']:
            _upgrade_state(context)
            try:
                count, shown, verified, expected = _presentation_text_details(context, definition, metadata)
            except Exception as exc:
                log('[UVH-TEXT] SUMMARY skill={} array=UNAVAILABLE {}: {!r}'.format(
                    name(definition)[:96], type(exc).__name__, str(exc)[:180]))
                raise  # Unknown/changing arrays/references abort before another target.
            status = 'NOT_APPLICABLE' if expected == 0 else ('VERIFIED' if verified == expected else 'PARTIAL')
            log('[UVH-TEXT] SUMMARY skill={} array=VERIFIED count={} references={}/{} fields={}/{} text={}'.format(
                name(definition)[:96], count, shown, count, verified, expected, status))
            total_verified += verified
            total_fields += expected
            complete += verified == expected
            _upgrade_state(context)
        state = _upgrade_state(context)
        log('[UVH-TEXT] FINAL points={} ranks={} unchanged_from_start=True'.format(state[0], state[1]))
        log('[UVH-TEXT] END complete_targets={}/3 fields={}/{} observers_added=0; no writes/native queries.'.format(
            complete, total_verified, total_fields))
        log('[UVH-TEXT] Raw strings are not rendered previews or eligibility. DO NOT BUY; CANCEL and exit.')
        return complete == 3
    except Exception as exc:
        log('[UVH-TEXT] ABORT {}: {!r}; no repair/refund attempted. CANCEL and exit.'.format(
            type(exc).__name__, str(exc)[:180]))
        return False


_PRESENTATION_DISPLAY_FLAGS = ('bDontDisplayNumber', 'bUseCustomNumberPlacement', 'bEnableTextColor')


def _presentation_display_property(cls, field):
    """Validate one observed flag/reference descriptor, never infer bit masks."""
    import unrealsdk
    if (field not in _PRESENTATION_DISPLAY_FLAGS + ('Attribute',)
            or not isinstance(cls, unrealsdk.unreal.UClass)
            or name(cls) != 'AttributePresentationDefinition'):
        raise ValueError('unverified presentation display class/field')
    prop = cls._find_prop(field)
    flags, offset, dim = (read(prop, attr) for attr in ('PropertyFlags', 'Offset_Internal', 'ArrayDim'))
    kind, expected_offset = ('ObjectProperty', 64) if field == 'Attribute' else ('BoolProperty', 116)
    if (name(prop) != field or read(prop, 'Outer') != cls
            or name(read(prop, 'Class')) != kind
            or type(flags) is not int or flags != 3
            or type(offset) is not int or offset != expected_offset
            or type(dim) is not int or dim != 1):
        raise ValueError('display descriptor differs from observed name/owner/type/flags/offset/dimension')
    declared = None
    if field == 'Attribute':
        declared = read(prop, 'PropertyClass')
        if not isinstance(declared, unrealsdk.unreal.UClass) or name(declared) != 'AttributeDefinition':
            raise ValueError('unverified declared AttributeDefinition class')
    return declared


def _presentation_attribute_reference(context, definition, cls, count, index, entry, declared, value):
    """Recheck a typed local reference without reading any Attribute values."""
    import unrealsdk
    _presentation_text_reference(context, definition, cls, count, index, entry)
    if _presentation_display_property(cls, 'Attribute') != declared:
        raise ValueError('declared Attribute class changed')
    _presentation_text_reference(context, definition, cls, count, index, entry)
    current = getattr(entry, 'Attribute')
    _presentation_text_reference(context, definition, cls, count, index, entry)
    if current is None:
        if value is not None:
            raise ValueError('typed Attribute reference changed to absence')
    elif (not isinstance(current, unrealsdk.unreal.UObject) or read(current, 'Class') != declared
          or current != value):
        raise ValueError('typed Attribute reference or class changed')
    _presentation_text_reference(context, definition, cls, count, index, entry)


def _presentation_display_details(context, definition, metadata):
    """Three exact bools and one typed Attribute identity per sampled entry."""
    import unrealsdk
    _upgrade_state(context)
    if definition not in context['definitions'] or read(definition, 'Class') != context['skill_class']:
        raise ValueError('unverified target definition identity/class')
    cls = _presentation_metadata(definition)
    if metadata.get('class') is not None and metadata['class'] != cls:
        raise ValueError('presentation element class differs between targets')
    metadata['class'] = cls  # Local per-call identities only.
    _upgrade_state(context)
    values = getattr(definition, 'SkillEffectPresentations')
    if not isinstance(values, unrealsdk.unreal.WrappedArray):
        raise ValueError('unverified presentation array wrapper')
    count = len(values)
    if not 0 <= count <= 256:
        raise ValueError('presentation array size exceeds 256; no entries read')
    shown, flags, attributes, present, absent = min(count, 4), 0, 0, 0, 0
    log('[UVH-DISPLAY] ARRAY skill={} count={} sample={} capped={}'.format(
        name(definition)[:96], count, shown, count > shown))
    for index in range(shown):
        _upgrade_state(context)
        entry = values[index]
        _presentation_text_reference(context, definition, cls, count, index, entry)
        path = entry._path_name()
        _presentation_text_reference(context, definition, cls, count, index, entry)
        if type(path) is not str or not path or len(path) > 384:
            raise ValueError('unverified/oversized presentation object path')
        log('[UVH-DISPLAY] REFERENCE skill={} index={} class={} path={!r}'.format(
            name(definition)[:96], index, name(cls), path))
        for field in _PRESENTATION_DISPLAY_FLAGS + ('Attribute',):
            _presentation_text_reference(context, definition, cls, count, index, entry)
            attribute_check, result, failure = None, None, None
            try:
                declared = _presentation_display_property(cls, field)
                if field == 'Attribute':
                    if metadata.get('attribute_class') is not None and metadata['attribute_class'] != declared:
                        raise ValueError('declared Attribute class differs between references')
                    metadata['attribute_class'] = declared
                _presentation_text_reference(context, definition, cls, count, index, entry)
                value = getattr(entry, field)
                _presentation_text_reference(context, definition, cls, count, index, entry)
                if field == 'Attribute':
                    if value is not None and (not isinstance(value, unrealsdk.unreal.UObject)
                                              or read(value, 'Class') != declared):
                        raise ValueError('Attribute payload is not the exact declared SDK object class')
                    attribute_check = (declared, value)
                    _presentation_attribute_reference(context, definition, cls, count, index, entry, declared, value)
                    if value is None:
                        result = 'presence=ABSENT'
                    else:
                        attribute_path = value._path_name()
                        _presentation_attribute_reference(context, definition, cls, count, index, entry, declared, value)
                        if type(attribute_path) is not str or not attribute_path or len(attribute_path) > 384:
                            raise ValueError('unverified/oversized Attribute object path')
                        result = 'presence=PRESENT class=AttributeDefinition path={!r}'.format(attribute_path)
                else:
                    if type(value) is not bool:
                        raise ValueError('display flag payload is not an exact bool')
                    result = 'value={}'.format(value)
            except Exception as exc:
                failure = '{}: {!r}'.format(type(exc).__name__, str(exc)[:180])
            # Changed state/membership/typed Attribute escapes field-level handling.
            _presentation_text_reference(context, definition, cls, count, index, entry)
            if attribute_check is not None:
                _presentation_attribute_reference(context, definition, cls, count, index, entry, *attribute_check)
            if failure is not None:
                log('[UVH-DISPLAY] VALUE skill={} index={} field={} status=UNAVAILABLE {}'.format(
                    name(definition)[:96], index, field, failure))
            else:
                log('[UVH-DISPLAY] VALUE skill={} index={} field={} status=VERIFIED {}'.format(
                    name(definition)[:96], index, field, result))
                if field == 'Attribute':
                    attributes += 1
                    present += value is not None
                    absent += value is None
                else:
                    flags += 1
            _presentation_text_reference(context, definition, cls, count, index, entry)
    _upgrade_state(context)
    current = getattr(definition, 'SkillEffectPresentations')
    if (read(definition, 'Class') != context['skill_class']
            or not isinstance(current, unrealsdk.unreal.WrappedArray) or len(current) != count):
        raise ValueError('presentation array length/definition class changed during snapshot')
    _upgrade_state(context)
    return count, shown, flags, attributes, present, absent


def inspect_overclock_presentation_display(_option=None):
    """Explicit synchronous flags/identities only; no Attribute evaluation."""
    import unrealsdk
    log('[UVH-DISPLAY] BEGIN v0.2.11 snapshot (READ ONLY; DO NOT BUY)')
    if (_init_armed or _init_hooks or _trace_hooks or _upgrade_context is not None or _upgrade_hooks
            or _ui_context is not None or _ui_hooks or _skillstate_context is not None or _skillstate_hooks):
        log('[UVH-DISPLAY] NOT INSPECTED: initialization/other observers must be stopped.')
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
                       skill_class=read(record['node'], 'Class'))
        context['baseline'] = _upgrade_state(context)
        log('[UVH-DISPLAY] BASELINE points={} ranks={}'.format(context['baseline'][0], context['baseline'][1]))
        metadata, complete, total_verified, total_fields = {}, 0, 0, 0
        for definition in context['definitions']:
            _upgrade_state(context)
            try:
                count, shown, flags, attributes, present, absent = _presentation_display_details(context, definition, metadata)
            except Exception as exc:
                log('[UVH-DISPLAY] SUMMARY skill={} snapshot=ABORTED {}: {!r}'.format(
                    name(definition)[:96], type(exc).__name__, str(exc)[:180]))
                raise
            verified, expected = flags + attributes, shown * 4
            status = 'NOT_APPLICABLE' if expected == 0 else ('VERIFIED' if verified == expected else 'PARTIAL')
            log('[UVH-DISPLAY] SUMMARY skill={} array=VERIFIED count={} references={}/{} flags={}/{} attributes={}/{} present={} absent={} display={}'.format(
                name(definition)[:96], count, shown, count, flags, shown * 3, attributes, shown, present, absent, status))
            total_verified += verified
            total_fields += expected
            complete += verified == expected
            _upgrade_state(context)
        state = _upgrade_state(context)
        log('[UVH-DISPLAY] FINAL points={} ranks={} unchanged_from_start=True'.format(state[0], state[1]))
        log('[UVH-DISPLAY] END complete_targets={}/3 fields={}/{} observers_added=0; no writes/native queries.'.format(
            complete, total_verified, total_fields))
        log('[UVH-DISPLAY] Flags/reference identities are not evaluated effects or eligibility. DO NOT BUY; CANCEL and exit.')
        return complete == 3
    except Exception as exc:
        log('[UVH-DISPLAY] ABORT {}: {!r}; no repair/refund attempted. CANCEL and exit.'.format(
            type(exc).__name__, str(exc)[:180]))
        return False


def _attribute_class_identity(cls):
    """Bounded SDK UClass metadata only; never an Attribute object's path."""
    import unrealsdk
    if not isinstance(cls, unrealsdk.unreal.UClass):
        raise ValueError('class metadata is not a loaded SDK UClass')
    label = getattr(cls, 'Name')
    if type(label) is not str or not 0 < len(label) <= 96:
        raise ValueError('class name is unknown or exceeds metadata bounds')
    path = cls._path_name()
    if type(path) is not str or not 0 < len(path) <= 384:
        raise ValueError('class path is unknown or exceeds metadata bounds')
    return label, path


def _attribute_class_reference(context, definition, cls, count, index, entry, declared, value, actual, path):
    """Check the same field/class identity without accepting it for gameplay use."""
    import unrealsdk
    _presentation_text_reference(context, definition, cls, count, index, entry)
    if _presentation_display_property(cls, 'Attribute') != declared:
        raise ValueError('declared Attribute class changed')
    _presentation_text_reference(context, definition, cls, count, index, entry)
    current = getattr(entry, 'Attribute')
    _presentation_text_reference(context, definition, cls, count, index, entry)
    if isinstance(value, unrealsdk.unreal.UObject):
        if not isinstance(current, unrealsdk.unreal.UObject) or current != value:
            raise ValueError('Attribute reference changed')
        current_class = getattr(current, 'Class')
        same = current_class == actual if isinstance(actual, unrealsdk.unreal.UClass) else current_class is actual
        if not same:
            raise ValueError('actual Attribute class changed')
    elif current is not value:
        raise ValueError('absence or unknown Attribute wrapper changed')
    if _presentation_display_property(cls, 'Attribute') != declared:
        raise ValueError('Attribute schema changed during reference check')
    _presentation_text_reference(context, definition, cls, count, index, entry)
    current_path = entry._path_name()
    _presentation_text_reference(context, definition, cls, count, index, entry)
    if type(current_path) is not str or current_path != path:
        raise ValueError('observed presentation identity path changed')
    if isinstance(value, unrealsdk.unreal.UObject):
        current_class = getattr(value, 'Class')
        same = current_class == actual if isinstance(actual, unrealsdk.unreal.UClass) else current_class is actual
        if not same:
            raise ValueError('actual Attribute class changed during reference check')
    _upgrade_state(context)


def _attribute_class_ancestry(guard, actual, declared):
    """At most eight loaded class nodes, using documented SuperField metadata."""
    import unrealsdk
    rows, cursor, coverage = [], actual, 'UNAVAILABLE'
    for _ in range(8):
        guard()
        try:
            identity = _attribute_class_identity(cursor)
            parent = getattr(cursor, 'SuperField')  # Getter errors are never a root.
        except Exception:
            guard()
            break
        guard()
        rows.append((cursor, identity, parent))
        if parent is None:
            coverage = 'COMPLETE'
            break
        if not isinstance(parent, unrealsdk.unreal.UClass):
            break
        if any(parent == row[0] for row in rows):
            coverage = 'CYCLE'
            break
        cursor = parent
    else:
        coverage = 'CAPPED'
    # No chain is logged until every captured identity/link is still current.
    for cls, identity, parent in rows:
        guard()
        if _attribute_class_identity(cls) != identity:
            raise ValueError('class identity metadata changed')
        current = getattr(cls, 'SuperField')
        same = current == parent if isinstance(parent, unrealsdk.unreal.UClass) else current is parent
        if not same:
            raise ValueError('class ancestry metadata changed')
        guard()
    seen_declared = any(cls == declared for cls, _, _ in rows)
    relation = 'UNKNOWN'
    if coverage in ('COMPLETE', 'CAPPED'):
        if actual == declared and seen_declared:
            relation = 'EXACT'
        elif seen_declared:
            relation = 'DERIVED'
        elif coverage == 'COMPLETE':
            relation = 'NO'
    return rows, coverage, relation


def inspect_overclock_attribute_class(_option=None):
    """One combined wrapper/class/ancestry test of the previously refused field."""
    import unrealsdk
    log('[UVH-CLASS] BEGIN v0.2.11 combined metadata snapshot (READ ONLY; DO NOT BUY)')
    if (_init_armed or _init_hooks or _trace_hooks or _upgrade_context is not None or _upgrade_hooks
            or _ui_context is not None or _ui_hooks or _skillstate_context is not None or _skillstate_hooks):
        log('[UVH-CLASS] NOT INSPECTED: initialization/other observers must be stopped.')
        return False
    try:
        pc, record = get_pc(possibly_loading=True), _uvh_node_state
        if record is None or 'init_tree' not in record or len(record['skills']) != 2:
            raise ValueError('ARM before Continue with the owned inert node')
        modes = unrealsdk.find_enum('ENetMode')
        context = dict(pc=pc, tree=record['init_tree'], record=record, pawn=read(pc, 'Pawn'),
                       world=read(pc, 'WorldInfo'), pri=read(pc, 'PlayerReplicationInfo'),
                       modes=(modes.NM_Standalone, modes.NM_ListenServer),
                       definitions=(record['node'], record['skills'][0], record['skills'][1]),
                       skill_class=read(record['node'], 'Class'))
        context['baseline'] = _upgrade_state(context)
        log('[UVH-CLASS] BASELINE points={} ranks={}'.format(context['baseline'][0], context['baseline'][1]))
        definition, index = context['definitions'][2], 1
        if name(definition) != 'Myelin':
            raise ValueError('refused presentation target is not current Myelin')
        cls = _presentation_metadata(definition)
        _upgrade_state(context)
        values = getattr(definition, 'SkillEffectPresentations')
        if not isinstance(values, unrealsdk.unreal.WrappedArray) or not 2 <= len(values) <= 256:
            raise ValueError('Myelin presentation count/wrapper is unknown or outside bounds')
        count, entry = len(values), values[index]
        _presentation_text_reference(context, definition, cls, count, index, entry)
        path = entry._path_name()
        _presentation_text_reference(context, definition, cls, count, index, entry)
        expected = 'GD_Tulip_Mechromancer_Skills.LittleBigTrouble.Myelin:AttributePresentationDefinition_0'
        if type(path) is not str or path != expected:
            raise ValueError('Myelin index1 is not the observed shield-capacity presentation')
        declared = _presentation_display_property(cls, 'Attribute')
        _presentation_text_reference(context, definition, cls, count, index, entry)
        try:
            value = getattr(entry, 'Attribute')
            actual = getattr(value, 'Class') if isinstance(value, unrealsdk.unreal.UObject) else None
        except Exception as exc:
            _presentation_text_reference(context, definition, cls, count, index, entry)
            if _presentation_display_property(cls, 'Attribute') != declared:
                raise ValueError('Attribute descriptor changed at unavailable getter')
            _presentation_text_reference(context, definition, cls, count, index, entry)
            log('[UVH-CLASS] FIELD status=UNAVAILABLE getter_error={}'.format(type(exc).__name__))
            raise ValueError('Attribute field/class getter unavailable') from None
        guard = lambda: _attribute_class_reference(context, definition, cls, count, index, entry, declared, value, actual, path)
        guard()
        rows, labels, coverage, relation = [], None, 'NOT_APPLICABLE', 'UNKNOWN'
        if value is None:
            wrapper, complete = 'KNOWN_ABSENT', True
        elif not isinstance(value, unrealsdk.unreal.UObject):
            wrapper, coverage, complete = 'UNKNOWN', 'UNAVAILABLE', False
        elif not isinstance(actual, unrealsdk.unreal.UClass):
            wrapper, coverage, complete = 'SDK_UOBJECT', 'UNAVAILABLE', False
        else:
            wrapper, coverage, complete = 'SDK_UOBJECT', 'UNAVAILABLE', False
            try:
                labels = (_attribute_class_identity(declared), _attribute_class_identity(actual))
            except Exception:
                guard()
            else:
                guard()
                rows, coverage, relation = _attribute_class_ancestry(guard, actual, declared)
                guard()
                if labels != (_attribute_class_identity(declared), _attribute_class_identity(actual)):
                    raise ValueError('declared/actual class metadata changed')
                guard()
                complete = coverage == 'COMPLETE'
        guard()
        log('[UVH-CLASS] REFERENCE skill=Myelin index=1 count={} path={!r}'.format(count, path))
        log('[UVH-CLASS] FIELD wrapper={} actual_class={} status={}'.format(
            wrapper, 'SDK_UCLASS' if isinstance(actual, unrealsdk.unreal.UClass) else 'UNAVAILABLE',
            'VERIFIED_ABSENCE' if value is None else ('VERIFIED_METADATA' if complete else 'PARTIAL_UNAVAILABLE')))
        if labels is not None:
            for role, (label, class_path) in zip(('DECLARED', 'ACTUAL'), labels):
                log('[UVH-CLASS] CLASS role={} name={!r} path={!r}'.format(role, label, class_path))
        for depth, (_, (label, class_path), _) in enumerate(rows):
            log('[UVH-CLASS] ANCESTOR depth={} name={!r} path={!r}'.format(depth, label, class_path))
        log('[UVH-CLASS] ANCESTRY coverage={} classes={} declared_relation={}'.format(coverage, len(rows), relation))
        guard()
        state = _upgrade_state(context)
        log('[UVH-CLASS] FINAL points={} ranks={} unchanged_from_start=True'.format(state[0], state[1]))
        log('[UVH-CLASS] END combined_checks=wrapper,class,ancestry observers_added=0; no writes/native queries.')
        log('[UVH-CLASS] Metadata does not authorize gameplay use. DO NOT BUY; CANCEL and exit.')
        return complete
    except Exception as exc:
        # Do not stringify getter exceptions which could contain unknown objects.
        log('[UVH-CLASS] ABORT {}: metadata/current state unavailable or changed; no repair/refund. CANCEL and exit.'.format(type(exc).__name__))
        return False


_DEATHTRAP_FIELDS = (
    ('Duration', 'ZFloatProperty'), ('DurationBaseValue', 'ZFloatProperty'),
    ('ActivatedTime', 'ZFloatProperty'), ('SkillInstigator', 'ZObjectProperty'),
    ('Definition', 'ZObjectProperty'), ('DurationModifierStack', 'ZArrayProperty'),
)


def _deathtrap_int(value, maximum, minimum=0):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError('invalid numeric metadata')
    return value


def _deathtrap_label(value, path=False):
    import re
    limit = 384 if path else 96
    pattern = r'[A-Za-z_][A-Za-z0-9_.:]*' if path else r'[A-Za-z_][A-Za-z0-9_]*'
    if type(value) is not str or not 0 < len(value) <= limit or re.fullmatch(pattern, value) is None:
        raise ValueError('invalid metadata label')
    return value


def _deathtrap_class(cls):
    import unrealsdk
    if not isinstance(cls, unrealsdk.unreal.UClass):
        raise ValueError('not an SDK UClass')
    try:
        label, path, parent, size = cls.Name, cls._path_name(), cls.SuperField, cls.PropertySize
    except Exception:
        raise LookupError('class metadata unavailable') from None
    _deathtrap_label(label)
    _deathtrap_label(path, True)
    if not path.endswith('.' + label) or (parent is not None and not isinstance(parent, unrealsdk.unreal.UClass)):
        raise ValueError('noncanonical class or untyped parent')
    return cls, label, path, parent, _deathtrap_int(size, 1048576)


def _deathtrap_session(context):
    import unrealsdk
    current = get_pc(possibly_loading=True)
    if not isinstance(current, unrealsdk.unreal.UObject):
        raise ValueError('untyped current controller')
    _deathtrap_class(context['pc'].Class)
    if (_init_armed or _init_hooks or _trace_hooks or _upgrade_context is not None or _upgrade_hooks
            or _ui_context is not None or _ui_hooks or _skillstate_context is not None or _skillstate_hooks):
        raise ValueError('initialization or observers overlap')
    return _upgrade_state(context)


def _deathtrap_check(context, checks):
    _deathtrap_session(context)
    for getter, expected in checks:
        try:
            current = getter()
        except Exception:
            raise ValueError('captured metadata became unavailable or invalid') from None
        if current != expected:
            raise ValueError('captured metadata changed')
        _deathtrap_session(context)


def _deathtrap_chain(context, checks, cls):
    nodes, cursor, coverage = [], cls, 'CAPPED'
    for _ in range(8):
        _deathtrap_session(context)
        current = _deathtrap_class(cursor)
        if any(current[0] == old[0] for old in nodes):
            raise ValueError('cyclic class metadata')
        nodes.append(current)
        checks.append((lambda item=cursor: _deathtrap_class(item), current))
        if current[3] is None:
            coverage = 'COMPLETE'
            break
        if any(current[3] == old[0] for old in nodes):
            raise ValueError('cyclic class metadata')
        cursor = current[3]
    return nodes, coverage


def _deathtrap_property(prop, owners, class_field=False):
    import unrealsdk
    sdk = unrealsdk.unreal
    if not isinstance(prop, sdk.ZProperty):
        raise ValueError('not an SDK property')
    try:
        values = (prop.Name, prop.Outer, prop.PropertyFlags, prop.Offset_Internal,
                  prop.ArrayDim, prop.ElementSize, prop.PropertyLinkNext)
        declared = prop.PropertyClass if isinstance(prop, sdk.ZObjectProperty) else None
        inner = prop.Inner if isinstance(prop, sdk.ZArrayProperty) else None
    except Exception:
        raise LookupError('property metadata unavailable') from None
    label, owner, flags, offset, dim, element, next_prop = values
    _deathtrap_label(label)
    if not isinstance(owner, (sdk.UClass, sdk.UFunction, sdk.ZProperty)) or not any(owner == item for item in owners):
        raise ValueError('property declaring owner is not verified')
    _deathtrap_int(flags, 2 ** 64 - 1)
    _deathtrap_int(offset, 1048576)
    _deathtrap_int(dim, 1 if class_field else 64, 1)
    _deathtrap_int(element, 65536, 1)
    if offset + dim * element > 1048576 or (class_field and flags & 0x580):
        raise ValueError('invalid field bounds or parameter flags')
    if next_prop is not None and not isinstance(next_prop, sdk.ZProperty):
        raise ValueError('untyped property link')
    if next_prop is not None and next_prop == prop:
        raise ValueError('cyclic property link')
    if isinstance(prop, sdk.ZObjectProperty) and not isinstance(declared, sdk.UClass):
        raise ValueError('untyped declared object class')
    if isinstance(prop, sdk.ZArrayProperty) and not isinstance(inner, sdk.ZProperty):
        raise ValueError('untyped array inner')
    if inner is not None and inner == prop:
        raise ValueError('cyclic array inner')
    return prop, label, _deathtrap_label(type(prop).__name__), owner, flags, offset, dim, element, next_prop, declared, inner


def _deathtrap_field_snapshot(cls, field, kind, owners):
    import unrealsdk
    try:
        prop = cls._find_prop(field)
    except Exception:
        raise LookupError('field lookup unavailable') from None
    if not isinstance(prop, getattr(unrealsdk.unreal, kind)):
        raise ValueError('field has unexpected SDK property type')
    data = _deathtrap_property(prop, owners, True)
    if data[1] != field:
        raise ValueError('field lookup name mismatch')
    inner_data = None
    if data[10] is not None:
        inner_data = _deathtrap_property(data[10], (prop, data[3]), True)
    return data, inner_data


def _deathtrap_function_header(cls, method, owners):
    import unrealsdk
    sdk = unrealsdk.unreal
    try:
        func = cls._find(method)
    except Exception:
        raise LookupError('function lookup unavailable') from None
    if not isinstance(func, sdk.UFunction):
        raise ValueError('lookup is not an SDK UFunction')
    try:
        label, owner, path = func.Name, func.Outer, func._path_name()
        numbers = (func.FunctionFlags, func.NumParams, func.ParamsSize, func.ReturnValueOffset, func.PropertySize)
        links = (func.SuperField, func.Children, func.PropertyLink)
        ret = func._find_return_param()
    except Exception:
        raise LookupError('function metadata unavailable') from None
    _deathtrap_label(label)
    _deathtrap_label(path, True)
    if label != method or not isinstance(owner, sdk.UClass) or not any(owner == item for item in owners):
        raise ValueError('function declaring owner or name mismatch')
    owner_path = _deathtrap_class(owner)[2]
    if path not in (owner_path + ':' + method, owner_path + '.' + method):
        raise ValueError('function path does not match its owner')
    for number, maximum in zip(numbers, (2 ** 32 - 1, 255, 65535, 65535, 1048576)):
        _deathtrap_int(number, maximum)
    if links[0] is not None:
        raise LookupError('inherited function metadata is not supported')
    if links[1] is not None and not isinstance(links[1], sdk.UField):
        raise ValueError('untyped function child')
    if links[2] is not None and not isinstance(links[2], sdk.ZProperty):
        raise ValueError('untyped function property link')
    if ret is not None and not isinstance(ret, sdk.ZProperty):
        raise ValueError('untyped function return descriptor')
    return func, label, owner, path, numbers, links, ret


def _deathtrap_function(context, checks, cls, method, owners):
    import unrealsdk
    header = _deathtrap_function_header(cls, method, owners)
    checks.append((lambda: _deathtrap_function_header(cls, method, owners), header))
    func, _, _, _, numbers, links, ret = header
    props, coverage, extra = [], 'COMPLETE', None
    try:
        iterator = iter(func._properties())
        for index in range(17):
            _deathtrap_session(context)
            try:
                prop = next(iterator)
            except StopIteration:
                break
            if index == 16:
                if not isinstance(prop, unrealsdk.unreal.ZProperty):
                    raise ValueError('untyped capped property link')
                extra, coverage = prop, 'CAPPED'
                break
            data = _deathtrap_property(prop, (func,))
            if any(data[1] == old[1] or data[0] == old[0] for old in props):
                raise ValueError('duplicate or cyclic function property')
            if data[5] + data[6] * data[7] > numbers[4]:
                raise ValueError('function property outside metadata size')
            props.append(data)
            checks.append((lambda item=prop: _deathtrap_property(item, (func,)), data))
    except (ValueError, LookupError):
        raise
    except Exception:
        raise LookupError('function property enumeration unavailable') from None
    if links[2] != (props[0][0] if props else None):
        raise ValueError('function property root disagrees with enumeration')
    for index, data in enumerate(props):
        expected_next = props[index + 1][0] if index + 1 < len(props) else extra
        if data[8] != expected_next:
            raise ValueError('function property links disagree with enumeration')
    marked = [data for data in props if data[4] & 0x400]
    selected_return = next((data for data in props if ret is not None and data[0] == ret), None)
    if len(marked) > 1 or (ret is None and marked):
        raise ValueError('ambiguous return metadata')
    if selected_return is not None:
        if not selected_return[4] & 0x400 or selected_return[5] != numbers[3]:
            raise ValueError('return flag/offset mismatch')
    elif ret is not None and coverage == 'COMPLETE':
        raise ValueError('return descriptor outside complete enumeration')
    if marked and marked[0][0] != ret:
        raise ValueError('return descriptor disagreement')
    _deathtrap_check(context, checks)
    return header, props, coverage, selected_return


def inspect_deathtrap_readiness(_option=None):
    """One bounded synchronous loaded-metadata collection; no gameplay calls."""
    import json
    import unrealsdk
    prefix = '[UVH-DEATHTRAP]'
    log(prefix + ' BEGIN v0.2.14 metadata_only=True')
    rows, checks, roots, statuses, class_paths = [], [], [], [], []
    try:
        pc, record = get_pc(possibly_loading=True), _uvh_node_state
        if record is None or 'init_tree' not in record or len(record['skills']) != 2:
            raise ValueError('owned inert initialization record unavailable')
        if not isinstance(pc, unrealsdk.unreal.UObject):
            raise ValueError('untyped controller before state reads')
        modes = unrealsdk.find_enum('ENetMode')
        context = dict(pc=pc, tree=record['init_tree'], record=record, pawn=read(pc, 'Pawn'),
                       world=read(pc, 'WorldInfo'), pri=read(pc, 'PlayerReplicationInfo'),
                       modes=(modes.NM_Standalone, modes.NM_ListenServer),
                       definitions=(record['node'], record['skills'][0], record['skills'][1]))
        for value in (pc, context['tree'], context['pawn'], context['world'], context['pri'], *context['definitions']):
            if not isinstance(value, unrealsdk.unreal.UObject):
                raise ValueError('untyped current session object')
        controller = pc.Class
        controller_data = _deathtrap_class(controller)
        context['baseline'] = _deathtrap_session(context)
        checks.append((lambda: _deathtrap_class(pc.Class), controller_data))

        def target(cls, label):
            if len(roots) >= 4 or any(cls == item for item in roots):
                raise ValueError('ambiguous or excessive target classes')
            chain, coverage = _deathtrap_chain(context, checks, cls)
            roots.append(cls)
            class_paths.extend((item[0], item[2]) for item in chain)
            statuses.append(coverage)
            rows.append(dict(kind='CLASS', target=label, path=chain[0][2], coverage=coverage,
                             ancestry=[dict(name=item[1], path=item[2]) for item in chain]))
            return tuple(item[0] for item in chain)

        owners = target(controller, 'controller')

        object_property_tags = ('ZClassProperty', 'ZComponentProperty', 'ZLazyObjectProperty', 'ZObjectProperty', 'ZSoftClassProperty', 'ZSoftObjectProperty', 'ZWeakObjectProperty')
        nonobject_property_tags = ('ZArrayProperty', 'ZBoolProperty', 'ZByteAttributeProperty', 'ZByteProperty', 'ZDelegateProperty', 'ZDoubleProperty', 'ZEnumProperty', 'ZFloatAttributeProperty', 'ZFloatProperty', 'ZGameDataHandleProperty', 'ZGbxDefPtrProperty', 'ZGbxInlineStructProperty', 'ZInt16Property', 'ZInt64Property', 'ZInt8Property', 'ZIntAttributeProperty', 'ZIntProperty', 'ZInterfaceProperty', 'ZMulticastDelegateProperty', 'ZNameProperty', 'ZProperty', 'ZStrProperty', 'ZStructProperty', 'ZTextProperty', 'ZUInt16Property', 'ZUInt32Property', 'ZUInt64Property')

        def parameter_class_snapshot(cls):
            try:
                return 'COMPLETE', _deathtrap_class(cls)
            except LookupError:
                return 'UNAVAILABLE', None

        def capture_function(cls, method, selected_owners):
            try:
                header, props, coverage, ret = _deathtrap_function(context, checks, cls, method, selected_owners)
            except LookupError:
                _deathtrap_check(context, checks)
                statuses.append('UNAVAILABLE')
                rows.append(dict(kind='FUNCTION', name=method, coverage='UNAVAILABLE'))
                return None
            property_rows, class_statuses = [], []
            for prop in props:
                _deathtrap_check(context, checks)
                if isinstance(prop[0], unrealsdk.unreal.ZObjectProperty):
                    if prop[2] not in object_property_tags:
                        raise ValueError('unsupported object property type tag')
                    snapshot = parameter_class_snapshot(prop[9])
                    checks.append((lambda cls=prop[9]: parameter_class_snapshot(cls), snapshot))
                    class_coverage, class_header = snapshot
                    declared = class_header[2] if class_header is not None else 'UNAVAILABLE'
                else:
                    if prop[2] not in nonobject_property_tags:
                        raise ValueError('unsupported nonobject property type tag')
                    class_coverage, declared = 'NOT_APPLICABLE', 'NOT_APPLICABLE'
                property_rows.append(dict(name=prop[1], type=prop[2], flags=prop[4], offset=prop[5],
                                          dimension=prop[6], element_size=prop[7],
                                          declared_class=declared, declared_class_coverage=class_coverage))
                class_statuses.append(class_coverage)
                _deathtrap_check(context, checks)
            parameter_coverage = ('CAPPED' if coverage == 'CAPPED' else
                                  'UNAVAILABLE' if 'UNAVAILABLE' in class_statuses else
                                  'COMPLETE' if 'COMPLETE' in class_statuses else 'NOT_APPLICABLE')
            statuses.append(coverage)
            if parameter_coverage != 'NOT_APPLICABLE':
                statuses.append(parameter_coverage)
            rows.append(dict(kind='FUNCTION', name=method, path=header[3], coverage=coverage,
                             flags=header[4][0], num_params=header[4][1], params_size=header[4][2],
                             return_offset=header[4][3], signature='NOT_ESTABLISHED',
                             parameter_classes_coverage=parameter_coverage, properties=property_rows))
            return ret

        primary = capture_function(controller, 'GetSkillManager', owners)
        if primary is None:
            statuses.append('UNAVAILABLE')
            rows.append(dict(kind='DISCOVERY', target='manager', coverage='UNAVAILABLE'))
        else:
            if not isinstance(primary[0], unrealsdk.unreal.ZObjectProperty):
                raise ValueError('manager return is not a typed object descriptor')
            manager = primary[9]
            manager_owners = target(manager, 'manager')
            rows.append(dict(kind='DISCOVERY', source_function='GetSkillManager', return_property=primary[1],
                             return_class=next(path for item, path in class_paths if item == manager)))
            for method in ('ActivateSkill', 'DeactivateSkill'):
                capture_function(manager, method, manager_owners)
            try:
                field = _deathtrap_field_snapshot(manager, 'ActiveSkills', 'ZArrayProperty', manager_owners)
            except LookupError:
                _deathtrap_check(context, checks)
                statuses.append('UNAVAILABLE')
                rows.append(dict(kind='FIELD', name='ActiveSkills', coverage='UNAVAILABLE'))
            else:
                checks.append((lambda: _deathtrap_field_snapshot(manager, 'ActiveSkills', 'ZArrayProperty', manager_owners), field))
                data, inner = field
                if inner is None or not isinstance(inner[0], unrealsdk.unreal.ZObjectProperty):
                    raise ValueError('ActiveSkills inner is not a typed object descriptor')
                skill = inner[9]
                skill_owners = target(skill, 'active_skill_class')
                rows.append(dict(kind='FIELD', name='ActiveSkills', type=data[2], flags=data[4], offset=data[5],
                                 dimension=data[6], element_size=data[7], inner_type=inner[2], coverage='COMPLETE',
                                 owner=next(path for item, path in class_paths if item == data[3]),
                                 element_class=next(path for item, path in class_paths if item == skill)))
                for field_name, kind in _DEATHTRAP_FIELDS:
                    try:
                        captured = _deathtrap_field_snapshot(skill, field_name, kind, skill_owners)
                    except LookupError:
                        _deathtrap_check(context, checks)
                        statuses.append('UNAVAILABLE')
                        rows.append(dict(kind='FIELD', name=field_name, coverage='UNAVAILABLE'))
                        continue
                    checks.append((lambda field_name=field_name, kind=kind:
                                   _deathtrap_field_snapshot(skill, field_name, kind, skill_owners), captured))
                    data, inner_data = captured
                    if field_name == 'SkillInstigator' and not any(data[9] == item for item in owners):
                        raise ValueError('instigator descriptor class is outside controller ancestry')
                    if field_name == 'Definition':
                        definition_class = data[9]
                        for definition in context['definitions']:
                            current = _deathtrap_class(definition.Class)
                            if current[0] != definition_class:
                                raise ValueError('definition descriptor class differs from owned definitions')
                            checks.append((lambda item=definition: _deathtrap_class(item.Class), current))
                        target(definition_class, 'definition_class')
                    rows.append(dict(kind='FIELD', name=field_name, type=data[2], flags=data[4], offset=data[5],
                                     dimension=data[6], element_size=data[7], coverage='COMPLETE',
                                     inner_type=inner_data[2] if inner_data is not None else 'NOT_APPLICABLE',
                                     owner=next(path for item, path in class_paths if item == data[3]),
                                     declared_class=(next(path for item, path in class_paths if item == data[9])
                                                     if data[9] is not None else 'NOT_APPLICABLE')))
        _deathtrap_check(context, checks)
        status = 'CAPPED' if 'CAPPED' in statuses else ('UNAVAILABLE' if 'UNAVAILABLE' in statuses else 'COMPLETE')
        state = _deathtrap_session(context)
        for row in rows:
            _deathtrap_check(context, checks)
            log(prefix + ' METADATA ' + json.dumps(row, sort_keys=True))
        _deathtrap_check(context, checks)
        log(prefix + ' FINAL points={} ranks={} unchanged_from_start=True'.format(state[0], state[1]))
        _deathtrap_check(context, checks)
        log(prefix + ' END coverage={} observers_added=0 native_calls=0 writes=0 signature=NOT_ESTABLISHED'.format(status))
        return status == 'COMPLETE'
    except LookupError:
        log(prefix + ' UNAVAILABLE metadata collection incomplete; no signature or absence inferred')
        return False
    except Exception:
        log(prefix + ' ABORT coverage=REFUSED; invalid/unavailable/drifting state or metadata; no repair')
        return False


_DT_EVENT_PATH = 'WillowGame.SkillEffectManager:DeactivateSkill'
_DT_EVENT_IDENT = 'UVH_DT_EVENT_V15_DEACTIVATE_PRE'
_DT_EVENT_INTEGER_MAX = 2147483647
_dt_event_context = None
_dt_event_closing_context = None
_dt_event_handles = []
_dt_event_uncertain = []
_dt_event_epoch = 0
_dt_event_busy = False
_dt_event_starting = False
_dt_event_stop_requested = False
_dt_event_stats = None


class _DTEventRefusal(Exception):
    def __init__(self, reason):
        self.reason = reason


class _DTEventChecks(list):
    def append(self, value):
        if len(self) >= 32:
            raise _DTEventRefusal('METADATA')
        super().append(value)


def _dt_event_emit(payload):
    prefix = '[UVH-DT-EVENT] '
    if type(payload) is not str or len((prefix + payload).encode('utf-8')) > 256:
        return False
    try:
        log(prefix + payload)
        return True
    except Exception:
        return False


def _dt_event_integer(value):
    if type(value) is not int or not 0 <= value <= _DT_EVENT_INTEGER_MAX:
        raise _DTEventRefusal('STATE')
    return value


def _dt_event_clock(context=None):
    import math
    import time
    now = time.monotonic()
    if type(now) is not float or not math.isfinite(now) or now < 0:
        raise _DTEventRefusal('CLOCK')
    if context is not None:
        elapsed = now - context['started']
        if now < context['last_time'] or not math.isfinite(elapsed) or elapsed < 0:
            raise _DTEventRefusal('CLOCK')
        context['last_time'] = now
    return now


def _dt_event_guard(context):
    try:
        state = _deathtrap_session(context)
    except Exception:
        raise _DTEventRefusal('STATE') from None
    for value in (*state[0], *state[1], *state[2], state[3]):
        _dt_event_integer(value)
    return state


def _dt_event_metadata(context):
    checks = _DTEventChecks()
    try:
        controller = context['pc'].Class
        captured = _deathtrap_class(controller)
        checks.append((lambda: _deathtrap_class(context['pc'].Class), captured))
        chain, coverage = _deathtrap_chain(context, checks, controller)
        if coverage != 'COMPLETE' or chain[0][2] != 'WillowGame.WillowPlayerController':
            raise ValueError()
        owners = tuple(item[0] for item in chain)
        header, props, coverage, ret = _deathtrap_function(context, checks, controller, 'GetSkillManager', owners)
        if (coverage != 'COMPLETE' or header[3] != 'WillowGame.WillowPlayerController:GetSkillManager'
                or header[4][:4] != (132097, 1, 4, 0) or len(props) != 1 or ret is None):
            raise ValueError()
        p = props[0]
        if (p[1:3] != ('ReturnValue', 'ZObjectProperty') or p[4:8] != (1408, 0, 1, 4)
                or p[0] != ret[0]):
            raise ValueError()
        manager = p[9]
        chain, coverage = _deathtrap_chain(context, checks, manager)
        if coverage != 'COMPLETE' or chain[0][2] != 'WillowGame.SkillEffectManager':
            raise ValueError()
        manager_owners = tuple(item[0] for item in chain)
        header, props, coverage, ret = _deathtrap_function(context, checks, manager, 'DeactivateSkill', manager_owners)
        if (coverage != 'COMPLETE' or header[3] != _DT_EVENT_PATH
                or header[4][:4] != (149506, 3, 12, 65535) or ret is not None or len(props) != 3):
            raise ValueError()
        specs = (('SkillInstigator', 'ZObjectProperty', 128, 0, 'Engine.Controller'),
                 ('Definition', 'ZObjectProperty', 128, 4, 'WillowGame.SkillDefinition'),
                 ('bIgnoreSkillInstigator', 'ZBoolProperty', 144, 8, None))
        for p, spec in zip(props, specs):
            label, kind, flags, offset, declared_path = spec
            if p[1:3] != (label, kind) or p[4:8] != (flags, offset, 1, 4):
                raise ValueError()
            if declared_path is not None:
                captured = _deathtrap_class(p[9])
                if captured[2] != declared_path:
                    raise ValueError()
                if label == 'SkillInstigator' and not any(p[9] == item for item in owners):
                    raise ValueError()
                checks.append((lambda cls=p[9]: _deathtrap_class(cls), captured))
                if label == 'Definition':
                    for definition in context['definitions']:
                        captured = _deathtrap_class(definition.Class)
                        if captured[0] != p[9] or captured[2] != declared_path:
                            raise ValueError()
                        checks.append((lambda obj=definition: _deathtrap_class(obj.Class), captured))
        _deathtrap_check(context, checks)
        return checks
    except _DTEventRefusal:
        raise
    except Exception:
        raise _DTEventRefusal('METADATA') from None


def _dt_event_revalidate(context, active=False):
    def stopped():
        return active and (_dt_event_context is not context or _dt_event_stop_requested)
    if stopped():
        return False
    _dt_event_guard(context)
    for getter, expected in context['checks']:
        if stopped():
            return False
        try:
            current = getter()
        except Exception:
            raise _DTEventRefusal('METADATA') from None
        if stopped():
            return False
        if current != expected:
            raise _DTEventRefusal('METADATA')
        _dt_event_guard(context)
    return not stopped()


def _dt_event_locked():
    return (_dt_event_context is not None or _dt_event_closing_context is not None
            or bool(_dt_event_handles) or bool(_dt_event_uncertain) or _dt_event_busy or _dt_event_starting)


def _dt_event_option_gate(handler):
    from functools import wraps
    @wraps(handler)
    def dispatch(option=None):
        if _cr_locked():
            _cr_emit('NOT_STARTED reason=OVERLAP')
            return False
        if _dt_event_locked():
            _dt_event_emit('NOT_STARTED reason=OVERLAP')
            return False
        return handler(option)
    return dispatch


def _dt_event_finish(reason, limit=False):
    global _dt_event_context, _dt_event_closing_context, _dt_event_stop_requested
    if _dt_event_context is not None:
        _dt_event_closing_context = _dt_event_context
    _dt_event_context = None
    _dt_event_stop_requested = True
    if _dt_event_stats is not None:
        if limit:
            _dt_event_stats['limit'] = reason
        else:
            _dt_event_stats['refused'] = True
    _dt_event_emit(('LIMIT reason=' if limit else 'ABORT reason=') + reason)


def stop_deathtrap_events(_option=None):
    global _dt_event_context, _dt_event_closing_context, _dt_event_handles
    global _dt_event_uncertain, _dt_event_epoch, _dt_event_stop_requested
    if not _dt_event_locked() and _dt_event_stats is None:
        return True
    context = _dt_event_context if _dt_event_context is not None else _dt_event_closing_context
    _dt_event_context = None
    _dt_event_closing_context = None
    _dt_event_epoch = min(_DT_EVENT_INTEGER_MAX, _dt_event_epoch + 1)
    if _dt_event_busy:
        _dt_event_closing_context = context
        _dt_event_stop_requested = True
        return False
    _dt_event_stop_requested = False
    stats = _dt_event_stats
    if context is not None:
        try:
            state = _dt_event_guard(context)
            now = _dt_event_clock(context)
            if now - context['started'] >= 30.0 and stats['limit'] is None:
                stats['limit'] = 'TIME'
                _dt_event_emit('LIMIT reason=TIME')
            if not _dt_event_emit('FINAL points={} ranks={} unchanged=True'.format(state[0], state[1])):
                stats['refused'] = True
        except Exception:
            stats['refused'] = True
            _dt_event_emit('FINAL UNVERIFIED reason=STATE')
    try:
        import unrealsdk
        phase = unrealsdk.hooks.Type.PRE
    except Exception:
        if stats is not None:
            stats['refused'] = True
        return False
    pending = []
    for path, ident in _dt_event_handles:
        failed = False
        try:
            removed = unrealsdk.hooks.remove_hook(path, phase, ident)
            absent = unrealsdk.hooks.has_hook(path, phase, ident)
            failed = type(removed) is not bool or type(absent) is not bool or absent
        except Exception:
            failed = True
        if failed:
            pending.append((path, ident))
            if stats is not None:
                stats['failures'] = min(_DT_EVENT_INTEGER_MAX, stats['failures'] + 1)
                stats['refused'] = True
            _dt_event_emit('REMOVAL_ERROR remaining=1')
    _dt_event_handles = pending
    uncertain = []
    for path, ident in _dt_event_uncertain:
        try:
            present = unrealsdk.hooks.has_hook(path, phase, ident)
            if type(present) is not bool or present:
                uncertain.append((path, ident))
        except Exception:
            uncertain.append((path, ident))
    _dt_event_uncertain = uncertain
    if stats is not None:
        if uncertain:
            stats['refused'] = True
        _dt_event_emit('STOP remaining={} captured={} attempts={} reentrant={} uncertain={} cleanup_failures={}'.format(
            len(pending) + len(uncertain), stats['captured'], stats['attempts'], stats['reentrant'], len(uncertain), stats['failures']))
        outcome = ('REFUSED' if stats['refused'] or pending or uncertain else
                   'OBSERVED_UNATTRIBUTED' if stats['captured'] else 'NOT_OBSERVED')
        _dt_event_emit('OUTCOME value=' + outcome)
    return not pending and not uncertain


def _dt_event_callback(epoch):
    def observe(obj, args, ret, func):
        global _dt_event_busy
        context = _dt_event_context
        if context is None or context['epoch'] != epoch or _dt_event_epoch != epoch:
            return None
        stats = _dt_event_stats
        stats['attempts'] = min(_DT_EVENT_INTEGER_MAX, stats['attempts'] + 1)
        if _dt_event_busy:
            stats['reentrant'] = min(_DT_EVENT_INTEGER_MAX, stats['reentrant'] + 1)
            if stats['attempts'] >= 64:
                _dt_event_finish('ATTEMPTS', limit=True)
            return None
        _dt_event_busy = True
        try:
            if stats['attempts'] >= 64:
                _dt_event_finish('ATTEMPTS', limit=True)
                return None
            if _dt_event_clock(context) - context['started'] >= 30.0:
                _dt_event_finish('TIME', limit=True)
                return None
            if not _dt_event_revalidate(context, active=True):
                return None
            _dt_event_guard(context)
            if _dt_event_clock(context) - context['started'] >= 30.0:
                _dt_event_finish('TIME', limit=True)
                return None
            if _dt_event_context is not context or _dt_event_stop_requested:
                return None
            ordinal = stats['captured'] + 1
            if not _dt_event_emit('EVENT ordinal={} target=DeactivateSkill phase=PRE attribution=NONE'.format(ordinal)):
                raise _DTEventRefusal('INTERNAL')
            stats['captured'] = ordinal
            if ordinal >= 24:
                _dt_event_finish('EVENTS', limit=True)
        except _DTEventRefusal as refusal:
            _dt_event_finish(refusal.reason)
        except Exception:
            _dt_event_finish('INTERNAL')
        finally:
            _dt_event_busy = False
            if _dt_event_stop_requested:
                stop_deathtrap_events()
        return None
    return observe


def start_deathtrap_events(_option=None):
    global _dt_event_context, _dt_event_epoch, _dt_event_stats, _dt_event_stop_requested
    global _dt_event_starting
    if _dt_event_locked():
        _dt_event_emit('NOT_STARTED reason=OVERLAP')
        return False
    _dt_event_stats = dict(captured=0, attempts=0, reentrant=0, failures=0, refused=False, limit=None)
    _dt_event_stop_requested = False
    _dt_event_starting = True
    try:
        import unrealsdk
        if _dt_event_epoch >= _DT_EVENT_INTEGER_MAX:
            raise _DTEventRefusal('INTERNAL')
        _dt_event_epoch += 1
        try:
            pc, record = get_pc(possibly_loading=True), _uvh_node_state
            if not isinstance(pc, unrealsdk.unreal.UObject) or record is None or 'init_tree' not in record or len(record['skills']) != 2:
                raise ValueError()
            modes = unrealsdk.find_enum('ENetMode')
            context = dict(pc=pc, tree=record['init_tree'], record=record, pawn=read(pc, 'Pawn'),
                world=read(pc, 'WorldInfo'), pri=read(pc, 'PlayerReplicationInfo'),
                modes=(modes.NM_Standalone, modes.NM_ListenServer),
                definitions=(record['node'], record['skills'][0], record['skills'][1]), epoch=_dt_event_epoch)
            for value in (pc, context['tree'], context['pawn'], context['world'], context['pri'], *context['definitions']):
                if not isinstance(value, unrealsdk.unreal.UObject):
                    raise ValueError()
            context['baseline'] = _dt_event_guard(context)
        except Exception:
            raise _DTEventRefusal('STATE') from None
        started = _dt_event_clock()
        context['started'] = context['last_time'] = started
        context['checks'] = _dt_event_metadata(context)
        phase = unrealsdk.hooks.Type.PRE
        try:
            present = unrealsdk.hooks.has_hook(_DT_EVENT_PATH, phase, _DT_EVENT_IDENT)
        except Exception:
            raise _DTEventRefusal('IDENTIFIER') from None
        if type(present) is not bool or present:
            raise _DTEventRefusal('IDENTIFIER')
        callback = _dt_event_callback(context['epoch'])
        try:
            added = unrealsdk.hooks.add_hook(_DT_EVENT_PATH, phase, _DT_EVENT_IDENT, callback)
        except Exception:
            _dt_event_uncertain.append((_DT_EVENT_PATH, _DT_EVENT_IDENT))
            raise _DTEventRefusal('REGISTRATION') from None
        if type(added) is not bool:
            _dt_event_uncertain.append((_DT_EVENT_PATH, _DT_EVENT_IDENT))
            raise _DTEventRefusal('REGISTRATION')
        if not added:
            raise _DTEventRefusal('REGISTRATION')
        _dt_event_handles.append((_DT_EVENT_PATH, _DT_EVENT_IDENT))
        try:
            present = unrealsdk.hooks.has_hook(_DT_EVENT_PATH, phase, _DT_EVENT_IDENT)
        except Exception:
            raise _DTEventRefusal('REGISTRATION') from None
        if type(present) is not bool or not present:
            raise _DTEventRefusal('REGISTRATION')
        _dt_event_guard(context)
        try:
            _deathtrap_check(context, context['checks'])
        except Exception:
            raise _DTEventRefusal('METADATA') from None
        if _dt_event_clock(context) - started >= 30.0:
            raise _DTEventRefusal('CLOCK')
        if not _dt_event_emit('START v0.2.15 target=DeactivateSkill phase=PRE attribution=NONE hooks=1'):
            raise _DTEventRefusal('INTERNAL')
        if not _dt_event_emit('BASELINE points={} ranks={}'.format(context['baseline'][0], context['baseline'][1])):
            raise _DTEventRefusal('INTERNAL')
        _dt_event_revalidate(context)
        if _dt_event_epoch != context['epoch'] or _dt_event_stop_requested:
            raise _DTEventRefusal('REGISTRATION')
        _dt_event_starting = False
        _dt_event_context = context
        return True
    except _DTEventRefusal as refusal:
        reason = refusal.reason
    except Exception:
        reason = 'INTERNAL'
    _dt_event_starting = False
    _dt_event_stats['refused'] = True
    if reason not in ('OVERLAP', 'STATE', 'METADATA', 'IDENTIFIER', 'REGISTRATION', 'CLOCK'):
        reason = 'REGISTRATION'
    _dt_event_emit('NOT_STARTED reason=' + reason)
    if _dt_event_handles or _dt_event_uncertain:
        stop_deathtrap_events()
    return False


# New reader state contains primitives and one fixed registration tuple only.
_CR_PATH = 'WillowGame.SkillEffectManager:ActivateSkill'
_CR_IDENT = 'UVH_ACTIVATION_READER_V18_PRE'
_cr_epoch = 0
_cr_accepting = False
_cr_starting = False
_cr_busy = False
_cr_stop_requested = False
_cr_pending = None
_cr_owned = False
_cr_stats = None


class _CRRefusal(Exception):
    pass


def _cr_emit(payload):
    if type(payload) is not str:
        return False
    message = '[UVH-ACTIVATION] ' + payload
    if len((TAG + ' ' + message).encode('utf-8')) > 384:
        return False
    try:
        log(message)
        return True
    except Exception:
        return False


def _cr_locked():
    return (_cr_accepting or _cr_starting or _cr_busy or _cr_pending is not None
            or _cr_stop_requested)


def _cr_overlap():
    # Only project Python control state; never inspect a retained game wrapper.
    return (_init_armed or bool(_init_hooks) or _uvh_node_state is not None
            or _record is not None or bool(_trace_hooks) or _trace_busy
            or bool(_upgrade_hooks) or _upgrade_context is not None or _upgrade_busy
            or bool(_ui_hooks) or _ui_context is not None or _ui_busy
            or bool(_skillstate_hooks) or _skillstate_context is not None or _skillstate_busy
            or _dt_event_locked())


def _cr_clock():
    import time
    now = time.monotonic()
    if type(now) is not float or not math.isfinite(now) or now < 0:
        raise _CRRefusal('CLOCK')
    if _cr_stats is not None:
        if now < _cr_stats['last'] or now < _cr_stats['started']:
            raise _CRRefusal('CLOCK')
        _cr_stats['last'] = now
    return now


class _CRBudget:
    """No game references, callbacks or exceptions may be stored here."""
    def __init__(self, epoch):
        self.epoch = epoch
        self.stage = 0
        self.counts = [0, 0, 0, 0]

    def tick(self):
        if not _cr_accepting or _cr_epoch != self.epoch or _cr_stop_requested:
            raise _CRRefusal('STOPPED')
        if _cr_clock() - _cr_stats['started'] >= 120.0:
            raise _CRRefusal('TIME')
        if self.counts[self.stage] >= (112, 80, 48, 80)[self.stage] or sum(self.counts) >= 320:
            raise _CRRefusal('BUDGET')
        self.counts[self.stage] += 1

    def get(self, obj, field):
        self.tick()
        return getattr(obj, field)

    def call(self, obj, method, *values):
        bound = self.get(obj, method)
        self.tick()
        return bound(*values)

    def lookup(self, lookup, label):
        self.tick()
        return lookup(label)

    def next(self, iterator):
        self.tick()
        return next(iterator, None)

    def length(self, value):
        self.tick()
        return len(value)

    def first(self, value):
        self.tick()
        return value[0]


def _cr_require(ok, reason='SCHEMA'):
    if not ok:
        raise _CRRefusal(reason)


def _cr_integer(value, expected=None, low=0, high=1048576):
    _cr_require(type(value) is int and low <= value <= high)
    if expected is not None:
        _cr_require(value == expected)
    return value


def _cr_loaded(budget, sdk, lookup, path, label):
    cls = budget.lookup(lookup, path)
    _cr_require(type(cls) is sdk.UClass)
    actual = budget.get(cls, 'Name')
    _cr_require(type(actual) is str and actual == label)
    return cls


def _cr_link(budget, sdk, obj, args, func, manager, function, expected_return=None):
    _cr_require(budget.get(func, 'object') is obj)
    _cr_require(budget.get(func, 'func') is function)
    _cr_require(budget.get(args, '_type') is function)
    _cr_require(budget.call(manager, '_find', 'ActivateSkill') is function)
    _cr_require(budget.get(function, 'Outer') is manager)
    label = budget.get(function, 'Name')
    _cr_require(type(label) is str and label == 'ActivateSkill')
    for field, value in (('FunctionFlags', 149506), ('NumParams', 6),
                         ('ParamsSize', 32), ('ReturnValueOffset', 28)):
        _cr_integer(budget.get(function, field), value)
    _cr_require(budget.get(function, 'SuperField') is None)
    return_prop = budget.call(function, '_find_return_param')
    if expected_return is not None:
        _cr_require(return_prop is expected_return)
    _cr_prop(budget, sdk, function, return_prop, 'ReturnValue',
             sdk.ZBoolProperty, 1408, 28, 4, None)
    return return_prop


def _cr_prop(budget, sdk, function, prop, label, kind, flags, offset, element_size, declared):
    _cr_require(type(prop) is kind)
    _cr_require(budget.get(prop, 'Outer') is function)
    actual = budget.get(prop, 'Name')
    _cr_require(type(actual) is str and actual == label)
    for field, value in (('PropertyFlags', flags), ('Offset_Internal', offset),
                         ('ArrayDim', 1), ('ElementSize', element_size)):
        high = max(1048576, value) if field == 'PropertyFlags' else 1048576
        _cr_integer(budget.get(prop, field), value, high=high)
    if declared is not None:
        _cr_require(budget.get(prop, 'PropertyClass') is declared)
    _cr_require(offset + element_size <= 32)
    _cr_require(budget.call(function, '_find_prop', label) is prop)


def _cr_member(budget, sdk, obj, args, func, manager, function, return_prop, prop, spec):
    _cr_link(budget, sdk, obj, args, func, manager, function, return_prop)
    _cr_prop(budget, sdk, function, prop, *spec)
    _cr_integer(budget.get(function, 'PropertySize'), low=32)


def _cr_solo(budget, sdk, base, pc, controller):
    _cr_require(type(pc) is sdk.UObject, 'PLAYER')
    _cr_require(budget.get(pc, 'Class') is controller, 'PLAYER')
    pawn = budget.get(pc, 'Pawn')
    player_class = budget.get(pc, 'PlayerClass')
    world = budget.get(pc, 'WorldInfo')
    pri = budget.get(pc, 'PlayerReplicationInfo')
    for value in (pawn, player_class, world, pri):
        _cr_require(type(value) is sdk.UObject, 'PLAYER')
    label = budget.get(player_class, 'Name')
    _cr_require(type(label) is str and label == 'CharClass_Mechromancer', 'PLAYER')
    mode = budget.get(world, 'NetMode')
    import unrealsdk
    modes = budget.lookup(unrealsdk.find_enum, 'ENetMode')
    _cr_require(isinstance(mode, int) and type(mode) is not bool, 'PLAYER')
    _cr_require(type(mode) in (int, modes), 'PLAYER')
    _cr_require(mode == modes.NM_Standalone or mode == modes.NM_ListenServer, 'PLAYER')
    engine = base.ENGINE  # SDK-owned global, used only as a local in this callback.
    _cr_require(type(engine) is sdk.UObject, 'PLAYER')
    players = budget.get(engine, 'GamePlayers')
    gri = budget.get(world, 'GRI')
    _cr_require(type(gri) is sdk.UObject, 'PLAYER')
    roster = budget.get(gri, 'PRIArray')
    _cr_require(type(players) is sdk.WrappedArray and type(roster) is sdk.WrappedArray, 'PLAYER')
    _cr_require(budget.length(players) == 1 and budget.length(roster) == 1, 'PLAYER')
    local = budget.first(players)
    _cr_require(type(local) is sdk.UObject, 'PLAYER')
    _cr_require(budget.get(local, 'Actor') is pc, 'PLAYER')
    _cr_require(budget.first(roster) is pri and budget.get(pri, 'Owner') is pc, 'PLAYER')
    # Array getters may create fresh value wrappers. Compare freshly checked
    # one-entry membership, not the Python identity of the array view itself.
    return pawn, player_class, world, pri, engine, gri, local, mode


def _cr_inspect(epoch, obj, args, func):
    """Native values and SDK exceptions die in this frame before primitive logging."""
    budget = _CRBudget(epoch)
    try:
        import unrealsdk
        import mods_base
        sdk = unrealsdk.unreal
        _cr_require(type(obj) is sdk.UObject and type(args) is sdk.WrappedStruct
                    and type(func) is sdk.BoundFunction)
        manager = _cr_loaded(budget, sdk, unrealsdk.find_class,
                             'WillowGame.SkillEffectManager', 'SkillEffectManager')
        controller = _cr_loaded(budget, sdk, unrealsdk.find_class,
                                'WillowGame.WillowPlayerController', 'WillowPlayerController')
        declared_controller = _cr_loaded(budget, sdk, unrealsdk.find_class,
                                         'Engine.Controller', 'Controller')
        definition_class = _cr_loaded(budget, sdk, unrealsdk.find_class,
                                      'WillowGame.SkillDefinition', 'SkillDefinition')
        object_class = _cr_loaded(budget, sdk, unrealsdk.find_class,
                                  'Core.Object', 'Object')
        _cr_require(budget.get(obj, 'Class') is manager)
        function = budget.call(manager, '_find', 'ActivateSkill')
        _cr_require(type(function) is sdk.UFunction)
        return_prop = _cr_link(budget, sdk, obj, args, func, manager, function)
        _cr_integer(budget.get(function, 'PropertySize'), low=32)
        specs = (('SkillInstigator', sdk.ZObjectProperty, 128, 0, 4, declared_controller),
                 ('Definition', sdk.ZObjectProperty, 128, 4, 4, definition_class),
                 ('AdditionalSkillTarget', sdk.ZObjectProperty, 144, 8, 4, object_class),
                 ('SkillGrade', sdk.ZIntProperty, 144, 12, 4, None),
                 ('StateChangeDelegate', sdk.ZDelegateProperty, 4194448, 16, 12, None),
                 ('ReturnValue', sdk.ZBoolProperty, 1408, 28, 4, None))
        properties = budget.call(function, '_properties')
        props = []
        for spec in specs:
            prop = budget.next(properties)
            _cr_prop(budget, sdk, function, prop, *spec)
            if spec[0] == 'ReturnValue':
                _cr_require(prop is return_prop)
            props.append(prop)
        _cr_require(budget.next(properties) is None)
        _cr_require(budget.call(function, '_find_return_param') is return_prop)

        budget.stage = 1
        _cr_member(budget, sdk, obj, args, func, manager, function, return_prop, props[0], specs[0])
        instigator = budget.get(args, 'SkillInstigator')
        _cr_member(budget, sdk, obj, args, func, manager, function, return_prop, props[0], specs[0])
        if instigator is None:
            return 'EVENT', 'NULL_INSTIGATOR', 'NOT_READ', '-', tuple(budget.counts)
        _cr_require(type(instigator) is sdk.UObject, 'PARAMETER')
        cls = budget.get(instigator, 'Class')
        _cr_require(type(cls) is sdk.UClass, 'PARAMETER')
        if cls is not controller:
            return 'EVENT', 'OTHER_CONTROLLER_CLASS', 'NOT_READ', '-', tuple(budget.counts)

        budget.stage = 2
        budget.tick()
        pc = get_pc(possibly_loading=True)
        _cr_require(type(pc) is sdk.UObject, 'PLAYER')
        if pc is not instigator:
            return 'EVENT', 'OTHER_WRAPPER', 'NOT_READ', '-', tuple(budget.counts)
        initial = _cr_solo(budget, sdk, mods_base, pc, controller)

        budget.stage = 3
        _cr_member(budget, sdk, obj, args, func, manager, function, return_prop, props[1], specs[1])
        definition = budget.get(args, 'Definition')
        _cr_member(budget, sdk, obj, args, func, manager, function, return_prop, props[1], specs[1])
        name = '-'
        if definition is None:
            result = 'NULL_DEFINITION'
        else:
            _cr_require(type(definition) is sdk.UObject, 'PARAMETER')
            _cr_require(budget.get(definition, 'Class') is definition_class, 'PARAMETER')
            label = budget.get(definition, 'Name')
            _cr_require(type(label) is str and 1 <= len(label) <= 128, 'PARAMETER')
            _cr_require(all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'
                            for c in label), 'PARAMETER')
            result = 'DEATHTRAP_NAME' if label == 'Skill_DeathTrap' else 'OTHER_NAME'
            name = label  # Validated primitive only; no additional SDK getter.
        _cr_require(budget.get(obj, 'Class') is manager)

        budget.stage = 2
        budget.tick()
        _cr_require(get_pc(possibly_loading=True) is pc, 'PLAYER')
        final = _cr_solo(budget, sdk, mods_base, pc, controller)
        _cr_require(all(a is b for a, b in zip(initial[:-1], final[:-1]))
                    and initial[-1] == final[-1], 'PLAYER')
        # Recheck accepting/clock after the last getter without another native read.
        if not _cr_accepting or _cr_stop_requested or _cr_epoch != epoch:
            raise _CRRefusal('STOPPED')
        if _cr_clock() - _cr_stats['started'] >= 120.0:
            raise _CRRefusal('TIME')
        return 'EVENT', 'SAME_WRAPPER', result, name, tuple(budget.counts)
    except _CRRefusal as exc:
        reason = 'INTERNAL'
        if type(exc) is _CRRefusal and len(exc.args) == 1 and type(exc.args[0]) is str:
            candidate = exc.args[0]
            if candidate in ('SCHEMA', 'PLAYER', 'PARAMETER', 'CLOCK', 'TIME', 'BUDGET', 'STOPPED'):
                reason = candidate
        return 'REFUSED', reason, 'NOT_READ', '-', tuple(budget.counts)
    except Exception:
        return 'ERROR', 'INTERNAL', 'NOT_READ', '-', tuple(budget.counts)


def _cr_option_gate(handler):
    from functools import wraps
    @wraps(handler)
    def dispatch(option=None):
        if _cr_locked():
            _cr_emit('NOT_STARTED reason=OVERLAP')
            return False
        return handler(option)
    return dispatch


def stop_callback_local_reader(_option=None):
    global _cr_accepting, _cr_stop_requested, _cr_pending, _cr_owned
    _cr_accepting = False
    if _cr_busy or _cr_starting:
        _cr_stop_requested = True
        return False
    _cr_stop_requested = False
    if _cr_stats is None:
        return True
    try:
        if _cr_clock() - _cr_stats['started'] >= 120.0 and _cr_stats['limit'] == 'NONE':
            _cr_stats['limit'] = 'TIME'
            _cr_emit('LIMIT reason=TIME')
    except Exception:
        _cr_stats['errors'] = min(2147483647, _cr_stats['errors'] + 1)
        _cr_emit('ERROR reason=CLOCK')
    uncertain = False
    if _cr_pending is not None:
        try:
            import unrealsdk
            phase = unrealsdk.hooks.Type.PRE
            if _cr_owned:
                removed = unrealsdk.hooks.remove_hook(_CR_PATH, phase, _CR_IDENT)
                present = unrealsdk.hooks.has_hook(_CR_PATH, phase, _CR_IDENT)
                if type(removed) is not bool or type(present) is not bool or present:
                    raise ValueError()
            else:
                present = unrealsdk.hooks.has_hook(_CR_PATH, phase, _CR_IDENT)
                if type(present) is not bool or present:
                    uncertain = True
            if not uncertain:
                _cr_pending = None
                _cr_owned = False
        except Exception:
            uncertain = not _cr_owned
            _cr_stats['cleanup_failures'] = min(2147483647, _cr_stats['cleanup_failures'] + 1)
            _cr_emit('REMOVAL_ERROR remaining=1')
    stats = _cr_stats
    payload = ('STOP epoch={} remaining={} uncertain={} attempts={} classified={} filtered={} nulls={} '
               'refusals={} errors={} reentry={} cleanup_failures={} limit={}').format(
        _cr_epoch, int(_cr_pending is not None), int(uncertain), stats['attempts'],
        stats['classified'], stats['filtered'], stats['nulls'], stats['refusals'],
        stats['errors'], stats['reentry'], stats['cleanup_failures'], stats['limit'])
    if not _cr_emit(payload):
        stats['errors'] = min(2147483647, stats['errors'] + 1)
    outcome = ('REFUSED' if _cr_pending is not None or stats['refusals'] or stats['errors']
               or stats['cleanup_failures'] else 'NOT_OBSERVED' if not stats['attempts']
               else 'OBSERVED_PRIMITIVE' if stats['classified'] > stats['filtered'] + stats['nulls']
               else 'OBSERVED_FILTERED')
    if not _cr_emit('OUTCOME epoch={} value={} ownership=UNESTABLISHED'.format(_cr_epoch, outcome)):
        stats['errors'] = min(2147483647, stats['errors'] + 1)
    return _cr_pending is None


def _cr_callback(epoch):
    def observe(obj, args, ret, func):
        global _cr_busy, _cr_accepting, _cr_stop_requested
        if not _cr_accepting or _cr_epoch != epoch or _cr_stats is None:
            return None
        if _cr_busy:
            _cr_stats['reentry'] = min(2147483647, _cr_stats['reentry'] + 1)
            return None
        stats = _cr_stats
        if stats['attempts'] >= 64 or stats['classified'] >= 24:
            return None
        _cr_busy = True
        kind, controller, definition, name, counts = 'REFUSED', 'STOPPED', 'NOT_READ', '-', (0, 0, 0, 0)
        try:
            stats['attempts'] += 1
            kind, controller, definition, name, counts = _cr_inspect(epoch, obj, args, func)
            # The inspection frame is gone. Drop the SDK callback's payload locals too.
            obj = args = func = ret = None
            if not _cr_accepting or _cr_epoch != epoch or _cr_stop_requested:
                kind, controller, definition, name = 'REFUSED', 'STOPPED', 'NOT_READ', '-'
            elif kind == 'EVENT':
                try:
                    if _cr_clock() - stats['started'] >= 120.0:
                        kind, controller, definition, name = 'REFUSED', 'TIME', 'NOT_READ', '-'
                except Exception:
                    kind, controller, definition, name = 'REFUSED', 'CLOCK', 'NOT_READ', '-'
            if kind == 'EVENT':
                ordinal = stats['classified'] + 1
                payload = ('EVENT epoch={} ordinal={} attempt={} schema=VALID controller={} definition={} name={} '
                           'ownership=UNESTABLISHED ops={} stages={},{},{},{}').format(
                    epoch, ordinal, stats['attempts'], controller, definition, name, sum(counts), *counts)
                if not _cr_emit(payload):
                    kind, controller = 'ERROR', 'LOGGING'
                else:
                    stats['classified'] = ordinal
                    if controller in ('OTHER_WRAPPER', 'OTHER_CONTROLLER_CLASS') or definition == 'OTHER_NAME':
                        stats['filtered'] += 1
                    elif controller == 'NULL_INSTIGATOR' or definition == 'NULL_DEFINITION':
                        stats['nulls'] += 1
            if kind != 'EVENT':
                name = '-'
                key = 'errors' if kind == 'ERROR' else 'refusals'
                stats[key] = min(2147483647, stats[key] + 1)
                if controller == 'TIME':
                    stats['limit'] = 'TIME'
                _cr_emit('{} epoch={} reason={} ops={} stages={},{},{},{}'.format(
                    kind, epoch, controller, sum(counts), *counts))
                _cr_accepting = False
                _cr_stop_requested = True
            if stats['attempts'] >= 64 or stats['classified'] >= 24:
                stats['limit'] = 'ATTEMPTS' if stats['attempts'] >= 64 else 'EVENTS'
                _cr_emit('LIMIT reason=' + stats['limit'])
                _cr_accepting = False
                _cr_stop_requested = True
        except Exception:
            obj = args = func = ret = None
            name = '-'
            stats['errors'] = min(2147483647, stats['errors'] + 1)
            _cr_accepting = False
            _cr_stop_requested = True
            _cr_emit('ERROR epoch={} reason=INTERNAL'.format(epoch))
        finally:
            obj = args = func = ret = None
            name = '-'
            _cr_busy = False
            if _cr_stop_requested:
                stop_callback_local_reader()
        return None
    return observe


def start_callback_local_reader(_option=None):
    global _cr_epoch, _cr_starting, _cr_accepting, _cr_stats, _cr_pending, _cr_owned
    global _cr_stop_requested
    if _cr_locked() or _cr_overlap():
        _cr_emit('NOT_STARTED reason=OVERLAP')
        return False
    if type(_cr_epoch) is not int or not 0 <= _cr_epoch < 2147483647:
        _cr_emit('NOT_STARTED reason=EPOCH')
        return False
    _cr_stats = None
    try:
        started = _cr_clock()
    except Exception:
        _cr_emit('NOT_STARTED reason=CLOCK')
        return False
    _cr_epoch += 1
    _cr_stats = dict(started=started, last=started, attempts=0, classified=0, filtered=0,
                     nulls=0, refusals=0, errors=0, reentry=0, cleanup_failures=0, limit='NONE')
    _cr_starting = True
    _cr_stop_requested = False
    reason = 'REGISTRATION'
    try:
        import unrealsdk
        phase = unrealsdk.hooks.Type.PRE
        present = unrealsdk.hooks.has_hook(_CR_PATH, phase, _CR_IDENT)
        if type(present) is not bool or present:
            reason = 'IDENTIFIER'
            raise ValueError()
        # Reserve before add: an exception may leave registration uncertain.
        _cr_pending = (_CR_PATH, _CR_IDENT)
        added = unrealsdk.hooks.add_hook(_CR_PATH, phase, _CR_IDENT, _cr_callback(_cr_epoch))
        if type(added) is not bool or not added:
            raise ValueError()
        _cr_owned = True
        present = unrealsdk.hooks.has_hook(_CR_PATH, phase, _CR_IDENT)
        if type(present) is not bool or not present or _cr_stop_requested or _cr_overlap():
            raise ValueError()
        if _cr_clock() - started >= 120.0:
            reason = 'CLOCK'
            raise ValueError()
        if not _cr_emit('START version=0.2.18 epoch={} target=ActivateSkill phase=PRE hooks=1 mode=STANDALONE_READER'.format(_cr_epoch)):
            raise ValueError()
        if _cr_stop_requested:
            raise ValueError()
        _cr_accepting = True
        _cr_starting = False
        return True
    except Exception:
        _cr_stats['refusals'] += 1
    _cr_starting = False
    _cr_emit('NOT_STARTED reason=' + reason)
    stop_callback_local_reader()
    return False


def shutdown():
    stop_tree_trace()
    cancel_init_node()


build_mod(
    name='UVH v0.2.18 - CALLBACK ACTIVATION READER',
    author='Borderlands Ultimate prototype',
    description=('Standalone PRE reader; bounded definition names, ownership unestablished. '
                 'Reader22/23 needs no ARM or node. V17 observed UpshotRobot; v18 is untested in game.'),
    version='0.2.18',
    supported_games=Game.BL2,
    coop_support=CoopSupport.ClientSide,
    options=[
        ButtonOption('uvh_init_node_arm', display_name='1 - ARM ONE GAIGE INIT NODE TEST (SOLO / INERT)', on_press=_dt_event_option_gate(arm_init_node)),
        ButtonOption('uvh_init_node_check', display_name='2 - CHECK INIT NODE RESULT (READ ONLY)', on_press=_dt_event_option_gate(inspect_init_node)),
        ButtonOption('uvh_init_node_cancel', display_name='3 - CANCEL / RESTORE NATIVE ARRAYS (THEN RESTART)', on_press=cancel_init_node),
        ButtonOption('uvh_purchase_snapshot', display_name='4 - INSPECT DEATHTRAP PARAMETER CLASSES (READ ONLY)', on_press=_dt_event_option_gate(inspect_deathtrap_readiness)),
        ButtonOption('uvh_upgrade_start', display_name='5 - START UPGRADE OBSERVERS (READ ONLY; DO NOT BUY)', on_press=_dt_event_option_gate(start_upgrade_trace)),
        ButtonOption('uvh_upgrade_stop', display_name='6 - STOP / REPORT UPGRADE OBSERVERS', on_press=_dt_event_option_gate(stop_upgrade_trace)),
        ButtonOption('uvh_ui_start', display_name='7 - START CORE SKILL UI TRACE (READ ONLY; DO NOT BUY)', on_press=_dt_event_option_gate(start_ui_trace)),
        ButtonOption('uvh_ui_stop', display_name='8 - STOP / REPORT UI TRACE + SNAPSHOT (READ ONLY)', on_press=_dt_event_option_gate(stop_ui_trace)),
        ButtonOption('uvh_state_start', display_name='9 - START FOCUSED STATE TRACE (READ ONLY; DO NOT BUY)', on_press=_dt_event_option_gate(start_skillstate_trace)),
        ButtonOption('uvh_state_stop', display_name='10 - STOP / REPORT FOCUSED STATE TRACE', on_press=_dt_event_option_gate(stop_skillstate_trace)),
        ButtonOption('uvh_loading_snapshot', display_name='Diagnostic - SNAPSHOT TREE LOADING (READ ONLY)', on_press=_dt_event_option_gate(inspect_tree_loading)),
        ButtonOption('uvh_loading_trace_start', display_name='Diagnostic - START TREE INIT TRACE (READ ONLY)', on_press=_dt_event_option_gate(start_tree_trace)),
        ButtonOption('uvh_loading_trace_stop', display_name='Diagnostic - STOP TREE INIT TRACE', on_press=_dt_event_option_gate(stop_tree_trace)),
        ButtonOption('uvh_insert_node_early', display_name='Legacy - INSERT INERT NODE AT MAIN MENU', on_press=_dt_event_option_gate(add_overclock_node)),
        ButtonOption('uvh_verify_node_early', display_name='Legacy - CHECK CURRENT NODE STATE (READ ONLY)', on_press=_dt_event_option_gate(check_overclock_preload)),
        ButtonOption('uvh_remove_node_early', display_name='Legacy - REMOVE NODE (if not purchased)', on_press=_dt_event_option_gate(remove_overclock_node)),
        ButtonOption('uvh_boost_inspect', display_name='Inspect live Deathtrap duration', on_press=_dt_event_option_gate(inspect)),
        ButtonOption('uvh_boost_apply', display_name='Apply +15s (working manual prototype)', on_press=_dt_event_option_gate(apply)),
        ButtonOption('uvh_boost_restore', display_name='Restore original duration', on_press=_dt_event_option_gate(restore)),
        ButtonOption('uvh_dt_event_start', display_name='20 - START PASSIVE MANAGER ENTRY OBSERVER (READ ONLY)', on_press=_cr_option_gate(start_deathtrap_events)),
        ButtonOption('uvh_dt_event_stop', display_name='21 - STOP / REPORT PASSIVE MANAGER ENTRY OBSERVER', on_press=_cr_option_gate(stop_deathtrap_events)),
        ButtonOption('uvh_callback_read_start', display_name='22 - START CALLBACK ACTIVATION READER (NO ARM)', on_press=start_callback_local_reader),
        ButtonOption('uvh_callback_read_stop', display_name='23 - STOP / REPORT CALLBACK ACTIVATION READER', on_press=stop_callback_local_reader),
    ],
    auto_enable=True,
    on_disable=shutdown,
)
