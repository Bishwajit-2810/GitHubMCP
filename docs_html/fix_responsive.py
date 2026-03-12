#!/usr/bin/env python3
"""Apply comprehensive responsive fixes to all docs_html files."""
import re, os

BASE = os.path.join(os.path.dirname(__file__), "docs_html")

# ─────────────────────────────────────────────────────────────────────────────
# SHARED helpers
# ─────────────────────────────────────────────────────────────────────────────


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✓ {os.path.basename(path)}")


# ─────────────────────────────────────────────────────────────────────────────
# STANDARD FILES  (index + 6 sidebar-layout docs pages)
# ─────────────────────────────────────────────────────────────────────────────

STANDARD_NAV_EXTRA_CSS = """\
      .nav-links {
        display: flex;
        align-items: center;
        gap: 1.5rem;
        overflow-x: auto;
        scrollbar-width: none;
        flex-shrink: 1;
        min-width: 0;
      }
      .nav-links::-webkit-scrollbar {
        display: none;
      }
      .nav-toggle {
        display: none;
        background: none;
        border: none;
        color: var(--text);
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0 4px;
        line-height: 56px;
        flex-shrink: 0;
        margin-left: auto;
      }"""

STANDARD_NAV_TOGGLE_JS = """\
    <script>
      (function () {
        var t = document.querySelector(".nav-toggle");
        var l = document.querySelector(".nav-links");
        if (t && l) {
          t.addEventListener("click", function () {
            l.classList.toggle("open");
          });
          document.addEventListener("click", function (e) {
            if (!e.target.closest("nav")) l.classList.remove("open");
          });
        }
      })();
    </script>"""


def inject_nav_extra_css(content):
    """Inject .nav-links / .nav-toggle CSS right after the closing brace of nav a.active."""
    # The pattern for the active/hover rule ends like:
    #   nav a:hover,\n      nav a.active {\n        color: var(--primary);\n      }
    marker = "        color: var(--primary);\n      }\n"
    # We want to insert after the FIRST occurrence of that pattern inside the nav block
    idx = content.find(
        "      nav a:hover,\n      nav a.active {\n        color: var(--primary);\n      }"
    )
    if idx == -1:
        # try alternate (index.html has different formatting)
        idx = content.find(
            "      nav a:hover,\n      nav a.active {\n        color: var(--primary);\n      }"
        )
    if idx == -1:
        print("    ! Could not find nav hover rule – skipping nav css injection")
        return content
    end = content.find(
        "\n",
        idx
        + len(
            "      nav a:hover,\n      nav a.active {\n        color: var(--primary);\n      }"
        ),
    )
    insert_at = content.find(
        "      nav a:hover,\n      nav a.active {\n        color: var(--primary);\n      }"
    ) + len(
        "      nav a:hover,\n      nav a.active {\n        color: var(--primary);\n      }"
    )
    return content[:insert_at] + "\n" + STANDARD_NAV_EXTRA_CSS + content[insert_at:]


def wrap_nav_html(content):
    """Wrap non-logo nav links in .nav-links and add hamburger button."""

    def repl(m):
        inner = m.group(1)
        logo_match = re.search(r'(\s+<a [^>]*class="logo"[^>]*>.*?</a>)', inner)
        if not logo_match:
            return m.group(0)
        logo_line = logo_match.group(1)
        rest = inner[logo_match.end() :]
        # Remove leading newline from rest
        rest = rest.lstrip("\n")
        # Indent each link line
        indented = ""
        for line in rest.splitlines():
            stripped = line.strip()
            if stripped:
                indented += "        " + stripped + "\n"
        return (
            "    <nav>\n"
            + logo_line
            + "\n"
            + '      <button class="nav-toggle" aria-label="Toggle navigation">&#9776;</button>\n'
            + '      <div class="nav-links">\n'
            + indented
            + "      </div>\n"
            + "    </nav>"
        )

    content = re.sub(
        r"    <nav>([\s\S]*?)\n    </nav>",
        repl,
        content,
        count=1,
    )
    return content


def expand_media_query_standard(content):
    """Replace existing @media (max-width: 768px) block with a comprehensive one."""
    old = re.compile(
        r"      @media \(max-width: 768px\) \{[\s\S]*?\n      \}",
        re.MULTILINE,
    )

    new_media = """\
      @media (max-width: 900px) {
        nav .logo {
          font-size: 1rem;
        }
      }
      @media (max-width: 768px) {
        .layout {
          flex-direction: column;
        }
        aside {
          display: none;
        }
        main {
          padding-left: 0;
        }
        nav {
          position: relative;
          height: auto;
          min-height: 56px;
          flex-wrap: wrap;
          padding: 0 1rem;
        }
        .nav-toggle {
          display: flex;
          align-items: center;
          line-height: normal;
          height: 56px;
        }
        .nav-links {
          display: none;
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: var(--surface);
          border-bottom: 1px solid var(--border);
          flex-direction: column;
          align-items: flex-start;
          gap: 0;
          padding: 0.5rem 0 1rem;
          z-index: 99;
          overflow-x: visible;
        }
        .nav-links.open {
          display: flex;
        }
        .nav-links a {
          padding: 0.6rem 1.5rem;
          width: 100%;
          font-size: 0.9rem;
          white-space: normal;
        }
        h1 {
          font-size: 1.8rem;
        }
      }
      @media (max-width: 480px) {
        .layout {
          padding: 1rem;
        }
        main {
          padding: 0;
        }
        pre {
          font-size: 0.78rem;
          padding: 0.8rem;
        }
        h1 {
          font-size: 1.5rem;
        }
        h2 {
          font-size: 1.2rem;
        }
        table {
          display: block;
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
        }
      }"""

    result = old.sub(new_media, content)
    if result == content:
        print("    ! @media 768px block not found – could not expand")
    return result


def fix_calc_bug(content):
    return content.replace("calc(100vh-80px)", "calc(100vh - 80px)")


def add_toggle_js(content):
    """Add hamburger JS just before </body>."""
    return content.replace("  </body>", STANDARD_NAV_TOGGLE_JS + "\n  </body>")


def fix_standard_file(path, has_flex_wrap=False, has_calc_bug=True):
    print(f"\nProcessing {os.path.basename(path)} …")
    c = read(path)
    c = fix_calc_bug(c) if has_calc_bug else c
    c = inject_nav_extra_css(c)
    c = wrap_nav_html(c)
    c = expand_media_query_standard(c)
    c = add_toggle_js(c)
    write(path, c)


# ─────────────────────────────────────────────────────────────────────────────
# INDEX.HTML  (uses a different @media block and nav spacing)
# ─────────────────────────────────────────────────────────────────────────────


def fix_index_html(path):
    print(f"\nProcessing {os.path.basename(path)} …")
    c = read(path)

    # The nav CSS uses gap: 2rem and has a spacer
    # Just replace the @media (max-width: 640px) block with a comprehensive one
    old_media = re.compile(
        r"      /\* responsive \*/\n      @media \(max-width: 640px\) \{[\s\S]*?\n      \}",
        re.MULTILINE,
    )
    new_media = """\
      /* responsive */
      @media (max-width: 900px) {
        .hero h1 {
          font-size: 2.4rem;
        }
      }
      @media (max-width: 768px) {
        nav {
          position: relative;
          height: auto;
          min-height: 56px;
          flex-wrap: wrap;
          padding: 0 1rem;
          gap: 0;
        }
        .nav-toggle {
          display: flex;
          align-items: center;
          height: 56px;
          line-height: normal;
        }
        .nav-links {
          display: none;
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: var(--surface);
          border-bottom: 1px solid var(--border);
          flex-direction: column;
          align-items: flex-start;
          gap: 0;
          padding: 0.5rem 0 1rem;
          z-index: 99;
        }
        .nav-links.open {
          display: flex;
        }
        .nav-links a,
        .nav-links span {
          padding: 0.6rem 1.5rem;
          width: 100%;
          font-size: 0.9rem;
          white-space: normal;
        }
        .hero {
          padding: 3rem 1.5rem;
        }
        .hero h1 {
          font-size: 2rem;
        }
        .hero p {
          font-size: 1rem;
        }
        .section {
          padding: 2rem 1.5rem;
        }
        table {
          display: block;
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
        }
      }
      @media (max-width: 480px) {
        .hero h1 {
          font-size: 1.6rem;
        }
        .task-grid {
          grid-template-columns: 1fr;
        }
        pre {
          font-size: 0.78rem;
          padding: 0.8rem;
        }
      }"""

    result = old_media.sub(new_media, c)
    if result == c:
        print("    ! Could not find index.html @media block")

    # Nav CSS: add .nav-links / .nav-toggle after nav a:hover rule
    result = inject_nav_extra_css(result)

    # Nav - also fix the nav CSS height declaration
    # index.html nav has no flex-wrap / height is set
    # The index nav CSS block (gap: 2rem version):
    old_nav_css = """\
      nav {
        background: var(--surface);
        border-bottom: 1px solid var(--border);
        padding: 0 2rem;
        display: flex;
        align-items: center;
        gap: 2rem;
        position: sticky;
        top: 0;
        z-index: 100;
        height: 56px;
      }"""
    new_nav_css = """\
      nav {
        background: var(--surface);
        border-bottom: 1px solid var(--border);
        padding: 0 2rem;
        display: flex;
        align-items: center;
        gap: 1.5rem;
        position: sticky;
        top: 0;
        z-index: 100;
        height: 56px;
      }"""
    result = result.replace(old_nav_css, new_nav_css)

    # Wrap nav HTML - index.html nav includes the spacer + span at the end
    # Replace the full nav block
    old_nav_html = """\
    <!-- Navigation -->
    <nav>
      <a href="index.html" class="logo">⚡ AI Ecosystem Docs</a>
      <a href="langchain.html">LangChain</a>
      <a href="langgraph.html">LangGraph</a>
      <a href="mcp.html">MCP</a>
      <a href="fastmcp.html">FastMCP</a>
      <a href="rag.html">RAG</a>
      <a href="rag_concept_docs.html">RAG Concepts</a>
      <a href="rag_learning_path.html">RAG Path</a>
      <a href="multi_agent.html">Multi-Agent</a>
      <a href="fastApi.html">FastAPI</a>
      <a href="pgAndPgVector.html">PgVector</a>
      <div class="spacer"></div>
      <span style="color: var(--muted); font-size: 0.8rem"
        >Groq · LangChain · FastMCP</span
      >
    </nav>"""
    new_nav_html = """\
    <!-- Navigation -->
    <nav>
      <a href="index.html" class="logo">⚡ AI Ecosystem Docs</a>
      <button class="nav-toggle" aria-label="Toggle navigation">&#9776;</button>
      <div class="nav-links">
        <a href="langchain.html">LangChain</a>
        <a href="langgraph.html">LangGraph</a>
        <a href="mcp.html">MCP</a>
        <a href="fastmcp.html">FastMCP</a>
        <a href="rag.html">RAG</a>
        <a href="rag_concept_docs.html">RAG Concepts</a>
        <a href="rag_learning_path.html">RAG Path</a>
        <a href="multi_agent.html">Multi-Agent</a>
        <a href="fastApi.html">FastAPI</a>
        <a href="pgAndPgVector.html">PgVector</a>
        <span style="color: var(--muted); font-size: 0.8rem; margin-left: auto;">Groq · LangChain · FastMCP</span>
      </div>
    </nav>"""
    result = result.replace(old_nav_html, new_nav_html)

    result = add_toggle_js(result)
    write(path, result)


# ─────────────────────────────────────────────────────────────────────────────
# fastApi.html  (different design system — cyan/dark, topnav scrollable)
# ─────────────────────────────────────────────────────────────────────────────


def fix_fastapi_html(path):
    print(f"\nProcessing {os.path.basename(path)} …")
    c = read(path)

    old_media = re.compile(
        r"      @media \(max-width: 900px\) \{[\s\S]*?\n      \}",
        re.MULTILINE,
    )

    new_media = """\
      @media (max-width: 1024px) {
        .sidebar {
          display: none;
        }
        .body-wrap {
          margin-left: 0;
        }
      }
      @media (max-width: 900px) {
        .sidebar {
          display: none;
        }
        .hero,
        .section {
          padding: 40px 24px;
        }
        .hero h1 {
          font-size: 32px;
        }
        .grid2,
        .grid3 {
          grid-template-columns: 1fr;
        }
      }
      @media (max-width: 600px) {
        .hero {
          padding: 32px 16px;
        }
        .hero h1 {
          font-size: 26px;
        }
        .section {
          padding: 28px 16px;
        }
        pre,
        .code-block {
          font-size: 0.78rem;
          padding: 0.8rem;
        }
        table {
          display: block;
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
          font-size: 0.82rem;
        }
        .topnav {
          padding: 0 12px;
          gap: 12px;
          font-size: 0.8rem;
        }
      }"""

    result = old_media.sub(new_media, c, count=1)
    if result == c:
        print("    ! Could not find fastApi.html @media 900px block")
    write(path, result)


# ─────────────────────────────────────────────────────────────────────────────
# pgAndPgVector.html  (fix .index-grid not responsive)
# ─────────────────────────────────────────────────────────────────────────────


def fix_pgvector_html(path):
    print(f"\nProcessing {os.path.basename(path)} …")
    c = read(path)

    # Add .index-grid to existing media query block
    old = "        .compare-row > div:first-child {\n          border-right: none;\n          border-bottom: 1px solid var(--border);\n        }\n      }"
    new = """\
        .compare-row > div:first-child {
          border-right: none;
          border-bottom: 1px solid var(--border);
        }
        .index-grid {
          grid-template-columns: 1fr !important;
        }
        table {
          display: block;
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
        }
      }
      @media (max-width: 600px) {
        .hero {
          padding: 32px 16px;
        }
        .content {
          padding: 16px;
        }
        pre,
        code {
          font-size: 0.78rem;
        }
        .topnav {
          padding: 0 12px;
          gap: 12px;
          font-size: 0.8rem;
        }
      }"""
    result = c.replace(old, new)
    if result == c:
        print("    ! pgAndPgVector.html: compare-row pattern not found")
    write(path, result)


# ─────────────────────────────────────────────────────────────────────────────
# rag_concept_docs.html  (fix .vs-block, add table overflow)
# ─────────────────────────────────────────────────────────────────────────────


def fix_rag_concept_html(path):
    print(f"\nProcessing {os.path.basename(path)} …")
    c = read(path)

    old_media = re.compile(
        r"      @media \(max-width: 900px\) \{[\s\S]*?\n      \}",
        re.MULTILINE,
    )

    new_media = """\
      @media (max-width: 900px) {
        .toc {
          display: none;
        }
        .vs-block {
          grid-template-columns: 1fr;
        }
        .vs-block > *:first-child {
          border-right: none;
          border-bottom: 1px solid var(--border);
          padding-bottom: 1rem;
        }
      }
      @media (max-width: 600px) {
        .section {
          padding: 1.5rem 1rem;
        }
        pre {
          font-size: 0.78rem;
          padding: 0.8rem;
        }
        h1 {
          font-size: 1.8rem;
        }
        h2 {
          font-size: 1.3rem;
        }
        table {
          display: block;
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
        }
        .metric-row {
          flex-direction: column;
        }
        .nav-pills {
          flex-wrap: wrap;
          gap: 0.4rem;
        }
      }"""

    result = old_media.sub(new_media, c, count=1)
    if result == c:
        print("    ! rag_concept_docs.html: @media 900px not found")

    # Also fix .vs-block CSS to use auto-fit grid or keep 1fr auto 1fr but add it to media
    # The vs-block may use grid-template-columns: 1fr auto 1fr
    # Check and ensure vs-block has column-gap and overflow protection
    result = result.replace(
        "grid-template-columns: 1fr auto 1fr;",
        "grid-template-columns: 1fr auto 1fr;\n        overflow-x: auto;",
        1,
    )
    write(path, result)


# ─────────────────────────────────────────────────────────────────────────────
# rag_learning_path.html  (fix .vs-wrap, expand media queries)
# ─────────────────────────────────────────────────────────────────────────────


def fix_rag_learning_path_html(path):
    print(f"\nProcessing {os.path.basename(path)} …")
    c = read(path)

    # Expand the 768px breakpoint (currently just hides nav links)
    old_768 = re.compile(
        r"      @media \(max-width: 768px\) \{[\s\S]*?\n      \}",
        re.MULTILINE,
    )

    new_768 = """\
      @media (max-width: 768px) {
        .top-nav a:not(.logo) {
          display: none;
        }
        .vs-wrap {
          grid-template-columns: 1fr;
          gap: 1rem;
        }
        .vs-wrap > *:first-child {
          border-right: none;
          border-bottom: 1px solid var(--border);
          padding-bottom: 1rem;
        }
        .page-wrap {
          padding: 0 1rem;
        }
        h1 {
          font-size: 1.8rem;
        }
        h2 {
          font-size: 1.3rem;
        }
        table {
          display: block;
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
        }
        pre {
          font-size: 0.8rem;
          padding: 0.8rem;
        }
      }
      @media (max-width: 480px) {
        .top-nav {
          padding: 0 1rem;
        }
        .top-nav .logo {
          font-size: 1rem;
        }
        h1 {
          font-size: 1.5rem;
        }
        .g2, .g3, .g4 {
          grid-template-columns: 1fr;
        }
      }"""

    result = old_768.sub(new_768, c, count=1)
    if result == c:
        print("    ! rag_learning_path.html: @media 768px not found")
    write(path, result)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Applying responsive fixes to docs_html ===\n")

    # index.html - special handling
    fix_index_html(os.path.join(BASE, "index.html"))

    # Standard sidebar-layout doc pages
    # langchain: already correct calc(), has flex-wrap in nav CSS
    fix_standard_file(
        os.path.join(BASE, "langchain.html"), has_flex_wrap=True, has_calc_bug=False
    )
    # langgraph: already correct calc(), no flex-wrap
    fix_standard_file(
        os.path.join(BASE, "langgraph.html"), has_flex_wrap=False, has_calc_bug=False
    )
    # mcp, fastmcp, rag, multi_agent: have the calc() bug
    fix_standard_file(
        os.path.join(BASE, "mcp.html"), has_flex_wrap=False, has_calc_bug=True
    )
    fix_standard_file(
        os.path.join(BASE, "fastmcp.html"), has_flex_wrap=False, has_calc_bug=True
    )
    fix_standard_file(
        os.path.join(BASE, "rag.html"), has_flex_wrap=False, has_calc_bug=True
    )
    fix_standard_file(
        os.path.join(BASE, "multi_agent.html"), has_flex_wrap=False, has_calc_bug=True
    )

    # Special files
    fix_fastapi_html(os.path.join(BASE, "fastApi.html"))
    fix_pgvector_html(os.path.join(BASE, "pgAndPgVector.html"))
    fix_rag_concept_html(os.path.join(BASE, "rag_concept_docs.html"))
    fix_rag_learning_path_html(os.path.join(BASE, "rag_learning_path.html"))

    print("\nDone.")
