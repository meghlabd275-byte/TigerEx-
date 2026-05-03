package com.tigerex.sdk

import okhttp3.*
import org.json.JSONObject
import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import java.util.concurrent.TimeUnit

class TigerExClient(private val apiKey: String, private val apiSecret: String) {
    private val baseUrl = "https://api.tigerex.com"
    private var token: String? = null
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .build()

    // ==================== AUTH ====================
    
    fun login(email: String, password: String): LoginResponse {
        val body = mapOf("email" to email, "password" to password)
        val response = request("POST", "/api/v1/auth/login", body)
        token = response.getJSONObject("data").getString("token")
        return LoginResponse(token!!, parseUser(response.getJSONObject("data").getJSONObject("user")))
    }

    fun register(email: String, password: String, username: String): User {
        val body = mapOf("email" to email, "password" to password, "username" to username)
        val response = request("POST", "/api/v1/auth/register", body)
        return parseUser(response.getJSONObject("data").getJSONObject("user"))
    }

    fun enable2FA(): TwoFactorResponse {
        val response = request("POST", "/api/v1/auth/2fa/enable", null)
        val data = response.getJSONObject("data")
        return TwoFactorResponse(data.getString("secret"), data.getString("qr"))
    }

    // ==================== MARKETS ====================

    fun getMarkets(): List<Market> {
        val response = request("GET", "/api/v1/markets", null)
        val markets = response.getJSONObject("data").getJSONArray("markets")
        return (0 until markets.length()).map { parseMarket(markets.getJSONObject(it)) }
    }

    fun getMarket(symbol: String): Market {
        val response = request("GET", "/api/v1/market/$symbol", null)
        return parseMarket(response.getJSONObject("data").getJSONObject("market"))
    }

    fun getDepth(symbol: String, limit: Int = 20): OrderBook {
        val response = request("GET", "/api/v1/depth/$symbol?limit=$limit", null)
        return parseOrderBook(response.getJSONObject("data").getJSONObject("orderbook"))
    }

    // ==================== TRADING ====================

    fun placeOrder(order: OrderRequest): Order {
        val body = mapOf(
            "symbol" to order.symbol,
            "side" to order.side,
            "type" to order.type,
            "quantity" to order.quantity,
            "price" to order.price
        )
        val response = request("POST", "/api/v1/order", body)
        return parseOrder(response.getJSONObject("data").getJSONObject("order"))
    }

    fun cancelOrder(orderId: String) {
        request("DELETE", "/api/v1/order/$orderId", null)
    }

    fun getOrders(symbol: String? = null, status: String? = null, limit: Int = 50): List<Order> {
        var endpoint = "/api/v1/orders?limit=$limit"
        symbol?.let { endpoint += "&symbol=$it" }
        status?.let { endpoint += "&status=$it" }
        
        val response = request("GET", endpoint, null)
        val orders = response.getJSONObject("data").getJSONArray("orders")
        return (0 until orders.length()).map { parseOrder(orders.getJSONObject(it)) }
    }

    // ==================== FUTURES ====================

    fun openPosition(pos: PositionRequest): Position {
        val body = mapOf(
            "symbol" to pos.symbol,
            "side" to pos.side,
            "quantity" to pos.quantity,
            "leverage" to pos.leverage
        )
        val response = request("POST", "/api/v1/futures/position", body)
        return parsePosition(response.getJSONObject("data").getJSONObject("position"))
    }

    fun closePosition(positionId: String) {
        request("POST", "/api/v1/futures/position/$positionId/close", null)
    }

    fun getPositions(): List<Position> {
        val response = request("GET", "/api/v1/futures/positions", null)
        val positions = response.getJSONObject("data").getJSONArray("positions")
        return (0 until positions.length()).map { parsePosition(positions.getJSONObject(it)) }
    }

    // ==================== WALLET ====================

    fun getBalance(): List<Balance> {
        val response = request("GET", "/api/v1/wallet/balance", null)
        val balances = response.getJSONObject("data").getJSONArray("balances")
        return (0 until balances.length()).map { parseBalance(balances.getJSONObject(it)) }
    }

    fun getDepositAddress(currency: String): DepositAddress {
        val response = request("GET", "/api/v1/wallet/deposit/address?currency=$currency", null)
        return parseDepositAddress(response.getJSONObject("data"))
    }

    fun withdraw(currency: String, amount: Double, address: String, memo: String? = null): String {
        val body = mutableMapOf(
            "currency" to currency,
            "amount" to amount,
            "address" to address
        )
        memo?.let { body["memo"] = it }
        
        val response = request("POST", "/api/v1/wallet/withdraw", body)
        return response.getJSONObject("data").getString("txId")
    }

    // ==================== P2P ====================

    fun getP2PAds(type: String? = null, currency: String? = null, payment: String? = null): List<P2PAd> {
        var endpoint = "/api/v1/p2p/ads"
        val params = mutableListOf<String>()
        type?.let { params.add("type=$it") }
        currency?.let { params.add("currency=$it") }
        payment?.let { params.add("paymentMethod=$it") }
        if (params.isNotEmpty()) endpoint += "?" + params.joinToString("&")
        
        val response = request("GET", endpoint, null)
        val ads = response.getJSONObject("data").getJSONArray("ads")
        return (0 until ads.length()).map { parseP2PAd(ads.getJSONObject(it)) }
    }

    // ==================== STAKING ====================

    fun getStakingProducts(): List<StakingProduct> {
        val response = request("GET", "/api/v1/staking/products", null)
        val products = response.getJSONObject("data").getJSONArray("products")
        return (0 until products.length()).map { parseStakingProduct(products.getJSONObject(it)) }
    }

    fun stake(productId: Int, amount: Double): StakingPosition {
        val body = mapOf("productId" to productId, "amount" to amount)
        val response = request("POST", "/api/v1/staking/stake", body)
        return parseStakingPosition(response.getJSONObject("data").getJSONObject("stake"))
    }

    // ==================== COPY TRADING ====================

    fun getTopTraders(): List<Trader> {
        val response = request("GET", "/api/v1/copy/traders", null)
        val traders = response.getJSONObject("data").getJSONArray("traders")
        return (0 until traders.length()).map { parseTrader(traders.getJSONObject(it)) }
    }

    fun followTrader(traderId: Int, amount: Double) {
        val body = mapOf("traderId" to traderId, "amount" to amount)
        request("POST", "/api/v1/copy/follow", body)
    }

    // ==================== AUTO INVEST ====================

    fun createAutoInvestPlan(plan: AutoInvestPlan): AutoInvestPlan {
        val body = mapOf(
            "name" to plan.name,
            "symbol" to plan.symbol,
            "amount" to plan.amount,
            "interval" to plan.interval
        )
        val response = request("POST", "/api/v1/autoinvest/create", body)
        return parseAutoInvestPlan(response.getJSONObject("data").getJSONObject("plan"))
    }

    fun getAutoInvestPlans(): List<AutoInvestPlan> {
        val response = request("GET", "/api/v1/autoinvest/plans", null)
        val plans = response.getJSONObject("data").getJSONArray("plans")
        return (0 until plans.length()).map { parseAutoInvestPlan(plans.getJSONObject(it)) }
    }

    // ==================== API KEYS ====================

    fun createAPIKey(name: String, permissions: List<String>): APIKeyResponse {
        val body = mapOf("name" to name, "permissions" to permissions)
        val response = request("POST", "/api/v1/api-key", body)
        return parseAPIKeyResponse(response.getJSONObject("data"))
    }

    fun getAPIKeys(): List<APIKey> {
        val response = request("GET", "/api/v1/api-keys", null)
        val keys = response.getJSONObject("data").getJSONArray("keys")
        return (0 until keys.length()).map { parseAPIKey(keys.getJSONObject(it)) }
    }

    fun deleteAPIKey(keyId: Int) {
        request("DELETE", "/api/v1/api-key/$keyId", null)
    }

    // ==================== HTTP REQUEST ====================

    private fun request(method: String, endpoint: String, body: Map<String, Any>?): JSONObject {
        val url = HttpUrl.parse("$baseUrl$endpoint")
        val requestBuilder = Request.Builder().url(url!!)

        requestBuilder.addHeader("Content-Type", "application/json")
        token?.let { requestBuilder.addHeader("Authorization", "Bearer $it") }

        // Add signature
        val timestamp = System.currentTimeMillis().toString()
        requestBuilder.addHeader("X-Timestamp", timestamp)
        
        val signatureData = "$method$endpoint$timestamp${body?.toString() ?: ""}"
        requestBuilder.addHeader("X-Signature", generateSignature(signatureData))

        if (body != null) {
            requestBuilder.post(RequestBody.create(
                MediaType.parse("application/json"),
                JSONObject(body).toString()
            ))
        }

        val response = client.newCall(requestBuilder.build()).execute()
        return JSONObject(response.body()?.string())
    }

    private fun generateSignature(data: String): String {
        val mac = Mac.getInstance("HmacSHA256")
        val secretKey = SecretKeySpec(apiSecret.toByteArray(), "HmacSHA256")
        mac.init(secretKey)
        val hmacData = mac.doFinal(data.toByteArray())
        return hmacData.joinToString("") { "%02x".format(it) }
    }

    // ==================== PARSERS ====================

    private fun parseUser(json: JSONObject) = User(
        json.getInt("id"),
        json.getString("email"),
        json.getString("username"),
        json.optString("kycStatus", "none")
    )

    private fun parseMarket(json: JSONObject) = Market(
        json.getString("symbol"),
        json.getString("baseAsset"),
        json.getString("quoteAsset"),
        json.getDouble("price"),
        json.getDouble("priceChange24h"),
        json.getDouble("volume24h"),
        json.getInt("maxLeverage")
    )

    private fun parseOrderBook(json: JSONObject) = OrderBook(
        parseLevels(json.getJSONArray("bids")),
        parseLevels(json.getJSONArray("asks"))
    )

    private fun parseLevels(json: JSONArray): List<PriceLevel> {
        return (0 until json.length()).map {
            val obj = json.getJSONObject(it)
            PriceLevel(obj.getDouble("price"), obj.getDouble("quantity"))
        }
    }

    private fun parseOrder(json: JSONObject) = Order(
        json.getString("orderId"),
        json.getString("symbol"),
        json.getString("side"),
        json.getString("type"),
        json.getDouble("quantity"),
        json.getDouble("price"),
        json.getString("status")
    )

    private fun parsePosition(json: JSONObject) = Position(
        json.getString("positionId"),
        json.getString("symbol"),
        json.getString("side"),
        json.getDouble("quantity"),
        json.getInt("leverage"),
        json.getDouble("margin"),
        json.getDouble("pnl")
    )

    private fun parseBalance(json: JSONObject) = Balance(
        json.getString("currency"),
        json.getDouble("balance"),
        json.getDouble("availableBalance"),
        json.getDouble("lockedBalance")
    )

    private fun parseDepositAddress(json: JSONObject) = DepositAddress(
        json.getString("currency"),
        json.getString("address"),
        json.optString("tag", null)
    )

    private fun parseP2PAd(json: JSONObject) = P2PAd(
        json.getInt("id"),
        json.getString("username"),
        json.getString("type"),
        json.getString("currency"),
        json.getDouble("price"),
        json.getDouble("minAmount"),
        json.getDouble("maxAmount"),
        json.getString("paymentMethod")
    )

    private fun parseStakingProduct(json: JSONObject) = StakingProduct(
        json.getInt("id"),
        json.getString("name"),
        json.getString("currency"),
        json.getDouble("apy"),
        json.getInt("lockPeriod")
    )

    private fun parseStakingPosition(json: JSONObject) = StakingPosition(
        json.getInt("id"),
        json.getInt("productId"),
        json.getDouble("amount"),
        json.getString("startAt"),
        json.getString("endAt"),
        json.getString("status")
    )

    private fun parseTrader(json: JSONObject) = Trader(
        json.getInt("id"),
        json.getString("username"),
        json.getDouble("pnl"),
        json.getInt("trades"),
        json.getDouble("winRate"),
        json.getInt("followers")
    )

    private fun parseAutoInvestPlan(json: JSONObject) = AutoInvestPlan(
        json.getInt("id"),
        json.getString("name"),
        json.getString("symbol"),
        json.getDouble("amount"),
        json.getString("interval"),
        json.getString("status")
    )

    private fun parseAPIKeyResponse(json: JSONObject) = APIKeyResponse(
        json.getString("apiKey"),
        json.getString("apiSecret")
    )

    private fun parseAPIKey(json: JSONObject) = APIKey(
        json.getInt("id"),
        json.getString("keyName"),
        json.getString("apiKey"),
        json.getString("permissions"),
        json.getBoolean("isActive")
    )
}

// ==================== DATA CLASSES ====================

data class LoginResponse(val token: String, val user: User)
data class User(val id: Int, val email: String, val username: String, val kycStatus: String)
data class TwoFactorResponse(val secret: String, val qr: String)
data class Market(val symbol: String, val baseAsset: String, val quoteAsset: String, val price: Double, val change24h: Double, val volume24h: Double, val maxLeverage: Int)
data class OrderBook(val bids: List<PriceLevel>, val asks: List<PriceLevel>)
data class PriceLevel(val price: Double, val quantity: Double)
data class Order(val orderId: String, val symbol: String, val side: String, val type: String, val quantity: Double, val price: Double, val status: String)
data class OrderRequest(var symbol: String = "", var side: String = "", var type: String = "limit", var quantity: Double = 0.0, var price: Double = 0.0)
data class Position(val positionId: String, val symbol: String, val side: String, val quantity: Double, val leverage: Int, val margin: Double, val pnl: Double)
data class PositionRequest(var symbol: String = "", var side: String = "", var quantity: Double = 0.0, var leverage: Int = 1)
data class Balance(val currency: String, val balance: Double, val availableBalance: Double, val lockedBalance: Double)
data class DepositAddress(val currency: String, val address: String, val tag: String?)
data class P2PAd(val id: Int, val username: String, val type: String, val currency: String, val price: Double, val minAmount: Double, val maxAmount: Double, val paymentMethod: String)
data class StakingProduct(val id: Int, val name: String, val currency: String, val apy: Double, val lockPeriod: Int)
data class StakingPosition(val id: Int, val productId: Int, val amount: Double, val startAt: String, val endAt: String, val status: String)
data class Trader(val id: Int, val username: String, val pnl: Double, val trades: Int, val winRate: Double, val followers: Int)
data class AutoInvestPlan(var id: Int = 0, var name: String = "", var symbol: String = "", var amount: Double = 0.0, var interval: String = "daily", var status: String = "active")
data class APIKeyResponse(val apiKey: String, val apiSecret: String)
data class APIKey(val id: Int, val keyName: String, val apiKey: String, val permissions: String, val isActive: Boolean)
// ==================== WALLET WITH 24-WORD SEED ====================
data class Wallet(val type: String, val chain: String, val seedPhrase: String?, val backupKey: String?, 
    val ownership: String, val fullControl: Boolean, val address: String, val privateKey: String?)
data class WalletRequest(val type: String)

fun createWallet(type: String): Wallet {
    val req = WalletRequest(type)
    return post("/api/wallet/create", req).get("wallet") as Wallet
}

fun listWallets(): Map<String, Wallet> {
    return get("/api/wallet/list") as Map<String, Wallet>
}

// ==================== DEFI ====================
data class DefiResponse(val txHash: String?, val poolId: String?, val stakeId: String?, 
    val tokenAddress: String?, val apy: Double?, val message: String)

fun defiSwap(tokenIn: String, tokenOut: String, amount: Double): DefiResponse {
    return post("/api/defi/swap", mapOf("tokenIn" to tokenIn, "tokenOut" to tokenOut, "amount" to amount)) as DefiResponse
}

fun defiCreatePool(tokenA: String, tokenB: String): DefiResponse {
    return post("/api/defi/pool", mapOf("tokenA" to tokenA, "tokenB" to tokenB)) as DefiResponse
}

fun defiStake(token: String, amount: Double, duration: Int): DefiResponse {
    return post("/api/defi/stake", mapOf("token" to token, "amount" to amount, "duration" to duration)) as DefiResponse
}

fun defiBridge(fromChain: String, toChain: String, token: String, amount: Double): DefiResponse {
    return post("/api/defi/bridge", mapOf("fromChain" to fromChain, "toChain" to toChain, "token" to token, "amount" to amount)) as DefiResponse
}

fun defiCreateToken(name: String, symbol: String, supply: Double): DefiResponse {
    return post("/api/defi/create-token", mapOf("name" to name, "symbol" to symbol, "supply" to supply)) as DefiResponse
}

// ==================== GAS FEES ====================
fun getGasFees(): Map<String, Map<String, Double>> {
    return get("/api/admin/gas-fees") as Map<String, Map<String, Double>>
}

fun setGasFee(chain: String, txType: String, fee: Double) {
    post("/api/admin/set-gas-fee", mapOf("chain" to chain, "tx_type" to txType, "fee" to fee))
}
