package com.tigerex.sdk;

import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import org.json.*;

public class TigerExClient {
    private final String apiKey;
    private final String apiSecret;
    private final String baseUrl = "https://api.tigerex.com";
    private String token;

    public TigerExClient(String apiKey, String apiSecret) {
        this.apiKey = apiKey;
        this.apiSecret = apiSecret;
    }

    // ==================== AUTH ====================
    
    public LoginResponse login(String email, String password) throws Exception {
        Map<String, String> body = new HashMap<>();
        body.put("email", email);
        body.put("password", password);
        
        JSONObject response = request("POST", "/api/v1/auth/login", body);
        this.token = response.getJSONObject("data").getString("token");
        
        return new LoginResponse(
            token,
            parseUser(response.getJSONObject("data").getJSONObject("user"))
        );
    }

    public User register(String email, String password, String username) throws Exception {
        Map<String, String> body = new HashMap<>();
        body.put("email", email);
        body.put("password", password);
        body.put("username", username);
        
        JSONObject response = request("POST", "/api/v1/auth/register", body);
        return parseUser(response.getJSONObject("data").getJSONObject("user"));
    }

    public TwoFactorResponse enable2FA() throws Exception {
        JSONObject response = request("POST", "/api/v1/auth/2fa/enable", null);
        JSONObject data = response.getJSONObject("data");
        return new TwoFactorResponse(
            data.getString("secret"),
            data.getString("qr")
        );
    }

    // ==================== MARKETS ====================

    public List<Market> getMarkets() throws Exception {
        JSONObject response = request("GET", "/api/v1/markets", null);
        JSONArray markets = response.getJSONObject("data").getJSONArray("markets");
        
        List<Market> result = new ArrayList<>();
        for (int i = 0; i < markets.length(); i++) {
            result.add(parseMarket(markets.getJSONObject(i)));
        }
        return result;
    }

    public Market getMarket(String symbol) throws Exception {
        JSONObject response = request("GET", "/api/v1/market/" + symbol, null);
        return parseMarket(response.getJSONObject("data").getJSONObject("market"));
    }

    public OrderBook getDepth(String symbol, int limit) throws Exception {
        JSONObject response = request("GET", "/api/v1/depth/" + symbol + "?limit=" + limit, null);
        return parseOrderBook(response.getJSONObject("data").getJSONObject("orderbook"));
    }

    public List<Kline> getKlines(String symbol, String interval, int limit) throws Exception {
        JSONObject response = request("GET", 
            "/api/v1/klines?symbol=" + symbol + "&interval=" + interval + "&limit=" + limit, null);
        
        List<Kline> result = new ArrayList<>();
        JSONArray klines = response.getJSONObject("data").getJSONArray("klines");
        for (int i = 0; i < klines.length(); i++) {
            result.add(parseKline(klines.getJSONObject(i)));
        }
        return result;
    }

    // ==================== TRADING ====================

    public Order placeOrder(OrderRequest order) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("symbol", order.symbol);
        body.put("side", order.side);
        body.put("type", order.type);
        body.put("quantity", order.quantity);
        body.put("price", order.price);
        
        JSONObject response = request("POST", "/api/v1/order", body);
        return parseOrder(response.getJSONObject("data").getJSONObject("order"));
    }

    public void cancelOrder(String orderId) throws Exception {
        request("DELETE", "/api/v1/order/" + orderId, null);
    }

    public List<Order> getOrders(String symbol, String status, int limit) throws Exception {
        String endpoint = "/api/v1/orders?limit=" + limit;
        if (symbol != null) endpoint += "&symbol=" + symbol;
        if (status != null) endpoint += "&status=" + status;
        
        JSONObject response = request("GET", endpoint, null);
        JSONArray orders = response.getJSONObject("data").getJSONArray("orders");
        
        List<Order> result = new ArrayList<>();
        for (int i = 0; i < orders.length(); i++) {
            result.add(parseOrder(orders.getJSONObject(i)));
        }
        return result;
    }

    // ==================== FUTURES ====================

    public Position openPosition(PositionRequest pos) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("symbol", pos.symbol);
        body.put("side", pos.side);
        body.put("quantity", pos.quantity);
        body.put("leverage", pos.leverage);
        
        JSONObject response = request("POST", "/api/v1/futures/position", body);
        return parsePosition(response.getJSONObject("data").getJSONObject("position"));
    }

    public void closePosition(String positionId) throws Exception {
        request("POST", "/api/v1/futures/position/" + positionId + "/close", null);
    }

    public List<Position> getPositions() throws Exception {
        JSONObject response = request("GET", "/api/v1/futures/positions", null);
        JSONArray positions = response.getJSONObject("data").getJSONArray("positions");
        
        List<Position> result = new ArrayList<>();
        for (int i = 0; i < positions.length(); i++) {
            result.add(parsePosition(positions.getJSONObject(i)));
        }
        return result;
    }

    // ==================== WALLET ====================

    public List<Balance> getBalance() throws Exception {
        JSONObject response = request("GET", "/api/v1/wallet/balance", null);
        JSONArray balances = response.getJSONObject("data").getJSONArray("balances");
        
        List<Balance> result = new ArrayList<>();
        for (int i = 0; i < balances.length(); i++) {
            result.add(parseBalance(balances.getJSONObject(i)));
        }
        return result;
    }

    public DepositAddress getDepositAddress(String currency) throws Exception {
        JSONObject response = request("GET", "/api/v1/wallet/deposit/address?currency=" + currency, null);
        return parseDepositAddress(response.getJSONObject("data"));
    }

    public String withdraw(String currency, double amount, String address) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("currency", currency);
        body.put("amount", amount);
        body.put("address", address);
        
        JSONObject response = request("POST", "/api/v1/wallet/withdraw", body);
        return response.getJSONObject("data").getString("txId");
    }

    public List<Transaction> getTransactions(String type, String currency, int limit) throws Exception {
        String endpoint = "/api/v1/wallet/transactions?limit=" + limit;
        if (type != null) endpoint += "&type=" + type;
        if (currency != null) endpoint += "&currency=" + currency;
        
        JSONObject response = request("GET", endpoint, null);
        JSONArray txs = response.getJSONObject("data").getJSONArray("transactions");
        
        List<Transaction> result = new ArrayList<>();
        for (int i = 0; i < txs.length(); i++) {
            result.add(parseTransaction(txs.getJSONObject(i)));
        }
        return result;
    }

    // ==================== P2P ====================

    public List<P2PAd> getP2PAds(String type, String currency, String payment) throws Exception {
        String endpoint = "/api/v1/p2p/ads";
        if (type != null || currency != null || payment != null) {
            endpoint += "?";
            if (type != null) endpoint += "type=" + type + "&";
            if (currency != null) endpoint += "currency=" + currency + "&";
            if (payment != null) endpoint += "paymentMethod=" + payment;
        }
        
        JSONObject response = request("GET", endpoint, null);
        JSONArray ads = response.getJSONObject("data").getJSONArray("ads");
        
        List<P2PAd> result = new ArrayList<>();
        for (int i = 0; i < ads.length(); i++) {
            result.add(parseP2PAd(ads.getJSONObject(i)));
        }
        return result;
    }

    public P2POrder createP2POrder(int adId, double amount) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("adId", adId);
        body.put("amount", amount);
        
        JSONObject response = request("POST", "/api/v1/p2p/order", body);
        return parseP2POrder(response.getJSONObject("data").getJSONObject("order"));
    }

    // ==================== STAKING ====================

    public List<StakingProduct> getStakingProducts() throws Exception {
        JSONObject response = request("GET", "/api/v1/staking/products", null);
        JSONArray products = response.getJSONObject("data").getJSONArray("products");
        
        List<StakingProduct> result = new ArrayList<>();
        for (int i = 0; i < products.length(); i++) {
            result.add(parseStakingProduct(products.getJSONObject(i)));
        }
        return result;
    }

    public StakingPosition stake(int productId, double amount) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("productId", productId);
        body.put("amount", amount);
        
        JSONObject response = request("POST", "/api/v1/staking/stake", body);
        return parseStakingPosition(response.getJSONObject("data").getJSONObject("stake"));
    }

    public void unstake(int stakeId) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("stakeId", stakeId);
        request("POST", "/api/v1/staking/unstake", body);
    }

    public List<StakingPosition> getStakingPositions() throws Exception {
        JSONObject response = request("GET", "/api/v1/staking/positions", null);
        JSONArray positions = response.getJSONObject("data").getJSONArray("positions");
        
        List<StakingPosition> result = new ArrayList<>();
        for (int i = 0; i < positions.length(); i++) {
            result.add(parseStakingPosition(positions.getJSONObject(i)));
        }
        return result;
    }

    // ==================== COPY TRADING ====================

    public List<Trader> getTopTraders() throws Exception {
        JSONObject response = request("GET", "/api/v1/copy/traders", null);
        JSONArray traders = response.getJSONObject("data").getJSONArray("traders");
        
        List<Trader> result = new ArrayList<>();
        for (int i = 0; i < traders.length(); i++) {
            result.add(parseTrader(traders.getJSONObject(i)));
        }
        return result;
    }

    public void followTrader(int traderId, double amount) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("traderId", traderId);
        body.put("amount", amount);
        request("POST", "/api/v1/copy/follow", body);
    }

    // ==================== AUTO INVEST ====================

    public AutoInvestPlan createAutoInvestPlan(AutoInvestPlan plan) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("name", plan.name);
        body.put("symbol", plan.symbol);
        body.put("amount", plan.amount);
        body.put("interval", plan.interval);
        
        JSONObject response = request("POST", "/api/v1/autoinvest/create", body);
        return parseAutoInvestPlan(response.getJSONObject("data").getJSONObject("plan"));
    }

    public List<AutoInvestPlan> getAutoInvestPlans() throws Exception {
        JSONObject response = request("GET", "/api/v1/autoinvest/plans", null);
        JSONArray plans = response.getJSONObject("data").getJSONArray("plans");
        
        List<AutoInvestPlan> result = new ArrayList<>();
        for (int i = 0; i < plans.length(); i++) {
            result.add(parseAutoInvestPlan(plans.getJSONObject(i)));
        }
        return result;
    }

    // ==================== API KEYS ====================

    public APIKeyResponse createAPIKey(String name, List<String> permissions) throws Exception {
        Map<String, Object> body = new HashMap<>();
        body.put("name", name);
        body.put("permissions", permissions);
        
        JSONObject response = request("POST", "/api/v1/api-key", body);
        return parseAPIKeyResponse(response.getJSONObject("data"));
    }

    public List<APIKey> getAPIKeys() throws Exception {
        JSONObject response = request("GET", "/api/v1/api-keys", null);
        JSONArray keys = response.getJSONObject("data").getJSONArray("keys");
        
        List<APIKey> result = new ArrayList<>();
        for (int i = 0; i < keys.length(); i++) {
            result.add(parseAPIKey(keys.getJSONObject(i)));
        }
        return result;
    }

    public void deleteAPIKey(int keyId) throws Exception {
        request("DELETE", "/api/v1/api-key/" + keyId, null);
    }

    // ==================== HTTP REQUEST ====================

    private JSONObject request(String method, String endpoint, Map<String, Object> body) throws Exception {
        URL url = new URL(baseUrl + endpoint);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        
        conn.setRequestMethod(method);
        conn.setRequestProperty("Content-Type", "application/json");
        
        if (token != null) {
            conn.setRequestProperty("Authorization", "Bearer " + token);
        }
        
        // Add timestamp and signature for authenticated requests
        if (body != null || !endpoint.contains("auth/login")) {
            String timestamp = String.valueOf(System.currentTimeMillis());
            conn.setRequestProperty("X-Timestamp", timestamp);
            
            String signature = generateSignature(method + endpoint + timestamp + (body != null ? body.toString() : ""));
            conn.setRequestProperty("X-Signature", signature);
        }
        
        if (body != null) {
            conn.setDoOutput(true);
            try (OutputStream os = conn.getOutputStream()) {
                os.write(new JSONObject(body).toString().getBytes(StandardCharsets.UTF_8));
            }
        }
        
        BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        
        return new JSONObject(response.toString());
    }

    private String generateSignature(String data) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        SecretKeySpec secretKey = new SecretKeySpec(apiSecret.getBytes(), "HmacSHA256");
        mac.init(secretKey);
        byte[] hmacData = mac.doFinal(data.getBytes());
        
        StringBuilder result = new StringBuilder();
        for (byte b : hmacData) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }

    // ==================== PARSERS ====================

    private User parseUser(JSONObject json) {
        return new User(
            json.getInt("id"),
            json.getString("email"),
            json.getString("username"),
            json.optString("kycStatus", "none")
        );
    }

    private Market parseMarket(JSONObject json) {
        return new Market(
            json.getString("symbol"),
            json.getString("baseAsset"),
            json.getString("quoteAsset"),
            json.getDouble("price"),
            json.getDouble("priceChange24h"),
            json.getDouble("volume24h"),
            json.getInt("maxLeverage")
        );
    }

    private OrderBook parseOrderBook(JSONObject json) {
        return new OrderBook(parseLevels(json.getJSONArray("bids")), parseLevels(json.getJSONArray("asks")));
    }

    private List<PriceLevel> parseLevels(JSONArray array) {
        List<PriceLevel> levels = new ArrayList<>();
        for (int i = 0; i < array.length(); i++) {
            JSONObject obj = array.getJSONObject(i);
            levels.add(new PriceLevel(obj.getDouble("price"), obj.getDouble("quantity")));
        }
        return levels;
    }

    private Kline parseKline(JSONObject json) {
        return new Kline(
            json.getLong("time"),
            json.getDouble("open"),
            json.getDouble("high"),
            json.getDouble("low"),
            json.getDouble("close"),
            json.getDouble("volume")
        );
    }

    private Order parseOrder(JSONObject json) {
        return new Order(
            json.getString("orderId"),
            json.getString("symbol"),
            json.getString("side"),
            json.getString("type"),
            json.getDouble("quantity"),
            json.getDouble("price"),
            json.getString("status")
        );
    }

    private Position parsePosition(JSONObject json) {
        return new Position(
            json.getString("positionId"),
            json.getString("symbol"),
            json.getString("side"),
            json.getDouble("quantity"),
            json.getInt("leverage"),
            json.getDouble("margin"),
            json.getDouble("pnl")
        );
    }

    private Balance parseBalance(JSONObject json) {
        return new Balance(
            json.getString("currency"),
            json.getDouble("balance"),
            json.getDouble("availableBalance"),
            json.getDouble("lockedBalance")
        );
    }

    private DepositAddress parseDepositAddress(JSONObject json) {
        return new DepositAddress(
            json.getString("currency"),
            json.getString("address"),
            json.optString("tag", null)
        );
    }

    private Transaction parseTransaction(JSONObject json) {
        return new Transaction(
            json.getInt("id"),
            json.getString("type"),
            json.getString("currency"),
            json.getDouble("amount"),
            json.getString("status")
        );
    }

    private P2PAd parseP2PAd(JSONObject json) {
        return new P2PAd(
            json.getInt("id"),
            json.getString("username"),
            json.getString("type"),
            json.getString("currency"),
            json.getDouble("price"),
            json.getDouble("minAmount"),
            json.getDouble("maxAmount"),
            json.getString("paymentMethod")
        );
    }

    private P2POrder parseP2POrder(JSONObject json) {
        return new P2POrder(
            json.getString("orderId"),
            json.getInt("adId"),
            json.getDouble("amount"),
            json.getDouble("price"),
            json.getString("status")
        );
    }

    private StakingProduct parseStakingProduct(JSONObject json) {
        return new StakingProduct(
            json.getInt("id"),
            json.getString("name"),
            json.getString("currency"),
            json.getDouble("apy"),
            json.getInt("lockPeriod")
        );
    }

    private StakingPosition parseStakingPosition(JSONObject json) {
        return new StakingPosition(
            json.getInt("id"),
            json.getInt("productId"),
            json.getDouble("amount"),
            json.getString("startAt"),
            json.getString("endAt"),
            json.getString("status")
        );
    }

    private Trader parseTrader(JSONObject json) {
        return new Trader(
            json.getInt("id"),
            json.getString("username"),
            json.getDouble("pnl"),
            json.getInt("trades"),
            json.getDouble("winRate"),
            json.getInt("followers")
        );
    }

    private AutoInvestPlan parseAutoInvestPlan(JSONObject json) {
        return new AutoInvestPlan(
            json.getInt("id"),
            json.getString("name"),
            json.getString("symbol"),
            json.getDouble("amount"),
            json.getString("interval"),
            json.getString("status")
        );
    }

    private APIKeyResponse parseAPIKeyResponse(JSONObject json) {
        return new APIKeyResponse(
            json.getString("apiKey"),
            json.getString("apiSecret")
        );
    }

    private APIKey parseAPIKey(JSONObject json) {
        return new APIKey(
            json.getInt("id"),
            json.getString("keyName"),
            json.getString("apiKey"),
            json.getString("permissions"),
            json.getBoolean("isActive")
        );
    }

    // ==================== DATA CLASSES ====================

    public static class LoginResponse {
        public final String token;
        public final User user;
        
        public LoginResponse(String token, User user) {
            this.token = token;
            this.user = user;
        }
    }

    public static class User {
        public final int id;
        public final String email;
        public final String username;
        public final String kycStatus;
        
        public User(int id, String email, String username, String kycStatus) {
            this.id = id;
            this.email = email;
            this.username = username;
            this.kycStatus = kycStatus;
        }
    }

    public static class TwoFactorResponse {
        public final String secret;
        public final String qr;
        
        public TwoFactorResponse(String secret, String qr) {
            this.secret = secret;
            this.qr = qr;
        }
    }

    public static class Market {
        public final String symbol;
        public final String baseAsset;
        public final String quoteAsset;
        public final double price;
        public final double change24h;
        public final double volume24h;
        public final int maxLeverage;
        
        public Market(String symbol, String baseAsset, String quoteAsset, double price, double change24h, double volume24h, int maxLeverage) {
            this.symbol = symbol;
            this.baseAsset = baseAsset;
            this.quoteAsset = quoteAsset;
            this.price = price;
            this.change24h = change24h;
            this.volume24h = volume24h;
            this.maxLeverage = maxLeverage;
        }
    }

    public static class OrderBook {
        public final List<PriceLevel> bids;
        public final List<PriceLevel> asks;
        
        public OrderBook(List<PriceLevel> bids, List<PriceLevel> asks) {
            this.bids = bids;
            this.asks = asks;
        }
    }

    public static class PriceLevel {
        public final double price;
        public final double quantity;
        
        public PriceLevel(double price, double quantity) {
            this.price = price;
            this.quantity = quantity;
        }
    }

    public static class Kline {
        public final long time;
        public final double open;
        public final double high;
        public final double low;
        public final double close;
        public final double volume;
        
        public Kline(long time, double open, double high, double low, double close, double volume) {
            this.time = time;
            this.open = open;
            this.high = high;
            this.low = low;
            this.close = close;
            this.volume = volume;
        }
    }

    public static class OrderRequest {
        public String symbol;
        public String side;
        public String type;
        public double quantity;
        public double price;
    }

    public static class Order {
        public final String orderId;
        public final String symbol;
        public final String side;
        public final String type;
        public final double quantity;
        public final double price;
        public final String status;
        
        public Order(String orderId, String symbol, String side, String type, double quantity, double price, String status) {
            this.orderId = orderId;
            this.symbol = symbol;
            this.side = side;
            this.type = type;
            this.quantity = quantity;
            this.price = price;
            this.status = status;
        }
    }

    public static class PositionRequest {
        public String symbol;
        public String side;
        public double quantity;
        public int leverage;
    }

    public static class Position {
        public final String positionId;
        public final String symbol;
        public final String side;
        public final double quantity;
        public final int leverage;
        public final double margin;
        public final double pnl;
        
        public Position(String positionId, String symbol, String side, double quantity, int leverage, double margin, double pnl) {
            this.positionId = positionId;
            this.symbol = symbol;
            this.side = side;
            this.quantity = quantity;
            this.leverage = leverage;
            this.margin = margin;
            this.pnl = pnl;
        }
    }

    public static class Balance {
        public final String currency;
        public final double balance;
        public final double availableBalance;
        public final double lockedBalance;
        
        public Balance(String currency, double balance, double availableBalance, double lockedBalance) {
            this.currency = currency;
            this.balance = balance;
            this.availableBalance = availableBalance;
            this.lockedBalance = lockedBalance;
        }
    }

    public static class DepositAddress {
        public final String currency;
        public final String address;
        public final String tag;
        
        public DepositAddress(String currency, String address, String tag) {
            this.currency = currency;
            this.address = address;
            this.tag = tag;
        }
    }

    public static class Transaction {
        public final int id;
        public final String type;
        public final String currency;
        public final double amount;
        public final String status;
        
        public Transaction(int id, String type, String currency, double amount, String status) {
            this.id = id;
            this.type = type;
            this.currency = currency;
            this.amount = amount;
            this.status = status;
        }
    }

    public static class P2PAd {
        public final int id;
        public final String username;
        public final String type;
        public final String currency;
        public final double price;
        public final double minAmount;
        public final double maxAmount;
        public final String paymentMethod;
        
        public P2PAd(int id, String username, String type, String currency, double price, double minAmount, double maxAmount, String paymentMethod) {
            this.id = id;
            this.username = username;
            this.type = type;
            this.currency = currency;
            this.price = price;
            this.minAmount = minAmount;
            this.maxAmount = maxAmount;
            this.paymentMethod = paymentMethod;
        }
    }

    public static class P2POrder {
        public final String orderId;
        public final int adId;
        public final double amount;
        public final double price;
        public final String status;
        
        public P2POrder(String orderId, int adId, double amount, double price, String status) {
            this.orderId = orderId;
            this.adId = adId;
            this.amount = amount;
            this.price = price;
            this.status = status;
        }
    }

    public static class StakingProduct {
        public final int id;
        public final String name;
        public final String currency;
        public final double apy;
        public final int lockPeriod;
        
        public StakingProduct(int id, String name, String currency, double apy, int lockPeriod) {
            this.id = id;
            this.name = name;
            this.currency = currency;
            this.apy = apy;
            this.lockPeriod = lockPeriod;
        }
    }

    public static class StakingPosition {
        public final int id;
        public final int productId;
        public final double amount;
        public final String startAt;
        public final String endAt;
        public final String status;
        
        public StakingPosition(int id, int productId, double amount, String startAt, String endAt, String status) {
            this.id = id;
            this.productId = productId;
            this.amount = amount;
            this.startAt = startAt;
            this.endAt = endAt;
            this.status = status;
        }
    }

    public static class Trader {
        public final int id;
        public final String username;
        public final double pnl;
        public final int trades;
        public final double winRate;
        public final int followers;
        
        public Trader(int id, String username, double pnl, int trades, double winRate, int followers) {
            this.id = id;
            this.username = username;
            this.pnl = pnl;
            this.trades = trades;
            this.winRate = winRate;
            this.followers = followers;
        }
    }

    public static class AutoInvestPlan {
        public int id;
        public String name;
        public String symbol;
        public double amount;
        public String interval;
        public String status;
        
        public AutoInvestPlan(int id, String name, String symbol, double amount, String interval, String status) {
            this.id = id;
            this.name = name;
            this.symbol = symbol;
            this.amount = amount;
            this.interval = interval;
            this.status = status;
        }
    }

    public static class APIKeyResponse {
        public final String apiKey;
        public final String apiSecret;
        
        public APIKeyResponse(String apiKey, String apiSecret) {
            this.apiKey = apiKey;
            this.apiSecret = apiSecret;
        }
    }

    public static class APIKey {
        public final int id;
        public final String keyName;
        public final String apiKey;
        public final String permissions;
        public final boolean isActive;
        
        public APIKey(int id, String keyName, String apiKey, String permissions, boolean isActive) {
            this.id = id;
            this.keyName = keyName;
            this.apiKey = apiKey;
            this.permissions = permissions;
            this.isActive = isActive;
        }
    }
}