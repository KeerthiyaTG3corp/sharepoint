import requests
from auth_delegated import get_access_token
from discover_site import get_site
import config

GRAPH = "https://graph.microsoft.com/v1.0"

def get_drives():
    site = get_site()
    site_id = site["id"]

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    url = f"{GRAPH}/sites/{site_id}/drives"
    print("GET", url)

    r = requests.get(url, headers=headers)
    print("Status:", r.status_code)
    print("Response:", r.text)

    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    drives = get_drives()
    for d in drives["value"]:
        print("DRIVE NAME:", d["name"])
        print("DRIVE ID:", d["id"])
        print("-----")
