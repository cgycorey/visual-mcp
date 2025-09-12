# Claude Desktop Configuration

To integrate the Visual MCP Server with Claude Desktop, add the following configuration to your Claude Desktop settings:

## Quick Setup

### 1. Get Your GLM API Key

1. Visit [https://z.ai/model-api](https://z.ai/model-api)
2. Sign up or log in to your account
3. Navigate to the [API Keys](https://z.ai/manage-apikey/apikey-list) management page
4. Generate a new API key

### 2. Add Configuration to Claude Desktop

**Option 1: Using Claude Desktop Settings (Recommended)**

1. Open Claude Desktop Settings
2. Click on the settings icon (⚙️)
3. Go to the "Developer" tab
4. Find the "MCP Servers" section
5. Click "Edit Config" or "Add Server"
6. Add this configuration:

```json
{
  "mcpServers": {
    "visual-mcp": {
      "command": "uvx",
      "args": ["visual-mcp"],
      "env": {
        "GLM_API_KEY": "your-actual-api-key-here",
        "GLM_MODEL_NAME": "glm-4.5v",
        "GLM_API_BASE": "https://api.z.ai/api/paas/v4"
      }
    }
  }
}
```

**Option 2: Manual Config File**

Locate your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the configuration above to the existing JSON file.

### 3. Restart Claude Desktop

After adding the configuration, restart Claude Desktop for the changes to take effect.

## Advanced Configuration

### Model Configuration (Optional)

The default model is `glm-4.5v`, which supports vision capabilities. However, the server supports any OpenAI-compatible vision model:

- `glm-4.5v` - Default GLM vision model (required for GLM platform)
- **Other OpenAI-compatible vision models** - Any vision model that works with OpenAI's API format, such as:
  - GPT-4V, GPT-4 Turbo Vision, Claude 3.5 Sonnet, etc.
  - Just set the appropriate model name and API base URL

Example configuration with custom model:
```json
{
  "mcpServers": {
    "visual-mcp": {
      "command": "uvx",
      "args": ["visual-mcp"],
      "env": {
        "GLM_API_KEY": "your-actual-api-key-here",
        "GLM_MODEL_NAME": "glm-4.5v"
      }
    }
  }
}
```

### API Base URL (Optional)

The default API base URL is `https://api.z.ai/api/paas/v4` (Z.AI platform), but you can customize it:

- **For Z.AI platform**: Keep the default or remove the `GLM_API_BASE` line
- **For BigModel platform**: Set to `https://open.bigmodel.cn/api/paas/v4`
- **For OpenAI-compatible endpoints**: Set to `https://api.openai.com/v1`
- **For local models**: Set to your local model server URL

Example configuration with custom base URL:
```json
{
  "mcpServers": {
    "visual-mcp": {
      "command": "uvx",
      "args": ["visual-mcp"],
      "env": {
        "GLM_API_KEY": "your-actual-api-key-here",
        "GLM_MODEL_NAME": "glm-4.5v",
        "GLM_API_BASE": "https://api.z.ai/api/paas/v4"
      }
    }
  }
}
```

## Verification

Once configured, you can verify the integration by:

1. **Check Claude Desktop Settings**
   - The "visual-mcp" server should appear in the MCP servers list
   - It should show as "Connected" or "Active"

2. **Test in Chat**
   - Start a new chat in Claude Desktop
   - Try using the tool: "Can you analyze this image for me?"
   - Claude should have access to the `analyze_image_with_context` tool

## Usage Examples in Claude Desktop

Once integrated, you can use natural language commands like:

- "Extract and summarize all text from this screenshot"
- "Analyze this architecture diagram and explain how it works"
- "What's wrong with this code in this image?"
- "Describe this photo in detail focusing on the people"
- "Explain this mathematical formula step by step"

## Troubleshooting

### Common Issues

1. **Server Not Connecting**
   - Ensure `uv` is installed and in your PATH
   - Verify the configuration syntax is correct

2. **API Configuration Issues**
   - **API Key**: Verify your GLM API key is valid and not expired
   - **API Credits**: Ensure the API key has sufficient credits
   - **Base URL**: Verify the `GLM_API_BASE` is correct and accessible
   - **Typos**: Check for typos in both API key and base URL
   - **Format**: Ensure the base URL includes the protocol (http/https)

### Debug Mode

To enable debug logging, modify the configuration:

```json
{
  "mcpServers": {
    "visual-mcp": {
      "command": "uvx",
      "args": ["visual-mcp"],
      "env": {
        "GLM_API_KEY": "your-actual-api-key-here",
        "GLM_API_BASE": "https://api.z.ai/api/paas/v4"
      }
    }
  }
}
```

## Security Notes

- **Keep your API key secure** - Never commit it to version control
- **Use environment variables** - The configuration supports env vars for sensitive data
- **API base URL security** - Ensure your custom endpoints use HTTPS in production
- **Regular key rotation** - Consider rotating your API keys periodically
- **Monitor usage** - Keep an eye on your GLM API usage and costs
- **Endpoint validation** - Only use trusted API endpoints

## Support

If you encounter issues with the Claude Desktop integration:

1. Check the Claude Desktop logs for error messages
2. Verify your configuration syntax is correct
3. Test the server manually: `uvx visual-mcp --help`