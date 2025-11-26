# auth_delegated.py
import msal
import config
import os
import json

CACHE_FILE = "token_cache.json"

def load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())
    return cache

def save_cache(cache):
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())

def get_access_token():
    cache = load_cache()

    app = msal.PublicClientApplication(
        client_id=config.CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{config.TENANT_ID}",
        token_cache=cache
    )

    # 1️⃣ Try silent login first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(config.SCOPE, account=accounts[0])
        if result and "access_token" in result:
            save_cache(cache)
            return result["access_token"]

    # 2️⃣ If silent login failed → do device-code login ONCE
    flow = app.initiate_device_flow(scopes=config.SCOPE)
    if "user_code" not in flow:
        raise Exception("Device flow failed:", flow)

    print("\n📌 DEVICE LOGIN REQUIRED (Only one-time)")
    print("👉 Open:", flow["verification_uri"])
    print("👉 Enter code:", flow["user_code"], "\n")

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        save_cache(cache)
        return result["access_token"]

    raise Exception("Token acquisition failed:", result)
