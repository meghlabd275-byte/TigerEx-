package com.tigerex.queue;

import io.nats.client.*;
import io.redis.clients.jedis.Jedis;
import io.redis.clients.jedis.JedisPool;
import io.redis.clients.jedis.JedisPoolConfig;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.logging.Logger;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.annotations.SerializedName;

/**
 * TigerEx Java Queue Service
 * High-performance message queue service for event processing
 * Part of TigerEx Multi-Language Microservices Architecture
 */

public class QueueService {
    private static final Logger logger = Logger.getLogger(QueueService.class.getName());
    private static final Gson gson = new GsonBuilder().setPrettyPrinting().create();
    
    // Configuration
    private final String exchangeId;
    private final String natsUrl;
    private final String redisUrl;
    private final int workerThreads;
    
    // Connections
    private Connection natsConnection;
    private JedisPool jedisPool;
    private ExecutorService executorService;
    
    // Statistics
    private final AtomicLong messagesProcessed = new AtomicLong(0);
    private final AtomicLong messagesFailed = new AtomicLong(0);
    private final Map<String, AtomicLong> queueCounters = new ConcurrentHashMap<>();
    
    // Message types
    public enum MessageType {
        ORDER_NEW,
        ORDER_CANCEL,
        ORDER_UPDATE,
        TRADE_EXECUTE,
        TRADE_SETTLE,
        BALANCE_UPDATE,
        WITHDRAWAL_REQUEST,
        DEPOSIT_CONFIRM,
        FEE_COLLECT,
        NOTIFICATION_SEND,
        KYC_UPDATE,
        AUDIT_LOG,
        SYSTEM_ALERT
    }
    
    // Message priorities
    public enum Priority {
        LOW(1),
        NORMAL(5),
        HIGH(10),
        CRITICAL(20);
        
        final int value;
        Priority(int value) { this.value = value; }
    }
    
    /**
     * Base message structure
     */
    public static class QueueMessage {
        @SerializedName("id")
        private String id;
        
        @SerializedName("type")
        private MessageType type;
        
        @SerializedName("priority")
        private Priority priority;
        
        @SerializedName("exchange_id")
        private String exchangeId;
        
        @SerializedName("timestamp")
        private long timestamp;
        
        @SerializedName("retry_count")
        private int retryCount;
        
        @SerializedName("payload")
        private Map<String, Object> payload;
        
        @SerializedName("metadata")
        private Map<String, String> metadata;
        
        public QueueMessage() {
            this.id = UUID.randomUUID().toString();
            this.timestamp = Instant.now().toEpochMilli();
            this.retryCount = 0;
            this.payload = new HashMap<>();
            this.metadata = new HashMap<>();
            this.priority = Priority.NORMAL;
        }
        
        // Getters and setters
        public String getId() { return id; }
        public void setId(String id) { this.id = id; }
        public MessageType getType() { return type; }
        public void setType(MessageType type) { this.type = type; }
        public Priority getPriority() { return priority; }
        public void setPriority(Priority priority) { this.priority = priority; }
        public String getExchangeId() { return exchangeId; }
        public void setExchangeId(String exchangeId) { this.exchangeId = exchangeId; }
        public long getTimestamp() { return timestamp; }
        public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
        public int getRetryCount() { return retryCount; }
        public void setRetryCount(int retryCount) { this.retryCount = retryCount; }
        public Map<String, Object> getPayload() { return payload; }
        public void setPayload(Map<String, Object> payload) { this.payload = payload; }
        public Map<String, String> getMetadata() { return metadata; }
        public void setMetadata(Map<String, String> metadata) { this.metadata = metadata; }
    }
    
    /**
     * Order message
     */
    public static class OrderMessage extends QueueMessage {
        private String orderId;
        private String userId;
        private String symbol;
        private String side;
        private String orderType;
        private double price;
        private double quantity;
        
        public OrderMessage() {
            super();
            setType(MessageType.ORDER_NEW);
        }
        
        // Getters and setters
        public String getOrderId() { return orderId; }
        public void setOrderId(String orderId) { this.orderId = orderId; }
        public String getUserId() { return userId; }
        public void setUserId(String userId) { this.userId = userId; }
        public String getSymbol() { return symbol; }
        public void setSymbol(String symbol) { this.symbol = symbol; }
        public String getSide() { return side; }
        public void setSide(String side) { this.side = side; }
        public String getOrderType() { return orderType; }
        public void setOrderType(String orderType) { this.orderType = orderType; }
        public double getPrice() { return price; }
        public void setPrice(double price) { this.price = price; }
        public double getQuantity() { return quantity; }
        public void setQuantity(double quantity) { this.quantity = quantity; }
    }
    
    /**
     * Trade message
     */
    public static class TradeMessage extends QueueMessage {
        private String tradeId;
        private String symbol;
        private String takerOrderId;
        private String makerOrderId;
        private String takerUserId;
        private String makerUserId;
        private double price;
        private double quantity;
        private double takerFee;
        private double makerFee;
        
        public TradeMessage() {
            super();
            setType(MessageType.TRADE_EXECUTE);
        }
        
        // Getters and setters...
        public String getTradeId() { return tradeId; }
        public void setTradeId(String tradeId) { this.tradeId = tradeId; }
        public String getSymbol() { return symbol; }
        public void setSymbol(String symbol) { this.symbol = symbol; }
        public String getTakerOrderId() { return takerOrderId; }
        public void setTakerOrderId(String takerOrderId) { this.takerOrderId = takerOrderId; }
        public String getMakerOrderId() { return makerOrderId; }
        public void setMakerOrderId(String makerOrderId) { this.makerOrderId = makerOrderId; }
        public String getTakerUserId() { return takerUserId; }
        public void setTakerUserId(String takerUserId) { this.takerUserId = takerUserId; }
        public String getMakerUserId() { return makerUserId; }
        public void setMakerUserId(String makerUserId) { this.makerUserId = makerUserId; }
        public double getPrice() { return price; }
        public void setPrice(double price) { this.price = price; }
        public double getQuantity() { return quantity; }
        public void setQuantity(double quantity) { this.quantity = quantity; }
        public double getTakerFee() { return takerFee; }
        public void setTakerFee(double takerFee) { this.takerFee = takerFee; }
        public double getMakerFee() { return makerFee; }
        public void setMakerFee(double makerFee) { this.makerFee = makerFee; }
    }
    
    /**
     * Message handler interface
     */
    @FunctionalInterface
    public interface MessageHandler {
        void handle(QueueMessage message) throws Exception;
    }
    
    // Message handlers
    private final Map<MessageType, MessageHandler> handlers = new ConcurrentHashMap<>();
    
    // Dead letter queue
    private final BlockingQueue<QueueMessage> deadLetterQueue = new LinkedBlockingQueue<>();
    
    /**
     * Constructor
     */
    public QueueService(String exchangeId, String natsUrl, String redisUrl, int workerThreads) {
        this.exchangeId = exchangeId;
        this.natsUrl = natsUrl;
        this.redisUrl = redisUrl;
        this.workerThreads = workerThreads;
    }
    
    /**
     * Initialize the queue service
     */
    public void start() throws IOException, InterruptedException {
        // Initialize NATS connection
        Options options = new Options.Builder()
            .server(natsUrl)
            .connectionTimeout(Duration.ofSeconds(5))
            .reconnectWait(Duration.ofSeconds(1))
            .maxReconnects(10)
            .build();
        
        natsConnection = Nats.connect(options);
        logger.info("Connected to NATS at " + natsUrl);
        
        // Initialize Redis connection
        JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxTotal(100);
        poolConfig.setMaxIdle(20);
        poolConfig.setMinIdle(5);
        poolConfig.setTestWhileIdle(true);
        
        jedisPool = new JedisPool(poolConfig, redisUrl);
        logger.info("Connected to Redis at " + redisUrl);
        
        // Initialize executor service
        executorService = Executors.newFixedThreadPool(workerThreads);
        logger.info("Started worker pool with " + workerThreads + " threads");
        
        // Start dead letter queue processor
        executorService.submit(this::processDeadLetterQueue);
        
        // Register default handlers
        registerDefaultHandlers();
    }
    
    /**
     * Register default message handlers
     */
    private void registerDefaultHandlers() {
        // Order handler
        registerHandler(MessageType.ORDER_NEW, this::handleNewOrder);
        registerHandler(MessageType.ORDER_CANCEL, this::handleCancelOrder);
        registerHandler(MessageType.ORDER_UPDATE, this::handleOrderUpdate);
        
        // Trade handler
        registerHandler(MessageType.TRADE_EXECUTE, this::handleTradeExecute);
        registerHandler(MessageType.TRADE_SETTLE, this::handleTradeSettle);
        
        // Balance handler
        registerHandler(MessageType.BALANCE_UPDATE, this::handleBalanceUpdate);
        
        // Withdrawal/Deposit handlers
        registerHandler(MessageType.WITHDRAWAL_REQUEST, this::handleWithdrawalRequest);
        registerHandler(MessageType.DEPOSIT_CONFIRM, this::handleDepositConfirm);
        
        // Fee handler
        registerHandler(MessageType.FEE_COLLECT, this::handleFeeCollect);
        
        // Notification handler
        registerHandler(MessageType.NOTIFICATION_SEND, this::handleNotificationSend);
        
        // KYC handler
        registerHandler(MessageType.KYC_UPDATE, this::handleKycUpdate);
        
        // Audit handler
        registerHandler(MessageType.AUDIT_LOG, this::handleAuditLog);
        
        // System alert handler
        registerHandler(MessageType.SYSTEM_ALERT, this::handleSystemAlert);
    }
    
    /**
     * Register a message handler
     */
    public void registerHandler(MessageType type, MessageHandler handler) {
        handlers.put(type, handler);
        queueCounters.put(type.name(), new AtomicLong(0));
        logger.info("Registered handler for " + type);
    }
    
    /**
     * Publish a message to a queue
     */
    public void publish(String queueName, QueueMessage message) {
        try {
            String json = gson.toJson(message);
            
            // Store in Redis for persistence
            try (Jedis jedis = jedisPool.getResource()) {
                jedis.lpush("queue:" + queueName, json);
                jedis.hset("message:status", message.getId(), "QUEUED");
            }
            
            // Publish to NATS for real-time processing
            natsConnection.publish(
                queueName,
                json.getBytes(StandardCharsets.UTF_8)
            );
            
            messagesProcessed.incrementAndGet();
            
        } catch (Exception e) {
            logger.severe("Failed to publish message: " + e.getMessage());
            messagesFailed.incrementAndGet();
        }
    }
    
    /**
     * Subscribe to a queue
     */
    public void subscribe(String queueName) {
        try {
            Dispatcher dispatcher = natsConnection.createDispatcher(msg -> {
                String json = new String(msg.getData(), StandardCharsets.UTF_8);
                QueueMessage message = gson.fromJson(json, QueueMessage.class);
                
                executorService.submit(() -> processMessage(message));
            });
            
            dispatcher.subscribe(queueName);
            logger.info("Subscribed to queue: " + queueName);
            
        } catch (Exception e) {
            logger.severe("Failed to subscribe: " + e.getMessage());
        }
    }
    
    /**
     * Process a message
     */
    private void processMessage(QueueMessage message) {
        try {
            MessageHandler handler = handlers.get(message.getType());
            if (handler == null) {
                logger.warning("No handler for message type: " + message.getType());
                return;
            }
            
            // Update status
            try (Jedis jedis = jedisPool.getResource()) {
                jedis.hset("message:status", message.getId(), "PROCESSING");
            }
            
            // Handle message
            handler.handle(message);
            
            // Update status
            try (Jedis jedis = jedisPool.getResource()) {
                jedis.hset("message:status", message.getId(), "COMPLETED");
                jedis.lpush("queue:completed", message.getId());
            }
            
            queueCounters.get(message.getType().name()).incrementAndGet();
            
        } catch (Exception e) {
            logger.severe("Failed to process message " + message.getId() + ": " + e.getMessage());
            
            // Handle retry
            if (message.getRetryCount() < 3) {
                message.setRetryCount(message.getRetryCount() + 1);
                message.setPriority(Priority.HIGH);
                
                // Re-queue with delay
                try {
                    Thread.sleep(1000 * message.getRetryCount());
                    publish("retry", message);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            } else {
                // Move to dead letter queue
                deadLetterQueue.offer(message);
                
                try (Jedis jedis = jedisPool.getResource()) {
                    jedis.hset("message:status", message.getId(), "FAILED");
                    jedis.lpush("queue:dead_letter", gson.toJson(message));
                }
            }
        }
    }
    
    /**
     * Process dead letter queue
     */
    private void processDeadLetterQueue() {
        while (!Thread.currentThread().isInterrupted()) {
            try {
                QueueMessage message = deadLetterQueue.poll(1, TimeUnit.SECONDS);
                if (message != null) {
                    logger.warning("Processing dead letter message: " + message.getId());
                    // Store for manual review
                    try (Jedis jedis = jedisPool.getResource()) {
                        jedis.lpush("queue:dead_letter", gson.toJson(message));
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
    }
    
    // Default handlers
    
    private void handleNewOrder(QueueMessage message) {
        logger.info("Processing new order: " + message.getId());
        // Implementation would call order matching service
    }
    
    private void handleCancelOrder(QueueMessage message) {
        logger.info("Processing cancel order: " + message.getId());
    }
    
    private void handleOrderUpdate(QueueMessage message) {
        logger.info("Processing order update: " + message.getId());
    }
    
    private void handleTradeExecute(QueueMessage message) {
        logger.info("Processing trade execute: " + message.getId());
        // Implementation would update balances, notify users, etc.
    }
    
    private void handleTradeSettle(QueueMessage message) {
        logger.info("Processing trade settle: " + message.getId());
    }
    
    private void handleBalanceUpdate(QueueMessage message) {
        logger.info("Processing balance update: " + message.getId());
    }
    
    private void handleWithdrawalRequest(QueueMessage message) {
        logger.info("Processing withdrawal request: " + message.getId());
    }
    
    private void handleDepositConfirm(QueueMessage message) {
        logger.info("Processing deposit confirm: " + message.getId());
    }
    
    private void handleFeeCollect(QueueMessage message) {
        logger.info("Processing fee collect: " + message.getId());
    }
    
    private void handleNotificationSend(QueueMessage message) {
        logger.info("Processing notification send: " + message.getId());
    }
    
    private void handleKycUpdate(QueueMessage message) {
        logger.info("Processing KYC update: " + message.getId());
    }
    
    private void handleAuditLog(QueueMessage message) {
        logger.info("Processing audit log: " + message.getId());
    }
    
    private void handleSystemAlert(QueueMessage message) {
        logger.info("Processing system alert: " + message.getId());
    }
    
    /**
     * Get queue statistics
     */
    public Map<String, Object> getStatistics() {
        Map<String, Object> stats = new HashMap<>();
        stats.put("exchange_id", exchangeId);
        stats.put("messages_processed", messagesProcessed.get());
        stats.put("messages_failed", messagesFailed.get());
        stats.put("dead_letter_queue_size", deadLetterQueue.size());
        stats.put("queue_counters", new HashMap<String, Long>());
        
        queueCounters.forEach((k, v) -> {
            ((Map<String, Long>) stats.get("queue_counters")).put(k, v.get());
        });
        
        return stats;
    }
    
    /**
     * Shutdown the service
     */
    public void shutdown() {
        logger.info("Shutting down queue service...");
        
        try {
            // Close NATS connection
            if (natsConnection != null) {
                natsConnection.close();
            }
            
            // Close Redis pool
            if (jedisPool != null) {
                jedisPool.close();
            }
            
            // Shutdown executor
            if (executorService != null) {
                executorService.shutdown();
                if (!executorService.awaitTermination(30, TimeUnit.SECONDS)) {
                    executorService.shutdownNow();
                }
            }
            
            logger.info("Queue service shutdown complete");
            
        } catch (Exception e) {
            logger.severe("Error during shutdown: " + e.getMessage());
        }
    }
    
    /**
     * Main entry point
     */
    public static void main(String[] args) {
        String exchangeId = System.getenv().getOrDefault("EXCHANGE_ID", "TIGEREX-MAIN");
        String natsUrl = System.getenv().getOrDefault("NATS_URL", "nats://localhost:4222");
        String redisUrl = System.getenv().getOrDefault("REDIS_URL", "localhost:6379");
        int workerThreads = Integer.parseInt(System.getenv().getOrDefault("WORKER_THREADS", "10"));
        
        QueueService service = new QueueService(exchangeId, natsUrl, redisUrl, workerThreads);
        
        // Add shutdown hook
        Runtime.getRuntime().addShutdownHook(new Thread(service::shutdown));
        
        try {
            service.start();
            
            // Subscribe to queues
            service.subscribe("orders");
            service.subscribe("trades");
            service.subscribe("notifications");
            service.subscribe("system");
            
            // Keep running
            Thread.currentThread().join();
            
        } catch (Exception e) {
            logger.severe("Failed to start queue service: " + e.getMessage());
            System.exit(1);
        }
    }
}