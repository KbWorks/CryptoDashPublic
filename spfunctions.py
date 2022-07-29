import json
from configparser import SectionProxy
from azure.identity import DeviceCodeCredential, ClientSecretCredential
from msgraph.core import GraphClient

class Graph:
    client_credential: ClientSecretCredential
    app_client: GraphClient
    def __init__(self, clientid,clientsecret,tenantid ):
        self.client_id = clientid
        self.client_secret=clientsecret
        self.tenant_id = tenantid
# </UserAuthConfigSnippet>
    def ensure_graph_for_app_only_auth(self):
        if not hasattr(self, 'client_credential'):
            client_id = self.client_id.value
            tenant_id = self.tenant_id.value
            client_secret = self.client_secret.value
            self.client_credential = ClientSecretCredential(tenant_id, client_id, client_secret)
        if not hasattr(self, 'app_client'):
            self.app_client = GraphClient(credential=self.client_credential,
                                          scopes=['https://graph.microsoft.com/.default'])
    # </AppOnyAuthConfigSnippet>

    def get_accounts(self):
        self.ensure_graph_for_app_only_auth()

        endpoint = '/sites/root/lists/21699ef9-82ed-4099-821a-e0a770b0cabf/items'
        select = 'Title'
        request_url = f'{endpoint}?expand=fields(select=title,keyname,secretname,coin)' 

        accounts_response = self.app_client.get(request_url)
        return accounts_response.json()
  