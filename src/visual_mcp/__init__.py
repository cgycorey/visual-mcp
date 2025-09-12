"""
Visual MCP Server - Multimodal image analysis using GLM-4.5V

An MCP server that provides a unified tool for analyzing images, sketches,
architecture diagrams, and extracting textual information using GLM-4.5V vision model.
One tool for all your visual analysis needs.
"""

from .server import mcp

__version__ = "0.1.0"
__all__ = ["mcp"]
