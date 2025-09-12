# Visual MCP Project

## Build/Test Commands
- **Development server**: `uv run mcp dev src/visual_mcp/server.py`
- **Install in Claude Desktop**: `uvx visual-mcp` (see CLAUDE_DESKTOP_SETUP.md)
- **Run tests**: `uv run pytest tests/test_server.py -v`
- **Run example**: `uv run python examples/example_usage.py`
- **Linting**: `uv run ruff check src/visual_mcp/server.py tests/test_server.py`
- **Formatting**: `uv run ruff format src/visual_mcp/server.py tests/test_server.py`
- **Type checking**: `uv run mypy src/visual_mcp/server.py tests/test_server.py`

## Code Style Guidelines
- **Python**: Use `uv ruff` for linting and formatting
- **Type hints**: Required for all function parameters and return values
- **Error handling**: Use try/catch blocks with informative error messages
- **Async/await**: All MCP tools must be async functions
- **Docstrings**: Required for all functions and classes
- **Naming**: 
  - Functions: snake_case
  - Classes: PascalCase
  - Constants: UPPER_SNAKE_CASE
  - Variables: snake_case
- **Imports**: Group imports (standard library, third-party, local)
- **API integration**: Use httpx for HTTP requests with proper timeout handling
- **MCP tools**: Use FastMCP decorators (@mcp.tool()) with proper type annotations

## Project Structure
- `src/visual_mcp/server.py`: Main MCP server implementation with image analysis tools
- `tests/test_server.py`: Comprehensive test suite with pytest
- `examples/example_usage.py`: Demonstration script showing how to use the tools
- `README.md`: Project documentation and setup instructions
- `pyproject.toml`: Project dependencies and configuration

## Environment Variables
- `GLM_API_KEY`: Required API key for GLM-4.5V vision model access

## Notes
- Uses GLM-4.5V Vision Model for multimodal AI analysis
- Supports image uploads via base64, file paths, and data URLs
- MCP tool available: analyze_image_with_context (unified tool for all image analysis)
- Repository uses git for version control
- Project uses uv for package management
- No existing Cursor or Copilot rules found