#!/usr/bin/env python3
"""Fix mermaid diagrams in all docs_html/*.html files.

Problem: HTML formatters collapse mermaid <div> content, inserting literal
newlines inside node labels and participant aliases → "Syntax error in text".

Fix: Replace <div class="mermaid">...</div> with empty <div id="merChart_N">
containers. Store diagram source as JS template literals (formatter-proof) in
a <script> block and render via mermaid.render().
"""

import re
import html as html_module
from pathlib import Path

DOCS_DIR = Path("/home/bk/code/Project/GitHubMCP/docs_html")

# Mermaid keywords that must start on a new line.
# Longer patterns listed first to avoid partial matches.
_NL_BEFORE = [
    r"end note",
    r"note right of \S+",
    r"note left of \S+",
    r"Note over [^\n]+?(?= (?:participant|Note|loop|alt|else|opt|end|rect|par|\w+->>|\w+-->>))",
    r"Note over [\w,]+",
    r"Note right of \S+",
    r"Note left of \S+",
    r"participant ",
    r"actor ",
    r"loop ",
    r"alt ",
    r"else(?:\s|$)",
    r"opt ",
    r"rect ",
    r"par ",
    r"and ",
    r"subgraph ",
    r"direction ",
    r"style ",
    r"classDef ",
    r"linkStyle ",
    r"end\b",
]

# Regex that matches a sequenceDiagram message line start.
# Matches things like "C->>S:", "S-->>C:", "U->>A:", etc.
_MSG_LINE = re.compile(r" (?=[A-Za-z_][\w]*(?:->>|-->>|-x|-))")


def _add_newlines(text: str) -> str:
    """Insert newlines before mermaid statement-starting keywords.

    Works character-by-character to avoid inserting newlines inside
    quoted node-label strings like ``["some label with keywords"]``.
    """
    result: list[str] = []
    depth = 0  # bracket nesting depth – inside [" ... "] we skip splits

    i = 0
    while i < len(text):
        ch = text[i]

        # Track bracket depth (node labels are inside [ ])
        if ch == "[":
            depth += 1
            result.append(ch)
            i += 1
            continue
        if ch == "]":
            depth = max(0, depth - 1)
            result.append(ch)
            i += 1
            continue

        if depth == 0 and ch == " ":
            rest = text[i + 1 :]
            matched = False
            for kw in _NL_BEFORE:
                m = re.match(kw, rest)
                if m:
                    result.append("\n")
                    # Don't emit the space – the keyword starts the new line
                    matched = True
                    break
            if not matched:
                result.append(ch)
        else:
            result.append(ch)
        i += 1

    return "".join(result)


def clean_diagram(raw: str) -> str:
    """Convert formatter-collapsed HTML content to properly formatted mermaid."""
    # Decode HTML entities (--&gt; → -->, &lt; → <, etc.)
    text = html_module.unescape(raw)
    # Collapse HTML line-wrap: real newline + indent spaces → single space
    text = re.sub(r"\n\s+", " ", text).strip()
    # Normalise multiple spaces to one
    text = re.sub(r" {2,}", " ", text)
    # Reconstruct proper newlines at statement boundaries
    text = _add_newlines(text)
    # Escape backticks and template literal interpolation markers
    text = text.replace("`", "\\`").replace("${", "\\${")
    return text


def process_file(path: Path) -> None:
    content = path.read_text("utf-8")

    diagrams: list[str] = []

    def replace_mermaid(m: re.Match) -> str:
        code = clean_diagram(m.group(1))
        idx = len(diagrams)
        diagrams.append(code)
        return f'<div id="merChart_{idx}"></div>'

    content = re.sub(
        r'<div class="mermaid">(.*?)</div>',
        replace_mermaid,
        content,
        flags=re.DOTALL,
    )

    if not diagrams:
        print(f"  {path.name}: no mermaid divs found, skipping")
        return

    # Disable startOnLoad so mermaid doesn't auto-scan for .mermaid elements
    if "startOnLoad: true," in content:
        content = content.replace("startOnLoad: true,", "startOnLoad: false,")
    elif "mermaid.initialize({" in content:
        # Insert startOnLoad: false as first key
        content = content.replace(
            "mermaid.initialize({",
            "mermaid.initialize({\n        startOnLoad: false,",
            1,
        )

    # Build JS definitions block
    defs_lines = []
    for i, code in enumerate(diagrams):
        defs_lines.append(f"      merChart_{i}: `{code}`,")
    defs_block = "\n".join(defs_lines)

    render_script = f"""    <script>
      (function () {{
        var _diagrams = {{
{defs_block}
        }};
        function renderAll() {{
          Object.keys(_diagrams).forEach(function (id) {{
            var el = document.getElementById(id);
            if (!el) return;
            mermaid.render("svg_" + id, _diagrams[id]).then(function (result) {{
              el.innerHTML = result.svg;
            }}).catch(function (err) {{
              console.error("Mermaid [" + id + "]:", err);
            }});
          }});
        }}
        if (document.readyState === "loading") {{
          document.addEventListener("DOMContentLoaded", renderAll);
        }} else {{
          renderAll();
        }}
      }})();
    </script>"""

    # Insert just before </body>
    if "  </body>" in content:
        content = content.replace("  </body>", render_script + "\n  </body>", 1)
    elif "</body>" in content:
        content = content.replace("</body>", render_script + "\n</body>", 1)

    path.write_text(content, "utf-8")
    print(f"  {path.name}: fixed {len(diagrams)} diagram(s)")


if __name__ == "__main__":
    print("Fixing mermaid diagrams in docs_html/...")
    for html_file in sorted(DOCS_DIR.glob("*.html")):
        process_file(html_file)
    print("Done.")
