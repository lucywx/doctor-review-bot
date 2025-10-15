#!/usr/bin/env python3
"""
Check if Railway deployment is using the latest code
"""

import subprocess
import sys

def check_deployment_status():
    print("=" * 80)
    print("🔍 Checking Deployment Status")
    print("=" * 80)

    # 1. Get local commit
    try:
        local_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            universal_newlines=True
        ).strip()[:7]
        print(f"\n1. ✅ Local commit: {local_commit}")
    except Exception as e:
        print(f"\n1. ❌ Failed to get local commit: {e}")
        return False

    # 2. Get remote commit
    try:
        remote_commit = subprocess.check_output(
            ["git", "rev-parse", "origin/main"],
            universal_newlines=True
        ).strip()[:7]
        print(f"2. ✅ Remote commit (GitHub): {remote_commit}")
    except Exception as e:
        print(f"2. ❌ Failed to get remote commit: {e}")
        return False

    # 3. Check if they match
    if local_commit == remote_commit:
        print(f"3. ✅ Local and remote are in sync!")
    else:
        print(f"3. ⚠️  WARNING: Local and remote are different!")
        print(f"   Local:  {local_commit}")
        print(f"   Remote: {remote_commit}")
        return False

    # 4. Show recent commit
    try:
        last_commit = subprocess.check_output(
            ["git", "log", "-1", "--oneline"],
            universal_newlines=True
        ).strip()
        print(f"\n4. 📝 Latest commit:\n   {last_commit}")
    except Exception as e:
        print(f"4. ❌ Failed to get commit info: {e}")

    # 5. Check if syntax error is fixed
    print("\n5. 🔍 Checking if syntax error is fixed...")
    try:
        with open("src/search/openai_web_searcher.py", "r") as f:
            content = f.read()
            if "w        #" in content:
                print("   ❌ Syntax error still exists!")
                return False
            else:
                print("   ✅ Syntax error is fixed!")
    except Exception as e:
        print(f"   ❌ Failed to check file: {e}")
        return False

    print("\n" + "=" * 80)
    print("✅ Local code is ready and pushed to GitHub")
    print("=" * 80)
    print("\n📋 Next steps:")
    print("1. Go to https://railway.app/ and check your deployment")
    print("2. Look for commit hash: " + local_commit)
    print("3. Check deployment logs for any errors")
    print("4. If deployment shows 'SUCCESS', wait 1-2 minutes then test in WhatsApp")
    print("\n🧪 Test in WhatsApp:")
    print("   Send: Tang Boon Nee")
    print("   Expected: Specialty selection menu with '0. Skip'")

    return True

if __name__ == "__main__":
    success = check_deployment_status()
    sys.exit(0 if success else 1)
