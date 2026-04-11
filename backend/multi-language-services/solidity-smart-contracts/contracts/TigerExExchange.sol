// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * TigerEx Smart Contracts
 * DeFi Integration - DEX, Staking, Yield Farming, Governance
 * Part of TigerEx Multi-Language Microservices Architecture
 */

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title TigerExToken
 * @dev Native governance token for TigerEx
 */
contract TigerExToken is ERC20, AccessControl {
    using Counters for Counters.Counter;
    
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant BURNER_ROLE = keccak256("BURNER_ROLE");
    
    Counters.Counter private _tokenIdCounter;
    
    // Total supply cap
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1 billion tokens
    
    constructor() ERC20("TigerEx Token", "TGX") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(BURNER_ROLE, msg.sender);
    }
    
    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) {
        require(totalSupply() + amount <= MAX_SUPPLY, "Exceeds max supply");
        _mint(to, amount);
    }
    
    function burn(address from, uint256 amount) public onlyRole(BURNER_ROLE) {
        _burn(from, amount);
    }
}

/**
 * @title TigerExDEX
 * @dev Decentralized Exchange with AMM functionality
 */
contract TigerExDEX is AccessControl, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant FEE_MANAGER_ROLE = keccak256("FEE_MANAGER_ROLE");
    
    // Exchange configuration
    string public exchangeId;
    address public feeRecipient;
    uint256 public tradingFee; // Basis points (100 = 1%)
    
    // Liquidity pools
    struct Pool {
        address token0;
        address token1;
        uint256 reserve0;
        uint256 reserve1;
        uint256 totalLiquidity;
        uint256 fee0;
        uint256 fee1;
        bool active;
    }
    
    mapping(bytes32 => Pool) public pools;
    mapping(address => mapping(bytes32 => uint256)) public liquidityBalances;
    
    // Order book for limit orders
    struct Order {
        address trader;
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint256 minAmountOut;
        uint256 price;
        bool isBuy;
        bool filled;
        uint256 timestamp;
    }
    
    mapping(bytes32 => Order) public orders;
    Counters.Counter private _orderIdCounter;
    
    // Events
    event PoolCreated(bytes32 indexed poolId, address token0, address token1);
    event LiquidityAdded(bytes32 indexed poolId, address provider, uint256 amount0, uint256 amount1);
    event LiquidityRemoved(bytes32 indexed poolId, address provider, uint256 amount0, uint256 amount1);
    event SwapExecuted(bytes32 indexed poolId, address trader, address tokenIn, address tokenOut, uint256 amountIn, uint256 amountOut);
    event OrderPlaced(bytes32 indexed orderId, address trader, address tokenIn, address tokenOut, uint256 amountIn, uint256 price);
    event OrderFilled(bytes32 indexed orderId, address filler, uint256 amount);
    event FeeCollected(address indexed token, uint256 amount);
    
    constructor(string memory _exchangeId, address _feeRecipient, uint256 _tradingFee) {
        exchangeId = _exchangeId;
        feeRecipient = _feeRecipient;
        tradingFee = _tradingFee;
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(FEE_MANAGER_ROLE, msg.sender);
    }
    
    /**
     * @dev Get pool ID for a token pair
     */
    function getPoolId(address token0, address token1) public pure returns (bytes32) {
        return keccak256(abi.encodePacked(token0 < token1 ? token0 : token1, token0 < token1 ? token1 : token0));
    }
    
    /**
     * @dev Create a new liquidity pool
     */
    function createPool(address token0, address token1) external onlyRole(ADMIN_ROLE) {
        require(token0 != token1, "Same tokens");
        
        bytes32 poolId = getPoolId(token0, token1);
        require(pools[poolId].token0 == address(0), "Pool exists");
        
        (address _token0, address _token1) = token0 < token1 ? (token0, token1) : (token1, token0);
        
        pools[poolId] = Pool({
            token0: _token0,
            token1: _token1,
            reserve0: 0,
            reserve1: 0,
            totalLiquidity: 0,
            fee0: 0,
            fee1: 0,
            active: true
        });
        
        emit PoolCreated(poolId, _token0, _token1);
    }
    
    /**
     * @dev Add liquidity to a pool
     */
    function addLiquidity(
        address token0,
        address token1,
        uint256 amount0,
        uint256 amount1,
        uint256 minLiquidity
    ) external nonReentrant whenNotPaused returns (uint256 liquidity) {
        bytes32 poolId = getPoolId(token0, token1);
        Pool storage pool = pools[poolId];
        
        require(pool.active, "Pool not active");
        
        // Transfer tokens
        IERC20(token0).transferFrom(msg.sender, address(this), amount0);
        IERC20(token1).transferFrom(msg.sender, address(this), amount1);
        
        if (pool.totalLiquidity == 0) {
            liquidity = sqrt(amount0 * amount1);
        } else {
            liquidity = (amount0 * pool.totalLiquidity) / pool.reserve0;
            uint256 liquidity2 = (amount1 * pool.totalLiquidity) / pool.reserve1;
            liquidity = liquidity < liquidity2 ? liquidity : liquidity2;
        }
        
        require(liquidity >= minLiquidity, "Insufficient liquidity");
        
        pool.reserve0 += amount0;
        pool.reserve1 += amount1;
        pool.totalLiquidity += liquidity;
        
        liquidityBalances[msg.sender][poolId] += liquidity;
        
        emit LiquidityAdded(poolId, msg.sender, amount0, amount1);
    }
    
    /**
     * @dev Remove liquidity from a pool
     */
    function removeLiquidity(
        address token0,
        address token1,
        uint256 liquidity,
        uint256 minAmount0,
        uint256 minAmount1
    ) external nonReentrant whenNotPaused returns (uint256 amount0, uint256 amount1) {
        bytes32 poolId = getPoolId(token0, token1);
        Pool storage pool = pools[poolId];
        
        require(pool.active, "Pool not active");
        require(liquidityBalances[msg.sender][poolId] >= liquidity, "Insufficient balance");
        
        amount0 = (liquidity * pool.reserve0) / pool.totalLiquidity;
        amount1 = (liquidity * pool.reserve1) / pool.totalLiquidity;
        
        require(amount0 >= minAmount0 && amount1 >= minAmount1, "Slippage too high");
        
        pool.reserve0 -= amount0;
        pool.reserve1 -= amount1;
        pool.totalLiquidity -= liquidity;
        
        liquidityBalances[msg.sender][poolId] -= liquidity;
        
        IERC20(token0).transfer(msg.sender, amount0);
        IERC20(token1).transfer(msg.sender, amount1);
        
        emit LiquidityRemoved(poolId, msg.sender, amount0, amount1);
    }
    
    /**
     * @dev Execute a swap
     */
    function swap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 minAmountOut
    ) external nonReentrant whenNotPaused returns (uint256 amountOut) {
        bytes32 poolId = getPoolId(tokenIn, tokenOut);
        Pool storage pool = pools[poolId];
        
        require(pool.active, "Pool not active");
        
        bool isToken0 = tokenIn == pool.token0;
        
        (uint256 reserveIn, uint256 reserveOut) = isToken0 
            ? (pool.reserve0, pool.reserve1) 
            : (pool.reserve1, pool.reserve0);
        
        // Calculate output with constant product formula
        uint256 amountInWithFee = amountIn * (10000 - tradingFee);
        amountOut = (amountInWithFee * reserveOut) / (reserveIn * 10000 + amountInWithFee);
        
        require(amountOut >= minAmountOut, "Slippage too high");
        
        // Transfer tokens
        IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        IERC20(tokenOut).transfer(msg.sender, amountOut);
        
        // Update reserves
        if (isToken0) {
            pool.reserve0 += amountIn;
            pool.reserve1 -= amountOut;
        } else {
            pool.reserve1 += amountIn;
            pool.reserve0 -= amountOut;
        }
        
        emit SwapExecuted(poolId, msg.sender, tokenIn, tokenOut, amountIn, amountOut);
    }
    
    /**
     * @dev Get expected output for a swap
     */
    function getAmountOut(
        address tokenIn,
        address tokenOut,
        uint256 amountIn
    ) external view returns (uint256) {
        bytes32 poolId = getPoolId(tokenIn, tokenOut);
        Pool storage pool = pools[poolId];
        
        bool isToken0 = tokenIn == pool.token0;
        
        (uint256 reserveIn, uint256 reserveOut) = isToken0 
            ? (pool.reserve0, pool.reserve1) 
            : (pool.reserve1, pool.reserve0);
        
        uint256 amountInWithFee = amountIn * (10000 - tradingFee);
        return (amountInWithFee * reserveOut) / (reserveIn * 10000 + amountInWithFee);
    }
    
    /**
     * @dev Place a limit order
     */
    function placeOrder(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 price,
        bool isBuy
    ) external nonReentrant whenNotPaused returns (bytes32) {
        bytes32 orderId = keccak256(abi.encodePacked(_orderIdCounter.current(), block.timestamp, msg.sender));
        _orderIdCounter.increment();
        
        IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        
        orders[orderId] = Order({
            trader: msg.sender,
            tokenIn: tokenIn,
            tokenOut: tokenOut,
            amountIn: amountIn,
            minAmountOut: 0,
            price: price,
            isBuy: isBuy,
            filled: false,
            timestamp: block.timestamp
        });
        
        emit OrderPlaced(orderId, msg.sender, tokenIn, tokenOut, amountIn, price);
        
        return orderId;
    }
    
    /**
     * @dev Fill an order
     */
    function fillOrder(bytes32 orderId, uint256 amountOut) external nonReentrant whenNotPaused {
        Order storage order = orders[orderId];
        
        require(!order.filled, "Order already filled");
        require(amountOut >= (order.amountIn * order.price) / 1e18, "Price not met");
        
        order.filled = true;
        
        IERC20(order.tokenIn).transfer(msg.sender, order.amountIn);
        IERC20(order.tokenOut).transferFrom(msg.sender, order.trader, amountOut);
        
        emit OrderFilled(orderId, msg.sender, amountOut);
    }
    
    /**
     * @dev Cancel an order
     */
    function cancelOrder(bytes32 orderId) external {
        Order storage order = orders[orderId];
        
        require(msg.sender == order.trader, "Not order owner");
        require(!order.filled, "Order already filled");
        
        order.filled = true;
        IERC20(order.tokenIn).transfer(order.trader, order.amountIn);
    }
    
    /**
     * @dev Set trading fee
     */
    function setTradingFee(uint256 _fee) external onlyRole(FEE_MANAGER_ROLE) {
        require(_fee <= 1000, "Fee too high"); // Max 10%
        tradingFee = _fee;
    }
    
    /**
     * @dev Pause exchange
     */
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause exchange
     */
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Collect accumulated fees
     */
    function collectFees(address token, uint256 amount) external onlyRole(ADMIN_ROLE) {
        IERC20(token).transfer(feeRecipient, amount);
        emit FeeCollected(token, amount);
    }
    
    // Helper function
    function sqrt(uint256 y) internal pure returns (uint256 z) {
        if (y > 3) {
            z = y;
            uint256 x = y / 2 + 1;
            while (x < z) {
                z = x;
                x = (y / x + x) / 2;
            }
        } else if (y != 0) {
            z = 1;
        }
    }
}

/**
 * @title TigerExStaking
 * @dev Staking contract for TGX token with tiered rewards
 */
contract TigerExStaking is AccessControl, ReentrancyGuard, Pausable {
    using Counters for Counters.Counter;
    
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    
    IERC20 public stakingToken;
    IERC20 public rewardToken;
    
    // Staking tiers
    struct Tier {
        string name;
        uint256 lockPeriod; // in seconds
        uint256 apy; // Annual percentage yield in basis points
        uint256 minStake;
        uint256 maxStake;
        bool active;
    }
    
    mapping(uint256 => Tier) public tiers;
    uint256 public tierCount;
    
    // User stakes
    struct Stake {
        uint256 amount;
        uint256 startTime;
        uint256 endTime;
        uint256 tierId;
        uint256 rewardDebt;
        bool active;
    }
    
    mapping(address => Stake[]) public userStakes;
    
    // Events
    event Staked(address indexed user, uint256 amount, uint256 tierId, uint256 stakeIndex);
    event Unstaked(address indexed user, uint256 amount, uint256 reward, uint256 stakeIndex);
    event TierAdded(uint256 tierId, string name, uint256 apy);
    
    constructor(address _stakingToken, address _rewardToken) {
        stakingToken = IERC20(_stakingToken);
        rewardToken = IERC20(_rewardToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        
        // Add default tiers
        _addTier("Regular", 0, 500, 100 * 10**18, 0); // 5% APY, no lock
        _addTier("VIP", 30 days, 1000, 1000 * 10**18, 0); // 10% APY, 30 day lock
        _addTier("Elite", 90 days, 2000, 10000 * 10**18, 0); // 20% APY, 90 day lock
    }
    
    function _addTier(
        string memory name,
        uint256 lockPeriod,
        uint256 apy,
        uint256 minStake,
        uint256 maxStake
    ) internal {
        tiers[tierCount] = Tier({
            name: name,
            lockPeriod: lockPeriod,
            apy: apy,
            minStake: minStake,
            maxStake: maxStake,
            active: true
        });
        
        emit TierAdded(tierCount, name, apy);
        tierCount++;
    }
    
    function addTier(
        string memory name,
        uint256 lockPeriod,
        uint256 apy,
        uint256 minStake,
        uint256 maxStake
    ) external onlyRole(ADMIN_ROLE) {
        _addTier(name, lockPeriod, apy, minStake, maxStake);
    }
    
    function stake(uint256 amount, uint256 tierId) external nonReentrant whenNotPaused {
        require(tierId < tierCount, "Invalid tier");
        Tier storage tier = tiers[tierId];
        require(tier.active, "Tier not active");
        require(amount >= tier.minStake, "Below minimum stake");
        if (tier.maxStake > 0) {
            require(amount <= tier.maxStake, "Above maximum stake");
        }
        
        stakingToken.transferFrom(msg.sender, address(this), amount);
        
        uint256 endTime = block.timestamp + tier.lockPeriod;
        
        userStakes[msg.sender].push(Stake({
            amount: amount,
            startTime: block.timestamp,
            endTime: endTime,
            tierId: tierId,
            rewardDebt: 0,
            active: true
        }));
        
        emit Staked(msg.sender, amount, tierId, userStakes[msg.sender].length - 1);
    }
    
    function unstake(uint256 stakeIndex) external nonReentrant {
        require(stakeIndex < userStakes[msg.sender].length, "Invalid stake index");
        Stake storage userStake = userStakes[msg.sender][stakeIndex];
        
        require(userStake.active, "Stake not active");
        require(block.timestamp >= userStake.endTime, "Lock period not ended");
        
        Tier storage tier = tiers[userStake.tierId];
        
        // Calculate reward
        uint256 duration = block.timestamp - userStake.startTime;
        uint256 reward = (userStake.amount * tier.apy * duration) / (365 days * 10000);
        
        userStake.active = false;
        
        stakingToken.transfer(msg.sender, userStake.amount);
        if (reward > 0) {
            rewardToken.transfer(msg.sender, reward);
        }
        
        emit Unstaked(msg.sender, userStake.amount, reward, stakeIndex);
    }
    
    function getPendingReward(address user, uint256 stakeIndex) external view returns (uint256) {
        require(stakeIndex < userStakes[user].length, "Invalid stake index");
        Stake storage userStake = userStakes[user][stakeIndex];
        
        if (!userStake.active) return 0;
        
        Tier storage tier = tiers[userStake.tierId];
        uint256 duration = block.timestamp - userStake.startTime;
        
        return (userStake.amount * tier.apy * duration) / (365 days * 10000);
    }
    
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }
}

/**
 * @title TigerExGovernance
 * @dev Governance contract for DAO functionality
 */
contract TigerExGovernance is AccessControl {
    using Counters for Counters.Counter;
    
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    
    IERC20 public governanceToken;
    
    struct Proposal {
        uint256 id;
        string description;
        address proposer;
        uint256 forVotes;
        uint256 againstVotes;
        uint256 startTime;
        uint256 endTime;
        bool executed;
        bool passed;
        bytes callData;
        address target;
    }
    
    mapping(uint256 => Proposal) public proposals;
    mapping(address => mapping(uint256 => bool)) public hasVoted;
    
    Counters.Counter private _proposalIdCounter;
    
    uint256 public votingPeriod = 3 days;
    uint256 public quorum = 1000 * 10**18; // 1000 tokens
    uint256 public proposalThreshold = 100 * 10**18; // 100 tokens to create proposal
    
    event ProposalCreated(uint256 indexed proposalId, address proposer, string description);
    event Voted(uint256 indexed proposalId, address voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId, bool passed);
    
    constructor(address _governanceToken) {
        governanceToken = IERC20(_governanceToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
    }
    
    function createProposal(
        string memory description,
        address target,
        bytes memory callData
    ) external returns (uint256) {
        require(
            governanceToken.balanceOf(msg.sender) >= proposalThreshold,
            "Below proposal threshold"
        );
        
        uint256 proposalId = _proposalIdCounter.current();
        _proposalIdCounter.increment();
        
        proposals[proposalId] = Proposal({
            id: proposalId,
            description: description,
            proposer: msg.sender,
            forVotes: 0,
            againstVotes: 0,
            startTime: block.timestamp,
            endTime: block.timestamp + votingPeriod,
            executed: false,
            passed: false,
            callData: callData,
            target: target
        });
        
        emit ProposalCreated(proposalId, msg.sender, description);
        
        return proposalId;
    }
    
    function vote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.timestamp >= proposal.startTime, "Voting not started");
        require(block.timestamp <= proposal.endTime, "Voting ended");
        require(!hasVoted[msg.sender][proposalId], "Already voted");
        
        uint256 weight = governanceToken.balanceOf(msg.sender);
        require(weight > 0, "No voting power");
        
        hasVoted[msg.sender][proposalId] = true;
        
        if (support) {
            proposal.forVotes += weight;
        } else {
            proposal.againstVotes += weight;
        }
        
        emit Voted(proposalId, msg.sender, support, weight);
    }
    
    function executeProposal(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        
        require(!proposal.executed, "Already executed");
        require(block.timestamp > proposal.endTime, "Voting not ended");
        
        uint256 totalVotes = proposal.forVotes + proposal.againstVotes;
        require(totalVotes >= quorum, "Quorum not reached");
        
        proposal.passed = proposal.forVotes > proposal.againstVotes;
        proposal.executed = true;
        
        if (proposal.passed && proposal.target != address(0)) {
            (bool success, ) = proposal.target.call(proposal.callData);
            require(success, "Execution failed");
        }
        
        emit ProposalExecuted(proposalId, proposal.passed);
    }
    
    function getProposal(uint256 proposalId) external view returns (Proposal memory) {
        return proposals[proposalId];
    }
}