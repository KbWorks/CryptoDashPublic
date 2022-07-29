from pybit import usdt_perpetual,inverse_perpetual
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from intrade import ActiveTrade
from Wallet import Walletbalance
from spfunctions import Graph
import app_config 
#from pybit import inverse_perpetual
import json
def startsession(apikey,apisecret,inverse):
    if(inverse==False):
        USDTSession_auth = usdt_perpetual.HTTP(
            endpoint="https://api.bybit.com",
            api_key=apikey,
            api_secret=apisecret
        )
        return USDTSession_auth
    else:
     InverseSession_auth = inverse_perpetual.HTTP(
         endpoint="https://api.bybit.com",
         api_key=apikey,
         api_secret=apisecret
     )
     return InverseSession_auth
        
class mainfunctions:
 def __init__(self,activetrades,session,account,walletbalance):
        self._account=account
        self._activetrades=activetrades
        self._walletbalances=walletbalance
        self._session=session
 
 def getopenposition(self,session,account):
    input_dict =session.my_position()
    # Filter python objects with list comprehensions
    openpos=[]
    output_dict = [x for x in input_dict['result'] if x['data']['unrealised_pnl'] != 0]
    for out in output_dict:
        output=out['data']
        openpos.append( ActiveTrade(account,output['symbol'],output['side'],output['unrealised_pnl'],output['size'],output['entry_price'],"0",output['leverage']))
    self._activetrades=openpos
    # Transform python object back into json
  #  output_json = json.dumps(output_dict)
    return self._activetrades
 def getbalance(self,session,account):
    balances=[]
    Balance_dict= session.get_wallet_balance()
    for bal in Balance_dict['result']:
       if(Balance_dict['result'][bal]['wallet_balance']!=0):
          balances.append(Walletbalance(account, bal,Balance_dict['result'][bal]['wallet_balance'],Balance_dict['result'][bal]['realised_pnl'],Balance_dict['result'][bal]['cum_realised_pnl']))
    self._walletbalances=balances
    return self._walletbalances
def concatcurrentjson(json):
    print(json)

