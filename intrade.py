
class ActiveTrade:
    def __init__(self,account,symbol,side,unrealisedpnl,size,entryprice,currentprice,leverage):
        self._account=account
        self._symbol=symbol
        self._side=side
        self._unrealisedpnl=unrealisedpnl
        self._size=size
        self._entryprice=entryprice
        self._leverage=leverage
        self._currentprice=currentprice
    def unrealisedpnl(self):
        return self._unrealisedpnl


