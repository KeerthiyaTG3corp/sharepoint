from auth_delegated import get_access_token

print("Trying login…")
token = get_access_token()
print("TOKEN (first 30 chars):", token[:30])
