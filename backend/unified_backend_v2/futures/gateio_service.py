from gate import GateSync

# @file gateio_service.py
# @author TigerEx Development Team
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
def create_wallet():
    import random
    return { 'address': '0x' + ''.join([random.choice('0123456789abcdef') for _ in range(40)]), 'seed': "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area", 'ownership': 'USER_OWNS' }
