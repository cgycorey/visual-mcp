#!/usr/bin/env python3
"""
Analyze the local image.png file using Visual MCP Server

This example demonstrates how to use the Visual MCP server for image analysis.
You can configure the model and API base using environment variables:

Environment Variables:
- GLM_API_KEY: Your API key (required)
- GLM_API_BASE: API base URL (default: https://api.z.ai/api/paas/v4)
- GLM_MODEL_NAME: Model name (default: glm-4.5v)

Example usage:
    export GLM_API_KEY='your-api-key'
    export GLM_API_BASE='https://your-api-base.com/api/paas/v4'
    export GLM_MODEL_NAME='glm-4.5v'
    python analyze_image.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import server
sys.path.insert(0, str(Path(__file__).parent))

from visual_mcp.server import analyze_image_with_context


async def analyze_image():
    """Analyze the image.png file"""
    print("=== Analyzing image.png ===")
    
    # Check if image exists
    image_path = "image.png"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        return
    
    print(f"Found image: {image_path}")
    
    # Check if API key is set
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("WARNING: GLM_API_KEY environment variable not set")
        print("Please set your API key with: export GLM_API_KEY='your-api-key'")
        return
    
    # Show configuration info
    api_base = os.getenv("GLM_API_BASE", "https://api.z.ai/api/paas/v4")
    model_name = os.getenv("GLM_MODEL_NAME", "glm-4.5v")
    
    print(f"API key found - proceeding with analysis...")
    print(f"API Base: {api_base}")
    print(f"Model: {model_name}")
    
    try:
        # Analyze the image with a general context
        print("\nAnalyzing image...")
        result = await analyze_image_with_context(
            image_path,  # Use file path directly
            user_context="Provide a comprehensive analysis of what you see in this image. Describe the main elements, any text content, and overall composition.",
            max_tokens=3000,
        )
        
        print("\n=== ANALYSIS RESULT ===")
        print(result)
        print("========================")
        
    except Exception as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    asyncio.run(analyze_image())