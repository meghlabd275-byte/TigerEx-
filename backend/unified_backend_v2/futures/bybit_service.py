from bybit import BybitSync

class BybitService:
    def __init__(self, api_key: str, api_secret: str):
        self.client = BybitSync(api_key=api_key, api_secret=api_secret)

    def get_server_time(self):
        return self.client.fetch_server_time()

    def get_order_book(self, symbol: str):
        return self.client.fetch_order_book(symbol)

    def create_order(self, symbol: str, type: str, side: str, amount: float, price: float):
        return self.client.create_order(symbol, type, side, amount, price)

if __name__ == '__main__':
    # This is for testing purposes only.
    # In a real application, the API key and secret should be stored securely.
    bybit_service = BybitService(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET")

    # Example usage:
    # server_time = bybit_service.get_server_time()
    # print(f"Bybit server time: {server_time}")

    # order_book = bybit_service.get_order_book("BTC/USDT")
    # print(f"BTC/USDT order book: {order_book}")
