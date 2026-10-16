# TODO — zmk-config

## Homerow mod timings on the cygnus — RESOLVED 2026-10-16

**Decision: charybdis timings.** After real use on the cygnus (fast typist),
the skeletyl `balanced` flavor caused accidental mods on fast rolls, and the
250ms pinky window felt sluggish. Switched to QMK-charybdis parity:

- single `hm` behavior: `flavor = "tap-preferred"`, `tapping-term-ms = <200>`,
  `quick-tap-ms = <0>` — pinky keys (`A ; O`) use the same `hm`, no distinction
- `hmp` behavior removed
- `scripts/check_keymap.py` updated to assert the new contract

Skeletyl keymap stays frozen (historic archive).
