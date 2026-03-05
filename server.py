"""GitHub MCP Server - Main Entry Point

A modular GitHub API MCP server with tools for managing repositories,
pull requests, issues, and GitHub Projects v2 boards.

This is the refactored version using a modular package structure.
See server_old.py for the original monolithic version.
"""

from loguru import logger
from fastmcp import FastMCP

from github_mcp.config import (
    GITHUB_TOKEN,
    DEFAULT_OWNER,
    DEFAULT_REPO,
    DEFAULT_PROJECT,
    validate_config,
)
from github_mcp.tools import register_all_tools

# Initialize FastMCP server
mcp = FastMCP("github-mcp")

# Register all GitHub tools
register_all_tools(mcp)


# ============================================================
# Entry point
# ============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub FastMCP server")
    parser.add_argument(
        "--port", type=int, default=8090, help="SSE port (default 8090)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default 0.0.0.0)")
    args = parser.parse_args()

    logger.info(f"GitHub MCP server starting → http://{args.host}:{args.port}/sse")
    logger.info(f"Token   : {'loaded' if GITHUB_TOKEN else 'MISSING'}")
    logger.info(f"Owner   : {DEFAULT_OWNER   or 'MISSING'}")
    logger.info(f"Repo    : {DEFAULT_REPO    or 'MISSING'}")
    logger.info(f"Project : {DEFAULT_PROJECT or 'MISSING'}")

    mcp.run(transport="sse", host=args.host, port=args.port)
