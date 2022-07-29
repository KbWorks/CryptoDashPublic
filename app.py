from distutils.command.config import config
import html
import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session  # https://pythonhosted.org/Flask-Session
import msal
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from intrade import ActiveTrade
from Wallet import Walletbalance
from spfunctions import Graph
from pybitlib import mainfunctions
from pybit import usdt_perpetual,inverse_perpetual
import app_config 

app = Flask(__name__)
app.config.from_object(app_config)
Session(app)

# This section is needed for url_for("foo", _external=True) to automatically
# generate http scheme when this sample is running on localhost,
# and to generate https scheme when it is deployed behind reversed proxy.
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route("/")
def index():
    if not session.get("user"):
        return redirect(url_for("login"))
    return render_template('index.html', user=session["user"], version=msal.__version__)

@app.route("/login")
def login():
    # Technically we could use empty list [] as scopes to do just sign in,
    # here we choose to also collect end user consent upfront
    session["flow"] = _build_auth_code_flow(scopes=["User.ReadBasic.All"])#app_config.SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)

@app.route("/getAToken")#app_config.REDIRECT_PATH)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()  # Wipe out user and its token cache from session
    return redirect(  # Also logout from your tenant's web session
        app_config.AUTHORITY + "/oauth2/v2.0/logout" +
        "?post_logout_redirect_uri=" + url_for("index", _external=True))
@app.route("/dashboard")
def dashboard():
    token = _get_token_from_cache(["User.ReadBasic.All"])#app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    #credential = app_config._credential #DefaultAzureCredential()
    secret_client = SecretClient(vault_url=app_config.KEYVAULT_URI, credential=app_config._credential)
    key = secret_client.get_secret("appid")
    apisecret=secret_client.get_secret("spkey") #secret_client.get_secret("spsecret")
    tenantid=secret_client.get_secret("tenantid")
    listitem= Graph(key,apisecret,tenantid)
    keys= listitem.get_accounts()
    avtivetrads=[]
    walletbalances=[]
    for k in keys['value']:
      account=""
      api_key=""
      api_secret=""
      accountname=k['fields']['Title']
      api_keyname=k['fields']['keyname']
      api_secretname=k['fields']['secretname']
      key = secret_client.get_secret(api_keyname)
      apisecret=secret_client.get_secret(api_secretname)
      if(accountname=="kbmain"):
        session=startsession(key.value,apisecret.value,True)
        openpos=mainfunctions.getopenposition(mainfunctions,session,accountname)
        if(openpos!=[]):
          for openp in openpos:
            avtivetrads.append( openp)
      session=startsession(key.value,apisecret.value,False)
      openpos=[]
      openpos=mainfunctions.getopenposition(mainfunctions,session,accountname)
      if(openpos!=[]):
          for openp in openpos:
            avtivetrads.append( openp)
      balances =mainfunctions.getbalance(mainfunctions,session,accountname)
      if(balances!=[]):
        for bal in balances:
          walletbalances.append(bal)
    #print(walletbalances)
   # print(avtivetrads)
    return render_template('dashboard.html', result=walletbalances , actr=avtivetrads)
@app.route("/graphcall")
def graphcall():
    token = _get_token_from_cache(["User.ReadBasic.All"])#app_config.SCOPE)
    if not token:
        return redirect(url_for("login"))
    graph_data = requests.get(  # Use token to call downstream service
        'https://graph.microsoft.com/v1.0/users',
        headers={'Authorization': 'Bearer ' + token['access_token']},
        ).json()
    return render_template('display.html', result=graph_data)
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

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def _build_msal_app(cache=None, authority=None):
   # credential = app_config._credential #DefaultAzureCredential()
    secret_client = SecretClient(vault_url=app_config.KEYVAULT_URI, credential=app_config._credential)
    key = secret_client.get_secret("appid")
    apisecret=secret_client.get_secret("spkey") #secret_client.get_secret("spsecret")
    tenantid=secret_client.get_secret("tenantid").value
    tenantid=f'https://login.microsoftonline.com/{tenantid}'
    return msal.ConfidentialClientApplication(
        key.value, authority=authority or tenantid,client_credential=apisecret.value,token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

def _get_token_from_cache(scope=None):
    cache = _load_cache()  # This web app maintains one cache per session
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

app.jinja_env.globals.update(_build_auth_code_flow=_build_auth_code_flow)  # Used in template

if __name__ == "__main__":
    app.run()

