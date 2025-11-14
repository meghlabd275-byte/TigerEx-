// TigerEx Blockchain Integration - Smart Contracts
// Complete Solidity Implementation for Trading Platform

pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title TigerEx Trading Contract
 * @dev Complete decentralized trading platform with advanced features
 */
contract TigerExTrading is ReentrancyGuard, Ownable, Pausable {
    using SafeMath for uint256;
    using SafeERC20 for IERC20;

    // Structs
    struct Order {
        uint256 id;
        address trader;
        IERC20 tokenA;
        IERC20 tokenB;
        uint256 amountA;
        uint256 amountB;
        bool isBuy;
        uint256 timestamp;
        bool isFilled;
        uint256 filledAmount;
    }

    struct Trade {
        uint256 id;
        uint256 order1Id;
        uint256 order2Id;
        address trader1;
        address trader2;
        IERC20 tokenA;
        IERC20 tokenB;
        uint256 amountA;
        uint256 amountB;
        uint256 timestamp;
        uint256 price;
    }

    struct LiquidityPool {
        IERC20 tokenA;
        IERC20 tokenB;
        uint256 reserveA;
        uint256 reserveB;
        uint256 totalLiquidity;
        mapping(address => uint256) liquidityProviders;
    }

    // State variables
    mapping(uint256 => Order) public orders;
    mapping(address => uint256[]) public userOrders;
    mapping(uint256 => Trade) public trades;
    mapping(bytes32 => LiquidityPool) public liquidityPools;
    mapping(address => mapping(address => bool)) public authorizedTraders;
    mapping(address => bool) public supportedTokens;
    mapping(address => uint256) public userBalances;
    
    uint256 public orderCounter;
    uint256 public tradeCounter;
    uint256 public constant FEE_RATE = 30; // 0.3%
    uint256 public constant MAX_ORDERS_PER_USER = 100;
    
    address public feeCollector;
    
    // Events
    event OrderCreated(
        uint256 indexed orderId,
        address indexed trader,
        address indexed tokenA,
        address tokenB,
        uint256 amountA,
        uint256 amountB,
        bool isBuy
    );
    
    event OrderFilled(
        uint256 indexed orderId,
        uint256 indexed fillAmount,
        address indexed filler
    );
    
    event TradeExecuted(
        uint256 indexed tradeId,
        address indexed trader1,
        address indexed trader2,
        address tokenA,
        address tokenB,
        uint256 amountA,
        uint256 amountB,
        uint256 price
    );
    
    event LiquidityAdded(
        address indexed provider,
        address indexed tokenA,
        address indexed tokenB,
        uint256 amountA,
        uint256 amountB,
        uint256 liquidity
    );
    
    event LiquidityRemoved(
        address indexed provider,
        address indexed tokenA,
        address indexed tokenB,
        uint256 amountA,
        uint256 amountB,
        uint256 liquidity
    );
    
    // Modifiers
    modifier onlyAuthorizedTrader(address trader) {
        require(authorizedTraders[msg.sender][trader] || msg.sender == trader, "Not authorized");
        _;
    }
    
    modifier onlySupportedToken(address token) {
        require(supportedTokens[token], "Token not supported");
        _;
    }
    
    modifier validOrder(uint256 orderId) {
        require(orderId > 0 && orderId <= orderCounter, "Invalid order");
        require(!orders[orderId].isFilled, "Order already filled");
        _;
    }

    constructor(address _feeCollector) {
        feeCollector = _feeCollector;
    }

    /**
     * @dev Create a new trading order
     */
    function createOrder(
        address _tokenA,
        address _tokenB,
        uint256 _amountA,
        uint256 _amountB,
        bool _isBuy
    ) external nonReentrant whenNotPaused onlySupportedToken(_tokenA) onlySupportedToken(_tokenB) returns (uint256) {
        require(_amountA > 0 && _amountB > 0, "Amounts must be greater than 0");
        require(_tokenA != _tokenB, "Tokens must be different");
        require(userOrders[msg.sender].length < MAX_ORDERS_PER_USER, "Too many orders");
        
        IERC20 tokenA = IERC20(_tokenA);
        IERC20 tokenB = IERC20(_tokenB);
        
        // For buy orders, lock tokenB (the token being spent)
        // For sell orders, lock tokenA (the token being spent)
        IERC20 tokenToLock = _isBuy ? tokenB : tokenA;
        uint256 amountToLock = _isBuy ? _amountB : _amountA;
        
        require(tokenToLock.balanceOf(msg.sender) >= amountToLock, "Insufficient balance");
        require(tokenToLock.allowance(msg.sender, address(this)) >= amountToLock, "Insufficient allowance");
        
        // Transfer tokens to contract
        tokenToLock.safeTransferFrom(msg.sender, address(this), amountToLock);
        
        // Create order
        orderCounter++;
        orders[orderCounter] = Order({
            id: orderCounter,
            trader: msg.sender,
            tokenA: tokenA,
            tokenB: tokenB,
            amountA: _amountA,
            amountB: _amountB,
            isBuy: _isBuy,
            timestamp: block.timestamp,
            isFilled: false,
            filledAmount: 0
        });
        
        userOrders[msg.sender].push(orderCounter);
        
        emit OrderCreated(
            orderCounter,
            msg.sender,
            _tokenA,
            _tokenB,
            _amountA,
            _amountB,
            _isBuy
        );
        
        return orderCounter;
    }

    /**
     * @dev Fill an existing order
     */
    function fillOrder(
        uint256 _orderId,
        uint256 _fillAmount
    ) external nonReentrant whenNotPaused validOrder(_orderId) {
        Order storage order = orders[_orderId];
        require(_fillAmount > 0, "Fill amount must be greater than 0");
        require(_fillAmount <= order.amountA - order.filledAmount, "Fill amount exceeds remaining");
        
        uint256 proportion = _fillAmount.mul(1e18).div(order.amountA - order.filledAmount);
        uint256 requiredAmountB = order.amountB.mul(proportion).div(1e18);
        
        IERC20 tokenToProvide = order.isBuy ? order.tokenA : order.tokenB;
        address tokenToProvideAddress = address(tokenToProvide);
        uint256 amountToProvide = order.isBuy ? _fillAmount : requiredAmountB;
        
        require(tokenToProvide.balanceOf(msg.sender) >= amountToProvide, "Insufficient balance");
        require(tokenToProvide.allowance(msg.sender, address(this)) >= amountToProvide, "Insufficient allowance");
        
        // Transfer tokens from filler
        tokenToProvide.safeTransferFrom(msg.sender, address(this), amountToProvide);
        
        // Calculate fees
        uint256 feeAmount = amountToProvide.mul(FEE_RATE).div(10000);
        uint256 amountAfterFee = amountToProvide.sub(feeAmount);
        
        // Transfer fee to collector
        if (feeAmount > 0) {
            tokenToProvide.safeTransfer(feeCollector, feeAmount);
        }
        
        // Transfer tokens to order creator
        IERC20 tokenToReceive = order.isBuy ? order.tokenB : order.tokenA;
        uint256 amountToReceive = order.isBuy ? requiredAmountB : _fillAmount;
        
        tokenToReceive.safeTransfer(order.trader, amountToReceive);
        
        // Update order
        order.filledAmount = order.filledAmount.add(_fillAmount);
        
        if (order.filledAmount >= order.amountA) {
            order.isFilled = true;
        }
        
        // Create trade record
        tradeCounter++;
        trades[tradeCounter] = Trade({
            id: tradeCounter,
            order1Id: _orderId,
            order2Id: 0, // Market order
            trader1: order.trader,
            trader2: msg.sender,
            tokenA: order.tokenA,
            tokenB: order.tokenB,
            amountA: _fillAmount,
            amountB: requiredAmountB,
            timestamp: block.timestamp,
            price: requiredAmountB.mul(1e18).div(_fillAmount)
        });
        
        emit OrderFilled(_orderId, _fillAmount, msg.sender);
        emit TradeExecuted(
            tradeCounter,
            order.trader,
            msg.sender,
            address(order.tokenA),
            address(order.tokenB),
            _fillAmount,
            requiredAmountB,
            trades[tradeCounter].price
        );
    }

    /**
     * @dev Add liquidity to a pool
     */
    function addLiquidity(
        address _tokenA,
        address _tokenB,
        uint256 _amountA,
        uint256 _amountB
    ) external nonReentrant whenNotPaused onlySupportedToken(_tokenA) onlySupportedToken(_tokenB) {
        require(_amountA > 0 && _amountB > 0, "Amounts must be greater than 0");
        
        IERC20 tokenA = IERC20(_tokenA);
        IERC20 tokenB = IERC20(_tokenB);
        
        bytes32 poolKey = keccak256(abi.encodePacked(_tokenA, _tokenB));
        LiquidityPool storage pool = liquidityPools[poolKey];
        
        if (pool.totalLiquidity == 0) {
            // New pool
            pool.tokenA = tokenA;
            pool.tokenB = tokenB;
            pool.reserveA = _amountA;
            pool.reserveB = _amountB;
            pool.totalLiquidity = _amountA.add(_amountB);
            pool.liquidityProviders[msg.sender] = _amountA.add(_amountB);
        } else {
            // Existing pool
            uint256 liquidityA = _amountA.mul(pool.totalLiquidity).div(pool.reserveA);
            uint256 liquidityB = _amountB.mul(pool.totalLiquidity).div(pool.reserveB);
            uint256 minLiquidity = liquidityA < liquidityB ? liquidityA : liquidityB;
            
            pool.reserveA = pool.reserveA.add(_amountA);
            pool.reserveB = pool.reserveB.add(_amountB);
            pool.totalLiquidity = pool.totalLiquidity.add(minLiquidity);
            pool.liquidityProviders[msg.sender] = pool.liquidityProviders[msg.sender].add(minLiquidity);
        }
        
        // Transfer tokens to contract
        tokenA.safeTransferFrom(msg.sender, address(this), _amountA);
        tokenB.safeTransferFrom(msg.sender, address(this), _amountB);
        
        emit LiquidityAdded(msg.sender, _tokenA, _tokenB, _amountA, _amountB, pool.liquidityProviders[msg.sender]);
    }

    /**
     * @dev Remove liquidity from a pool
     */
    function removeLiquidity(
        address _tokenA,
        address _tokenB,
        uint256 _liquidity
    ) external nonReentrant whenNotPaused {
        bytes32 poolKey = keccak256(abi.encodePacked(_tokenA, _tokenB));
        LiquidityPool storage pool = liquidityPools[poolKey];
        
        require(pool.totalLiquidity > 0, "Pool does not exist");
        require(pool.liquidityProviders[msg.sender] >= _liquidity, "Insufficient liquidity");
        
        uint256 amountA = _liquidity.mul(pool.reserveA).div(pool.totalLiquidity);
        uint256 amountB = _liquidity.mul(pool.reserveB).div(pool.totalLiquidity);
        
        pool.reserveA = pool.reserveA.sub(amountA);
        pool.reserveB = pool.reserveB.sub(amountB);
        pool.totalLiquidity = pool.totalLiquidity.sub(_liquidity);
        pool.liquidityProviders[msg.sender] = pool.liquidityProviders[msg.sender].sub(_liquidity);
        
        // Transfer tokens back to user
        pool.tokenA.safeTransfer(msg.sender, amountA);
        pool.tokenB.safeTransfer(msg.sender, amountB);
        
        emit LiquidityRemoved(msg.sender, _tokenA, _tokenB, amountA, amountB, _liquidity);
    }

    /**
     * @dev Swap tokens using liquidity pools
     */
    function swapTokens(
        address _tokenIn,
        address _tokenOut,
        uint256 _amountIn,
        uint256 _minAmountOut
    ) external nonReentrant whenNotPaused onlySupportedToken(_tokenIn) onlySupportedToken(_tokenOut) returns (uint256) {
        require(_amountIn > 0, "Amount must be greater than 0");
        
        IERC20 tokenIn = IERC20(_tokenIn);
        IERC20 tokenOut = IERC20(_tokenOut);
        
        bytes32 poolKey = keccak256(abi.encodePacked(_tokenIn, _tokenOut));
        LiquidityPool storage pool = liquidityPools[poolKey];
        
        require(pool.totalLiquidity > 0, "Pool does not exist");
        
        // Calculate amount out using constant product formula
        uint256 amountInWithFee = _amountIn.mul(10000 - FEE_RATE).div(10000);
        uint256 numerator = amountInWithFee.mul(pool.reserveB);
        uint256 denominator = pool.reserveA.add(amountInWithFee);
        uint256 amountOut = numerator.div(denominator);
        
        require(amountOut >= _minAmountOut, "Insufficient output amount");
        require(tokenIn.balanceOf(msg.sender) >= _amountIn, "Insufficient balance");
        require(tokenIn.allowance(msg.sender, address(this)) >= _amountIn, "Insufficient allowance");
        
        // Transfer tokens
        tokenIn.safeTransferFrom(msg.sender, address(this), _amountIn);
        tokenOut.safeTransfer(msg.sender, amountOut);
        
        // Update pool reserves
        pool.reserveA = pool.reserveA.add(_amountIn);
        pool.reserveB = pool.reserveB.sub(amountOut);
        
        return amountOut;
    }

    /**
     * @dev Authorize a trader to act on behalf of another
     */
    function authorizeTrader(address trader) external {
        authorizedTraders[msg.sender][trader] = true;
    }

    /**
     * @dev Revoke trader authorization
     */
    function revokeTraderAuthorization(address trader) external {
        authorizedTraders[msg.sender][trader] = false;
    }

    /**
     * @dev Add support for a new token
     */
    function addSupportedToken(address token) external onlyOwner {
        supportedTokens[token] = true;
    }

    /**
     * @dev Remove support for a token
     */
    function removeSupportedToken(address token) external onlyOwner {
        supportedTokens[token] = false;
    }

    /**
     * @dev Update fee collector address
     */
    function updateFeeCollector(address newFeeCollector) external onlyOwner {
        feeCollector = newFeeCollector;
    }

    /**
     * @dev Cancel an order
     */
    function cancelOrder(uint256 _orderId) external nonReentrant validOrder(_orderId) {
        Order storage order = orders[_orderId];
        require(msg.sender == order.trader, "Only order creator can cancel");
        
        // Return locked tokens to order creator
        IERC20 tokenToReturn = order.isBuy ? order.tokenB : order.tokenA;
        uint256 amountToReturn = order.isBuy ? order.amountB : order.amountA;
        
        tokenToReturn.safeTransfer(order.trader, amountToReturn);
        
        // Mark order as filled (canceled)
        order.isFilled = true;
        
        emit OrderFilled(_orderId, order.amountA, msg.sender);
    }

    /**
     * @dev Get user's orders
     */
    function getUserOrders(address user) external view returns (uint256[] memory) {
        return userOrders[user];
    }

    /**
     * @dev Get pool information
     */
    function getPoolInfo(address _tokenA, address _tokenB) external view returns (
        uint256 reserveA,
        uint256 reserveB,
        uint256 totalLiquidity,
        uint256 userLiquidity
    ) {
        bytes32 poolKey = keccak256(abi.encodePacked(_tokenA, _tokenB));
        LiquidityPool storage pool = liquidityPools[poolKey];
        
        return (
            pool.reserveA,
            pool.reserveB,
            pool.totalLiquidity,
            pool.liquidityProviders[msg.sender]
        );
    }

    /**
     * @dev Get expected swap amount
     */
    function getSwapAmount(address _tokenIn, address _tokenOut, uint256 _amountIn) external view returns (uint256) {
        bytes32 poolKey = keccak256(abi.encodePacked(_tokenIn, _tokenOut));
        LiquidityPool storage pool = liquidityPools[poolKey];
        
        if (pool.totalLiquidity == 0) return 0;
        
        uint256 amountInWithFee = _amountIn.mul(10000 - FEE_RATE).div(10000);
        uint256 numerator = amountInWithFee.mul(pool.reserveB);
        uint256 denominator = pool.reserveA.add(amountInWithFee);
        uint256 amountOut = numerator.div(denominator);
        
        return amountOut;
    }

    /**
     * @dev Emergency pause function
     */
    function emergencyPause() external onlyOwner {
        _pause();
    }

    /**
     * @dev Unpause function
     */
    function unpause() external onlyOwner {
        _unpause();
    }

    /**
     * @dev Emergency withdraw function
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyOwner {
        IERC20(token).safeTransfer(owner(), amount);
    }
}