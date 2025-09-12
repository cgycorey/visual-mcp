"""
Test suite for Visual MCP Server

This project uses a unified approach with a single tool `analyze_image_with_context`
that handles all image analysis needs. The AI determines the best analysis approach
based on the user's natural language context, eliminating the need for multiple
specialized tools.
"""

import base64
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Import the server functions
from visual_mcp.server import (
    analyze_image_with_context,
    call_glm_vision_api,
    encode_file_to_base64,
    prepare_image_for_api,
)


class TestImageEncoding:
    """Test image encoding utilities"""

    def test_encode_file_to_base64_file_exists(self):
        """Test encoding existing file"""
        # Create a temporary image file
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".jpg", delete=False) as tmp:
            # Write minimal JPEG header
            tmp.write(
                b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xd9"
            )
            tmp_path = tmp.name

        try:
            result, mime_type = encode_file_to_base64(tmp_path)
            assert isinstance(result, str)
            assert isinstance(mime_type, str)
            assert len(result) > 0
            assert mime_type == "image/jpeg"
            # Should be valid base64
            decoded = base64.b64decode(result)
            assert len(decoded) > 0
        finally:
            os.unlink(tmp_path)

    def test_encode_file_to_base64_file_not_exists(self):
        """Test encoding non-existent file raises error"""
        with pytest.raises(ValueError, match="File not found"):
            encode_file_to_base64("/non/existent/file.txt")

    def test_prepare_image_for_api_file_path(self):
        """Test preparing image from file path"""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            # Write some test data
            tmp.write(b"fake_image_data")
            tmp.flush()

            try:
                result, mime_type = prepare_image_for_api(tmp.name)
                assert isinstance(result, str)
                assert isinstance(mime_type, str)
                assert len(result) > 0
                assert mime_type == "image/jpeg"
                # Should be base64 without data URL prefix
                assert not result.startswith("data:")
            finally:
                os.unlink(tmp.name)

    def test_prepare_image_for_api_base64_with_url(self):
        """Test preparing image from data URL"""
        data_url = "data:image/png;base64,ZmFrZV9pbWFnZV9kYXRh"
        result, mime_type = prepare_image_for_api(data_url)
        assert result == "ZmFrZV9pbWFnZV9kYXRh"
        assert mime_type == "image/png"

    def test_prepare_image_for_api_base64_only(self):
        """Test preparing image from base64 only"""
        base64_data = "ZmFrZV9pbWFnZV9kYXRh"
        result, mime_type = prepare_image_for_api(base64_data)
        assert result == base64_data
        assert mime_type == "image/jpeg"  # Default fallback


class TestGLMAPI:
    """Test GLM API integration"""

    @pytest.mark.asyncio
    @patch("visual_mcp.server.httpx.AsyncClient")
    @patch("visual_mcp.server.GLM_API_KEY", "test-api-key")
    @patch("visual_mcp.server.GLM_MODEL_NAME", "glm-4.5v")
    async def test_call_glm_vision_api_success(self, mock_client):
        """Test successful GLM vision API call"""
        # Mock the HTTP client response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "This is a test analysis response"}}]
        }

        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        # Test the API call
        result = await call_glm_vision_api(
            "dGVzdF9iYXNlNjRfaW1hZ2VfZGF0YQ==", "Test prompt", max_tokens=1000
        )

        assert result == "This is a test analysis response"

        # Verify the API call was made correctly
        mock_client.return_value.__aenter__.return_value.post.assert_called_once()
        call_args = mock_client.return_value.__aenter__.return_value.post.call_args

        assert call_args[1]["json"]["model"] == "glm-4.5v"
        assert call_args[1]["json"]["max_tokens"] == 1000
        assert len(call_args[1]["json"]["messages"]) == 1
        assert call_args[1]["json"]["messages"][0]["role"] == "user"

    @pytest.mark.asyncio
    @patch("visual_mcp.server.httpx.AsyncClient")
    @patch("visual_mcp.server.GLM_API_KEY", "test-api-key")
    async def test_call_glm_vision_api_http_error(self, mock_client):
        """Test GLM vision API call with HTTP error"""
        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 404")
        mock_response.json.return_value = {"error": {"message": "Not found"}}

        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response
        )

        # Test the API call handles error
        with pytest.raises(RuntimeError, match="Failed to call GLM API"):
            await call_glm_vision_api("dGVzdF9kYXRh", "test prompt")

    @pytest.mark.asyncio
    async def test_call_glm_vision_api_no_api_key(self):
        """Test GLM vision API call without API key"""
        # Temporarily remove API key
        original_key = os.environ.get("GLM_API_KEY")
        if "GLM_API_KEY" in os.environ:
            del os.environ["GLM_API_KEY"]

        try:
            with pytest.raises(
                ValueError, match="GLM_API_KEY environment variable not set"
            ):
                await call_glm_vision_api("test_data", "test prompt")
        finally:
            # Restore API key if it existed
            if original_key:
                os.environ["GLM_API_KEY"] = original_key


class TestUnifiedTool:
    """Test the unified analyze_image_with_context tool -
    the single tool for all image analysis needs"""

    @pytest.mark.asyncio
    @patch("visual_mcp.server.call_glm_vision_api")
    @patch("visual_mcp.server.prepare_image_for_api")
    async def test_analyze_image_with_context_success(self, mock_prepare, mock_glm_api):
        """Test successful image analysis with context"""
        # Mock dependencies
        mock_prepare.return_value = ("prepared_base64_data", "image/jpeg")
        mock_glm_api.return_value = "Comprehensive analysis based on user context"

        # Mock context
        mock_ctx = AsyncMock()

        result = await analyze_image_with_context(
            "test_image_data",
            "Extract and summarize all text in this document",
            ctx=mock_ctx,
        )

        assert result == "Comprehensive analysis based on user context"
        mock_prepare.assert_called_once_with("test_image_data")

        # Verify the enhanced prompt includes user context
        call_args = mock_glm_api.call_args[0]
        assert "Extract and summarize all text in this document" in call_args[1]
        assert "comprehensive visual analysis assistant" in call_args[1]
        mock_ctx.info.assert_called()

    @pytest.mark.asyncio
    @patch("visual_mcp.server.call_glm_vision_api")
    @patch("visual_mcp.server.prepare_image_for_api")
    async def test_analyze_image_with_context_diagram_analysis(
        self, mock_prepare, mock_glm_api
    ):
        """Test diagram analysis - unified tool handles specialized analysis
        through context"""
        # Mock dependencies
        mock_prepare.return_value = ("prepared_base64_data", "image/jpeg")
        mock_glm_api.return_value = (
            "Architecture diagram analysis with system flow explanation"
        )

        # Mock context
        mock_ctx = AsyncMock()

        result = await analyze_image_with_context(
            "test_diagram_data",
            "Analyze this architecture diagram and explain the system flow",
            ctx=mock_ctx,
        )

        assert result == "Architecture diagram analysis with system flow explanation"
        mock_prepare.assert_called_once_with("test_diagram_data")

        # Verify the prompt handles diagram context through user context
        call_args = mock_glm_api.call_args[0]
        assert "architecture diagram" in call_args[1].lower()
        assert "system flow" in call_args[1].lower()

    @pytest.mark.asyncio
    @patch("visual_mcp.server.call_glm_vision_api")
    @patch("visual_mcp.server.prepare_image_for_api")
    async def test_analyze_image_with_context_text_extraction(
        self, mock_prepare, mock_glm_api
    ):
        """Test text extraction - unified tool handles document analysis
        through context"""
        # Mock dependencies
        mock_prepare.return_value = ("prepared_base64_data", "image/jpeg")
        mock_glm_api.return_value = "Extracted text and summary from document"

        # Mock context
        mock_ctx = AsyncMock()

        result = await analyze_image_with_context(
            "test_document_data",
            "What does this contract say about termination clauses?",
            ctx=mock_ctx,
        )

        assert result == "Extracted text and summary from document"
        mock_prepare.assert_called_once_with("test_document_data")

        # Verify the prompt handles text extraction context through user context
        call_args = mock_glm_api.call_args[0]
        assert "termination clauses" in call_args[1]
        assert "text extraction" in call_args[1].lower()

    @pytest.mark.asyncio
    @patch("visual_mcp.server.call_glm_vision_api")
    @patch("visual_mcp.server.prepare_image_for_api")
    async def test_analyze_image_with_context_custom_max_tokens(
        self, mock_prepare, mock_glm_api
    ):
        """Test custom max tokens parameter"""
        # Mock dependencies
        mock_prepare.return_value = ("prepared_base64_data", "image/jpeg")
        mock_glm_api.return_value = "Analysis with custom token limit"

        # Mock context
        mock_ctx = AsyncMock()

        result = await analyze_image_with_context(
            "test_image_data", "Brief analysis needed", max_tokens=1000, ctx=mock_ctx
        )

        assert result == "Analysis with custom token limit"

        # Verify custom max_tokens is passed
        call_args = mock_glm_api.call_args
        assert (
            call_args[0][3] == 1000
        )  # Fourth argument should be max_tokens (after mime_type)


class TestErrorHandling:
    """Test error handling in the unified tool"""

    @pytest.mark.asyncio
    @patch("visual_mcp.server.call_glm_vision_api")
    @patch("visual_mcp.server.prepare_image_for_api")
    async def test_analyze_image_with_context_api_error(
        self, mock_prepare, mock_glm_api
    ):
        """Test image analysis with API error"""
        # Mock dependencies to raise error
        mock_prepare.return_value = ("prepared_data", "image/jpeg")
        mock_glm_api.side_effect = Exception("API Error")

        # Mock context
        mock_ctx = AsyncMock()

        result = await analyze_image_with_context(
            "test_data", "analyze this", ctx=mock_ctx
        )

        assert "Image analysis failed: API Error" in result
        mock_ctx.error.assert_called_once()

    @pytest.mark.asyncio
    @patch("visual_mcp.server.prepare_image_for_api")
    async def test_analyze_image_with_context_preparation_error(self, mock_prepare):
        """Test image analysis with image preparation error"""
        # Mock preparation to raise error
        mock_prepare.side_effect = ValueError("Invalid image data")

        # Mock context
        mock_ctx = AsyncMock()

        result = await analyze_image_with_context(
            "test_data", "analyze this", ctx=mock_ctx
        )

        assert "Image analysis failed: Invalid image data" in result
        mock_ctx.error.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
