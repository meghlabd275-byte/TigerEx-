/**
 * TigerEx C++ Matching Engine
 * Ultra-high performance matching engine written in C++
 * Part of TigerEx Multi-Language Microservices Architecture
 */

#include <iostream>
#include <string>
#include <memory>
#include <vector>
#include <map>
#include <unordered_map>
#include <set>
#include <queue>
#include <mutex>
#include <shared_mutex>
#include <chrono>
#include <atomic>
#include <functional>
#include <thread>
#include <condition_variable>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <cstdint>

// HTTP server includes (using cpp-httplib for simplicity)
#include "httplib.h"
#include "nlohmann/json.hpp"

using json = nlohmann::json;
using namespace std::chrono;

// Decimal precision for financial calculations
class Decimal {
private:
    int64_t value; // Store as fixed-point (8 decimal places)
    static constexpr int64_t SCALE = 100000000;

public:
    Decimal() : value(0) {}
    Decimal(double d) : value(static_cast<int64_t>(d * SCALE)) {}
    Decimal(int64_t v, bool raw) : value(v) {} // Raw constructor
    
    static Decimal fromString(const std::string& s) {
        Decimal d;
        size_t dotPos = s.find('.');
        if (dotPos == std::string::npos) {
            d.value = std::stoll(s) * SCALE;
        } else {
            std::string intPart = s.substr(0, dotPos);
            std::string fracPart = s.substr(dotPos + 1);
            while (fracPart.length() < 8) fracPart += '0';
            fracPart = fracPart.substr(0, 8);
            d.value = std::stoll(intPart) * SCALE + std::stoll(fracPart);
        }
        return d;
    }
    
    double toDouble() const { return static_cast<double>(value) / SCALE; }
    int64_t raw() const { return value; }
    
    Decimal operator+(const Decimal& other) const { return Decimal(value + other.value, true); }
    Decimal operator-(const Decimal& other) const { return Decimal(value - other.value, true); }
    Decimal operator*(const Decimal& other) const { return Decimal((value * other.value) / SCALE, true); }
    Decimal operator/(const Decimal& other) const { return Decimal((value * SCALE) / other.value, true); }
    
    bool operator==(const Decimal& other) const { return value == other.value; }
    bool operator!=(const Decimal& other) const { return value != other.value; }
    bool operator<(const Decimal& other) const { return value < other.value; }
    bool operator>(const Decimal& other) const { return value > other.value; }
    bool operator<=(const Decimal& other) const { return value <= other.value; }
    bool operator>=(const Decimal& other) const { return value >= other.value; }
    
    std::string toString() const {
        int64_t intPart = value / SCALE;
        int64_t fracPart = value % SCALE;
        std::stringstream ss;
        ss << intPart << "." << std::setfill('0') << std::setw(8) << fracPart;
        return ss.str();
    }
};

// Order types
enum class OrderSide { BUY, SELL };
enum class OrderType { LIMIT, MARKET, STOP_LIMIT, STOP_MARKET, IOC, FOK, POST_ONLY };
enum class OrderStatus { NEW, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED, EXPIRED };
enum class ExchangeStatus { ACTIVE, PAUSED, HALTED, MAINTENANCE };

// String conversion functions
std::string orderSideToString(OrderSide side) {
    return side == OrderSide::BUY ? "buy" : "sell";
}

OrderSide stringToOrderSide(const std::string& s) {
    return s == "buy" ? OrderSide::BUY : OrderSide::SELL;
}

std::string orderTypeToString(OrderType type) {
    switch (type) {
        case OrderType::LIMIT: return "limit";
        case OrderType::MARKET: return "market";
        case OrderType::STOP_LIMIT: return "stop_limit";
        case OrderType::STOP_MARKET: return "stop_market";
        case OrderType::IOC: return "ioc";
        case OrderType::FOK: return "fok";
        case OrderType::POST_ONLY: return "post_only";
        default: return "unknown";
    }
}

OrderType stringToOrderType(const std::string& s) {
    if (s == "limit") return OrderType::LIMIT;
    if (s == "market") return OrderType::MARKET;
    if (s == "stop_limit") return OrderType::STOP_LIMIT;
    if (s == "stop_market") return OrderType::STOP_MARKET;
    if (s == "ioc") return OrderType::IOC;
    if (s == "fok") return OrderType::FOK;
    return OrderType::POST_ONLY;
}

std::string orderStatusToString(OrderStatus status) {
    switch (status) {
        case OrderStatus::NEW: return "new";
        case OrderStatus::PARTIALLY_FILLED: return "partially_filled";
        case OrderStatus::FILLED: return "filled";
        case OrderStatus::CANCELLED: return "cancelled";
        case OrderStatus::REJECTED: return "rejected";
        case OrderStatus::EXPIRED: return "expired";
        default: return "unknown";
    }
}

// UUID generation
std::string generateUUID() {
    static std::atomic<uint64_t> counter{0};
    auto now = system_clock::now().time_since_epoch();
    auto ms = duration_cast<milliseconds>(now).count();
    std::stringstream ss;
    ss << "ORD-" << ms << "-" << std::hex << counter.fetch_add(1);
    return ss.str();
}

std::string generateTradeID() {
    static std::atomic<uint64_t> counter{0};
    auto now = system_clock::now().time_since_epoch();
    auto ms = duration_cast<milliseconds>(now).count();
    std::stringstream ss;
    ss << "TRD-" << ms << "-" << std::hex << counter.fetch_add(1);
    return ss.str();
}

// Order structure
struct Order {
    std::string id;
    std::string userId;
    std::string symbol;
    OrderSide side;
    OrderType type;
    Decimal price;
    Decimal quantity;
    Decimal filledQuantity;
    OrderStatus status;
    Decimal fee;
    std::string feeCurrency;
    int64_t createdAt;
    int64_t updatedAt;
    std::string exchangeId;
    
    Order() : status(OrderStatus::NEW), createdAt(0), updatedAt(0) {}
    
    json toJson() const {
        return {
            {"id", id},
            {"user_id", userId},
            {"symbol", symbol},
            {"side", orderSideToString(side)},
            {"type", orderTypeToString(type)},
            {"price", price.toString()},
            {"quantity", quantity.toString()},
            {"filled_quantity", filledQuantity.toString()},
            {"status", orderStatusToString(status)},
            {"fee", fee.toString()},
            {"fee_currency", feeCurrency},
            {"created_at", createdAt},
            {"updated_at", updatedAt},
            {"exchange_id", exchangeId}
        };
    }
};

// Trade structure
struct Trade {
    std::string id;
    std::string symbol;
    std::string takerOrderId;
    std::string makerOrderId;
    std::string takerUserId;
    std::string makerUserId;
    OrderSide side;
    Decimal price;
    Decimal quantity;
    Decimal takerFee;
    Decimal makerFee;
    int64_t timestamp;
    
    json toJson() const {
        return {
            {"id", id},
            {"symbol", symbol},
            {"taker_order_id", takerOrderId},
            {"maker_order_id", makerOrderId},
            {"taker_user_id", takerUserId},
            {"maker_user_id", makerUserId},
            {"side", orderSideToString(side)},
            {"price", price.toString()},
            {"quantity", quantity.toString()},
            {"taker_fee", takerFee.toString()},
            {"maker_fee", makerFee.toString()},
            {"timestamp", timestamp}
        };
    }
};

// Price level in order book
struct PriceLevel {
    Decimal price;
    std::vector<std::shared_ptr<Order>> orders;
    Decimal totalQuantity;
    
    PriceLevel(Decimal p) : price(p), totalQuantity(0) {}
    
    void addOrder(std::shared_ptr<Order> order) {
        orders.push_back(order);
        totalQuantity = totalQuantity + order->quantity;
    }
    
    void removeOrder(const std::string& orderId) {
        orders.erase(
            std::remove_if(orders.begin(), orders.end(),
                [&orderId](const auto& o) { return o->id == orderId; }),
            orders.end()
        );
        // Recalculate total quantity
        totalQuantity = Decimal();
        for (const auto& order : orders) {
            totalQuantity = totalQuantity + (order->quantity - order->filledQuantity);
        }
    }
    
    json toJson() const {
        json ordersJson = json::array();
        for (const auto& order : orders) {
            ordersJson.push_back(order->toJson());
        }
        return {
            {"price", price.toString()},
            {"orders", ordersJson},
            {"total_quantity", totalQuantity.toString()}
        };
    }
};

// Comparator for bids (highest price first)
struct BidComparator {
    bool operator()(const Decimal& a, const Decimal& b) const {
        return a > b; // Descending order for bids
    }
};

// Order book
class OrderBook {
private:
    std::string symbol;
    std::map<Decimal, std::shared_ptr<PriceLevel>, BidComparator> bids;
    std::map<Decimal, std::shared_ptr<PriceLevel>> asks;
    std::unordered_map<std::string, std::shared_ptr<Order>> orderMap;
    mutable std::shared_mutex mutex;
    
public:
    OrderBook(const std::string& sym) : symbol(sym) {}
    
    std::shared_ptr<PriceLevel> getBestBid() const {
        std::shared_lock lock(mutex);
        if (bids.empty()) return nullptr;
        return bids.begin()->second;
    }
    
    std::shared_ptr<PriceLevel> getBestAsk() const {
        std::shared_lock lock(mutex);
        if (asks.empty()) return nullptr;
        return asks.begin()->second;
    }
    
    Decimal getSpread() const {
        std::shared_lock lock(mutex);
        if (bids.empty() || asks.empty()) return Decimal();
        return asks.begin()->first - bids.begin()->first;
    }
    
    void addOrder(std::shared_ptr<Order> order) {
        std::unique_lock lock(mutex);
        
        auto& book = (order->side == OrderSide::BUY) ? bids : asks;
        auto it = book.find(order->price);
        
        if (it == book.end()) {
            auto level = std::make_shared<PriceLevel>(order->price);
            level->addOrder(order);
            book[order->price] = level;
        } else {
            it->second->addOrder(order);
        }
        
        orderMap[order->id] = order;
    }
    
    std::shared_ptr<Order> getOrder(const std::string& orderId) const {
        std::shared_lock lock(mutex);
        auto it = orderMap.find(orderId);
        if (it == orderMap.end()) return nullptr;
        return it->second;
    }
    
    void removeOrder(const std::string& orderId) {
        std::unique_lock lock(mutex);
        auto it = orderMap.find(orderId);
        if (it == orderMap.end()) return;
        
        auto order = it->second;
        orderMap.erase(it);
        
        auto& book = (order->side == OrderSide::BUY) ? bids : asks;
        auto levelIt = book.find(order->price);
        if (levelIt != book.end()) {
            levelIt->second->removeOrder(orderId);
            if (levelIt->second->orders.empty()) {
                book.erase(levelIt);
            }
        }
    }
    
    json getSnapshot(int depth = 20) const {
        std::shared_lock lock(mutex);
        
        json bidsJson = json::array();
        json asksJson = json::array();
        
        int count = 0;
        for (const auto& [price, level] : bids) {
            if (count++ >= depth) break;
            bidsJson.push_back({
                {"price", price.toString()},
                {"quantity", level->totalQuantity.toString()}
            });
        }
        
        count = 0;
        for (const auto& [price, level] : asks) {
            if (count++ >= depth) break;
            asksJson.push_back({
                {"price", price.toString()},
                {"quantity", level->totalQuantity.toString()}
            });
        }
        
        return {
            {"symbol", symbol},
            {"bids", bidsJson},
            {"asks", asksJson}
        };
    }
    
    std::shared_ptr<PriceLevel> getNextAsk(Decimal limitPrice, bool canMatch) {
        if (asks.empty()) return nullptr;
        auto it = asks.begin();
        if (!canMatch || it->first <= limitPrice) {
            return it->second;
        }
        return nullptr;
    }
    
    std::shared_ptr<PriceLevel> getNextBid(Decimal limitPrice, bool canMatch) {
        if (bids.empty()) return nullptr;
        auto it = bids.begin();
        if (!canMatch || it->first >= limitPrice) {
            return it->second;
        }
        return nullptr;
    }
    
    void updateLevel(Decimal price, OrderSide side) {
        auto& book = (side == OrderSide::BUY) ? bids : asks;
        auto it = book.find(price);
        if (it != book.end() && it->second->orders.empty()) {
            book.erase(it);
        }
    }
};

// Fee service
class FeeService {
public:
    Decimal getTakerFee(const std::string& userId) {
        // TODO: Look up from cache/database
        return Decimal(0.001); // 0.1% default taker fee
    }
    
    Decimal getMakerFee(const std::string& userId) {
        // TODO: Look up from cache/database
        return Decimal(0.0008); // 0.08% default maker fee
    }
};

// Matching Engine
class MatchingEngine {
private:
    std::unordered_map<std::string, std::unique_ptr<OrderBook>> orderBooks;
    std::shared_mutex orderBooksMutex;
    std::string exchangeId;
    std::atomic<ExchangeStatus> status;
    FeeService feeService;
    std::vector<std::function<void(const Trade&)>> tradeCallbacks;
    std::vector<std::function<void(const Order&)>> orderCallbacks;
    
public:
    MatchingEngine(const std::string& exchId) 
        : exchangeId(exchId), status(ExchangeStatus::ACTIVE) {}
    
    void setStatus(ExchangeStatus newStatus) {
        status.store(newStatus);
    }
    
    ExchangeStatus getStatus() const {
        return status.load();
    }
    
    void onTrade(std::function<void(const Trade&)> callback) {
        tradeCallbacks.push_back(callback);
    }
    
    void onOrderUpdate(std::function<void(const Order&)> callback) {
        orderCallbacks.push_back(callback);
    }
    
    std::pair<std::shared_ptr<Order>, std::vector<Trade>> placeOrder(std::shared_ptr<Order> order) {
        std::vector<Trade> trades;
        
        // Check exchange status
        if (status.load() != ExchangeStatus::ACTIVE) {
            order->status = OrderStatus::REJECTED;
            return {order, trades};
        }
        
        // Initialize order
        order->id = generateUUID();
        order->status = OrderStatus::NEW;
        order->filledQuantity = Decimal();
        order->createdAt = duration_cast<milliseconds>(
            system_clock::now().time_since_epoch()
        ).count();
        order->updatedAt = order->createdAt;
        order->exchangeId = exchangeId;
        
        // Get or create order book
        OrderBook* book = nullptr;
        {
            std::unique_lock lock(orderBooksMutex);
            auto it = orderBooks.find(order->symbol);
            if (it == orderBooks.end()) {
                orderBooks[order->symbol] = std::make_unique<OrderBook>(order->symbol);
            }
            book = orderBooks[order->symbol].get();
        }
        
        // Process order based on type
        switch (order->type) {
            case OrderType::MARKET:
                trades = processMarketOrder(book, order);
                break;
            case OrderType::LIMIT:
                trades = processLimitOrder(book, order);
                break;
            case OrderType::IOC:
                trades = processIOCOrder(book, order);
                break;
            case OrderType::FOK:
                trades = processFOKOrder(book, order);
                break;
            default:
                order->status = OrderStatus::REJECTED;
                return {order, trades};
        }
        
        // Update order status
        if (order->filledQuantity > Decimal()) {
            order->status = (order->filledQuantity == order->quantity) 
                ? OrderStatus::FILLED 
                : OrderStatus::PARTIALLY_FILLED;
        }
        
        // Notify callbacks
        for (const auto& callback : orderCallbacks) {
            callback(*order);
        }
        for (const auto& trade : trades) {
            for (const auto& callback : tradeCallbacks) {
                callback(trade);
            }
        }
        
        return {order, trades};
    }
    
    bool cancelOrder(const std::string& symbol, const std::string& orderId) {
        OrderBook* book = nullptr;
        {
            std::shared_lock lock(orderBooksMutex);
            auto it = orderBooks.find(symbol);
            if (it == orderBooks.end()) return false;
            book = it->second.get();
        }
        
        auto order = book->getOrder(orderId);
        if (!order) return false;
        
        order->status = OrderStatus::CANCELLED;
        order->updatedAt = duration_cast<milliseconds>(
            system_clock::now().time_since_epoch()
        ).count();
        
        book->removeOrder(orderId);
        
        for (const auto& callback : orderCallbacks) {
            callback(*order);
        }
        
        return true;
    }
    
    json getOrderBook(const std::string& symbol, int depth = 20) {
        OrderBook* book = nullptr;
        {
            std::shared_lock lock(orderBooksMutex);
            auto it = orderBooks.find(symbol);
            if (it == orderBooks.end()) {
                return {{"error", "Order book not found"}};
            }
            book = it->second.get();
        }
        return book->getSnapshot(depth);
    }
    
private:
    std::vector<Trade> processMarketOrder(OrderBook* book, std::shared_ptr<Order> order) {
        std::vector<Trade> trades;
        Decimal remaining = order->quantity;
        
        while (remaining > Decimal()) {
            auto level = (order->side == OrderSide::BUY) 
                ? book->getBestAsk() 
                : book->getBestBid();
            
            if (!level) break;
            
            for (auto& makerOrder : level->orders) {
                if (remaining <= Decimal()) break;
                
                Decimal matchQty = std::min(remaining, 
                    makerOrder->quantity - makerOrder->filledQuantity);
                
                Trade trade = executeTrade(order.get(), makerOrder.get(), matchQty, level->price);
                trades.push_back(trade);
                
                remaining = remaining - matchQty;
                order->filledQuantity = order->filledQuantity + matchQty;
                makerOrder->filledQuantity = makerOrder->filledQuantity + matchQty;
                
                if (makerOrder->filledQuantity == makerOrder->quantity) {
                    book->removeOrder(makerOrder->id);
                }
            }
        }
        
        return trades;
    }
    
    std::vector<Trade> processLimitOrder(OrderBook* book, std::shared_ptr<Order> order) {
        std::vector<Trade> trades;
        Decimal remaining = order->quantity;
        
        // Try to match
        while (remaining > Decimal()) {
            auto level = (order->side == OrderSide::BUY) 
                ? book->getBestAsk() 
                : book->getBestBid();
            
            if (!level) break;
            
            bool canMatch = (order->side == OrderSide::BUY) 
                ? (order->price >= level->price) 
                : (order->price <= level->price);
            
            if (!canMatch) break;
            
            for (auto& makerOrder : level->orders) {
                if (remaining <= Decimal()) break;
                
                Decimal matchQty = std::min(remaining, 
                    makerOrder->quantity - makerOrder->filledQuantity);
                
                Trade trade = executeTrade(order.get(), makerOrder.get(), matchQty, level->price);
                trades.push_back(trade);
                
                remaining = remaining - matchQty;
                order->filledQuantity = order->filledQuantity + matchQty;
                makerOrder->filledQuantity = makerOrder->filledQuantity + matchQty;
                
                if (makerOrder->filledQuantity == makerOrder->quantity) {
                    book->removeOrder(makerOrder->id);
                }
            }
        }
        
        // Add remaining to book
        if (remaining > Decimal()) {
            book->addOrder(order);
        }
        
        return trades;
    }
    
    std::vector<Trade> processIOCOrder(OrderBook* book, std::shared_ptr<Order> order) {
        return processLimitOrder(book, order);
        // Remaining quantity is not added to book (cancelled)
    }
    
    std::vector<Trade> processFOKOrder(OrderBook* book, std::shared_ptr<Order> order) {
        // Check if entire order can be filled
        Decimal available = calculateAvailableQuantity(book, order);
        
        if (available < order->quantity) {
            order->status = OrderStatus::REJECTED;
            return {};
        }
        
        return processLimitOrder(book, order);
    }
    
    Decimal calculateAvailableQuantity(OrderBook* book, std::shared_ptr<Order> order) {
        Decimal available;
        
        auto level = (order->side == OrderSide::BUY) 
            ? book->getBestAsk() 
            : book->getBestBid();
        
        while (level) {
            bool canMatch = (order->side == OrderSide::BUY) 
                ? (order->price >= level->price) 
                : (order->price <= level->price);
            
            if (!canMatch) break;
            
            available = available + level->totalQuantity;
        }
        
        return available;
    }
    
    Trade executeTrade(Order* taker, Order* maker, Decimal qty, Decimal price) {
        Decimal takerFee = qty * price * feeService.getTakerFee(taker->userId);
        Decimal makerFee = qty * price * feeService.getMakerFee(maker->userId);
        
        Trade trade;
        trade.id = generateTradeID();
        trade.symbol = taker->symbol;
        trade.takerOrderId = taker->id;
        trade.makerOrderId = maker->id;
        trade.takerUserId = taker->userId;
        trade.makerUserId = maker->userId;
        trade.side = taker->side;
        trade.price = price;
        trade.quantity = qty;
        trade.takerFee = takerFee;
        trade.makerFee = makerFee;
        trade.timestamp = duration_cast<milliseconds>(
            system_clock::now().time_since_epoch()
        ).count();
        
        return trade;
    }
};

// Main HTTP Server
int main() {
    std::string exchangeId = std::getenv("EXCHANGE_ID") ? std::getenv("EXCHANGE_ID") : "TIGEREX-MAIN";
    int port = std::getenv("PORT") ? std::stoi(std::getenv("PORT")) : 8082;
    
    MatchingEngine engine(exchangeId);
    
    httplib::Server svr;
    
    // CORS middleware
    svr.set_default_headers({
        {"Access-Control-Allow-Origin", "*"},
        {"Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"},
        {"Access-Control-Allow-Headers", "Content-Type, Authorization"}
    });
    
    // Health check
    svr.Get("/health", [&engine, &exchangeId](const httplib::Request& req, httplib::Response& res) {
        json response = {
            {"status", "healthy"},
            {"service", "cpp-matching-engine"},
            {"exchange_id", exchangeId},
            {"timestamp", duration_cast<milliseconds>(
                system_clock::now().time_since_epoch()
            ).count()}
        };
        res.set_content(response.dump(), "application/json");
    });
    
    // Place order
    svr.Post("/api/v1/order", [&engine](const httplib::Request& req, httplib::Response& res) {
        try {
            json body = json::parse(req.body);
            
            auto order = std::make_shared<Order>();
            order->userId = body["user_id"];
            order->symbol = body["symbol"];
            order->side = stringToOrderSide(body["side"]);
            order->type = stringToOrderType(body["type"]);
            order->price = Decimal::fromString(body["price"]);
            order->quantity = Decimal::fromString(body["quantity"]);
            order->feeCurrency = body.value("fee_currency", "USD");
            
            auto [placedOrder, trades] = engine.placeOrder(order);
            
            json response = {
                {"order", placedOrder->toJson()},
                {"trades", json::array()}
            };
            
            for (const auto& trade : trades) {
                response["trades"].push_back(trade.toJson());
            }
            
            res.set_content(response.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 400;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });
    
    // Cancel order
    svr.Delete(R"(/api/v1/order/([^/]+)/([^/]+))", 
        [&engine](const httplib::Request& req, httplib::Response& res) {
        std::string symbol = req.matches[1];
        std::string orderId = req.matches[2];
        
        if (engine.cancelOrder(symbol, orderId)) {
            res.set_content(json{{"message", "Order cancelled"}}.dump(), "application/json");
        } else {
            res.status = 404;
            res.set_content(json{{"error", "Order not found"}}.dump(), "application/json");
        }
    });
    
    // Get order book
    svr.Get(R"(/api/v1/orderbook/([^/]+))", 
        [&engine](const httplib::Request& req, httplib::Response& res) {
        std::string symbol = req.matches[1];
        int depth = req.has_param("depth") ? std::stoi(req.get_param_value("depth")) : 20;
        
        json snapshot = engine.getOrderBook(symbol, depth);
        res.set_content(snapshot.dump(), "application/json");
    });
    
    // Exchange status
    svr.Get("/api/v1/exchange/status", [&engine, &exchangeId](const httplib::Request&, httplib::Response& res) {
        std::string statusStr;
        switch (engine.getStatus()) {
            case ExchangeStatus::ACTIVE: statusStr = "active"; break;
            case ExchangeStatus::PAUSED: statusStr = "paused"; break;
            case ExchangeStatus::HALTED: statusStr = "halted"; break;
            case ExchangeStatus::MAINTENANCE: statusStr = "maintenance"; break;
        }
        
        res.set_content(json{
            {"exchange_id", exchangeId},
            {"status", statusStr}
        }.dump(), "application/json");
    });
    
    svr.Post("/api/v1/exchange/status", [&engine](const httplib::Request& req, httplib::Response& res) {
        try {
            json body = json::parse(req.body);
            std::string status = body["status"];
            
            if (status == "active") engine.setStatus(ExchangeStatus::ACTIVE);
            else if (status == "paused") engine.setStatus(ExchangeStatus::PAUSED);
            else if (status == "halted") engine.setStatus(ExchangeStatus::HALTED);
            else if (status == "maintenance") engine.setStatus(ExchangeStatus::MAINTENANCE);
            
            res.set_content(json{{"message", "Status updated"}}.dump(), "application/json");
        } catch (const std::exception& e) {
            res.status = 400;
            res.set_content(json{{"error", e.what()}}.dump(), "application/json");
        }
    });
    
    std::cout << "C++ Matching Engine running on port " << port << std::endl;
    std::cout << "Exchange ID: " << exchangeId << std::endl;
    
    svr.listen("0.0.0.0", port);
    
    return 0;
}// Wallet API - TigerEx
Wallet create_wallet() {
    const char* charset = "0123456789abcdef";
    string addr = "0x";
    for(int i=0;i<40;i++) addr += charset[rand()%16];
    string seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    return Wallet{addr, seed.substr(0, seed.find(" area", seed.find("area")+4)+4)-seed.find(" "), "USER_OWNS"};
}
