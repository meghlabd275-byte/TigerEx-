from kucoin.client import Client
from .exchange_connector import ExchangeConnector

class KuCoinConnector(ExchangeConnector):
    """
    A connector for the KuCoin exchange.
    """

    def __init__(self, api_key: str, api_secret: str, api_passphrase: str):
        super().__init__(api_key, api_secret)
        self.client = Client(api_key, api_secret, api_passphrase)

    async def get_order_book(self, symbol: str):
        """
        Get the order book for a given symbol.
        """
        return self.client.get_order_book(symbol)

    async def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        """
        Place an order on the exchange.
        """
        if order_type == 'limit':
            return self.client.create_limit_order(
                symbol=symbol,
                side=side,
                size=quantity,
                price=price
            )
        elif order_type == 'market':
            return self.client.create_market_order(
                symbol=symbol,
                side=side,
                size=quantity
            )

    async def get_balance(self):
        """
        Get the account balance.
        """
        return self.client.get_accounts()
