# config.py

# Azure App Registration
CLIENT_ID = "35df2ca6-0e59-4f04-a48c-37a9138e4b2b"
TENANT_ID = "767af4fd-29cb-4f6e-9539-8020b3ae3d4e"

# Delegated permissions (NO admin approval needed)
SCOPE = ["User.Read", "Files.ReadWrite"]

# Device Code Redirect
REDIRECT_URI = "https://login.microsoftonline.com/common/oauth2/nativeclient"

# SharePoint site you own
SITE_HOSTNAME = "g3cyberspace3.sharepoint.com"   # your tenant domain
SITE_NAME = "Demosite"                          # the site name after /sites/

# Leave SITE_ID empty unless you know your site ID
SITE_ID = None

# Local DB for MCP metadata
DB_PATH = "mcp_metadata.db"
