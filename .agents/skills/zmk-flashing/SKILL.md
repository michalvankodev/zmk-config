---
name: zmk-flashing
description: Flash UF2 firmware to Michal's ZMK split keyboards (nice!nano v2 — cygnus + skeletyl from ~/Projects/zmk-config). Use when flashing or updating keyboard firmware, downloading CI build artifacts, entering the nice!nano bootloader, running settings_reset, re-pairing BLE halves, or diagnosing a keyboard whose right-half keys type wrong characters.
---

# Flashing the keyboards (zmk-config)

Repo: `~/Projects/zmk-config`. Two hand-built split keyboards on **nice!nano v2** controllers: **cygnus** (active development) and **skeletyl** (frozen archive — never flash it new keymaps). The **left half is the BLE central** and holds the host pairing; device names "Cygnus" / "Skeletyl". Builds run in GitHub Actions on push (`michalvankodev/zmk-config`); no local toolchain exists.

## Routine firmware update

1. Confirm the latest run is green and contains the intended commit:
   `gh run list --limit 3` — *done when: a `success` run newer than your last keymap/shield change.*
2. Download that run's artifacts and refresh the local copies:
   ```fish
   set run <run-id>
   gh run download $run -n firmware -D /tmp/zmk-artifacts
   cp /tmp/zmk-artifacts/*.uf2 firmware/; and rm -rf /tmp/zmk-artifacts
   ```
   *Done when: `firmware/` UF2 timestamps are newer than the build.*
3. Flash each half, one at a time: **double-tap the reset button** on the nice!nano → it appears as a USB device labeled `NICENANO` ("Adafruit nRF UF2", ~32 MB). The desktop may NOT automount it — drive it yourself:
   ```fish
   # poll up to 60 s for the UF2 drive (it can appear late after the double-tap)
   for i in (seq 60)
       set dev (lsblk -nrpo NAME,LABEL,TRAN | awk '$3=="usb" && $2 ~ /NANO/ {print $1}' | head -1)
       test -n "$dev"; and break
       sleep 1
   end
   udisksctl mount -b $dev
   cp firmware/cygnus_left-nice_nano_v2-zmk.uf2 /run/media/$USER/NICENANO/
   # drive disappears when the board reboots — that's the completion signal
   ```
   Left UF2 to the left controller, right to the right. A fresh double-tap is needed for EVERY flash — after `settings_reset` or any UF2 copy the board reboots out of bootloader mode.
4. Smoke test: both halves reconnect to each other, `yuiop` / `nm,./` type correctly, layers behave.

## Full reset (broken pairing / starting fresh)

1. Flash `settings_reset-nice_nano_v2-zmk.uf2` to **both** halves (clears all bonds and the host pairing).
2. Flash `cygnus_left` then `cygnus_right` (the per-half UF2s carry the keymap — **both halves need reflashing whenever the keymap changes**; `settings_reset` alone is keymap-independent).
3. Power both halves on together: they auto-bond (left = central). *Done when: right half responds within ~30 s.*
4. Remove any stale host-side bond first (`bluetoothctl remove <mac>`): `settings_reset` wipes the keyboard's bonds but not the host's copy, and it's mandatory when the board identity changed (Skeletyl→Cygnus). Then pair the host to "Cygnus" — the first pairing lands in profile 0. If halves won't find each other: clear bonds from the keymap (cygnus: hold the 6th thumb, press `b` = `BT_CLR`) and power-cycle both.

## Reference

- **Firmware ↔ hardware consistency**: the cygnus right half once had its col6/col7 wires swapped (`u↔i`, `m↔,`, extra thumb typing BSPC); wires were physically fixed 2026-10 and `cygnus_right.overlay` follows the skeletyl convention. If right-half characters ever scramble again, diagnose by typing `yuiop` then `nm,./` and reading which pairs swap — a clean pair-swap means wire order, not the keymap. Decode outputs through the *active* base layer (Q+P toggles colemak — outputs look shifted, e.g. `july;`).
- **In-keymap BT management** — cygnus: hold 6th thumb → `z x c v` = `BT_SEL 0-3`, `b` = `BT_CLR`; combos `P+;` / `P+/` cycle profiles, `T+Y` toggles USB/BLE output. skeletyl: media layer (hold ESC thumb). Definitions: `config/cygnus.keymap` / `config/skeletyl.keymap`.
- **Identify which firmware a half runs** — the BT advertise name and split role are baked into each half's firmware (`ZMK_KEYBOARD_NAME` in the shield's `Kconfig.defconfig`): advertising as "Skeletyl" means that half still runs skeletyl firmware. Halves only bond as a matched pair — skeletyl central + cygnus peripheral = right half dead. Flashed firmware can also predate in-repo fixes (wake-on-keypress = `wakeup-source;` on the kscan node, commit `6368cf2`): when behavior is inexplicable, reflash both halves with current UF2s. USB signatures: running ZMK half = `1d50:615e` "ZMK Project" (peripheral halves enumerate with no interfaces — normal); bootloader = lsusb `239a:00b3` "Adafruit nice!nano v2" + the `NICENANO` drive.
- `firmware/` is untracked in git — manually kept copies only; always re-download before assuming freshness.
- Verify a mounted UF2 bootloader by `INFO_UF2.TXT` ("Model: nice!nano") before copying — protects against flashing some other USB stick.
- Layout changes are validated before pushing with `python3 scripts/check_keymap.py` (exit 0 = contract holds: 12 layers × 36 bindings, positions, combos, timings).
