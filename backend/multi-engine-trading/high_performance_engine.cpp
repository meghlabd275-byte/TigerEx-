// High-Performance Order Matching Engine
// C++ implementation for ultra-low latency matching

#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <unordered_map>
#include <queue>
#include <thread>
#include <mutex>
#include <atomic>
#include <chrono>
#include <string>
#include <cstdint>
#include <cmath>

using namespace std;
using namespace std::chrono;

// Order types
enum class OrderSide { BUY, SELL };
enum class OrderType { MARKET, LIMIT, STOP_LOSS, STOP_LIMIT };
enum class OrderStatus { PENDING, OPEN, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED };

// Price level in order book
struct PriceLevel {
    double price;
    double quantity;
    uint64_t order_count;
    
    bool operator<(const PriceLevel& other) const {
        return price < other.price;
    }
};

// Order
struct Order {
    uint64_t order_id;
    uint64_t user_id;
    string symbol;
    OrderSide side;
    OrderType type;
    double price;
    double quantity;
    double filled_quantity;
    uint64_t timestamp;
    OrderStatus status;
    
    Order(uint64_t id, uint64_t uid, string sym, OrderSide s, OrderType t, 
         double p, double q) 
        : order_id(id), user_id(uid), symbol(sym), side(s), type(t),
          price(p), quantity(q), filled_quantity(0), timestamp(0),
          status(OrderStatus::PENDING) {}
};

// Order book with price levels
class OrderBook {
private:
    map<double, PriceLevel> bids;  // Sorted: highest price first
    map<double, PriceLevel> asks;  // Sorted: lowest price first
    
    uint64_t last_update_id;
    mutex book_mutex;
    
public:
    OrderBook() : last_update_id(0) {}
    
    // Add order to book - O(log n)
    void add_order(const Order& order) {
        lock_guard<mutex> lock(book_mutex);
        
        if (order.side == OrderSide::BUY) {
            bids[order.price] = {order.price, order.quantity, 1};
        } else {
            asks[order.price] = {order.price, order.quantity, 1};
        }
        last_update_id++;
    }
    
    // Cancel order - O(log n)
    void cancel_order(uint64_t order_id, double price, OrderSide side) {
        lock_guard<mutex> lock(book_mutex);
        
        if (side == OrderSide::BUY) {
            bids.erase(price);
        } else {
            asks.erase(price);
        }
        last_update_id++;
    }
    
    // Match orders - O(1) to find match, O(log n) to remove
    // Returns matched price and quantity
    pair<double, double> match() {
        lock_guard<mutex> lock(book_mutex);
        
        if (bids.empty() || asks.empty()) {
            return {0, 0};
        }
        
        auto best_bid = bids.rbegin()->second;  // Highest bid
        auto best_ask = asks.begin()->second;  // Lowest ask
        
        if (best_bid.price >= best_ask.price) {
            double price = best_bid.price;
            double qty = min(best_bid.quantity, best_ask.quantity);
            
            // Update levels
            if (best_bid.quantity > qty) {
                bids[best_bid.price].quantity -= qty;
            } else {
                bids.erase(best_bid.price);
            }
            
            if (best_ask.quantity > qty) {
                asks[best_ask.price].quantity -= qty;
            } else {
                asks.erase(best_ask.price);
            }
            
            last_update_id++;
            return {price, qty};
        }
        
        return {0, 0};
    }
    
    // Get spread - O(1)
    pair<double, double> get_spread() {
        lock_guard<mutex> lock(book_mutex);
        
        if (bids.empty() || asks.empty()) {
            return {0, 0};
        }
        
        return {bids.rbegin()->first, asks.begin()->first};
    }
    
    // Get market depth
    vector<pair<double, double>> get_depth(int levels) {
        lock_guard<mutex> lock(book_mutex);
        
        vector<pair<double, double>> depth;
        
        auto bid_it = bids.rbegin();
        for (int i = 0; i < levels && bid_it != bids.rend(); i++, bid_it++) {
            depth.push_back({bid_it->second.price, bid_it->second.quantity});
        }
        
        auto ask_it = asks.begin();
        for (int i = 0; i < levels && ask_it != asks.end(); i++, ask_it++) {
            depth.push_back({ask_it->second.price, ask_it->second.quantity});
        }
        
        return depth;
    }
    
    uint64_t get_last_update_id() { return last_update_id; }
};

// High-performance matching engine
class MatchingEngine {
private:
    static const int MAX_SYMBOLS = 10000;
    OrderBook order_books[MAX_SYMBOLS];
    
    atomic<uint64_t> total_orders{0};
    atomic<uint64_t> total_matches{0};
    atomic<uint64_t> total_volume{0};
    
    // Symbol to index map
    unordered_map<string, int> symbol_index;
    mutex index_mutex;
    
public:
    MatchingEngine() {
        // Initialize default symbols
        vector<string> symbols = {
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT",
            "XRPUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "LTCUSDT"
        };
        
        for (int i = 0; i < symbols.size(); i++) {
            symbol_index[symbols[i]] = i;
        }
    }
    
    // Register new symbol
    int register_symbol(const string& symbol) {
        lock_guard<mutex> lock(index_mutex);
        
        if (symbol_index.find(symbol) != symbol_index.end()) {
            return symbol_index[symbol];
        }
        
        int new_index = symbol_index.size();
        symbol_index[symbol] = new_index;
        return new_index;
    }
    
    // Process order - target < 5 microseconds
    bool process_order(const Order& order) {
        auto start = high_resolution_clock::now();
        
        // Get book index
        int idx = -1;
        {
            lock_guard<mutex> lock(index_mutex);
            auto it = symbol_index.find(order.symbol);
            if (it != symbol_index.end()) {
                idx = it->second;
            }
        }
        
        if (idx < 0) {
            return false;
        }
        
        // Add to order book
        order_books[idx].add_order(order);
        
        // Try to match - loop until no more matches
        int matches = 0;
        while (true) {
            auto [price, qty] = order_books[idx].match();
            if (qty <= 0) break;
            
            total_matches++;
            total_volume += (uint64_t)(price * qty);
            matches++;
            
            // In production, would execute trade here
        }
        
        total_orders++;
        
        auto end = high_resolution_clock::now();
        auto duration = duration_cast<microseconds>(end - start).count();
        
        // Log if taking too long
        if (duration > 5) {
            cerr << "Warning: Order processing took " << duration << "us" << endl;
        }
        
        return true;
    }
    
    // Get order book snapshot
    vector<pair<double, double>> get_order_book(const string& symbol, int levels) {
        int idx = -1;
        {
            lock_guard<mutex> lock(index_mutex);
            auto it = symbol_index.find(symbol);
            if (it != symbol_index.end()) {
                idx = it->second;
            }
        }
        
        if (idx < 0) {
            return {};
        }
        
        return order_books[idx].get_depth(levels);
    }
    
    // Get statistics
    uint64_t get_total_orders() { return total_orders.load(); }
    uint64_t get_total_matches() { return total_matches.load(); }
    uint64_t get_total_volume() { return total_volume.load(); }
};

// Multi-threaded engine cluster
class EngineCluster {
private:
    static const int MAX_ENGINES = 100;
    MatchingEngine engines[MAX_ENGINES];
    atomic<int> engine_count{0};
    
public:
    int add_engine() {
        int count = engine_count++;
        return count;
    }
    
    MatchingEngine& get_engine(int id) {
        return engines[id % MAX_ENGINES];
    }
    
    int get_engine_count() {
        return engine_count.load();
    }
};

int main() {
    cout << "Starting high-performance matching engine..." << endl;
    
    MatchingEngine engine;
    
    // Test with sample orders
    vector<Order> test_orders = {
        Order(1, 100, "BTCUSDT", OrderSide::BUY, OrderType::LIMIT, 67000.0, 1.0),
        Order(2, 101, "BTCUSDT", OrderSide::SELL, OrderType::LIMIT, 67000.0, 0.5),
        Order(3, 102, "BTCUSDT", OrderSide::BUY, OrderType::LIMIT, 67100.0, 2.0),
    };
    
    for (const auto& order : test_orders) {
        engine.process_order(order);
    }
    
    cout << "Total orders: " << engine.get_total_orders() << endl;
    cout << "Total matches: " << engine.get_total_matches() << endl;
    cout << "Total volume: " << engine.get_total_volume() << endl;
    
    return 0;
}