import requests
from auth_delegated import get_access_token
import config

GRAPH = "https://graph.microsoft.com/v1.0"

def get_site():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Resolve using hostname + site name (no admin needed)
    url = f"{GRAPH}/sites/{config.SITE_HOSTNAME}:/sites/{config.SITE_NAME}"
    print("Trying:", url)

    r = requests.get(url, headers=headers)
    print("Status:", r.status_code)
    print("Response:", r.text)

    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("Cannot access the site. Check SITENAME/host.")

if __name__ == "__main__":
    site = get_site()
    print("SITE ID:", site["id"])
    print("WEB URL:", site["webUrl"])
