"""
Diagnose why Places API is not being enabled
"""
import os
import sys

print("=" * 60)
print("PLACES API DIAGNOSIS")
print("=" * 60)

# Check 1: Environment variable
env_value = os.getenv("GOOGLE_PLACES_API_KEY")
print(f"\n1. Environment Variable Check:")
print(f"   GOOGLE_PLACES_API_KEY exists: {env_value is not None}")
print(f"   Value type: {type(env_value)}")
print(f"   Value repr: {repr(env_value)}")
print(f"   Value length: {len(env_value) if env_value else 0}")
print(f"   Is empty string: {env_value == ''}")
print(f"   Is 'not_required': {env_value == 'not_required'}")

# Check 2: Try to load with pydantic
print(f"\n2. Pydantic Settings Check:")
try:
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class TestSettings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=".env" if os.path.exists(".env") else None,
            env_file_encoding="utf-8",
            case_sensitive=False,
            env_ignore_empty=True,
            extra="ignore"
        )
        google_places_api_key: str | None = Field(None, env="GOOGLE_PLACES_API_KEY")

    test_settings = TestSettings()
    print(f"   Pydantic loaded value: {repr(test_settings.google_places_api_key)}")
    print(f"   Value is None: {test_settings.google_places_api_key is None}")
    print(f"   Value == 'not_required': {test_settings.google_places_api_key == 'not_required'}")

    # Check 3: The problematic condition
    print(f"\n3. GooglePlacesClient.__init__ Logic Check:")
    api_key = test_settings.google_places_api_key
    print(f"   api_key = {repr(api_key)}")
    print(f"   not api_key = {not api_key}")
    print(f"   api_key == 'not_required' = {api_key == 'not_required'}")
    print(f"   (not api_key or api_key == 'not_required') = {not api_key or api_key == 'not_required'}")

    if not api_key or api_key == "not_required":
        print(f"   ❌ ENABLED = FALSE (This is the problem!)")
    else:
        print(f"   ✅ ENABLED = TRUE")

except ImportError as e:
    print(f"   ⚠️ Cannot import pydantic_settings: {e}")
    print(f"   This is expected in development without venv")

# Check 4: .env file check
print(f"\n4. .env File Check:")
if os.path.exists(".env"):
    print(f"   .env file exists: YES")
    with open(".env", "r") as f:
        for line in f:
            if "GOOGLE_PLACES_API_KEY" in line:
                print(f"   Found line: {line.strip()}")
else:
    print(f"   .env file exists: NO")

print("\n" + "=" * 60)
print("DIAGNOSIS COMPLETE")
print("=" * 60)
