#!/usr/bin/env python3
"""
Example usage script for Visual MCP Server

This script demonstrates the power of the unified analyze_image_with_context tool.
Instead of multiple specialized tools, you get ONE tool that handles ALL image analysis
needs through natural language context. The AI figures out the best approach!
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import server
sys.path.insert(0, str(Path(__file__).parent))

from visual_mcp.server import analyze_image_with_context


def create_sample_base64_image():
    """Create a simple base64 image for demonstration"""
    # Create a minimal 1x1 pixel PNG in base64
    # This is a tiny transparent PNG
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI/hjBqQAAAAABJRU5ErkJggg=="


async def demonstrate_unified_analysis():
    """Demonstrate the unified analysis capabilities - ONE TOOL FOR EVERYTHING!"""
    print("=== Visual MCP Server - Unified Analysis Demo ===")
    print("One tool. Unlimited possibilities. The AI figures out what you need!\n")

    # Create sample base64 image data
    print("1. Preparing sample image data...")
    sample_image = create_sample_base64_image()
    print(f"   Created sample base64 image (length: {len(sample_image)} chars)")

    try:
        # Example 1: Text extraction
        print("\n2. Example: Text Extraction")
        text_analysis = await analyze_image_with_context(
            sample_image,
            user_context="Extract and summarize all text visible in this image. Focus on any document structure or key information.",
            max_tokens=2000,
        )
        print("   Result:")
        print(f"   {text_analysis[:200]}...")

        # Example 2: Diagram analysis
        print("\n3. Example: Diagram Analysis")
        diagram_analysis = await analyze_image_with_context(
            sample_image,
            user_context="This appears to be a technical diagram. Analyze the components, relationships, and explain the overall system architecture.",
            max_tokens=2500,
        )
        print("   Result:")
        print(f"   {diagram_analysis[:200]}...")

        # Example 3: General description
        print("\n4. Example: General Description")
        general_analysis = await analyze_image_with_context(
            sample_image,
            user_context="Provide a comprehensive description of what you see in this image, including colors, composition, objects, and any notable features.",
            max_tokens=1500,
        )
        print("   Result:")
        print(f"   {general_analysis[:200]}...")

        # Example 4: Problem identification
        print("\n5. Example: Problem Identification")
        problem_analysis = await analyze_image_with_context(
            sample_image,
            user_context="Look at this image and identify any issues, errors, or areas that need improvement. Explain what's wrong and suggest fixes.",
            max_tokens=2000,
        )
        print("   Result:")
        print(f"   {problem_analysis[:200]}...")

        # Example 5: Educational content
        print("\n6. Example: Educational Analysis")
        educational_analysis = await analyze_image_with_context(
            sample_image,
            user_context="Explain this image as if teaching someone who has never seen this before. Break it down step by step.",
            max_tokens=2500,
        )
        print("   Result:")
        print(f"   {educational_analysis[:200]}...")

    except Exception as e:
        print(f"   Error during demonstration: {e}")
        print("   Note: This is expected if GLM_API_KEY is not set")

    print("\n7. Demo complete")


async def demonstrate_context_variations():
    """Demonstrate how different contexts produce different results"""
    print("\n=== Context Variations Demo ===")

    sample_image = create_sample_base64_image()

    contexts = [
        "Quick summary in 1-2 sentences",
        "Detailed technical analysis for developers",
        "Explain this to a non-technical person",
        "Extract only the text content, no descriptions",
        "What's the most important thing to understand here?",
        "Compare and contrast elements in this image",
    ]

    try:
        for i, context in enumerate(contexts, 1):
            print(f"\n{i}. Context: '{context}'")
            result = await analyze_image_with_context(
                sample_image, user_context=context, max_tokens=1000
            )
            print(f"   Result: {result[:100]}...")
    except Exception as e:
        print(f"   Error: {e}")


async def main():
    """Main demonstration function"""
    print("Visual MCP Server - Unified Analysis Tool")
    print("=" * 50)

    # Check if API key is set
    api_key = os.getenv("GLM_API_KEY")
    if not api_key:
        print("WARNING: GLM_API_KEY environment variable not set")
        print("The demonstration will show the functionality but API calls will fail.")
        print("Set your API key with: export GLM_API_KEY='your-api-key'\n")
    else:
        print("GLM_API_KEY is set - ready for API calls\n")

    print("🎯 The Power of ONE Unified Tool:")
    print("• Just ONE tool: analyze_image_with_context")
    print("• NO need to choose between specialized tools")
    print("• AI figures out the best approach from your context")
    print("• Natural, flexible, and powerful usage\n")

    # Run demonstrations
    await demonstrate_unified_analysis()
    await demonstrate_context_variations()

    print("\n=== Demo Complete ===")
    print("\n🚀 Why This Approach is Brilliant:")
    print("Instead of 5 different tools, you have ONE smart tool that:")
    print("• Adapts to ANY image analysis need")
    print("• Understands natural language context")
    print("• Lets the AI choose the best analysis method")
    print("\n💡 Example Contexts (all use the SAME tool):")
    print("• 'Extract and summarize all text in this contract'")
    print("• 'Analyze this architecture diagram and explain data flow'")
    print("• 'What safety issues do you see in this workplace photo?'")
    print("• 'Explain this mathematical formula step by step'")
    print("• 'Compare the design elements in this UI mockup'")
    print("• 'Identify bugs in this code screenshot'")
    print("• 'Describe this medical image for a patient'")
    print("• ANYTHING else you can imagine!\n")

    print("🎯 Simple Usage:")
    print("1. Set your GLM_API_KEY environment variable")
    print("2. Run: uv run mcp dev server.py")
    print("3. Use: analyze_image_with_context(image, 'what you want to know')")
    print("4. That's it! The AI handles the rest.")


if __name__ == "__main__":
    asyncio.run(main())
