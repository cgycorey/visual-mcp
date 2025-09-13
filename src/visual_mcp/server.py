"""
Visual MCP Server - Multimodal image analysis using GLM vision models

An MCP server that provides a unified tool for analyzing images, sketches,
architecture diagrams, and extracting textual information using GLM vision models.
One tool for all your visual analysis needs.
"""

import asyncio
import base64
import mimetypes
import os
import traceback
from pathlib import Path

import httpx
from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field

# Initialize FastMCP server
mcp = FastMCP(
    "Visual MCP",
    instructions="""
I am a visual analysis assistant powered by GLM vision models.
    Upload an image with context about what
you want to know, and I'll provide comprehensive analysis including descriptions,
text extraction, diagram analysis, or summaries as needed.
""",
)

# Configuration
GLM_API_BASE = os.getenv("GLM_API_BASE", "https://nano-gpt.com/api/v1")
GLM_API_KEY = os.getenv("GLM_API_KEY")
GLM_MODEL_NAME = os.getenv("GLM_MODEL_NAME", "zai-org/GLM-4.5V-FP8")


class ImageAnalysisRequest(BaseModel):
    """Unified request model for image analysis"""

    image_data: str = Field(
        ..., description="Base64 encoded image data, file path, or data URL"
    )
    user_context: str = Field(
        ...,
        description="What you want to know about the image - be specific"
        " about your needs",
    )
    max_tokens: int = Field(
        default=3000, description="Maximum tokens in response (default: 3000)"
    )


def prepare_image_for_api(image_input: str) -> tuple[str, str]:
    """Prepare image data for API call and return (base64_data, mime_type)"""
    # Check if it's a file path
    if os.path.exists(image_input):
        return encode_file_to_base64(image_input)

    # Check if it's a base64 string with data URL prefix
    if image_input.startswith("data:image"):
        # Extract mime type and base64 part from data URL
        try:
            header, data = image_input.split(",", 1)
            mime_type = header.split(";", 1)[0].split(":", 1)[
                1
            ]  # Extract "image/xxx" from "data:image/xxx;base64"
            return data, mime_type
        except (IndexError, ValueError):
            # Fallback to default if parsing fails
            return image_input.split(",", 1)[1], "image/jpeg"
    else:
        # Assume it's already base64 encoded, but we need to detect format
        # For now, default to JPEG, but could implement format detection
        return image_input, "image/jpeg"


def encode_file_to_base64(file_path: str | Path) -> tuple[str, str]:
    """Encode file to base64 string and detect mime type"""
    try:
        # Detect mime type from file extension
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type or not mime_type.startswith("image/"):
            # Default to JPEG if we can't determine the type
            mime_type = "image/jpeg"

        with open(file_path, "rb") as file:
            base64_data = base64.b64encode(file.read()).decode("utf-8")
            return base64_data, mime_type
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}") from None
    except PermissionError:
        raise ValueError(f"Permission denied when reading file: {file_path}") from None
    except Exception as e:
        raise ValueError(f"Failed to encode file {file_path}: {e}") from None


def is_valid_base64(base64_string: str) -> bool:
    """Check if a string is valid base64"""
    try:
        # Add padding if needed
        padding_needed = len(base64_string) % 4
        if padding_needed:
            base64_string += "=" * (4 - padding_needed)

        # Try to decode
        base64.b64decode(base64_string, validate=True)
        return True
    except Exception:
        return False


def validate_image_format(mime_type: str) -> str:
    """Validate and normalize image format"""
    # List of explicitly supported image formats based on official
    # GLM-4.5V documentation
    # PNG is shown in the official example, JPEG/JPG mentioned in video API
    supported_formats = {"image/jpeg", "image/jpg", "image/png"}

    # Normalize to lowercase
    mime_type = mime_type.lower()

    if mime_type not in supported_formats:
        # Default to JPEG for unsupported formats (most universally supported)
        return "image/jpeg"

    return mime_type


async def call_glm_vision_api(
    image_base64: str,
    prompt: str,
    mime_type: str = "image/jpeg",
    max_tokens: int = 2048,
    max_retries: int = 5,
    retry_delay: float = 2.0,
) -> str:
    """Call GLM-4.5V vision API for image analysis with retry logic"""
    if not GLM_API_KEY:
        raise ValueError("GLM_API_KEY environment variable not set")

    if not GLM_API_BASE:
        raise ValueError("GLM_API_BASE environment variable not set")

    # Validate base64 data
    if not is_valid_base64(image_base64):
        raise ValueError("Invalid base64 image data")

    # Validate and normalize image format
    mime_type = validate_image_format(mime_type)

    headers = {
        "Authorization": f"Bearer {GLM_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GLM_MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,
    }

    last_error = None
    
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{GLM_API_BASE}/chat/completions", headers=headers, json=payload
                )
                response.raise_for_status()

                result = response.json()
                return result["choices"][0]["message"]["content"]

        except httpx.HTTPStatusError as e:
            error_msg = f"GLM API error: {e.response.status_code}"
            try:
                error_detail = e.response.json()
                error_msg += (
                    f" - {error_detail.get('error', {}).get('message', 'Unknown')}"
                    f" error"
                )
            except Exception:
                error_msg += f" - {e.response.text}"
            
            last_error = RuntimeError(error_msg)
            
            # Don't retry on authentication errors or certain HTTP status codes
            if e.response.status_code in (401, 403, 429):
                break
                
        except httpx.TimeoutException as e:
            last_error = RuntimeError(f"GLM API timeout: {e}")
        except httpx.NetworkError as e:
            last_error = RuntimeError(f"GLM API network error: {e}")
        except Exception as e:
            error_details = f"Failed to call GLM API: {str(e)}\
            Traceback: {traceback.format_exc()}"
            last_error = RuntimeError(error_details)
        
        # If this is not the last attempt, wait before retrying
        if attempt < max_retries - 1:
            await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
    
    # All retries failed, raise the last error
    if last_error:
        raise last_error
    else:
        raise RuntimeError("Failed to call GLM API after maximum retries")


@mcp.tool()
async def analyze_image_with_context(
    image_data: str,
    user_context: str,
    max_tokens: int = 3000,
    ctx: Context | None = None,
) -> str:
    """
    Upload an image and get comprehensive analysis based on your specific needs.
    The AI will figure out the best approach (description, text extraction,
    diagram analysis, etc.) based on your context.

    Args:
        image_data: Base64 encoded image data, file path, or data URL.
            Supports explicitly confirmed formats:
            - JPEG, JPG, PNG
        user_context: What you want to know - be specific! Examples:
            - "Extract and summarize all text in this document"
            - "Analyze this architecture diagram and explain the system flow"
            - "Describe this photo in detail focusing on people and setting"
            - "What's wrong with this code screenshot?"
            - "Explain this mathematical diagram step by step"
        max_tokens: Maximum tokens in response (default: 3000)

    Returns:
        Comprehensive analysis tailored to your specific needs
    """
    try:
        if ctx:
            await ctx.info("Starting image analysis with context...")

        # Prepare image data and detect format
        image_base64, mime_type = prepare_image_for_api(image_data)

        # Build an enhanced prompt that guides the AI to provide the right
        # type of analysis
        enhanced_prompt = f"""
You are a comprehensive visual analysis assistant. The user has provided
        an image and specific context about what they need.

USER CONTEXT: {user_context}

Based on this context, provide the most appropriate analysis which may include:
- Detailed description of visual elements
- Text extraction and transcription (if text is present)
- Diagram/technical analysis (if it's a diagram, chart, or technical drawing)
- Summary of key information
- Identification of issues, patterns, or insights
- Step-by-step explanations when appropriate

Adapt your response style and focus based on what the user is asking for.
Be thorough but concise.
"""

        # Call GLM vision API with retry logic
        result = await call_glm_vision_api(
            image_base64, enhanced_prompt, mime_type, max_tokens
        )

        if ctx:
            await ctx.info("Image analysis completed successfully")

        return result

    except Exception as e:
        error_msg = f"Image analysis failed: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        return error_msg


def main():
    """Main entry point for the MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
