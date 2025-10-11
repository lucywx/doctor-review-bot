#!/usr/bin/env python3
"""
Test user approval system
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.models.user_approval import user_approval_manager

async def test_approval_flow():
    """Test the approval workflow"""

    test_user = "+60123456789"
    admin = "+8613800138000"

    print("=" * 80)
    print("Testing User Approval System")
    print("=" * 80)

    # Test 1: New user (should be denied)
    print("\n1. Testing new user access...")
    is_approved = await user_approval_manager.is_user_approved(test_user)
    print(f"   New user approved: {is_approved}")
    assert not is_approved, "New user should NOT be approved"
    print("   ✅ PASS: New user correctly denied")

    # Test 2: Admin is always approved
    print("\n2. Testing admin access...")
    is_admin_approved = await user_approval_manager.is_user_approved(admin)
    print(f"   Admin approved: {is_admin_approved}")
    assert is_admin_approved, "Admin should ALWAYS be approved"
    print("   ✅ PASS: Admin correctly approved")

    # Test 3: Check pending users
    print("\n3. Checking pending users...")
    pending = await user_approval_manager.get_pending_users()
    print(f"   Pending users: {len(pending)}")
    for user in pending:
        print(f"     - {user['phone_number']}")
    print("   ✅ PASS: Pending list retrieved")

    # Test 4: Approve user
    print("\n4. Approving test user...")
    success = await user_approval_manager.approve_user(test_user)
    print(f"   Approval success: {success}")
    assert success, "Approval should succeed"
    print("   ✅ PASS: User approved successfully")

    # Test 5: Check approved user
    print("\n5. Checking approved user access...")
    is_now_approved = await user_approval_manager.is_user_approved(test_user)
    print(f"   User now approved: {is_now_approved}")
    assert is_now_approved, "User should be approved now"
    print("   ✅ PASS: Approved user has access")

    # Test 6: Reject user
    print("\n6. Rejecting user...")
    success = await user_approval_manager.reject_user(test_user)
    print(f"   Rejection success: {success}")
    assert success, "Rejection should succeed"
    print("   ✅ PASS: User rejected successfully")

    # Test 7: Check rejected user
    print("\n7. Checking rejected user access...")
    is_still_approved = await user_approval_manager.is_user_approved(test_user)
    print(f"   User still approved: {is_still_approved}")
    assert not is_still_approved, "Rejected user should NOT have access"
    print("   ✅ PASS: Rejected user denied access")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_approval_flow())
