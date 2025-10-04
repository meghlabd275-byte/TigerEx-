#include "matching_engine.hpp"
#include <algorithm>
#include <iostream>
#include <sstream>

namespace tigerex {

// OrderBook Implementation
OrderBook::OrderBook(const std::string& symbol) : symbol_(symbol) {}

bool OrderBook::add_order(std::shared_ptr<Order> order) {
    std::unique_lock<std::shared_mutex> lock(mutex_);
    
    auto& levels = (order->side == Order::Side::BUY) ? bids_ : asks_;
    auto& volume = (order->side == Order::Side::BUY) ? total_bid_volume_ : total_ask_volume_;
    
    auto it = levels.find(order->price);
    if (it == levels.end()) {
        levels.emplace(order->price, PriceLevel(order->price));
        it = levels.find(order->price);
    }
    
    it->second.orders.push_back(order);
    it->second.total_quantity += order->quantity;
    volume.fetch_add(static_cast<uint64_t>(order->quantity * 1e8));
    
    return true;
}

bool OrderBook::cancel_order(uint64_t order_id) {
    std::unique_lock<std::shared_mutex> lock(mutex_);
    
    // Search in bids
    for (auto& [price, level] : bids_) {
        auto it = std::find_if(level.orders.begin(), level.orders.end(),
            [order_id](const auto& order) { return order->order_id == order_id; });
        
        if (it != level.orders.end()) {
            level.total_quantity -= (*it)->quantity;
            total_bid_volume_.fetch_sub(static_cast<uint64_t>((*it)->quantity * 1e8));
            level.orders.erase(it);
            
            if (level.orders.empty()) {
                bids_.erase(price);
            }
            return true;
        }
    }
    
    // Search in asks
    for (auto& [price, level] : asks_) {
        auto it = std::find_if(level.orders.begin(), level.orders.end(),
            [order_id](const auto& order) { return order->order_id == order_id; });
        
        if (it != level.orders.end()) {
            level.total_quantity -= (*it)->quantity;
            total_ask_volume_.fetch_sub(static_cast<uint64_t>((*it)->quantity * 1e8));
            level.orders.erase(it);
            
            if (level.orders.empty()) {
                asks_.erase(price);
            }
            return true;
        }
    }
    
    return false;
}

std::vector<std::pair<std::shared_ptr<Order>, std::shared_ptr<Order>>> 
OrderBook::match_orders(std::shared_ptr<Order> incoming_order) {
    std::unique_lock<std::shared_mutex> lock(mutex_);
    
    std::vector<std::pair<std::shared_ptr<Order>, std::shared_ptr<Order>>> matches;
    
    if (incoming_order->side == Order::Side::BUY) {
        // Match with asks
        while (!asks_.empty() && incoming_order->filled_quantity < incoming_order->quantity) {
            auto& [price, level] = *asks_.begin();
            
            if (incoming_order->type == Order::Type::LIMIT && 
                price > incoming_order->price) {
                break;
            }
            
            while (!level.orders.empty() && 
                   incoming_order->filled_quantity < incoming_order->quantity) {
                auto& resting_order = level.orders.front();
                
                double match_quantity = std::min(
                    incoming_order->quantity - incoming_order->filled_quantity,
                    resting_order->quantity - resting_order->filled_quantity
                );
                
                incoming_order->filled_quantity += match_quantity;
                resting_order->filled_quantity += match_quantity;
                
                matches.emplace_back(incoming_order, resting_order);
                
                last_traded_price_.store(price);
                
                if (resting_order->filled_quantity >= resting_order->quantity) {
                    resting_order->status = Order::Status::FILLED;
                    level.orders.erase(level.orders.begin());
                    level.total_quantity -= resting_order->quantity;
                    total_ask_volume_.fetch_sub(
                        static_cast<uint64_t>(resting_order->quantity * 1e8));
                } else {
                    resting_order->status = Order::Status::PARTIAL;
                }
            }
            
            if (level.orders.empty()) {
                asks_.erase(asks_.begin());
            }
        }
    } else {
        // Match with bids
        while (!bids_.empty() && incoming_order->filled_quantity < incoming_order->quantity) {
            auto& [price, level] = *bids_.begin();
            
            if (incoming_order->type == Order::Type::LIMIT && 
                price < incoming_order->price) {
                break;
            }
            
            while (!level.orders.empty() && 
                   incoming_order->filled_quantity < incoming_order->quantity) {
                auto& resting_order = level.orders.front();
                
                double match_quantity = std::min(
                    incoming_order->quantity - incoming_order->filled_quantity,
                    resting_order->quantity - resting_order->filled_quantity
                );
                
                incoming_order->filled_quantity += match_quantity;
                resting_order->filled_quantity += match_quantity;
                
                matches.emplace_back(incoming_order, resting_order);
                
                last_traded_price_.store(price);
                
                if (resting_order->filled_quantity >= resting_order->quantity) {
                    resting_order->status = Order::Status::FILLED;
                    level.orders.erase(level.orders.begin());
                    level.total_quantity -= resting_order->quantity;
                    total_bid_volume_.fetch_sub(
                        static_cast<uint64_t>(resting_order->quantity * 1e8));
                } else {
                    resting_order->status = Order::Status::PARTIAL;
                }
            }
            
            if (level.orders.empty()) {
                bids_.erase(bids_.begin());
            }
        }
    }
    
    if (incoming_order->filled_quantity >= incoming_order->quantity) {
        incoming_order->status = Order::Status::FILLED;
    } else if (incoming_order->filled_quantity > 0) {
        incoming_order->status = Order::Status::PARTIAL;
    }
    
    return matches;
}

std::pair<double, double> OrderBook::get_best_bid_ask() const {
    std::shared_lock<std::shared_mutex> lock(mutex_);
    
    double best_bid = bids_.empty() ? 0.0 : bids_.begin()->first;
    double best_ask = asks_.empty() ? 0.0 : asks_.begin()->first;
    
    return {best_bid, best_ask};
}

std::vector<std::pair<double, double>> OrderBook::get_depth(size_t levels) const {
    std::shared_lock<std::shared_mutex> lock(mutex_);
    
    std::vector<std::pair<double, double>> depth;
    depth.reserve(levels * 2);
    
    size_t count = 0;
    for (const auto& [price, level] : bids_) {
        if (count++ >= levels) break;
        depth.emplace_back(price, level.total_quantity);
    }
    
    count = 0;
    for (const auto& [price, level] : asks_) {
        if (count++ >= levels) break;
        depth.emplace_back(price, level.total_quantity);
    }
    
    return depth;
}

// MatchingEngine Implementation
MatchingEngine::MatchingEngine() {
    // Initialize with common trading pairs
    add_symbol("BTCUSDT");
    add_symbol("ETHUSDT");
    add_symbol("BNBUSDT");
}

MatchingEngine::~MatchingEngine() = default;

uint64_t MatchingEngine::submit_order(uint64_t user_id, const std::string& symbol,
                                      double price, double quantity,
                                      Order::Side side, Order::Type type) {
    auto start = std::chrono::high_resolution_clock::now();
    
    uint64_t order_id = next_order_id_.fetch_add(1);
    auto order = std::make_shared<Order>(order_id, user_id, symbol, price, quantity, side, type);
    
    std::shared_lock<std::shared_mutex> lock(books_mutex_);
    auto it = order_books_.find(symbol);
    if (it == order_books_.end()) {
        return 0; // Invalid symbol
    }
    
    // Match order
    auto matches = it->second->match_orders(order);
    
    // If not fully filled and it's a limit order, add to book
    if (order->status != Order::Status::FILLED && type == Order::Type::LIMIT) {
        it->second->add_order(order);
    }
    
    // Process matches
    if (!matches.empty()) {
        process_matched_orders(matches);
        trades_executed_.fetch_add(matches.size());
    }
    
    orders_processed_.fetch_add(1);
    
    auto end = std::chrono::high_resolution_clock::now();
    auto latency = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
    update_latency_stats(latency);
    
    return order_id;
}

bool MatchingEngine::cancel_order(uint64_t order_id, const std::string& symbol) {
    std::shared_lock<std::shared_mutex> lock(books_mutex_);
    auto it = order_books_.find(symbol);
    if (it == order_books_.end()) {
        return false;
    }
    
    return it->second->cancel_order(order_id);
}

std::pair<double, double> MatchingEngine::get_best_bid_ask(const std::string& symbol) const {
    std::shared_lock<std::shared_mutex> lock(books_mutex_);
    auto it = order_books_.find(symbol);
    if (it == order_books_.end()) {
        return {0.0, 0.0};
    }
    
    return it->second->get_best_bid_ask();
}

void MatchingEngine::add_symbol(const std::string& symbol) {
    std::unique_lock<std::shared_mutex> lock(books_mutex_);
    if (order_books_.find(symbol) == order_books_.end()) {
        order_books_[symbol] = std::make_unique<OrderBook>(symbol);
    }
}

void MatchingEngine::process_matched_orders(
    const std::vector<std::pair<std::shared_ptr<Order>, std::shared_ptr<Order>>>& matches) {
    // Process trade execution, update balances, send notifications, etc.
    for (const auto& [taker, maker] : matches) {
        // Trade execution logic here
        // This would typically:
        // 1. Update user balances
        // 2. Record trade in database
        // 3. Send WebSocket notifications
        // 4. Update market data
    }
}

void MatchingEngine::update_latency_stats(uint64_t latency_ns) {
    total_latency_ns_.fetch_add(latency_ns);
    
    uint64_t current_max = max_latency_ns_.load();
    while (latency_ns > current_max && 
           !max_latency_ns_.compare_exchange_weak(current_max, latency_ns)) {}
    
    uint64_t current_min = min_latency_ns_.load();
    while (latency_ns < current_min && 
           !min_latency_ns_.compare_exchange_weak(current_min, latency_ns)) {}
}

MatchingEngine::Statistics MatchingEngine::get_statistics() const {
    uint64_t orders = orders_processed_.load();
    uint64_t trades = trades_executed_.load();
    uint64_t total_latency = total_latency_ns_.load();
    
    return {
        orders,
        trades,
        orders > 0 ? total_latency / orders : 0,
        max_latency_ns_.load(),
        min_latency_ns_.load(),
        0.0 // Calculate throughput based on time window
    };
}

} // namespace tigerex