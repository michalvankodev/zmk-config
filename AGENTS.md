# AGENTS.md — zmk-config

## Project Overview

Personal [ZMK firmware](https://zmk.dev) configuration for a **Skeletyl** split keyboard (Bastardkb Skeletyl, 3×5+3 per half) built on **nice!nano v2** controllers with a custom shield definition. No application code — the repo contains only ZMK config; the firmware itself is pulled in as a west module and built by GitHub Actions.

- Technology stack: ZMK (tracking the `zmkfirmware/zmk` **`main`** branch, Zephyr 4.1 / HWMv2 based), Zephyr devicetree overlays (`.dtsi`/`.overlay`), Kconfig (`.conf`), west manifest, GitHub Actions reusable workflow.
- Remote: `git@github.com:michalvankodev/zmk-config.git`, default branch `master`.

## Architecture

```
build.yaml                              # Build matrix for CI: board+shield combos
.github/workflows/build.yml             # CI: reuses zmkfirmware/zmk build-user-config.yml@main
config/                                 # West "self" module (config root)
├── west.yml                            # Tracks zmkfirmware/zmk @ main
├── skeletyl.conf                       # Global Kconfig: sleep, 7ms debounce, pointing/mouse enabled
├── skeletyl.keymap                     # THE keymap: layers, behaviors, combos (main editable file)
└── boards/shields/skeletyl/            # Custom shield definition (DIY board, not in mainline ZMK)
    ├── skeletyl.zmk.yml                # Shield metadata; siblings skeletyl_left/right
    ├── skeletyl.dtsi                   # Shared: matrix transform (10 cols × 4 rows), kscan node
    ├── skeletyl_{left,right}.overlay   # Per-half GPIO wiring; right half uses col-offset 5
    ├── skeletyl_{left,right}.conf      # Per-half Kconfig (sleep)
    ├── skeletyl.conf                   # Shield-level Kconfig
    └── Kconfig.shield / Kconfig.defconfig  # Enables split BLE; left half is central
firmware/                               # Prebuilt UF2 artifacts (left, right, settings_reset)
```

Data flow: `build.yaml` → CI matrix → for each board+shield, ZMK builds a `.uf2` (artifacts on the GH Actions run; `firmware/` holds manually kept copies). The keymap references the physical matrix defined in the shield's `default_transform`; split halves communicate over BLE with the **left half as central**.

## Key Entry Points

- `config/skeletyl.keymap` — keymap with 8 layers: `qwerty` (default), `colemak`, nav, num, mouse, symbol, media, fun. Defines custom hold-tap behaviors `hm`/`hmp` (homerow mods, 200/250ms) and combos (Colemak toggle, BT next/prev, output toggle). Layers are switched via `&lt` from the thumb row.
- `config/skeletyl.conf` — `CONFIG_ZMK_POINTING=y` enables mouse; `ZMK_POINTING_DEFAULT_MOVE_VAL`/`SCRL_VAL` are `#define`d at the top of the keymap.
- `build.yaml` — add/remove board+shield combos here to change what CI builds.

## Code Conventions

- Devicetree syntax throughout: `#include`/`#define` at top, bindings aligned in column-major grids mirroring physical key positions. Keep the grid alignment when editing keymap rows.
- Layer indices are `#define`d as numbers (QWERTY 0 … FUN 7); `&tog`/`&lt` reference them by name.
- Kconfig files use `CONFIG_...=y` one per line; commented-out options are kept as documentation (e.g. USB logging).
- No linters/formatters configured (no .editorconfig/prettier/eslint) — this is not a source-code project.
- Commit style: short lowercase-ish imperative messages (e.g. "fix wake", "higher dpi").

## Setup Requirements

- No local toolchain needed: **builds happen in GitHub Actions** on push/PR/manual dispatch. Download UF2 artifacts from the run page.
- Local builds (optional) require ZMK's Docker-based setup (`zmk-sdk/zmk-docker`); west workspace is defined by `config/west.yml` (`west init -l config`).
- No environment variables.
- Flashing: copy the matching `.uf2` to each nice!nano while in bootloader mode; `settings_reset-*.uf2` clears BLE bonds before re-pairing halves.

## Important Files

- `build.yaml` — defines what gets built (currently: skeletyl_left/right + settings_reset on `nice_nano//zmk`, the HWMv2 name for nice_nano v2; `artifact-name` keeps output filenames on the old `nice_nano_v2` convention).
- `config/west.yml` — ZMK revision (`main`). Keep in sync with the workflow ref in `.github/workflows/build.yml`; pin both to a release tag (e.g. `v0.4.0` when released) for stability.
- `.github/workflows/build.yml` — delegates to `zmkfirmware/zmk/.github/workflows/build-user-config.yml@main`.
- `config/boards/shields/skeletyl/` — hardware definition; only touch if wiring/matrix changes.
