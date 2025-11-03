#!/usr/bin/env python3
"""
调试 Responses API 返回结构
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from openai import AsyncOpenAI

async def debug_responses_api():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found")
        return

    client = AsyncOpenAI(api_key=api_key)

    print("🔍 Testing Responses API with simple query...")
    print("="*60)

    response = await client.responses.create(
        model="gpt-5-mini",
        tools=[{"type": "web_search"}],
        input="Search for patient reviews about Dr Tang Boon Nee in Malaysia. Find any reviews from Facebook or forums."
    )

    print(f"\n📦 Response object: {response}")
    print(f"\n🔍 Response type: {type(response)}")
    print(f"\n🔍 Has 'output' attribute: {hasattr(response, 'output')}")

    if hasattr(response, 'output'):
        print(f"\n📦 Output object: {response.output}")
        print(f"🔍 Output type: {type(response.output)}")
        print(f"🔍 Has 'messages' attribute: {hasattr(response.output, 'messages')}")

        if hasattr(response.output, 'messages'):
            messages = response.output.messages
            print(f"\n📝 Number of messages: {len(messages)}")

            for i, msg in enumerate(messages):
                print(f"\n--- Message {i+1} ---")
                print(f"Message type: {type(msg)}")
                print(f"Message: {msg}")
                print(f"Has 'content': {hasattr(msg, 'content')}")
                print(f"Has 'role': {hasattr(msg, 'role')}")

                if hasattr(msg, 'role'):
                    print(f"Role: {msg.role}")

                if hasattr(msg, 'content'):
                    content = msg.content
                    print(f"Content type: {type(content)}")
                    print(f"Content length: {len(content) if hasattr(content, '__len__') else 'N/A'}")

                    if isinstance(content, list):
                        for j, block in enumerate(content):
                            print(f"\n  --- Content Block {j+1} ---")
                            print(f"  Block type: {type(block)}")
                            print(f"  Block: {block}")

                            if hasattr(block, 'text'):
                                print(f"  Text: {block.text[:200]}...")

                            if hasattr(block, 'annotations'):
                                print(f"  Has annotations: {len(block.annotations)}")
                    else:
                        print(f"  Content (string): {content[:200]}...")

    # Print the raw response structure
    print("\n" + "="*60)
    print("📋 Full response structure:")
    print("="*60)
    print(response.model_dump_json(indent=2) if hasattr(response, 'model_dump_json') else response)

if __name__ == "__main__":
    asyncio.run(debug_responses_api())
