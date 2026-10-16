# AGENTS.md — zmk-config

## Project Overview

Personal [ZMK firmware](https://zmk.dev) configuration for two hand-built split keyboards (3×5+3 per half) on **nice!nano v2** controllers with custom shield definitions (DIY boards, not in mainline ZMK):

- **cygnus** — the active keyboard. **All keymap and config work happens on cygnus.**
- **skeletyl** — **read-only**: frozen archive of the old skeletyl build, kept for history. Never edit skeletyl files, never flash new keymaps to that board.

No application code — the repo contains only ZMK config; the firmware itself is pulled in as a west module and built by GitHub Actions.

- Technology stack: ZMK (tracking the `zmkfirmware/zmk` **`main`** branch, Zephyr 4.1 / HWMv2 based), Zephyr devicetree overlays (`.dtsi`/`.overlay`), Kconfig (`.conf`), west manifest, GitHub Actions reusable workflow.
- Remote: `git@github.com:michalvankodev/zmk-config.git`, default branch `master`.

## Architecture

```
build.yaml                              # Build matrix for CI: board+shield combos
.github/workflows/build.yml             # CI: reuses zmkfirmware/zmk build-user-config.yml@main
config/                                 # West "self" module (config root)
├── west.yml                            # Tracks zmkfirmware/zmk @ main
├── cygnus.conf                         # Active keyboard Kconfig: sleep, 7ms debounce, pointing/mouse enabled
├── cygnus.keymap                       # THE keymap: 12 layers, behaviors, combos (main editable file)
├── skeletyl.conf / skeletyl.keymap     # READ-ONLY (frozen skeletyl archive)
├── boards/shields/cygnus/              # Active custom shield definition
│   ├── cygnus.zmk.yml                  # Shield metadata; siblings cygnus_left/right
│   ├── cygnus.dtsi                     # Shared: matrix transform (10 cols × 4 rows), kscan node
│   ├── cygnus_{left,right}.overlay     # Per-half GPIO wiring; right half uses col-offset 5
│   ├── cygnus_{left,right}.conf        # Per-half Kconfig
│   └── Kconfig.shield / Kconfig.defconfig  # Enables split BLE; left half is central
└── boards/shields/skeletyl/            # READ-ONLY (frozen skeletyl archive)
scripts/check_keymap.py                 # Contract checker for cygnus.keymap (run before pushing)
firmware/                               # Prebuilt UF2 artifacts (untracked, manually refreshed)
```

Data flow: `build.yaml` → CI matrix → for each board+shield, ZMK builds a `.uf2` (artifacts on the GH Actions run; `firmware/` holds manually kept copies). The keymap references the physical matrix defined in the shield's `default_transform`; split halves communicate over BLE with the **left half as central**.

## Key Entry Points

- `config/cygnus.keymap` — keymap with 12 layers: `qwerty`/`colemak` base pair (switched via Q+P / Q+; combos), nav, num, mouse, symbol, media, fun, gamepad (+ gamepad L1/L2), bt. Single hold-tap behavior `hm` (tap-preferred, 200ms, no pinky distinction). Mouse layer is held on `Z` / `/` (move diamond in Colemak labels: `u , n o` = up/down/left/right); BT layer on the 6th thumb. Ported from the QMK charybdis keymap — see the header comments for the porting decisions.
- `config/cygnus.conf` — `CONFIG_ZMK_POINTING=y` enables mouse; `ZMK_POINTING_DEFAULT_MOVE_VAL`/`SCRL_VAL` are `#define`d at the top of the keymap.
- `scripts/check_keymap.py` — validates `config/cygnus.keymap` against its embedded contract spec. Run it before pushing any keymap change (exit 0 = pass); when a layout change is intentional, update the spec in the same commit.
- `build.yaml` — add/remove board+shield combos here to change what CI builds.

## Code Conventions

- Devicetree syntax throughout: `#include`/`#define` at top, bindings aligned in column-major grids mirroring physical key positions. Keep the grid alignment when editing keymap rows.
- Layer indices are `#define`d as numbers (QWERTY 0 … BT 11); `&tog`/`&to`/`&lt` reference them by name.
- Key positions in comments/docs refer to the **active base layer's labels** — state which layout (Colemak/QWERTY) a label refers to; the two differ by a column.
- Kconfig files use `CONFIG_...=y` one per line; commented-out options are kept as documentation (e.g. USB logging).
- No linters/formatters configured (no .editorconfig/prettier/eslint) — `scripts/check_keymap.py` is the only automated check.
- Commit style: short lowercase-ish imperative messages (e.g. "fix wake", "fix cygnus mouse move diamond").

## Setup Requirements

- No local toolchain needed: **builds happen in GitHub Actions** on push/PR/manual dispatch. Download UF2 artifacts from the run page.
- Local builds (optional) require ZMK's Docker-based setup (`zmk-sdk/zmk-docker`); west workspace is defined by `config/west.yml` (`west init -l config`).
- No environment variables.
- Flashing (cygnus only): copy the matching `.uf2` to each nice!nano while in bootloader mode; `settings_reset-*.uf2` clears BLE bonds before re-pairing halves. See the zmk-flashing skill for the full routine.

## Important Files

- `build.yaml` — defines what gets built (currently: cygnus_left/right + skeletyl_left/right + settings_reset on `nice_nano//zmk`, the HWMv2 name for nice_nano v2; `artifact-name` keeps output filenames on the old `nice_nano_v2` convention).
- `config/west.yml` — ZMK revision (`main`). Keep in sync with the workflow ref in `.github/workflows/build.yml`; pin both to a release tag (e.g. `v0.4.0` when released) for stability.
- `.github/workflows/build.yml` — delegates to `zmkfirmware/zmk/.github/workflows/build-user-config.yml@main`.
- `config/skeletyl.*` + `config/boards/shields/skeletyl/` — frozen archive, read-only (history of the old skeletyl build; still built by CI but never modified).
