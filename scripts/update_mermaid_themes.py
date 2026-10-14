"""Utility script to inject high-contrast Mermaid directives across all project Markdown files."""

import re
from pathlib import Path

INIT_HEADER = "%%{init: {'theme': 'neutral', 'themeVariables': { 'fontSize': '13px', 'lineColor': '#2b7fff', 'edgeLabelBackground': '#ffffff', 'textColor': '#1f2937' }, 'flowchart': { 'nodeSpacing': 30, 'rankSpacing': 40, 'padding': 15, 'useMaxWidth': true } } }%%"

def update_mermaid_charts():
    files = list(Path("docs").glob("*.md")) + list(Path("plans").glob("*.md")) + [Path("README.md")]
    updated_files = []

    for f in files:
        if not f.exists():
            continue
        text = f.read_text(encoding="utf-8")
        if "```mermaid" not in text:
            continue

        lines = text.splitlines()
        new_lines = []
        i = 0
        changed = False

        while i < len(lines):
            line = lines[i]
            if line.strip() == "```mermaid":
                new_lines.append(line)
                i += 1
                # Check next line
                if i < len(lines) and lines[i].strip().startswith("%%{init:"):
                    new_lines.append(INIT_HEADER)
                    i += 1
                else:
                    new_lines.append(INIT_HEADER)
                changed = True
                continue
            new_lines.append(line)
            i += 1

        if changed:
            f.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
            updated_files.append(str(f))

    print(f"Successfully updated Mermaid theme in {len(updated_files)} files:")
    for uf in updated_files:
        print(f" - {uf}")

if __name__ == "__main__":
    update_mermaid_charts()
