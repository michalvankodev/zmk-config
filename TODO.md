# TODO — zmk-config

## Decide: homerow mod timings on the cygnus (open)

**Status: undecided — do not forget.** (noted 2026-10-15)

The cygnus keymap (`config/cygnus.keymap`) currently uses the **skeletyl**
homerow mod timings, but the charybdis is now the reference keyboard. Decide
which feel the cygnus should have after using it for a while.

### Current state on cygnus (inherited from skeletyl)

| Behavior | Keys | Flavor | Term |
|---|---|---|---|
| `hm`  | S D F / J K L | `balanced` (≈ QMK `PERMISSIVE_HOLD`) | 200ms |
| `hmp` | A / ; (pinkies) | `tap-preferred` (≈ QMK default) | 250ms |

Both have `quick-tap-ms = <0>` (ZMK default is off anyway).

### The alternative: charybdis feel

QMK charybdis uses stock mod-taps, no overrides:
all 8 keys identical — ≈ ZMK `tap-preferred`, 200ms, no pinky distinction.
To switch, edit the `hm`/`hmp` nodes in `config/cygnus.keymap`:

```
flavor = "tap-preferred";
tapping-term-ms = <200>;
```

(either unify `hmp` with `hm` or drop `hmp` and use `hm` everywhere)

### Context for the decision

- Michal types fine on the charybdis; the only charybdis pain point was the
  num-layer/delete bug, which is `QUICK_TAP_TERM` — already TODO'd in the QMK
  userspace repo (charybdis keymap TODO.md) and unrelated to timings.
- Practical difference: `balanced` fires the mod when another key is tapped
  while held (faster shift-chords, slightly more accidental mods on very fast
  rolls); `tap-preferred` is pure timing (fewer accidental mods, quick
  shift-chords can come out unshifted).
- QMK ↔ ZMK flavor mapping: default ≈ `tap-preferred`,
  `PERMISSIVE_HOLD` ≈ `balanced`, `HOLD_ON_OTHER_KEY_PRESS` ≈ `hold-preferred`.
- Skeletyl keymap stays frozen (historic archive) — only touch `config/cygnus.keymap`.
