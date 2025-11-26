# auth_delegated.py
import msal
import config

def get_access_token():
    app = msal.PublicClientApplication(
        client_id=config.CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{config.TENANT_ID}"
    )

    # Try silent login
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(config.SCOPE, account=accounts[0])
        if "access_token" in result:
            return result["access_token"]

    # Start device-code flow
    flow = app.initiate_device_flow(scopes=config.SCOPE)
    if "user_code" not in flow:
        raise Exception("Device flow failed:", flow)

    print("\n📌 DEVICE LOGIN REQUIRED")
    print("👉 Open this URL in your browser:")
    print(flow["verification_uri"])
    print("\n👉 Enter this code:")
    print(flow["user_code"])
    print()

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        return result["access_token"]

    raise Exception("Token acquisition failed:", result)
