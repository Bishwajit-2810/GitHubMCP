# GitHub MCP Server

A modular GitHub API server using MCP (Model Context Protocol) and FastMCP.

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Setup](#-setup)
- [Usage](#-usage)
- [Development](#-development)
- [Documentation](#-documentation)
- [Migration from Old Version](#-migration-from-old-version)
- [Contributing](#-contributing)
- [License](#-license)

## ⚡ Quick Start

```bash
# Clone and install
git clone <your-repo-url>
cd GitHubMCP

# Install dependencies with uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -e .

# Configure
cp .env.example .env
# Edit .env with your GitHub token and settings

# Run
python server.py
```

The server starts on `http://localhost:8090/sse` by default.

## ✨ Features

- 🔧 **10 GitHub Tools** - Complete repository, PR, issues, and Projects v2 management
- 📦 **Modular Architecture** - Each tool in its own file for easy maintenance
- 🚀 **FastMCP Integration** - Built on the FastMCP framework
- 🔐 **Secure** - Environment-based configuration with dotenv
- 📊 **Projects v2 Support** - Full GitHub Projects v2 API integration

## 📁 Project Structure

```
GitHubMCP/
├── server.py                   # Main entry point (48 lines!)
├── server_fallback.py          # Original monolithic version (backup)
├── pyproject.toml              # Dependencies (uv managed)
├── README.md                   # This file
├── docs.html                   # Interactive documentation
├── .env                        # Your configuration (create from .env.example)
│
└── github_mcp/                 # Main package
    ├── __init__.py
    ├── config.py               # Configuration & environment variables
    ├── constants.py            # API URLs & GraphQL queries
    │
    ├── core/                   # Core HTTP & API utilities
    │   ├── __init__.py
    │   └── github_api.py       # GitHub API helpers
    │
    ├── utils/                  # Helper functions
    │   ├── __init__.py
    │   └── project_helpers.py  # Projects v2 helpers
    │
    └── tools/                  # MCP Tools (one per file)
        ├── __init__.py         # Tool registration
        ├── files.py            # list_files
        ├── branches.py         # create_branch
        ├── file_operations.py  # create_file
        ├── pull_requests.py    # create_pull_request
        ├── tasks.py            # create_project_task
        ├── task_list.py        # list_project_tasks
        ├── task_assign.py      # assign_task
        ├── task_status.py      # update_task_status
        ├── project_fields.py   # create_project_field
        └── task_fields.py      # set_task_fields
```

## 🚀 Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- GitHub Personal Access Token

### Installation

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd GitHubMCP
   ```

2. **Install dependencies with uv:**

   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Configure environment variables:**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your credentials:

   ```env
   GITHUB_TOKEN=ghp_...           # Your GitHub PAT
   GITHUB_OWNER=your-username     # GitHub username/org
   GITHUB_REPO=your-repo          # Default repository
   PROJECT_ID=123                 # GitHub Projects v2 number
   ```

### GitHub Token Permissions

Your GitHub Personal Access Token needs these scopes:

- `repo` - Full repository access
- `project` - GitHub Projects access (for Projects v2 features)
- `read:org` - Read organization data (if using org projects)

## 🎯 Usage

### Start the MCP Server

```bash
# Using uv
uv run server.py

# Or activate venv first
source .venv/bin/activate
python server.py

# With custom port/host
python server.py --port 8090 --host 0.0.0.0
```

The server will start on `http://localhost:8090/sse` by default.

### Available Tools

The server provides 10 MCP tools:

1. **`list_files`** - List repository files and directories
2. **`create_branch`** - Create new branches
3. **`create_file`** - Create or update files
4. **`create_pull_request`** - Open pull requests
5. **`create_project_task`** - Create tasks on Projects v2
6. **`list_project_tasks`** - List project items with pagination
7. **`assign_task`** - Assign users/labels to issues
8. **`update_task_status`** - Update task status
9. **`create_project_field`** - Create custom fields
10. **`set_task_fields`** - Set field values on tasks

## 🔧 Development

### Project Organization

The modular structure makes it easy to:

- **Add new tools**: Create a new file in `github_mcp/tools/`
- **Modify existing tools**: Edit the specific tool file
- **Test individual tools**: Import and test each tool separately
- **Reuse utilities**: Share helpers across tools via `core/` and `utils/`

### Adding a New Tool

1. Create a new file in `github_mcp/tools/your_tool.py`:

   ```python
   from typing import Optional
   from fastmcp import FastMCP
   from ..core.github_api import _headers

   def register_your_tool(mcp: FastMCP):
       @mcp.tool()
       async def your_tool(param: str) -> dict:
           """Your tool description."""
           # Implementation
           return {"result": "success"}
   ```

2. Add to `github_mcp/tools/__init__.py`:

   ```python
   from .your_tool import register_your_tool

   def register_all_tools(mcp):
       # ... existing tools ...
       register_your_tool(mcp)
   ```

3. Done! The tool is now available.

### Running Tests

```bash
# Install dev dependencies
uv pip install pytest pytest-asyncio

# Run tests
pytest
```

## 📚 Documentation

- **Interactive Docs**: Open `docs.html` in your browser
- **API Reference**: See individual tool files for detailed docstrings
- **GitHub API Docs**: [GitHub REST API](https://docs.github.com/en/rest)

## 🔄 Migration from Old Version

The original monolithic `server_fallback.py` (1,241 lines) has been refactored into a modular structure:

- **Old**: All code in `server_fallback.py`
- **New**: Code organized in `github_mcp/` package
- **Backup**: Original saved as `server_fallback.py`

All functionality remains identical — only the code organization changed.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes in the appropriate module
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Uses [GitHub REST API](https://docs.github.com/en/rest) and [GraphQL API](https://docs.github.com/en/graphql)
- Package management by [uv](https://github.com/astral-sh/uv)
  - Check that your Groq API key is valid
  - Verify you have available quota

### Debug Mode

The server logs to stderr. You can see detailed logs when running the agent to help debug issues.

## License

MIT
