// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "./AdminController.sol";

/**
 * @title TradingEngine
 * @dev Complete trading engine supporting all trading types with admin controls
 */
contract TradingEngine is AccessControl, ReentrancyGuard, Pausable {
    using SafeERC20 for IERC20;

    // Reference to AdminController
    AdminController public adminController;

    // Trading Types (matching AdminController)
    enum TradingType {
        SPOT,
        FUTURES_PERPETUAL,
        FUTURES_CROSS,
        FUTURES_DELIVERY,
        MARGIN,
        MARGIN_CROSS,
        MARGIN_ISOLATED,
        OPTIONS,
        DERIVATIVES,
        COPY_TRADING,
        ETF,
        LEVERAGED_TOKENS,
        STRUCTURED_PRODUCTS
    }

    enum OrderType {
        MARKET,
        LIMIT,
        STOP_LOSS,
        STOP_LOSS_LIMIT,
        TAKE_PROFIT,
        TAKE_PROFIT_LIMIT,
        TRAILING_STOP
    }

    enum OrderSide {
        BUY,
        SELL
    }

    enum OrderStatus {
        PENDING,
        PARTIALLY_FILLED,
        FILLED,
        CANCELLED,
        EXPIRED,
        REJECTED
    }

    // Structs
    struct Order {
        bytes32 orderId;
        address trader;
        bytes32 contractId;
        TradingType tradingType;
        OrderType orderType;
        OrderSide side;
        address baseToken;
        address quoteToken;
        uint256 quantity;
        uint256 price;
        uint256 filledQuantity;
        uint256 leverage;
        uint256 stopPrice;
        uint256 createdAt;
        uint256 expiresAt;
        OrderStatus status;
        string metadata;
    }

    struct Position {
        bytes32 positionId;
        address trader;
        bytes32 contractId;
        TradingType tradingType;
        OrderSide side;
        address baseToken;
        address quoteToken;
        uint256 size;
        uint256 entryPrice;
        uint256 leverage;
        uint256 margin;
        uint256 unrealizedPnL;
        uint256 createdAt;
        uint256 updatedAt;
        bool isOpen;
    }

    struct Trade {
        bytes32 tradeId;
        bytes32 buyOrderId;
        bytes32 sellOrderId;
        address buyer;
        address seller;
        bytes32 contractId;
        address baseToken;
        address quoteToken;
        uint256 quantity;
        uint256 price;
        uint256 timestamp;
        uint256 makerFee;
        uint256 takerFee;
    }

    struct MarketData {
        bytes32 contractId;
        address baseToken;
        address quoteToken;
        uint256 lastPrice;
        uint256 volume24h;
        uint256 high24h;
        uint256 low24h;
        uint256 priceChange24h;
        uint256 openInterest; // for futures
        int256 fundingRate; // for perpetual futures
        uint256 updatedAt;
    }

    // State Variables
    mapping(bytes32 => Order) public orders;
    mapping(bytes32 => Position) public positions;
    mapping(bytes32 => Trade) public trades;
    mapping(bytes32 => MarketData) public marketData;
    mapping(address => bytes32[]) public userOrders;
    mapping(address => bytes32[]) public userPositions;
    mapping(bytes32 => bytes32[]) public contractOrders;
    mapping(bytes32 => bytes32[]) public contractTrades;

    // Order book: contractId => price => quantity
    mapping(bytes32 => mapping(uint256 => uint256)) public buyOrderBook;
    mapping(bytes32 => mapping(uint256 => uint256)) public sellOrderBook;
    mapping(bytes32 => uint256[]) public buyPriceLevels;
    mapping(bytes32 => uint256[]) public sellPriceLevels;

    // Balances: user => token => amount
    mapping(address => mapping(address => uint256)) public balances;
    mapping(address => mapping(address => uint256)) public lockedBalances;

    // Counters
    uint256 public orderCounter;
    uint256 public positionCounter;
    uint256 public tradeCounter;

    // Roles
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    bytes32 public constant LIQUIDATOR_ROLE = keccak256("LIQUIDATOR_ROLE");

    // Events
    event OrderPlaced(bytes32 indexed orderId, address indexed trader, bytes32 indexed contractId);
    event OrderFilled(bytes32 indexed orderId, uint256 filledQuantity, uint256 price);
    event OrderCancelled(bytes32 indexed orderId, address indexed trader);
    event TradeExecuted(bytes32 indexed tradeId, bytes32 indexed buyOrderId, bytes32 indexed sellOrderId);
    event PositionOpened(bytes32 indexed positionId, address indexed trader, bytes32 indexed contractId);
    event PositionClosed(bytes32 indexed positionId, address indexed trader, int256 pnl);
    event PositionLiquidated(bytes32 indexed positionId, address indexed trader, address indexed liquidator);
    event Deposit(address indexed user, address indexed token, uint256 amount);
    event Withdrawal(address indexed user, address indexed token, uint256 amount);
    event MarketDataUpdated(bytes32 indexed contractId, uint256 price, uint256 volume);

    // Modifiers
    modifier onlyOperator() {
        require(hasRole(OPERATOR_ROLE, msg.sender), "TradingEngine: Operator required");
        _;
    }

    modifier onlyLiquidator() {
        require(hasRole(LIQUIDATOR_ROLE, msg.sender), "TradingEngine: Liquidator required");
        _;
    }

    modifier contractActive(bytes32 contractId) {
        // Check with AdminController if contract is active
        (,,,,,AdminController.ContractStatus status,,,,,,,,,,) = adminController.getContract(contractId);
        require(status == AdminController.ContractStatus.ACTIVE, "TradingEngine: Contract not active");
        _;
    }

    modifier userCanTrade(address user, TradingType tradingType) {
        require(adminController.hasTradingPermission(user, AdminController.TradingType(uint8(tradingType))), 
                "TradingEngine: User lacks trading permission");
        _;
    }

    // Constructor
    constructor(address _adminController) {
        adminController = AdminController(_adminController);
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
        _grantRole(LIQUIDATOR_ROLE, msg.sender);

        orderCounter = 1;
        positionCounter = 1;
        tradeCounter = 1;
    }

    // ==================== DEPOSIT & WITHDRAWAL ====================

    /**
     * @dev Deposit tokens to trading account
     */
    function deposit(address token, uint256 amount) external nonReentrant {
        require(amount > 0, "TradingEngine: Invalid amount");
        
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        balances[msg.sender][token] += amount;

        emit Deposit(msg.sender, token, amount);
    }

    /**
     * @dev Withdraw tokens from trading account
     */
    function withdraw(address token, uint256 amount) external nonReentrant {
        require(amount > 0, "TradingEngine: Invalid amount");
        require(balances[msg.sender][token] >= amount, "TradingEngine: Insufficient balance");
        require(balances[msg.sender][token] - lockedBalances[msg.sender][token] >= amount, 
                "TradingEngine: Insufficient available balance");

        balances[msg.sender][token] -= amount;
        IERC20(token).safeTransfer(msg.sender, amount);

        emit Withdrawal(msg.sender, token, amount);
    }

    // ==================== ORDER MANAGEMENT ====================

    /**
     * @dev Place a new order
     */
    function placeOrder(
        bytes32 contractId,
        TradingType tradingType,
        OrderType orderType,
        OrderSide side,
        address baseToken,
        address quoteToken,
        uint256 quantity,
        uint256 price,
        uint256 leverage,
        uint256 stopPrice,
        uint256 expiresAt,
        string memory metadata
    ) external 
        nonReentrant 
        whenNotPaused 
        contractActive(contractId)
        userCanTrade(msg.sender, tradingType)
        returns (bytes32) 
    {
        require(quantity > 0, "TradingEngine: Invalid quantity");
        
        bytes32 orderId = keccak256(abi.encodePacked(
            msg.sender,
            contractId,
            block.timestamp,
            orderCounter++
        ));

        // Calculate required margin/balance
        uint256 requiredAmount = _calculateRequiredAmount(
            tradingType, side, quantity, price, leverage
        );

        address requiredToken = side == OrderSide.BUY ? quoteToken : baseToken;
        require(balances[msg.sender][requiredToken] >= lockedBalances[msg.sender][requiredToken] + requiredAmount,
                "TradingEngine: Insufficient balance");

        // Lock the required amount
        lockedBalances[msg.sender][requiredToken] += requiredAmount;

        // Create order
        Order storage newOrder = orders[orderId];
        newOrder.orderId = orderId;
        newOrder.trader = msg.sender;
        newOrder.contractId = contractId;
        newOrder.tradingType = tradingType;
        newOrder.orderType = orderType;
        newOrder.side = side;
        newOrder.baseToken = baseToken;
        newOrder.quoteToken = quoteToken;
        newOrder.quantity = quantity;
        newOrder.price = price;
        newOrder.leverage = leverage;
        newOrder.stopPrice = stopPrice;
        newOrder.createdAt = block.timestamp;
        newOrder.expiresAt = expiresAt;
        newOrder.status = OrderStatus.PENDING;
        newOrder.metadata = metadata;

        // Add to mappings
        userOrders[msg.sender].push(orderId);
        contractOrders[contractId].push(orderId);

        // Add to order book for limit orders
        if (orderType == OrderType.LIMIT) {
            _addToOrderBook(contractId, side, price, quantity);
        }

        // Try to match immediately for market orders
        if (orderType == OrderType.MARKET) {
            _matchMarketOrder(orderId);
        }

        emit OrderPlaced(orderId, msg.sender, contractId);
        return orderId;
    }

    /**
     * @dev Cancel an order
     */
    function cancelOrder(bytes32 orderId) external nonReentrant {
        Order storage order = orders[orderId];
        require(order.trader == msg.sender, "TradingEngine: Not order owner");
        require(order.status == OrderStatus.PENDING, "TradingEngine: Order not cancellable");

        order.status = OrderStatus.CANCELLED;

        // Unlock funds
        uint256 lockedAmount = _calculateRequiredAmount(
            order.tradingType, order.side, order.quantity - order.filledQuantity, 
            order.price, order.leverage
        );
        
        address lockedToken = order.side == OrderSide.BUY ? order.quoteToken : order.baseToken;
        lockedBalances[msg.sender][lockedToken] -= lockedAmount;

        // Remove from order book
        if (order.orderType == OrderType.LIMIT) {
            _removeFromOrderBook(order.contractId, order.side, order.price, 
                               order.quantity - order.filledQuantity);
        }

        emit OrderCancelled(orderId, msg.sender);
    }

    /**
     * @dev Match market order against order book
     */
    function _matchMarketOrder(bytes32 orderId) internal {
        Order storage order = orders[orderId];
        uint256 remainingQuantity = order.quantity;
        
        // Get opposite side price levels
        uint256[] memory priceLevels = order.side == OrderSide.BUY ? 
            sellPriceLevels[order.contractId] : buyPriceLevels[order.contractId];

        // Sort prices (ascending for buy, descending for sell)
        priceLevels = _sortPrices(priceLevels, order.side == OrderSide.BUY);

        for (uint256 i = 0; i < priceLevels.length && remainingQuantity > 0; i++) {
            uint256 price = priceLevels[i];
            uint256 availableQuantity = order.side == OrderSide.BUY ? 
                sellOrderBook[order.contractId][price] : buyOrderBook[order.contractId][price];

            if (availableQuantity > 0) {
                uint256 matchQuantity = remainingQuantity > availableQuantity ? 
                    availableQuantity : remainingQuantity;

                _executeTrade(orderId, price, matchQuantity);
                remainingQuantity -= matchQuantity;
            }
        }

        // Update order status
        if (remainingQuantity == 0) {
            order.status = OrderStatus.FILLED;
        } else if (order.filledQuantity > 0) {
            order.status = OrderStatus.PARTIALLY_FILLED;
        }
    }

    /**
     * @dev Execute a trade between orders
     */
    function _executeTrade(bytes32 orderId, uint256 price, uint256 quantity) internal {
        Order storage order = orders[orderId];
        
        bytes32 tradeId = keccak256(abi.encodePacked(
            orderId,
            price,
            quantity,
            block.timestamp,
            tradeCounter++
        ));

        // Create trade record
        Trade storage newTrade = trades[tradeId];
        newTrade.tradeId = tradeId;
        newTrade.buyOrderId = order.side == OrderSide.BUY ? orderId : bytes32(0);
        newTrade.sellOrderId = order.side == OrderSide.SELL ? orderId : bytes32(0);
        newTrade.buyer = order.side == OrderSide.BUY ? order.trader : address(0);
        newTrade.seller = order.side == OrderSide.SELL ? order.trader : address(0);
        newTrade.contractId = order.contractId;
        newTrade.baseToken = order.baseToken;
        newTrade.quoteToken = order.quoteToken;
        newTrade.quantity = quantity;
        newTrade.price = price;
        newTrade.timestamp = block.timestamp;

        // Update order
        order.filledQuantity += quantity;

        // Update balances
        _updateBalancesAfterTrade(order, price, quantity);

        // Update market data
        _updateMarketData(order.contractId, price, quantity);

        // Handle position for leveraged trading
        if (_isLeveragedTrading(order.tradingType)) {
            _handleLeveragedPosition(order, price, quantity);
        }

        contractTrades[order.contractId].push(tradeId);

        emit TradeExecuted(tradeId, newTrade.buyOrderId, newTrade.sellOrderId);
        emit OrderFilled(orderId, quantity, price);
    }

    /**
     * @dev Update balances after trade execution
     */
    function _updateBalancesAfterTrade(Order storage order, uint256 price, uint256 quantity) internal {
        uint256 quoteAmount = (quantity * price) / 1e18;
        
        if (order.side == OrderSide.BUY) {
            // Buyer receives base token, pays quote token
            balances[order.trader][order.baseToken] += quantity;
            lockedBalances[order.trader][order.quoteToken] -= quoteAmount;
        } else {
            // Seller receives quote token, pays base token
            balances[order.trader][order.quoteToken] += quoteAmount;
            lockedBalances[order.trader][order.baseToken] -= quantity;
        }
    }

    /**
     * @dev Handle leveraged position creation/update
     */
    function _handleLeveragedPosition(Order storage order, uint256 price, uint256 quantity) internal {
        // Check if user has existing position
        bytes32[] memory userPos = userPositions[order.trader];
        bytes32 existingPositionId = bytes32(0);
        
        for (uint256 i = 0; i < userPos.length; i++) {
            Position storage pos = positions[userPos[i]];
            if (pos.contractId == order.contractId && pos.isOpen) {
                existingPositionId = userPos[i];
                break;
            }
        }

        if (existingPositionId != bytes32(0)) {
            // Update existing position
            _updatePosition(existingPositionId, order, price, quantity);
        } else {
            // Create new position
            _createPosition(order, price, quantity);
        }
    }

    /**
     * @dev Create new leveraged position
     */
    function _createPosition(Order storage order, uint256 price, uint256 quantity) internal {
        bytes32 positionId = keccak256(abi.encodePacked(
            order.trader,
            order.contractId,
            block.timestamp,
            positionCounter++
        ));

        Position storage newPosition = positions[positionId];
        newPosition.positionId = positionId;
        newPosition.trader = order.trader;
        newPosition.contractId = order.contractId;
        newPosition.tradingType = order.tradingType;
        newPosition.side = order.side;
        newPosition.baseToken = order.baseToken;
        newPosition.quoteToken = order.quoteToken;
        newPosition.size = quantity;
        newPosition.entryPrice = price;
        newPosition.leverage = order.leverage;
        newPosition.margin = (quantity * price) / (order.leverage * 1e18);
        newPosition.createdAt = block.timestamp;
        newPosition.updatedAt = block.timestamp;
        newPosition.isOpen = true;

        userPositions[order.trader].push(positionId);

        emit PositionOpened(positionId, order.trader, order.contractId);
    }

    /**
     * @dev Update existing position
     */
    function _updatePosition(bytes32 positionId, Order storage order, uint256 price, uint256 quantity) internal {
        Position storage position = positions[positionId];
        
        if (position.side == order.side) {
            // Increase position size
            uint256 totalValue = (position.size * position.entryPrice) + (quantity * price);
            uint256 totalSize = position.size + quantity;
            position.entryPrice = totalValue / totalSize;
            position.size = totalSize;
        } else {
            // Reduce or close position
            if (quantity >= position.size) {
                // Close position
                int256 pnl = _calculatePnL(position, price);
                position.isOpen = false;
                emit PositionClosed(positionId, position.trader, pnl);
            } else {
                // Reduce position
                position.size -= quantity;
            }
        }
        
        position.updatedAt = block.timestamp;
    }

    /**
     * @dev Calculate PnL for position
     */
    function _calculatePnL(Position storage position, uint256 currentPrice) internal view returns (int256) {
        int256 priceDiff = int256(currentPrice) - int256(position.entryPrice);
        int256 pnl = (int256(position.size) * priceDiff) / 1e18;
        
        if (position.side == OrderSide.SELL) {
            pnl = -pnl;
        }
        
        return pnl;
    }

    // ==================== ORDER BOOK MANAGEMENT ====================

    /**
     * @dev Add order to order book
     */
    function _addToOrderBook(bytes32 contractId, OrderSide side, uint256 price, uint256 quantity) internal {
        if (side == OrderSide.BUY) {
            if (buyOrderBook[contractId][price] == 0) {
                buyPriceLevels[contractId].push(price);
            }
            buyOrderBook[contractId][price] += quantity;
        } else {
            if (sellOrderBook[contractId][price] == 0) {
                sellPriceLevels[contractId].push(price);
            }
            sellOrderBook[contractId][price] += quantity;
        }
    }

    /**
     * @dev Remove order from order book
     */
    function _removeFromOrderBook(bytes32 contractId, OrderSide side, uint256 price, uint256 quantity) internal {
        if (side == OrderSide.BUY) {
            buyOrderBook[contractId][price] -= quantity;
            if (buyOrderBook[contractId][price] == 0) {
                _removePriceLevel(buyPriceLevels[contractId], price);
            }
        } else {
            sellOrderBook[contractId][price] -= quantity;
            if (sellOrderBook[contractId][price] == 0) {
                _removePriceLevel(sellPriceLevels[contractId], price);
            }
        }
    }

    /**
     * @dev Remove price level from array
     */
    function _removePriceLevel(uint256[] storage priceLevels, uint256 price) internal {
        for (uint256 i = 0; i < priceLevels.length; i++) {
            if (priceLevels[i] == price) {
                priceLevels[i] = priceLevels[priceLevels.length - 1];
                priceLevels.pop();
                break;
            }
        }
    }

    /**
     * @dev Sort price levels
     */
    function _sortPrices(uint256[] memory prices, bool ascending) internal pure returns (uint256[] memory) {
        // Simple bubble sort (can be optimized for production)
        for (uint256 i = 0; i < prices.length; i++) {
            for (uint256 j = i + 1; j < prices.length; j++) {
                if ((ascending && prices[i] > prices[j]) || (!ascending && prices[i] < prices[j])) {
                    uint256 temp = prices[i];
                    prices[i] = prices[j];
                    prices[j] = temp;
                }
            }
        }
        return prices;
    }

    // ==================== MARKET DATA ====================

    /**
     * @dev Update market data after trade
     */
    function _updateMarketData(bytes32 contractId, uint256 price, uint256 quantity) internal {
        MarketData storage data = marketData[contractId];
        
        if (data.contractId == bytes32(0)) {
            // Initialize market data
            data.contractId = contractId;
            data.lastPrice = price;
            data.high24h = price;
            data.low24h = price;
        } else {
            data.lastPrice = price;
            if (price > data.high24h) data.high24h = price;
            if (price < data.low24h) data.low24h = price;
        }
        
        data.volume24h += quantity;
        data.updatedAt = block.timestamp;

        emit MarketDataUpdated(contractId, price, quantity);
    }

    // ==================== LIQUIDATION ====================

    /**
     * @dev Liquidate underwater position
     */
    function liquidatePosition(bytes32 positionId, uint256 currentPrice) 
        external 
        onlyLiquidator 
        nonReentrant 
    {
        Position storage position = positions[positionId];
        require(position.isOpen, "TradingEngine: Position not open");
        
        // Check if position is underwater
        int256 pnl = _calculatePnL(position, currentPrice);
        uint256 liquidationThreshold = (position.margin * 80) / 100; // 80% of margin
        
        require(uint256(-pnl) >= liquidationThreshold, "TradingEngine: Position not liquidatable");
        
        // Close position
        position.isOpen = false;
        position.updatedAt = block.timestamp;
        
        // Handle liquidation penalty and rewards
        uint256 liquidationReward = (position.margin * 5) / 100; // 5% reward
        balances[msg.sender][position.quoteToken] += liquidationReward;
        
        emit PositionLiquidated(positionId, position.trader, msg.sender);
    }

    // ==================== UTILITY FUNCTIONS ====================

    /**
     * @dev Calculate required amount for order
     */
    function _calculateRequiredAmount(
        TradingType tradingType,
        OrderSide side,
        uint256 quantity,
        uint256 price,
        uint256 leverage
    ) internal pure returns (uint256) {
        uint256 notional = (quantity * price) / 1e18;
        
        if (_isLeveragedTrading(tradingType)) {
            return notional / leverage; // Margin requirement
        } else {
            return side == OrderSide.BUY ? notional : quantity;
        }
    }

    /**
     * @dev Check if trading type is leveraged
     */
    function _isLeveragedTrading(TradingType tradingType) internal pure returns (bool) {
        return tradingType == TradingType.FUTURES_PERPETUAL ||
               tradingType == TradingType.FUTURES_CROSS ||
               tradingType == TradingType.FUTURES_DELIVERY ||
               tradingType == TradingType.MARGIN ||
               tradingType == TradingType.MARGIN_CROSS ||
               tradingType == TradingType.MARGIN_ISOLATED;
    }

    // ==================== VIEW FUNCTIONS ====================

    /**
     * @dev Get order details
     */
    function getOrder(bytes32 orderId) external view returns (Order memory) {
        return orders[orderId];
    }

    /**
     * @dev Get position details
     */
    function getPosition(bytes32 positionId) external view returns (Position memory) {
        return positions[positionId];
    }

    /**
     * @dev Get user orders
     */
    function getUserOrders(address user) external view returns (bytes32[] memory) {
        return userOrders[user];
    }

    /**
     * @dev Get user positions
     */
    function getUserPositions(address user) external view returns (bytes32[] memory) {
        return userPositions[user];
    }

    /**
     * @dev Get order book for contract
     */
    function getOrderBook(bytes32 contractId) 
        external 
        view 
        returns (
            uint256[] memory buyPrices,
            uint256[] memory buyQuantities,
            uint256[] memory sellPrices,
            uint256[] memory sellQuantities
        ) 
    {
        buyPrices = buyPriceLevels[contractId];
        sellPrices = sellPriceLevels[contractId];
        
        buyQuantities = new uint256[](buyPrices.length);
        sellQuantities = new uint256[](sellPrices.length);
        
        for (uint256 i = 0; i < buyPrices.length; i++) {
            buyQuantities[i] = buyOrderBook[contractId][buyPrices[i]];
        }
        
        for (uint256 i = 0; i < sellPrices.length; i++) {
            sellQuantities[i] = sellOrderBook[contractId][sellPrices[i]];
        }
    }

    /**
     * @dev Get market data
     */
    function getMarketData(bytes32 contractId) external view returns (MarketData memory) {
        return marketData[contractId];
    }

    /**
     * @dev Get user balance
     */
    function getBalance(address user, address token) external view returns (uint256, uint256) {
        return (balances[user][token], lockedBalances[user][token]);
    }

    // ==================== ADMIN FUNCTIONS ====================

    /**
     * @dev Set funding rate for perpetual futures
     */
    function setFundingRate(bytes32 contractId, int256 fundingRate) external onlyOperator {
        marketData[contractId].fundingRate = fundingRate;
    }

    /**
     * @dev Emergency pause
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Update admin controller
     */
    function updateAdminController(address _adminController) external onlyRole(DEFAULT_ADMIN_ROLE) {
        adminController = AdminController(_adminController);
    }
}