#!/usr/bin/env python3
"""Update already-processed mermaid files to use proper multi-line diagrams.

Finds the _diagrams object in each HTML file and reconstructs proper
newlines in all diagram definitions.
"""

import re
import html as html_module
from pathlib import Path

DOCS_DIR = Path("/home/bk/code/Project/GitHubMCP/docs_html")

# ── Keywords that must start on a new line ──────────────────────────────────
# Checked only when NOT inside a bracketed node label [ ... ]
_SPLIT_AFTER_SPACE = [
    "end note",
    "note right of ",
    "note left of ",
    "Note over ",
    "Note right of ",
    "Note left of ",
    "participant ",
    "actor ",
    "loop ",
    "alt ",
    "else",
    "opt ",
    "rect ",
    "par ",
    "and ",
    "subgraph ",
    "end",
    "direction ",
    "style ",
    "classDef ",
    "linkStyle ",
]


def _reconstruct(text: str) -> str:
    """Insert newlines before statement-starting keywords.

    Skips content inside ``[...]`` brackets (node labels).
    Sequences like ``->>`` or ``-->>`` also get a leading newline when
    outside brackets (sequenceDiagram message lines).
    """
    result: list[str] = []
    bracket_depth = 0
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        if ch == "[":
            bracket_depth += 1
            result.append(ch)
            i += 1
            continue
        if ch == "]":
            bracket_depth = max(0, bracket_depth - 1)
            result.append(ch)
            i += 1
            continue

        if bracket_depth == 0 and ch == " " and i + 1 < n:
            rest = text[i + 1 :]
            inserted_nl = False
            for kw in _SPLIT_AFTER_SPACE:
                if rest.startswith(kw):
                    # For bare "end": must be followed by space/newline/EOS, NOT "note"
                    if kw == "end":
                        after = rest[len(kw) :]
                        if after and after[0] not in (" ", "\n", "\t", ""):
                            continue  # e.g. "endnote" – not a keyword here
                        if rest.startswith("end note"):
                            continue  # already handled by "end note" entry
                    result.append("\n")
                    # skip the space; keyword starts the new line
                    inserted_nl = True
                    break
            if not inserted_nl:
                # Check for sequenceDiagram message patterns: Foo->>Bar:
                m = re.match(r"([A-Za-z_]\w*(?:->>|-->>|-x|--))", rest)
                if m:
                    result.append("\n")
                    inserted_nl = True
            if not inserted_nl:
                result.append(ch)
        else:
            result.append(ch)

        i += 1

    return "".join(result).strip()


def update_file(path: Path) -> None:
    content = path.read_text("utf-8")

    # Find the _diagrams block: var _diagrams = { ... };
    block_match = re.search(
        r"(var _diagrams = \{)(.*?)(\s*\};)",
        content,
        re.DOTALL,
    )
    if not block_match:
        return

    block_body = block_match.group(2)

    # Each entry looks like:   merChart_N: `...`,
    def fix_entry(m: re.Match) -> str:
        key = m.group(1)
        code = m.group(2)
        fixed = _reconstruct(code)
        return f"      {key}: `{fixed}`,"

    new_body = re.sub(
        r"      (merChart_\d+): `(.*?)`,+",
        fix_entry,
        block_body,
        flags=re.DOTALL,
    )

    new_content = (
        content[: block_match.start(2)] + new_body + content[block_match.end(2) :]
    )

    path.write_text(new_content, "utf-8")
    count = len(re.findall(r"merChart_\d+:", new_body))
    print(f"  {path.name}: updated {count} diagram(s)")


if __name__ == "__main__":
    print("Updating mermaid diagram newlines in docs_html/...")
    for html_file in sorted(DOCS_DIR.glob("*.html")):
        update_file(html_file)
    print("Done.")
