#!/usr/bin/env python3
"""Convert a VSCode theme JSON into a TextMate .tmTheme (plist XML).

The conversion maps:
  - VSCode `colors` (editor.*)  -> tmTheme global settings
  - VSCode `tokenColors`        -> tmTheme scoped settings

It also appends a Typst-specific adjustment: declaration keywords
(fn/function/struct/enum/trait/impl/interface/class/def/module) carry more
specific storage.type.* scopes than primitive types (i32/str/number ...) and
are remapped to bold black, since Typst's syntect ignores VSCode semantic
tokens.

Usage: python3 convert_theme.py <input.json> <output.tmTheme>
"""
import json
import re
import sys
import uuid
from xml.sax.saxutils import escape


def load_jsonc(path):
    """Load JSON with trailing commas / line comments (VSCode JSONC)."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    text = re.sub(r"(^|[^:])//.*$", r"\1", text, flags=re.MULTILINE)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    return json.loads(text)


def norm_hex(color: str) -> str:
    """Expand 3-digit hex to 6-digit; leave 6/8-digit as-is."""
    c = color.strip()
    if c.startswith("#"):
        c = c[1:]
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return f"#{c.upper()}"


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    src, dst = sys.argv[1], sys.argv[2]

    theme = load_jsonc(src)

    colors = theme.get("colors", {})
    token_colors = theme.get("tokenColors", [])

    # --- global editor settings -------------------------------------------
    glob = {
        "background": colors.get("editor.background"),
        "foreground": colors.get("editor.foreground"),
        "caret": colors.get("editorCursor.foreground"),
        "selection": colors.get("editor.selectionBackground"),
        "selectionBorder": colors.get("editor.selectionHighlightBackground"),
        "inactiveSelection": colors.get("editor.inactiveSelectionBackground"),
        "lineHighlight": colors.get("editor.lineHighlightBackground"),
        "invisibles": colors.get("editorWhitespace.foreground"),
        "gutter": colors.get("editorGutter.background"),
        "gutterForeground": colors.get("editorLineNumber.foreground"),
        "findHighlight": colors.get("editor.findMatchBackground"),
        "findHighlightForeground": colors.get("editor.findMatchBorder"),
    }
    glob = {k: norm_hex(v) for k, v in glob.items() if v}

    # --- scoped token settings --------------------------------------------
    rules = []
    for tc in token_colors:
        scope = tc.get("scope")
        if scope is None:
            continue
        if isinstance(scope, list):
            scope = ", ".join(s.strip() for s in scope)
        settings = tc.get("settings", {}) or {}
        fg = settings.get("foreground")
        bg = settings.get("background")
        fs = settings.get("fontStyle")
        if not (fg or bg or fs):
            continue
        rules.append({
            "name": tc.get("name", ""),
            "scope": scope,
            "foreground": norm_hex(fg) if fg else None,
            "background": norm_hex(bg) if bg else None,
            "fontStyle": fs,
        })

    # --- Typst-specific adjustment ----------------------------------------
    # syntect only understands TextMate scopes, not VSCode semantic tokens.
    # Declaration keywords (fn, function, struct, enum, trait, impl, interface,
    # class, def, module) carry a more specific storage.type.* scope than
    # primitive types (i32, str, number, ...) which stay on the base
    # storage.type. Remap those sub-scopes to bold black so they read as
    # keywords, while real types keep their amber color. Sub-scopes are more
    # specific than base storage.type so they win regardless of order.
    rules.append({
        "name": "declaration keyword",
        "scope": ("storage.type.function, storage.type.class, "
                  "storage.type.struct, storage.type.enum, "
                  "storage.type.trait, storage.type.impl, "
                  "storage.type.interface, storage.type.def, "
                  "storage.type.module"),
        "foreground": "#000000",
        "background": None,
        "fontStyle": "bold",
    })

    # Function names -> solid black. syntect keeps the FIRST match among
    # equal-specificity selectors, so a duplicate appended scope would lose to
    # the original. Patch the existing rules in place instead. This covers
    # user-defined (entity.name.function), builtin (support.function) and
    # method-definition (meta.definition.method entity.name.function) names, so
    # every function reads as solid black. Object properties and field
    # declarations (variable.object.property / meta.field.declaration ...) are
    # left on their original color.
    function_scopes = {
        "entity.name.function",
        "support.function",
        "meta.definition.method entity.name.function",
    }
    for r in rules:
        parts = [p.strip() for p in r["scope"].split(",")]
        if any(s in parts for s in function_scopes):
            r["foreground"] = "#000000"

    # Modifiers (mut, static, const, pub, ...) -> black bold, matching the
    # declaration keywords. The original theme scopes them as
    # `storage.modifier, storage.control`; patch that rule in place.
    modifier_scopes = {"storage.modifier", "storage.control"}
    for r in rules:
        parts = [p.strip() for p in r["scope"].split(",")]
        if any(s in parts for s in modifier_scopes):
            r["foreground"] = "#000000"
            r["fontStyle"] = "bold"

    # --- emit plist XML ---------------------------------------------------
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                 '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">')
    lines.append('<plist version="1.0">')
    lines.append('<dict>')

    name = theme.get("name") or "Minimal Kiwi"
    lines.append('  <key>author</key>')
    lines.append('  <string>Minimal Kiwi</string>')
    lines.append('  <key>colorSpaceName</key>')
    lines.append('  <string>sRGB</string>')
    lines.append('  <key>name</key>')
    lines.append(f'  <string>{escape(name)}</string>')
    lines.append('  <key>semanticClass</key>')
    lines.append(f'  <string>{escape(name.lower().replace(" ", "."))}</string>')
    lines.append('  <key>settings</key>')
    lines.append('  <array>')

    # global settings block
    lines.append('    <dict>')
    lines.append('      <key>settings</key>')
    lines.append('      <dict>')
    for k in ["background", "foreground", "caret", "invisibles",
              "selection", "selectionBorder", "inactiveSelection",
              "lineHighlight", "gutter", "gutterForeground",
              "findHighlight", "findHighlightForeground"]:
        if k in glob:
            lines.append(f'        <key>{k}</key>')
            lines.append(f'        <string>{glob[k]}</string>')
    lines.append('      </dict>')
    lines.append('    </dict>')

    # scoped rule blocks
    for r in rules:
        lines.append('    <dict>')
        if r["name"]:
            lines.append('      <key>name</key>')
            lines.append(f'      <string>{escape(r["name"])}</string>')
        lines.append('      <key>scope</key>')
        lines.append(f'      <string>{escape(r["scope"])}</string>')
        lines.append('      <key>settings</key>')
        lines.append('      <dict>')
        if r["fontStyle"]:
            lines.append('        <key>fontStyle</key>')
            lines.append(f'        <string>{escape(r["fontStyle"])}</string>')
        if r["background"]:
            lines.append('        <key>background</key>')
            lines.append(f'        <string>{r["background"]}</string>')
        if r["foreground"]:
            lines.append('        <key>foreground</key>')
            lines.append(f'        <string>{r["foreground"]}</string>')
        lines.append('      </dict>')
        lines.append('    </dict>')

    lines.append('  </array>')
    lines.append('  <key>uuid</key>')
    lines.append(f'  <string>{uuid.uuid4()}</string>')
    lines.append('</dict>')
    lines.append('</plist>')

    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Converted {len(rules)} token rules -> {dst}")


if __name__ == "__main__":
    main()
