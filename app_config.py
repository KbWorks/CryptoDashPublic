import os
from azure.identity import ClientSecretCredential
#CLIENT_SECRET = "Enter_the_Client_Secret_Here" # Placeholder - for use ONLY during testing.
# In a production app, we recommend you use a more secure method of storing your secret,
# like Azure Key Vault. Or, use an environment variable as described in Flask's documentation:
# https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-environment-variables
TENANTID=os.getenv("AZURE_TENANT_ID")
AUTHORITY = f'https://login.microsoftonline.com/{TENANTID}'
if not AUTHORITY:
  raise ValueError("Need to define AUTHORITY environment variable")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
if not CLIENT_ID:
  raise ValueError("Need to define CLIENT_ID environment variable")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
if not CLIENT_SECRET:
  raise ValueError("Need to define CLIENT_SECRET environment variable")
_credential=ClientSecretCredential(
  tenant_id=TENANTID,
  client_id=CLIENT_ID,
  client_secret=CLIENT_SECRET
)
KEYVAULT_NAME=os.getenv("AZURE_KEYVAULT_NAME","")
KEYVAULT_URI=f'https://{KEYVAULT_NAME}.vault.azure.net/'



REDIRECT_PATH = "/getAToken"  # Used for forming an absolute URL to your redirect URI.
                              # The absolute URL must match the redirect URI you set
                              # in the app's registration in the Azure portal.

# You can find more Microsoft Graph API endpoints from Graph Explorer
# https://developer.microsoft.com/en-us/graph/graph-explorer
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'  # This resource requires no admin consent

# You can find the proper permission names from this document
# https://docs.microsoft.com/en-us/graph/permissions-reference
SCOPE = ["User.ReadBasic.All"]

SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session
