from binance.client import Client
from .exchange_connector import ExchangeConnector

class BinanceConnector(ExchangeConnector):
    """
    A connector for the Binance exchange.
    """

    def __init__(self, api_key: str, api_secret: str):
        super().__init__(api_key, api_secret)
        self.client = Client(api_key, api_secret)

    async def get_order_book(self, symbol: str):
        """
        Get the order book for a given symbol.
        """
        return self.client.get_order_book(symbol=symbol)

    async def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        """
        Place an order on the exchange.
        """
        if order_type == 'limit':
            return self.client.order_limit(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price
            )
        elif order_type == 'market':
            return self.client.order_market(
                symbol=symbol,
                side=side,
                quantity=quantity
            )

    async def get_balance(self):
        """
        Get the account balance.
        """
        return self.client.get_account()
