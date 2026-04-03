from gate import GateSync

class GateioService:
    def __init__(self, api_key: str, api_secret: str):
        self.client = GateSync(api_key=api_key, api_secret=api_secret)

    def get_server_time(self):
        return self.client.fetch_server_time()

    def get_order_book(self, symbol: str):
        return self.client.fetch_order_book(symbol)

    def create_order(self, symbol: str, type: str, side: str, amount: float, price: float):
        return self.client.create_order(symbol, type, side, amount, price)

if __name__ == '__main__':
    # This is for testing purposes only.
    # In a real application, the API key and secret should be stored securely.
    gateio_service = GateioService(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET")

    # Example usage:
    # server_time = gateio_service.get_server_time()
    # print(f"Gate.io server time: {server_time}")

    # order_book = gateio_service.get_order_book("BTC/USDT")
    # print(f"BTC/USDT order book: {order_book}")
