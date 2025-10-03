#pragma once

#include <atomic>
#include <memory>
#include <unordered_map>
#include <vector>
#include <queue>
#include <mutex>
#include <shared_mutex>
#include <chrono>
#include <string>
#include <cstdint>

namespace tigerex {

// Ultra-low latency order structure
struct Order {
    uint64_t order_id;
    uint64_t user_id;
    std::string symbol;
    double price;
    double quantity;
    double filled_quantity;
    enum class Side : uint8_t { BUY, SELL } side;
    enum class Type : uint8_t { MARKET, LIMIT, STOP_LOSS, TAKE_PROFIT } type;
    enum class Status : uint8_t { NEW, PARTIAL, FILLED, CANCELLED } status;
    std::chrono::nanoseconds timestamp;
    
    Order() = default;
    Order(uint64_t oid, uint64_t uid, const std::string& sym, 
          double p, double q, Side s, Type t)
        : order_id(oid), user_id(uid), symbol(sym), price(p), 
          quantity(q), filled_quantity(0.0), side(s), type(t),
          status(Status::NEW),
          timestamp(std::chrono::high_resolution_clock::now().time_since_epoch()) {}
};

// Lock-free order book level
struct PriceLevel {
    double price;
    double total_quantity;
    std::vector<std::shared_ptr<Order>> orders;
    
    PriceLevel(double p) : price(p), total_quantity(0.0) {}
};

// High-performance order book
class OrderBook {
private:
    std::string symbol_;
    std::map<double, PriceLevel, std::greater<double>> bids_; // Buy orders (descending)
    std::map<double, PriceLevel, std::less<double>> asks_;    // Sell orders (ascending)
    mutable std::shared_mutex mutex_;
    
    std::atomic<uint64_t> total_bid_volume_{0};
    std::atomic<uint64_t> total_ask_volume_{0};
    std::atomic<double> last_traded_price_{0.0};
    
public:
    explicit OrderBook(const std::string& symbol);
    
    // Core operations (microsecond latency)
    bool add_order(std::shared_ptr<Order> order);
    bool cancel_order(uint64_t order_id);
    bool modify_order(uint64_t order_id, double new_price, double new_quantity);
    
    // Matching engine
    std::vector<std::pair<std::shared_ptr<Order>, std::shared_ptr<Order>>> 
        match_orders(std::shared_ptr<Order> incoming_order);
    
    // Market data
    std::pair<double, double> get_best_bid_ask() const;
    std::vector<std::pair<double, double>> get_depth(size_t levels) const;
    double get_last_price() const { return last_traded_price_.load(); }
    
    // Statistics
    uint64_t get_total_bid_volume() const { return total_bid_volume_.load(); }
    uint64_t get_total_ask_volume() const { return total_ask_volume_.load(); }
};

// Ultra-fast matching engine
class MatchingEngine {
private:
    std::unordered_map<std::string, std::unique_ptr<OrderBook>> order_books_;
    mutable std::shared_mutex books_mutex_;
    
    std::atomic<uint64_t> next_order_id_{1};
    std::atomic<uint64_t> orders_processed_{0};
    std::atomic<uint64_t> trades_executed_{0};
    
    // Performance monitoring
    std::atomic<uint64_t> total_latency_ns_{0};
    std::atomic<uint64_t> max_latency_ns_{0};
    std::atomic<uint64_t> min_latency_ns_{UINT64_MAX};
    
    // Memory pool for order allocation
    class MemoryPool;
    std::unique_ptr<MemoryPool> memory_pool_;
    
public:
    MatchingEngine();
    ~MatchingEngine();
    
    // Order management (sub-microsecond latency target)
    uint64_t submit_order(uint64_t user_id, const std::string& symbol,
                         double price, double quantity,
                         Order::Side side, Order::Type type);
    
    bool cancel_order(uint64_t order_id, const std::string& symbol);
    bool modify_order(uint64_t order_id, const std::string& symbol,
                     double new_price, double new_quantity);
    
    // Market data
    std::pair<double, double> get_best_bid_ask(const std::string& symbol) const;
    std::vector<std::pair<double, double>> get_order_book_depth(
        const std::string& symbol, size_t levels) const;
    
    // Statistics
    struct Statistics {
        uint64_t orders_processed;
        uint64_t trades_executed;
        uint64_t avg_latency_ns;
        uint64_t max_latency_ns;
        uint64_t min_latency_ns;
        double throughput_ops_per_sec;
    };
    
    Statistics get_statistics() const;
    void reset_statistics();
    
    // Symbol management
    void add_symbol(const std::string& symbol);
    void remove_symbol(const std::string& symbol);
    std::vector<std::string> get_symbols() const;
    
private:
    void process_matched_orders(
        const std::vector<std::pair<std::shared_ptr<Order>, std::shared_ptr<Order>>>& matches);
    
    void update_latency_stats(uint64_t latency_ns);
};

// Lock-free queue for order processing
template<typename T>
class LockFreeQueue {
private:
    struct Node {
        std::shared_ptr<T> data;
        std::atomic<Node*> next;
        Node() : next(nullptr) {}
    };
    
    std::atomic<Node*> head_;
    std::atomic<Node*> tail_;
    
public:
    LockFreeQueue() {
        Node* dummy = new Node();
        head_.store(dummy);
        tail_.store(dummy);
    }
    
    ~LockFreeQueue() {
        while (Node* old_head = head_.load()) {
            head_.store(old_head->next);
            delete old_head;
        }
    }
    
    void enqueue(std::shared_ptr<T> data) {
        Node* new_node = new Node();
        new_node->data = data;
        
        Node* old_tail = tail_.load();
        while (!tail_.compare_exchange_weak(old_tail, new_node)) {
            old_tail = tail_.load();
        }
        old_tail->next.store(new_node);
    }
    
    std::shared_ptr<T> dequeue() {
        Node* old_head = head_.load();
        Node* next = old_head->next.load();
        
        if (next == nullptr) {
            return nullptr;
        }
        
        if (head_.compare_exchange_strong(old_head, next)) {
            std::shared_ptr<T> data = next->data;
            delete old_head;
            return data;
        }
        
        return nullptr;
    }
};

} // namespace tigerex