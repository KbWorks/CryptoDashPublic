
class Walletbalance:
    def __init__(self,account,Symbol,walletbalance,realisedpnl,cumrealisedpnl):
        self._account=account
        self._Symbol=Symbol
        self._walletbalance=walletbalance
        self._realisedpnl=realisedpnl
        self._cumrealisedpnl=cumrealisedpnl

    def walletbalance(self):
        return self._walletbalance