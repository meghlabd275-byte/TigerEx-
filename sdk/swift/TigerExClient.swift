import Foundation
import CryptoKit

// TigerEx Swift SDK for iOS/macOS

public class TigerExClient {
    private let apiKey: String
    private let apiSecret: String
    private let baseURL = "https://api.tigerex.com"
    private var token: String?

    public init(apiKey: String, apiSecret: String) {
        self.apiKey = apiKey
        self.apiSecret = apiSecret
    }

    // ==================== AUTH ====================

    public func login(email: String, password: String) async throws -> LoginResponse {
        let body = ["email": email, "password": password]
        let response = try await request(method: "POST", endpoint: "/api/v1/auth/login", body: body)
        token = response["data"]["token"].stringValue
        let user = parseUser(response["data"]["user"])
        return LoginResponse(token: token!, user: user)
    }

    public func register(email: String, password: String, username: String) async throws -> User {
        let body = ["email": email, "password": password, "username": username]
        let response = try await request(method: "POST", endpoint: "/api/v1/auth/register", body: body)
        return parseUser(response["data"]["user"])
    }

    public func enable2FA() async throws -> TwoFactorResponse {
        let response = try await request(method: "POST", endpoint: "/api/v1/auth/2fa/enable", body: nil)
        return TwoFactorResponse(
            secret: response["data"]["secret"].stringValue,
            qr: response["data"]["qr"].stringValue
        )
    }

    // ==================== MARKETS ====================

    public func getMarkets() async throws -> [Market] {
        let response = try await request(method: "GET", endpoint: "/api/v1/markets", body: nil)
        let markets = response["data"]["markets"].arrayValue
        return markets.map { parseMarket($0) }
    }

    public func getMarket(symbol: String) async throws -> Market {
        let response = try await request(method: "GET", endpoint: "/api/v1/market/\(symbol)", body: nil)
        return parseMarket(response["data"]["market"])
    }

    public func getDepth(symbol: String, limit: Int = 20) async throws -> OrderBook {
        let response = try await request(method: "GET", endpoint: "/api/v1/depth/\(symbol)?limit=\(limit)", body: nil)
        return parseOrderBook(response["data"]["orderbook"])
    }

    public func getKlines(symbol: String, interval: String = "1h", limit: Int = 500) async throws -> [Kline] {
        let response = try await request(method: "GET", endpoint: "/api/v1/klines?symbol=\(symbol)&interval=\(interval)&limit=\(limit)", body: nil)
        let klines = response["data"]["klines"].arrayValue
        return klines.map { parseKline($0) }
    }

    // ==================== TRADING ====================

    public func placeOrder(_ order: OrderRequest) async throws -> Order {
        let body: [String: Any] = [
            "symbol": order.symbol,
            "side": order.side,
            "type": order.type,
            "quantity": order.quantity,
            "price": order.price
        ]
        let response = try await request(method: "POST", endpoint: "/api/v1/order", body: body)
        return parseOrder(response["data"]["order"])
    }

    public func cancelOrder(orderId: String) async throws {
        _ = try await request(method: "DELETE", endpoint: "/api/v1/order/\(orderId)", body: nil)
    }

    public func getOrders(symbol: String? = nil, status: String? = nil, limit: Int = 50) async throws -> [Order] {
        var endpoint = "/api/v1/orders?limit=\(limit)"
        if let symbol = symbol { endpoint += "&symbol=\(symbol)" }
        if let status = status { endpoint += "&status=\(status)" }
        
        let response = try await request(method: "GET", endpoint: endpoint, body: nil)
        let orders = response["data"]["orders"].arrayValue
        return orders.map { parseOrder($0) }
    }

    // ==================== FUTURES ====================

    public func openPosition(_ pos: PositionRequest) async throws -> Position {
        let body: [String: Any] = [
            "symbol": pos.symbol,
            "side": pos.side,
            "quantity": pos.quantity,
            "leverage": pos.leverage
        ]
        let response = try await request(method: "POST", endpoint: "/api/v1/futures/position", body: body)
        return parsePosition(response["data"]["position"])
    }

    public func closePosition(positionId: String) async throws {
        _ = try await request(method: "POST", endpoint: "/api/v1/futures/position/\(positionId)/close", body: nil)
    }

    public func getPositions() async throws -> [Position] {
        let response = try await request(method: "GET", endpoint: "/api/v1/futures/positions", body: nil)
        let positions = response["data"]["positions"].arrayValue
        return positions.map { parsePosition($0) }
    }

    // ==================== WALLET ====================

    public func getBalance() async throws -> [Balance] {
        let response = try await request(method: "GET", endpoint: "/api/v1/wallet/balance", body: nil)
        let balances = response["data"]["balances"].arrayValue
        return balances.map { parseBalance($0) }
    }

    public func getDepositAddress(currency: String) async throws -> DepositAddress {
        let response = try await request(method: "GET", endpoint: "/api/v1/wallet/deposit/address?currency=\(currency)", body: nil)
        return parseDepositAddress(response["data"])
    }

    public func withdraw(currency: String, amount: Double, address: String, memo: String? = nil) async throws -> String {
        var body: [String: Any] = [
            "currency": currency,
            "amount": amount,
            "address": address
        ]
        if let memo = memo { body["memo"] = memo }
        
        let response = try await request(method: "POST", endpoint: "/api/v1/wallet/withdraw", body: body)
        return response["data"]["txId"].stringValue
    }

    public func getTransactions(type: String? = nil, currency: String? = nil, limit: Int = 50) async throws -> [Transaction] {
        var endpoint = "/api/v1/wallet/transactions?limit=\(limit)"
        if let type = type { endpoint += "&type=\(type)" }
        if let currency = currency { endpoint += "&currency=\(currency)" }
        
        let response = try await request(method: "GET", endpoint: endpoint, body: nil)
        let txs = response["data"]["transactions"].arrayValue
        return txs.map { parseTransaction($0) }
    }

    // ==================== P2P ====================

    public func getP2PAds(type: String? = nil, currency: String? = nil, payment: String? = nil) async throws -> [P2PAd] {
        var endpoint = "/api/v1/p2p/ads?"
        var params: [String] = []
        if let type = type { params.append("type=\(type)") }
        if let currency = currency { params.append("currency=\(currency)") }
        if let payment = payment { params.append("paymentMethod=\(payment)") }
        endpoint += params.joined(separator: "&")
        
        let response = try await request(method: "GET", endpoint: endpoint, body: nil)
        let ads = response["data"]["ads"].arrayValue
        return ads.map { parseP2PAd($0) }
    }

    // ==================== STAKING ====================

    public func getStakingProducts() async throws -> [StakingProduct] {
        let response = try await request(method: "GET", endpoint: "/api/v1/staking/products", body: nil)
        let products = response["data"]["products"].arrayValue
        return products.map { parseStakingProduct($0) }
    }

    public func stake(productId: Int, amount: Double) async throws -> StakingPosition {
        let body: [String: Any] = ["productId": productId, "amount": amount]
        let response = try await request(method: "POST", endpoint: "/api/v1/staking/stake", body: body)
        return parseStakingPosition(response["data"]["stake"])
    }

    // ==================== COPY TRADING ====================

    public func getTopTraders() async throws -> [Trader] {
        let response = try await request(method: "GET", endpoint: "/api/v1/copy/traders", body: nil)
        let traders = response["data"]["traders"].arrayValue
        return traders.map { parseTrader($0) }
    }

    public func followTrader(traderId: Int, amount: Double) async throws {
        let body: [String: Any] = ["traderId": traderId, "amount": amount]
        _ = try await request(method: "POST", endpoint: "/api/v1/copy/follow", body: body)
    }

    // ==================== AUTO INVEST ====================

    public func createAutoInvestPlan(_ plan: AutoInvestPlan) async throws -> AutoInvestPlan {
        let body: [String: Any] = [
            "name": plan.name,
            "symbol": plan.symbol,
            "amount": plan.amount,
            "interval": plan.interval
        ]
        let response = try await request(method: "POST", endpoint: "/api/v1/autoinvest/create", body: body)
        return parseAutoInvestPlan(response["data"]["plan"])
    }

    public func getAutoInvestPlans() async throws -> [AutoInvestPlan] {
        let response = try await request(method: "GET", endpoint: "/api/v1/autoinvest/plans", body: nil)
        let plans = response["data"]["plans"].arrayValue
        return plans.map { parseAutoInvestPlan($0) }
    }

    // ==================== API KEYS ====================

    public func createAPIKey(name: String, permissions: [String]) async throws -> APIKeyResponse {
        let body: [String: Any] = ["name": name, "permissions": permissions]
        let response = try await request(method: "POST", endpoint: "/api/v1/api-key", body: body)
        return APIKeyResponse(
            apiKey: response["data"]["apiKey"].stringValue,
            apiSecret: response["data"]["apiSecret"].stringValue
        )
    }

    public func getAPIKeys() async throws -> [APIKey] {
        let response = try await request(method: "GET", endpoint: "/api/v1/api-keys", body: nil)
        let keys = response["data"]["keys"].arrayValue
        return keys.map { parseAPIKey($0) }
    }

    public func deleteAPIKey(keyId: Int) async throws {
        _ = try await request(method: "DELETE", endpoint: "/api/v1/api-key/\(keyId)", body: nil)
    }

    // ==================== HTTP REQUEST ====================

    private func request(method: String, endpoint: String, body: [String: Any]?) async throws -> [String: Any] {
        guard let url = URL(string: baseURL + endpoint) else {
            throw TigerExError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = token {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        // Add signature
        let timestamp = String(Int(Date().timeIntervalSince1970 * 1000))
        request.setValue(timestamp, forHTTPHeaderField: "X-Timestamp")

        let signatureData = method + endpoint + timestamp + (body.map { String(describing: $0) } ?? "")
        let signature = generateSignature(signatureData)
        request.setValue(signature, forHTTPHeaderField: "X-Signature")

        if let body = body {
            request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        }

        let (data, _) = try await URLSession.shared.data(for: request)
        guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw TigerExError.invalidResponse
        }

        return json
    }

    private func generateSignature(_ data: String) -> String {
        let key = SymmetricKey(data: Data(apiSecret.utf8))
        let signature = HMAC<SHA256>.authenticationCode(for: Data(data.utf8), using: key)
        return Data(signature).map { String(format: "%02x", $0) }.joined()
    }

    // ==================== PARSERS ====================

    private func parseUser(_ json: [String: Any]) -> User {
        return User(
            id: json["id"] as? Int ?? 0,
            email: json["email"] as? String ?? "",
            username: json["username"] as? String ?? "",
            kycStatus: json["kycStatus"] as? String ?? "none"
        )
    }

    private func parseMarket(_ json: JSON) -> Market {
        return Market(
            symbol: json["symbol"].stringValue,
            baseAsset: json["baseAsset"].stringValue,
            quoteAsset: json["quoteAsset"].stringValue,
            price: json["price"].doubleValue,
            change24h: json["priceChange24h"].doubleValue,
            volume24h: json["volume24h"].doubleValue,
            maxLeverage: json["maxLeverage"].intValue
        )
    }

    private func parseOrderBook(_ json: JSON) -> OrderBook {
        let bids = parseLevels(json["bids"])
        let asks = parseLevels(json["asks"])
        return OrderBook(bids: bids, asks: asks)
    }

    private func parseLevels(_ json: JSON) -> [PriceLevel] {
        guard let array = json.array else { return [] }
        return array.map { PriceLevel(price: $0["price"].doubleValue, quantity: $0["quantity"].doubleValue) }
    }

    private func parseKline(_ json: JSON) -> Kline {
        return Kline(
            time: Int64(json["time"].doubleValue),
            open: json["open"].doubleValue,
            high: json["high"].doubleValue,
            low: json["low"].doubleValue,
            close: json["close"].doubleValue,
            volume: json["volume"].doubleValue
        )
    }

    private func parseOrder(_ json: JSON) -> Order {
        return Order(
            orderId: json["orderId"].stringValue,
            symbol: json["symbol"].stringValue,
            side: json["side"].stringValue,
            type: json["type"].stringValue,
            quantity: json["quantity"].doubleValue,
            price: json["price"].doubleValue,
            status: json["status"].stringValue
        )
    }

    private func parsePosition(_ json: JSON) -> Position {
        return Position(
            positionId: json["positionId"].stringValue,
            symbol: json["symbol"].stringValue,
            side: json["side"].stringValue,
            quantity: json["quantity"].doubleValue,
            leverage: json["leverage"].intValue,
            margin: json["margin"].doubleValue,
            pnl: json["pnl"].doubleValue
        )
    }

    private func parseBalance(_ json: JSON) -> Balance {
        return Balance(
            currency: json["currency"].stringValue,
            balance: json["balance"].doubleValue,
            availableBalance: json["availableBalance"].doubleValue,
            lockedBalance: json["lockedBalance"].doubleValue
        )
    }

    private func parseDepositAddress(_ json: JSON) -> DepositAddress {
        return DepositAddress(
            currency: json["currency"].stringValue,
            address: json["address"].stringValue,
            tag: json["tag"].string
        )
    }

    private func parseTransaction(_ json: JSON) -> Transaction {
        return Transaction(
            id: json["id"].intValue,
            type: json["type"].stringValue,
            currency: json["currency"].stringValue,
            amount: json["amount"].doubleValue,
            status: json["status"].stringValue
        )
    }

    private func parseP2PAd(_ json: JSON) -> P2PAd {
        return P2PAd(
            id: json["id"].intValue,
            username: json["username"].stringValue,
            type: json["type"].stringValue,
            currency: json["currency"].stringValue,
            price: json["price"].doubleValue,
            minAmount: json["minAmount"].doubleValue,
            maxAmount: json["maxAmount"].doubleValue,
            paymentMethod: json["paymentMethod"].stringValue
        )
    }

    private func parseStakingProduct(_ json: JSON) -> StakingProduct {
        return StakingProduct(
            id: json["id"].intValue,
            name: json["name"].stringValue,
            currency: json["currency"].stringValue,
            apy: json["apy"].doubleValue,
            lockPeriod: json["lockPeriod"].intValue
        )
    }

    private func parseStakingPosition(_ json: JSON) -> StakingPosition {
        return StakingPosition(
            id: json["id"].intValue,
            productId: json["productId"].intValue,
            amount: json["amount"].doubleValue,
            startAt: json["startAt"].stringValue,
            endAt: json["endAt"].stringValue,
            status: json["status"].stringValue
        )
    }

    private func parseTrader(_ json: JSON) -> Trader {
        return Trader(
            id: json["id"].intValue,
            username: json["username"].stringValue,
            pnl: json["pnl"].doubleValue,
            trades: json["trades"].intValue,
            winRate: json["winRate"].doubleValue,
            followers: json["followers"].intValue
        )
    }

    private func parseAutoInvestPlan(_ json: JSON) -> AutoInvestPlan {
        return AutoInvestPlan(
            id: json["id"].intValue,
            name: json["name"].stringValue,
            symbol: json["symbol"].stringValue,
            amount: json["amount"].doubleValue,
            interval: json["interval"].stringValue,
            status: json["status"].stringValue
        )
    }

    private func parseAPIKey(_ json: JSON) -> APIKey {
        return APIKey(
            id: json["id"].intValue,
            keyName: json["keyName"].stringValue,
            apiKey: json["apiKey"].stringValue,
            permissions: json["permissions"].stringValue,
            isActive: json["isActive"].boolValue
        )
    }
}

// ==================== ERRORS ====================

public enum TigerExError: Error {
    case invalidURL
    case invalidResponse
    case authenticationRequired
}

// ==================== DATA CLASSES ====================

public struct LoginResponse {
    public let token: String
    public let user: User
}

public struct User {
    public let id: Int
    public let email: String
    public let username: String
    public let kycStatus: String
}

public struct TwoFactorResponse {
    public let secret: String
    public let qr: String
}

public struct Market {
    public let symbol: String
    public let baseAsset: String
    public let quoteAsset: String
    public let price: Double
    public let change24h: Double
    public let volume24h: Double
    public let maxLeverage: Int
}

public struct OrderBook {
    public let bids: [PriceLevel]
    public let asks: [PriceLevel]
}

public struct PriceLevel {
    public let price: Double
    public let quantity: Double
}

public struct Kline {
    public let time: Int64
    public let open: Double
    public let high: Double
    public let low: Double
    public let close: Double
    public let volume: Double
}

public struct Order {
    public let orderId: String
    public let symbol: String
    public let side: String
    public let type: String
    public let quantity: Double
    public let price: Double
    public let status: String
}

public struct OrderRequest {
    public var symbol: String = ""
    public var side: String = ""
    public var type: String = "limit"
    public var quantity: Double = 0
    public var price: Double = 0
}

public struct Position {
    public let positionId: String
    public let symbol: String
    public let side: String
    public let quantity: Double
    public let leverage: Int
    public let margin: Double
    public let pnl: Double
}

public struct PositionRequest {
    public var symbol: String = ""
    public var side: String = ""
    public var quantity: Double = 0
    public var leverage: Int = 1
}

public struct Balance {
    public let currency: String
    public let balance: Double
    public let availableBalance: Double
    public let lockedBalance: Double
}

public struct DepositAddress {
    public let currency: String
    public let address: String
    public let tag: String?
}

public struct Transaction {
    public let id: Int
    public let type: String
    public let currency: String
    public let amount: Double
    public let status: String
}

public struct P2PAd {
    public let id: Int
    public let username: String
    public let type: String
    public let currency: String
    public let price: Double
    public let minAmount: Double
    public let maxAmount: Double
    public let paymentMethod: String
}

public struct StakingProduct {
    public let id: Int
    public let name: String
    public let currency: String
    public let apy: Double
    public let lockPeriod: Int
}

public struct StakingPosition {
    public let id: Int
    public let productId: Int
    public let amount: Double
    public let startAt: String
    public let endAt: String
    public let status: String
}

public struct Trader {
    public let id: Int
    public let username: String
    public let pnl: Double
    public let trades: Int
    public let winRate: Double
    public let followers: Int
}

public struct AutoInvestPlan {
    public var id: Int = 0
    public var name: String = ""
    public var symbol: String = ""
    public var amount: Double = 0
    public var interval: String = "daily"
    public var status: String = "active"
}

public struct APIKeyResponse {
    public let apiKey: String
    public let apiSecret: String
}

public struct APIKey {
    public let id: Int
    public let keyName: String
    public let apiKey: String
    public let permissions: String
    public let isActive: Bool
}

// JSON Helper
public struct JSON {
    private let json: Any

    init(_ json: Any) {
        self.json = json
    }

    public var stringValue: String { (json as? String) ?? "" }
    public var intValue: Int { (json as? Int) ?? 0 }
    public var doubleValue: Double { (json as? Double) ?? 0 }
    public var boolValue: Bool { (json as? Bool) ?? false }
    public var arrayValue: [JSON] { (json as? [Any])?.map { JSON($0) } ?? [] }
    public var string: String? { json as? String }

    public subscript(key: String) -> JSON {
        guard let dict = json as? [String: Any] else { return JSON("") }
        return JSON(dict[key] ?? "")
    }
}
// ==================== WALLET WITH 24-WORD SEED ====================
public struct Wallet: Codable {
    let type: String
    let chain: String
    let seedPhrase: String?
    let backupKey: String?
    let ownership: String
    let fullControl: Bool
    let address: String
    let privateKey: String?
}

public func createWallet(type: String) -> Wallet? {
    let req: [String: Any] = ["type": type]
    guard let resp = try? client.request("POST", "/api/wallet/create", req),
          let wallet = resp["wallet"] as? [String: Any] else { return nil }
    return try? JSONDecoder().decode(Wallet.self, from: JSONSerialization.data(withJSONObject: wallet))
}

public func listWallets() -> [String: Wallet]? {
    guard let resp = try? client.request("GET", "/api/wallet/list", nil),
          let wallets = resp["wallets"] as? [String: Any] else { return nil }
    return try? JSONDecoder().decode([String: Wallet].self, from: JSONSerialization.data(withJSONObject: wallets))
}

// ==================== DEFI ====================
public struct DefiResponse: Codable {
    let txHash: String?
    let poolId: String?
    let stakeId: String?
    let tokenAddress: String?
    let apy: Double?
    let message: String
}

public func defiSwap(tokenIn: String, tokenOut: String, amount: Double) -> DefiResponse? {
    let req: [String: Any] = ["tokenIn": tokenIn, "tokenOut": tokenOut, "amount": amount]
    guard let resp = try? client.request("POST", "/api/defi/swap", req),
          let data = try? JSONEncoder().encode(resp),
          let defi = try? JSONDecoder().decode(DefiResponse.self, from: data) else { return nil }
    return defi
}

public func defiCreatePool(tokenA: String, tokenB: String) -> DefiResponse? {
    let req: [String: Any] = ["tokenA": tokenA, "tokenB": tokenB]
    guard let resp = try? client.request("POST", "/api/defi/pool", req) else { return nil }
    return try? JSONDecoder().decode(DefiResponse.self, from: JSONSerialization.data(withJSONObject: resp))
}

public func defiStake(token: String, amount: Double, duration: Int) -> DefiResponse? {
    let req: [String: Any] = ["token": token, "amount": amount, "duration": duration]
    guard let resp = try? client.request("POST", "/api/defi/stake", req) else { return nil }
    return try? JSONDecoder().decode(DefiResponse.self, from: JSONSerialization.data(withJSONObject: resp))
}

public func defiBridge(fromChain: String, toChain: String, token: String, amount: Double) -> DefiResponse? {
    let req: [String: Any] = ["fromChain": fromChain, "toChain": toChain, "token": token, "amount": amount]
    guard let resp = try? client.request("POST", "/api/defi/bridge", req) else { return nil }
    return try? JSONDecoder().decode(DefiResponse.self, from: JSONSerialization.data(withJSONObject: resp))
}

public func defiCreateToken(name: String, symbol: String, supply: Double) -> DefiResponse? {
    let req: [String: Any] = ["name": name, "symbol": symbol, "supply": supply]
    guard let resp = try? client.request("POST", "/api/defi/create-token", req) else { return nil }
    return try? JSONDecoder().decode(DefiResponse.self, from: JSONSerialization.data(withJSONObject: resp))
}

// ==================== GAS FEES ====================
public func getGasFees() -> [String: [String: Double]]? {
    guard let resp = try? client.request("GET", "/api/admin/gas-fees", nil),
          let fees = resp["gas_fees"] as? [String: [String: Double]] else { return nil }
    return fees
}

public func setGasFee(chain: String, txType: String, fee: Double) {
    let req: [String: Any] = ["chain": chain, "tx_type": txType, "fee": fee]
    _ = try? client.request("POST", "/api/admin/set-gas-fee", req)
}
