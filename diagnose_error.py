#!/usr/bin/env python3
"""
Diagnose the production error
"""

import asyncio
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_full_flow():
    """Test the complete flow that runs in production"""

    print("=" * 80)
    print("TESTING FULL PRODUCTION FLOW")
    print("=" * 80)

    try:
        # Step 1: Import modules
        print("\n1. Testing imports...")
        from src.search.aggregator import search_aggregator
        from src.whatsapp.formatter import format_review_response
        print("   ✅ Imports successful")

        # Step 2: Search for reviews
        print("\n2. Testing search...")
        doctor_name = "Tang Boon Nee"
        result = await search_aggregator.search_all_sources(
            doctor_id=f"test_{doctor_name.lower().replace(' ', '_')}",
            doctor_name=doctor_name
        )
        print(f"   ✅ Search completed: {result['total_count']} reviews found")

        # Step 3: Format response
        print("\n3. Testing formatter...")
        message = format_review_response(doctor_name, result['reviews'])
        print(f"   ✅ Message formatted: {len(message)} characters")
        print(f"\n   Preview:\n{message[:200]}...")

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)

        return True

    except Exception as e:
        print("\n" + "=" * 80)
        print("❌ ERROR DETECTED")
        print("=" * 80)
        print(f"\nError Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print(f"\nFull Traceback:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_flow())
    sys.exit(0 if success else 1)
