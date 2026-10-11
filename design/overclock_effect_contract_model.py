"""Simulated contract only: opaque facts in, proposed actions as data out.

No SDK imports, object discovery, native writes or runtime integration. A native
adapter does not exist. Token identity, liveness, unique membership, generation,
quiescence and proof flags are hypothetical validated adapter facts, not engine
claims. The accepted contract is docs/overclock_identity_cleanup_contract.md.
"""
from dataclasses import dataclass, replace
import math

MAX_ATTEMPTS = 1024


def finite(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


@dataclass(frozen=True)
class Observation:
    session: object
    owner: object
    world: object
    definition: object
    skill: object
    generation: object
    activated_time: object
    duration: object
    base: object
    modifiers: object
    rank: object
    matches: tuple
    verified: bool = True
    quiescent: bool = True


@dataclass(frozen=True)
class Action:
    kind: str
    target: object
    value: float
    operation: int


@dataclass(frozen=True)
class Record:
    observation: Observation
    before: float
    after: float
    phase: str


class ContractModel:
    """One-session ledger. Returned Action objects never execute themselves."""
    def __init__(self, session, owner, world, definition):
        if any(token is None for token in (session, owner, world, definition)):
            raise ValueError('missing abstract identity token')
        self.session, self.owner, self.world, self.definition = session, owner, world, definition
        self.record = None
        self.pending = None
        self.enabled = True
        self.hooks_pending = False
        self.watermark = 0
        self.attempts = 0
        self.operation = 0
        # Fixed keys/counters retain failure history without an unbounded ledger.
        self.counts = dict.fromkeys(('refused', 'rank_zero', 'repeat', 'apply_failed',
                                    'cleanup_failed', 'hook_failed', 'conflict',
                                    'retired', 'restored', 'stale_ack'), 0)
        self.last = 'IDLE'

    def _owned(self, obs):
        return (type(obs) is Observation and obs.verified is True and obs.quiescent is True
                and obs.session is self.session and obs.owner is self.owner
                and obs.world is self.world and obs.definition is self.definition
                and obs.skill is not None and type(obs.matches) is tuple
                and len(obs.matches) == 1 and obs.matches[0] is obs.skill
                and type(obs.generation) is int and obs.generation > 0
                and finite(obs.activated_time) and obs.activated_time >= 0)

    def _same(self, obs):
        original = self.record.observation
        return (self._owned(obs) and obs.skill is original.skill
                and obs.generation == original.generation
                and obs.activated_time == original.activated_time)

    def _action(self, kind, target, value):
        self.operation += 1
        self.pending = Action(kind, target, value, self.operation)
        return self.pending

    def propose_apply(self, obs):
        if not self.enabled or self.hooks_pending or self.record is not None:
            self.counts['repeat'] += 1
            return None
        if not self._owned(obs) or type(obs.rank) is not int or obs.rank not in (0, 1):
            self.counts['refused'] += 1
            self.last = 'REFUSED'
            return None
        if obs.rank == 0:
            self.counts['rank_zero'] += 1
            self.last = 'RANK_ZERO_SKIP'
            return None
        if obs.generation <= self.watermark or self.attempts >= MAX_ATTEMPTS:
            self.counts['refused'] += 1
            self.last = 'REUSED_GENERATION_OR_EXHAUSTED'
            return None
        if (not finite(obs.duration) or not finite(obs.base)
                or not math.isclose(obs.duration, 60, rel_tol=0, abs_tol=0.05)
                or not math.isclose(obs.base, 60, rel_tol=0, abs_tol=0.05)
                or type(obs.modifiers) is not int or obs.modifiers != 0):
            self.counts['refused'] += 1
            self.last = 'VALUES_REFUSED'
            return None
        before, after = float(obs.duration), float(obs.duration) + 15
        if not math.isfinite(after) or after > 180:
            self.counts['refused'] += 1
            return None
        self.watermark = obs.generation
        self.attempts += 1
        self.record = Record(obs, before, after, 'PENDING_APPLY')
        self.last = 'PENDING_APPLY'
        return self._action('PROPOSE_DURATION', obs.skill, after)

    def acknowledge(self, action, obs, write_ok):
        # Exact issued action prevents an old/counterfeit response changing state.
        if action is not self.pending or self.record is None or action is None:
            self.counts['stale_ack'] += 1
            return False
        phase = self.record.phase
        self.pending = None
        unchanged = (self._same(obs) and finite(obs.base)
                     and obs.base == self.record.observation.base
                     and type(obs.modifiers) is int and obs.modifiers == 0)
        expected = self.record.after if phase == 'PENDING_APPLY' else self.record.before
        value_ok = unchanged and finite(obs.duration) and obs.duration == expected
        rank_ok = phase != 'PENDING_APPLY' or (type(obs.rank) is int and obs.rank == 1)
        if write_ok is True and value_ok and rank_ok:
            if phase == 'PENDING_APPLY':
                self.record = replace(self.record, phase='APPLIED')
                self.last = 'APPLIED'
            elif phase == 'PENDING_RESTORE':
                self.record = None
                self.counts['restored'] += 1
                self.last = 'RESTORED'
            return True
        self.enabled = False
        failed = 'apply_failed' if phase == 'PENDING_APPLY' else 'cleanup_failed'
        self.counts[failed] += 1
        state = 'UNCERTAIN' if phase == 'PENDING_APPLY' else 'INERT_RETRY'
        self.record = replace(self.record, phase=state)
        self.last = state
        return False

    def stop(self):
        # Context is inert before offering observer removal/any cleanup attempt.
        self.enabled = False
        self.hooks_pending = True
        self.pending = None
        if self.record is not None and self.record.phase.startswith('PENDING'):
            self.record = replace(self.record, phase='INERT_RETRY')
        self.last = 'DISABLED'
        return ('PROPOSE_REMOVE_OBSERVERS',)

    def retire_original(self, skill, generation, *, verified_ended=False, write_interval_closed=False):
        """Hypothetical natural end proof; never a name/absence inference or rearm."""
        if (self.record is None or verified_ended is not True or write_interval_closed is not True
                or skill is not self.record.observation.skill or type(generation) is not int
                or generation != self.record.observation.generation):
            return False
        self.pending = None
        self.record = None
        self.counts['retired'] += 1
        self.last = 'ORIGINAL_ENDED'
        return True

    def acknowledge_hook_removal(self, success):
        if success is True:
            self.hooks_pending = False
        else:
            self.enabled = False
            self.hooks_pending = True
            self.counts['hook_failed'] += 1
        # Even successful removal never rearms the effect.
        return not self.hooks_pending

    def propose_cleanup(self, obs=None, *, original_ended=False):
        self.enabled = False
        if self.record is None:
            return None
        if self.pending is not None:
            return None
        if original_ended is True:
            # Explicit hypothetical proof about the recorded original, not absence.
            self.record = None
            self.counts['retired'] += 1
            self.last = 'ORIGINAL_ENDED'
            return None
        if self.record.phase == 'CONFLICT':
            return None
        if not self._same(obs):
            self.record = replace(self.record, phase='INERT_RETRY')
            self.last = 'INERT_RETRY'
            return None
        if (not finite(obs.duration) or not finite(obs.base)
                or type(obs.modifiers) is not int or obs.modifiers < 0):
            self.record = replace(self.record, phase='INERT_RETRY')
            self.last = 'INERT_RETRY'
            return None
        if (obs.base != self.record.observation.base or obs.modifiers != 0
                or obs.duration not in (self.record.before, self.record.after)):
            self.record = replace(self.record, phase='CONFLICT')
            self.counts['conflict'] += 1
            self.last = 'CONFLICT'
            return None
        if obs.duration == self.record.before:
            self.record = None
            self.counts['restored'] += 1
            self.last = 'ALREADY_CLEAN'
            return None
        self.record = replace(self.record, phase='PENDING_RESTORE')
        self.last = 'PENDING_RESTORE'
        return self._action('PROPOSE_RESTORE_DURATION', self.record.observation.skill, self.record.before)
