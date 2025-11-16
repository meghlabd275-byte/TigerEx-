from abc import ABC, abstractmethod

class ExchangeConnector(ABC):
    """
    An abstract base class for connecting to external cryptocurrency exchanges.
    """

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret

    @abstractmethod
    async def get_order_book(self, symbol: str):
        """
        Get the order book for a given symbol.
        """
        pass

    @abstractmethod
    async def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        """
        Place an order on the exchange.
        """
        pass

    @abstractmethod
    async def get_balance(self):
        """
        Get the account balance.
        """
        pass
