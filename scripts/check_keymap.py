#!/usr/bin/env python3
"""ZMK keymap correctness checker for the cygnus keymap (config/cygnus.keymap).

Validates against the porting contract derived from the QMK reference keymap
(bk_qmk_userspace/keyboards/bastardkb/charybdis/3x5/keymaps/michalvanko/keymap.c)
plus the session decisions for the cygnus build:

  - 12 layers in the defined order, exactly 36 bindings each (10+10+10+6)
  - position -> binding assertions per layer (embedded SPEC below)
  - QMK translation rules for thumbs: XXXXXXX -> &none, KC_TRNS -> &trans
    (positions 30-34); the extra 6th thumb (position 35) is a cygnus-only key
  - combos and hold-tap behavior parameters

Usage:  python3 check_keymap.py [path/to/cygnus.keymap]
Deps:   python3 stdlib only. Read-only. Exit 0 = all checks pass.
"""

import re
import sys

KEYMAP = sys.argv[1] if len(sys.argv) > 1 else "config/cygnus.keymap"

# ---------------------------------------------------------------------------
# Contract spec
# ---------------------------------------------------------------------------

# Layer indexes (#define names, uppercase as in the file) in required order.
LAYER_DEFINES = ["QWERTY", "COLEMAK", "NAV", "NUM", "MOUSE", "SYM",
                 "MEDIA", "FUN", "GAMEPAD", "GP_L1", "GP_L2", "BT"]

# Keymap child-node names in required order (must match LAYER_DEFINES order).
LAYER_NODE_NAMES = ["qwerty", "colemak", "nav_layer", "num_layer", "mouse_layer",
                    "symbol_layer", "media_layer", "fun_layer", "gamepad",
                    "gamepad_l1", "gamepad_l2", "bt_layer"]

THUMB_BASE = ["&lt MEDIA ESC", "&lt NAV SPACE", "&lt FUN TAB",
              "&lt SYM RET", "&lt NUM BSPC", "&lt BT DEL"]

# Position -> expected binding, per layer. Index = row*10 + col; row 3 cols
# 2..7 are the 6 thumbs (positions 30..35). Positions absent from the dict
# fall back to `default` for that layer; default=None means "must be listed".
SPEC = {
    "qwerty": {
        "default": None,
        0: "&kp Q", 1: "&kp W", 2: "&kp E", 3: "&kp R", 4: "&kp T",
        5: "&kp Y", 6: "&kp U", 7: "&kp I", 8: "&kp O", 9: "&kp P",
        10: "&hm LGUI A", 11: "&hm LALT S", 12: "&hm LCTRL D", 13: "&hm LSHIFT F", 14: "&kp G",
        15: "&kp H", 16: "&hm LSHIFT J", 17: "&hm LCTRL K", 18: "&hm LALT L", 19: "&hm LGUI SEMI",
        20: "&lt MOUSE Z", 21: "&kp X", 22: "&kp C", 23: "&kp V", 24: "&kp B",
        25: "&kp N", 26: "&kp M", 27: "&kp COMMA", 28: "&kp DOT", 29: "&lt MOUSE FSLH",
        30: THUMB_BASE[0], 31: THUMB_BASE[1], 32: THUMB_BASE[2],
        33: THUMB_BASE[3], 34: THUMB_BASE[4], 35: THUMB_BASE[5],
    },
    "colemak": {
        "default": None,
        0: "&kp Q", 1: "&kp W", 2: "&kp F", 3: "&kp P", 4: "&kp G",
        5: "&kp J", 6: "&kp L", 7: "&kp U", 8: "&kp Y", 9: "&kp SEMI",
        10: "&hm LGUI A", 11: "&hm LALT R", 12: "&hm LCTRL S", 13: "&hm LSHIFT T", 14: "&kp D",
        15: "&kp H", 16: "&hm LSHIFT N", 17: "&hm LCTRL E", 18: "&hm LALT I", 19: "&hm LGUI O",
        20: "&lt MOUSE Z", 21: "&kp X", 22: "&kp C", 23: "&kp V", 24: "&kp B",
        25: "&kp K", 26: "&kp M", 27: "&kp COMMA", 28: "&kp DOT", 29: "&lt MOUSE FSLH",
        30: THUMB_BASE[0], 31: THUMB_BASE[1], 32: THUMB_BASE[2],
        33: THUMB_BASE[3], 34: THUMB_BASE[4], 35: THUMB_BASE[5],
    },
    # nav = QMK LAYOUT_LAYER_NAVIGATION; DEAD_HALF_ROW -> &none + &tog GAMEPAD
    "nav": {
        "default": "&none",
        4: "&tog GAMEPAD", 9: "&tog GAMEPAD",
        5: "&kp K_APP", 6: "&kp K_PASTE", 7: "&kp K_COPY", 8: "&kp K_CUT", 9 + 0: "&kp K_UNDO",
        10: "&kp LGUI", 11: "&kp LALT", 12: "&kp LCTRL", 13: "&kp LSHIFT",
        15: "&kp CAPS", 16: "&kp LEFT", 17: "&kp DOWN", 18: "&kp UP", 19: "&kp RIGHT",
        24: "&tog GAMEPAD", 29: "&tog GAMEPAD",
        25: "&kp INS", 26: "&kp HOME", 27: "&kp PG_DN", 28: "&kp PG_UP", 29 + 0: "&kp END",
        # thumbs: XXXXXXX, KC_TRNS, XXXXXXX, KC_ENT, KC_DEL + extra
        30: "&none", 31: "&trans", 32: "&none", 33: "&kp RET", 34: "&kp DEL",
        35: "&trans",
    },
    "num": {
        "default": "&none",
        0: "&kp LBKT", 1: "&kp N7", 2: "&kp N8", 3: "&kp N9", 4: "&kp RBKT",
        9: "&tog GAMEPAD", 29: "&tog GAMEPAD",
        10: "&kp SQT", 11: "&kp N4", 12: "&kp N5", 13: "&kp N6", 14: "&kp EQUAL",
        15: "&none", 16: "&kp LSHIFT", 17: "&kp LCTRL", 18: "&kp LALT", 19: "&kp LGUI",
        20: "&kp GRAVE", 21: "&kp N1", 22: "&kp N2", 23: "&kp N3", 24: "&kp BSLH",
        # thumbs: KC_DOT, KC_0, KC_MINS, XXXXXXX, KC_TRNS + extra
        30: "&kp DOT", 31: "&kp N0", 32: "&kp MINUS", 33: "&none", 34: "&trans",
        35: "&trans",
    },
    # Mouse layer, Colemak labels (2026 session decision, supersedes the QMK
    # pointer-layer port): move diamond u=MOVE_UP ,=MOVE_DOWN n=MOVE_LEFT
    # o=MOVE_RIGHT; scroll m/e/i// = SCRL left/down/up/right (e,i match nav
    # arrows); LCLK/RCLK/MCLK on the right thumbs; left thumbs &trans.
    "mouse": {
        "default": "&none",
        7: "&mmv MOVE_UP",
        10: "&kp LGUI", 11: "&kp LALT", 12: "&kp LCTRL", 13: "&kp LSHIFT",
        16: "&mmv MOVE_LEFT", 17: "&msc SCRL_DOWN", 18: "&msc SCRL_UP", 19: "&mmv MOVE_RIGHT",
        26: "&msc SCRL_LEFT", 27: "&mmv MOVE_DOWN", 29: "&msc SCRL_RIGHT",
        30: "&trans", 31: "&trans", 32: "&trans",
        33: "&mkp LCLK", 34: "&mkp RCLK", 35: "&mkp MCLK",
    },
    "sym": {
        "default": "&none",
        0: "&kp LBRC", 1: "&kp AMPS", 2: "&kp ASTRK", 3: "&kp LPAR", 4: "&kp RBRC",
        9: "&tog GAMEPAD", 29: "&tog GAMEPAD",
        10: "&kp DQT", 11: "&kp DLLR", 12: "&kp PRCNT", 13: "&kp CARET", 14: "&kp PLUS",
        15: "&none", 16: "&kp LSHIFT", 17: "&kp LCTRL", 18: "&kp LALT", 19: "&kp LGUI",
        20: "&kp TILDE", 21: "&kp EXCL", 22: "&kp AT", 23: "&kp HASH", 24: "&kp PIPE",
        # thumbs: KC_LPRN, KC_RPRN, KC_UNDS, KC_TRNS, XXXXXXX + extra
        30: "&kp LPAR", 31: "&kp RPAR", 32: "&kp UNDER", 33: "&trans", 34: "&none",
        35: "&trans",
    },
    # QMK media layer; RM_*/EE_CLR/INVY have no ZMK translation (dropped);
    # &bootloader (QK_BOOT translation) at the single QMK spot (n); INVY dropped (trackball-only).
    "media": {
        "default": "&none",
        10: "&kp K_MUTE", 11: "&kp K_PREV", 12: "&kp K_VOL_DN", 13: "&kp K_VOL_UP", 14: "&kp K_NEXT",
        15: "&kp K_MUTE", 16: "&kp K_PREV", 17: "&kp K_VOL_DN", 18: "&kp K_VOL_UP", 19: "&kp K_NEXT",
        24: "&none", 25: "&bootloader",
        # thumbs: KC_TRNS, KC_MPLY, KC_MSTP, KC_MSTP, KC_MPLY + extra
        30: "&trans", 31: "&kp K_PP", 32: "&kp K_STOP", 33: "&kp K_STOP", 34: "&kp K_PP",
        35: "&trans",
    },
    "fun": {
        "default": "&none",
        4: "&tog GAMEPAD", 24: "&tog GAMEPAD",
        5: "&kp PSCRN", 6: "&kp F7", 7: "&kp F8", 8: "&kp F9", 9: "&kp F12",
        10: "&kp LGUI", 11: "&kp LALT", 12: "&kp LCTRL", 13: "&kp LSHIFT",
        15: "&kp SLCK", 16: "&kp F4", 17: "&kp F5", 18: "&kp F6", 19: "&kp F11",
        25: "&kp PAUSE_BREAK", 26: "&kp F1", 27: "&kp F2", 28: "&kp F3", 29: "&kp F10",
        # thumbs: XXXXXXX, XXXXXXX, KC_TRNS, XXXXXXX, XXXXXXX + extra
        30: "&none", 31: "&none", 32: "&trans", 33: "&none", 34: "&none",
        35: "&trans",
    },
    "gamepad": {
        "default": None,
        0: "&kp LALT", 1: "&kp W", 2: "&kp E", 3: "&kp R", 4: "&kp T",
        5: "&kp Y", 6: "&kp U", 7: "&kp I", 8: "&kp O", 9: "&kp P",
        10: "&kp LSHIFT", 11: "&kp S", 12: "&kp D", 13: "&kp F", 14: "&kp G",
        15: "&kp H", 16: "&kp J", 17: "&kp K", 18: "&kp L", 19: "&kp SEMI",
        20: "&kp LCTRL", 21: "&kp X", 22: "&kp C", 23: "&kp V", 24: "&kp B",
        25: "&kp N", 26: "&kp M", 27: "&kp COMMA", 28: "&kp DOT", 29: "&kp FSLH",
        # MO(L1), SPC_NAV, MO(L2), ENT_SYM, MO(L2) + extra = tog GAMEPAD (contract)
        30: "&mo GP_L1", 31: "&lt NAV SPACE", 32: "&mo GP_L2",
        33: "&lt SYM RET", 34: "&mo GP_L2", 35: "&tog GAMEPAD",
    },
    "gp_l1": {
        "default": None,
        0: "&trans", 1: "&kp N7", 2: "&trans", 3: "&kp N9", 4: "&kp ESC",
        5: "&kp Y", 6: "&kp U", 7: "&kp I", 8: "&kp O", 9: "&kp P",
        10: "&trans", 11: "&trans", 12: "&trans", 13: "&trans", 14: "&kp TAB",
        15: "&kp H", 16: "&kp J", 17: "&kp K", 18: "&kp L", 19: "&kp SEMI",
        20: "&trans", 21: "&kp N1", 22: "&kp N2", 23: "&kp N3", 24: "&kp N0",
        25: "&kp N", 26: "&kp M", 27: "&kp COMMA", 28: "&kp DOT", 29: "&kp FSLH",
        # MO(L1), SPC_NAV, XXXXXXX, ENT_SYM, BSP_NUM + extra
        30: "&mo GP_L1", 31: "&lt NAV SPACE", 32: "&none",
        33: "&lt SYM RET", 34: "&lt NUM BSPC", 35: "&none",
    },
    "gp_l2": {
        "default": None,
        0: "&trans", 1: "&kp F7", 2: "&trans", 3: "&kp F9", 4: "&kp ESC",
        5: "&kp Y", 6: "&kp U", 7: "&kp I", 8: "&kp O", 9: "&tog GAMEPAD",
        10: "&trans", 11: "&trans", 12: "&trans", 13: "&trans", 14: "&kp TAB",
        15: "&kp H", 16: "&kp J", 17: "&kp K", 18: "&kp L", 19: "&kp SEMI",
        20: "&trans", 21: "&kp F1", 22: "&kp F2", 23: "&kp F3", 24: "&kp N0",
        25: "&kp N", 26: "&kp M", 27: "&kp COMMA", 28: "&kp DOT", 29: "&kp FSLH",
        # XXXXXXX, SPC_NAV, MO(L2), ENT_SYM, MO(L2) + extra
        30: "&none", 31: "&lt NAV SPACE", 32: "&mo GP_L2",
        33: "&lt SYM RET", 34: "&mo GP_L2", 35: "&none",
    },
    "bt": {
        "default": "&none",
        20: "&bt BT_SEL 0", 21: "&bt BT_SEL 1", 22: "&bt BT_SEL 2",
        23: "&bt BT_SEL 3", 24: "&bt BT_CLR",
        30: "&trans", 31: "&trans", 32: "&trans", 33: "&trans", 34: "&trans", 35: "&trans",
    },
}

COMBOS = {
    # name: (key-positions string, binding string)
    "combo_to_colemak": ("0 9", "&to COLEMAK"),
    "combo_to_qwerty": ("0 19", "&to QWERTY"),
    "combo_bt_next": ("9 19", "&bt BT_NXT"),
    "combo_bt_prev": ("9 29", "&bt BT_PRV"),
    "combo_bt_out_tog": ("4 5", "&out OUT_TOG"),
}

BEHAVIORS = {
    "hm": {"tapping-term-ms": "200", "flavor": '"tap-preferred"'},
}

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

def parse_keymap_layers(raw):
    """Ordered [(node_name, [binding strings], bindings_first_line_no)] for
    keymap child nodes that have a `bindings = <...>;` property."""
    layers = []
    i = 0
    while i < len(raw):
        m = re.match(r"^\s{8}(\w+)\s*\{\s*$", raw[i])
        if m:
            name, j, started, toks, first_line = m.group(1), i + 1, False, [], None
            while j < len(raw):
                line = re.sub(r"//.*$", "", raw[j])
                if not started:
                    if re.match(r"^\s*bindings\s*=", line):
                        started, first_line = True, j + 1
                        if "<" in line:
                            line = line.split("<", 1)[1]
                        else:
                            j += 1
                            continue
                    elif re.match(r"^\s*\}", line):
                        break
                    else:
                        j += 1
                        continue
                if ">" in line:
                    toks += line.split(">", 1)[0].split()
                    break
                toks += line.split()
                j += 1
            if started:
                # group tokens into bindings: a binding starts with '&'
                bindings, cur = [], None
                for t in toks:
                    if t.startswith("&"):
                        if cur:
                            bindings.append(" ".join(cur))
                        cur = [t]
                    elif cur is not None:
                        cur.append(t)
                if cur:
                    bindings.append(" ".join(cur))
                layers.append((name, bindings, first_line))
            i = j
        i += 1
    return layers


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def main(path):
    errors = []
    raw = open(path).read().splitlines()
    text = "\n".join(raw)

    # 1) layer index defines
    defines = dict(re.findall(r"^#define\s+(\w+)\s+(\d+)\s*$", text, re.M))
    defines = {k: int(v) for k, v in defines.items()}
    for idx, name in enumerate(LAYER_DEFINES):
        got = defines.get(name)
        if got != idx:
            errors.append(f"#define {name}: expected {idx}, got {got}")

    # 2) keymap child-node order
    layers = [l for l in parse_keymap_layers(raw) if l[0] in LAYER_NODE_NAMES]
    got_order = [l[0] for l in layers]
    if got_order != LAYER_NODE_NAMES:
        errors.append(f"keymap layer order mismatch:\n  expected {LAYER_NODE_NAMES}\n  got      {got_order}")

    # 3) binding counts + per-position spec (grid: idx = row*10+col, 36 keys)
    for li, (name, bindings, line) in enumerate(layers):
        if len(bindings) != 36:
            errors.append(f"layer {name} (bindings start line {line}): "
                          f"{len(bindings)} bindings, expected 36 (10+10+10+6)")
            continue
        spec = SPEC[LAYER_DEFINES[li].lower()]
        default = spec.get("default", "&none")
        for pos, got in enumerate(bindings):
            want = spec.get(pos, default)
            if want is None:
                errors.append(f"layer {name} pos {pos}: no assertion in SPEC (got '{got}')")
            elif got != want:
                where = (f"row {pos // 10} col {pos % 10}" if pos < 30
                         else f"thumb #{pos - 29}")
                errors.append(f"layer {name} pos {pos:2d} ({where}, bindings start "
                              f"line {line}): expected '{want}', got '{got}'")

    # 4) combos
    for cname, (positions, binding) in COMBOS.items():
        block = re.search(rf"{cname}\s*\{{(.*?)\}}", text, re.S)
        if not block:
            errors.append(f"combo {cname}: not found")
            continue
        body = block.group(1)
        kp = re.search(r"key-positions\s*=\s*<([^>]*)>", body)
        kb = re.search(r"bindings\s*=\s*<([^>]*)>", body)
        if not kp or not kb:
            errors.append(f"combo {cname}: missing key-positions or bindings")
            continue
        if kp.group(1).split() != positions.split():
            errors.append(f"combo {cname}: key-positions <{kp.group(1).strip()}>, "
                          f"expected <{positions}>")
        if kb.group(1).split() != binding.split():
            errors.append(f"combo {cname}: bindings <{kb.group(1).strip()}>, "
                          f"expected <{binding}>")

    # 5) hold-tap behaviors
    for bname, props in BEHAVIORS.items():
        m = re.search(rf"\b{bname}:\s*\w+\s*\{{(.*?)\}}", text, re.S)
        if not m:
            errors.append(f"behavior {bname}: not found")
            continue
        body = m.group(1)
        for prop, want in props.items():
            pm = re.search(rf"{prop}\s*=\s*([^;]+);", body)
            got = pm.group(1).strip() if pm else None
            if got is not None:
                got = got.strip("<>").strip()
            if got != want:
                errors.append(f"behavior {bname}: {prop} = {got}, expected {want}")

    if errors:
        print(f"FAIL ({path}): {len(errors)} problem(s)")
        for e in errors:
            print("  - " + e)
        sys.exit(1)
    print(f"OK ({path}): 12 layers x 36 bindings, layer order, per-position "
          "bindings, combos and behaviors all match the embedded contract spec.")


main(KEYMAP)
