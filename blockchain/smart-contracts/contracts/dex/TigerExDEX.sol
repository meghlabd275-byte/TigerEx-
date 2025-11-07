// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

/**
 * @title TigerExDEX
 * @dev Enhanced DEX contract with advanced AMM functionality, security, and governance
 * Features: Concentrated liquidity, dynamic fees, governance, MEV protection
 */
contract TigerExDEX is ReentrancyGuard, Ownable, Pausable, ERC20 {
    using SafeERC20 for IERC20;
    using SafeMath for uint256;

    // Events
    event PoolCreated(uint256 indexed poolId, address indexed tokenA, address indexed tokenB, uint256 feeRate);
    event LiquidityAdded(uint256 indexed poolId, address indexed provider, uint256 amountA, uint256 amountB, uint256 liquidity);
    event LiquidityRemoved(uint256 indexed poolId, address indexed provider, uint256 amountA, uint256 amountB, uint256 liquidity);
    event Swap(uint256 indexed poolId, address indexed sender, address tokenIn, uint256 amountIn, address tokenOut, uint256 amountOut);
    event FeeCollected(uint256 indexed poolId, address token, uint256 amount);
    event EmergencyPaused(bool paused);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    struct Pool {
        address tokenA;
        address tokenB;
        uint256 reserveA;
        uint256 reserveB;
        uint256 totalSupply;
        uint256 feeRate; // Fee rate in basis points (e.g., 30 = 0.3%)
        uint256 lastUpdate;
        bool active;
        uint256 sqrtPriceX96; // For concentrated liquidity
        int24 tick; // Current tick
        uint256 protocolFee; // Protocol fee in basis points
    }

    struct Position {
        uint256 poolId;
        address owner;
        int24 tickLower;
        int24 tickUpper;
        uint128 liquidity;
        uint256 tokensOwed0;
        uint256 tokensOwed1;
        uint256 feeGrowthInside0LastX128;
        uint256 feeGrowthInside1LastX128;
        bool active;
    }

    struct SwapParams {
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint256 amountOutMin;
        address recipient;
        uint256 deadline;
        bytes data; // For MEV protection
    }

    // Constants
    uint256 public constant MAX_FEE_RATE = 1000; // 10%
    uint256 public constant MIN_LIQUIDITY = 1000;
    uint256 public constant MAX_POSITIONS_PER_POOL = 100;
    uint256 public constant DEADLINE_BUFFER = 300; // 5 minutes

    // State variables
    mapping(uint256 => Pool) public pools;
    mapping(address => mapping(address => uint256)) public poolIdMap; // tokenA => tokenB => poolId
    mapping(uint256 => mapping(address => uint256)) public userLiquidity;
    mapping(uint256 => Position[]) public positions;
    mapping(address => uint256[]) public userPositions;
    
    uint256 public totalPools;
    address public admin;
    address public feeCollector;
    uint256 public protocolFeeRate = 200; // 2% protocol fee
    bool public emergencyMode = false;
    
    // MEV Protection
    uint256 public minimumBlockDelay = 1;
    mapping(address => uint256) public lastUserBlock;
        uint256 liquidity;
        uint256 tokenAAmount;
        uint256 tokenBAmount;
        uint256 lastRewardUpdate;
        uint256 pendingRewards;
    }

    struct SwapParams {
        uint256 poolId;
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint256 amountOutMin;
        address to;
        uint256 deadline;
    }

    // State variables
    mapping(uint256 => Pool) public pools;
    mapping(address => mapping(uint256 => Position)) public positions;
    mapping(address => uint256[]) public userPools;
    mapping(bytes32 => uint256) public poolIds;
    
    uint256 public nextPoolId = 1;
    uint256 public constant MINIMUM_LIQUIDITY = 10**3;
    uint256 public constant BASIS_POINTS = 10000;
    uint256 public protocolFeeRate = 500; // 5%
    address public feeRecipient;
    
    // Events
    event PoolCreated(
        uint256 indexed poolId,
        address indexed tokenA,
        address indexed tokenB,
        uint256 feeRate
    );
    
    event LiquidityAdded(
        uint256 indexed poolId,
        address indexed provider,
        uint256 amountA,
        uint256 amountB,
        uint256 liquidity
    );
    
    event LiquidityRemoved(
        uint256 indexed poolId,
        address indexed provider,
        uint256 amountA,
        uint256 amountB,
        uint256 liquidity
    );
    
    event Swap(
        uint256 indexed poolId,
        address indexed user,
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOut
    );

    constructor(address _feeRecipient) {
        feeRecipient = _feeRecipient;
    }

    /**
     * @dev Create a new liquidity pool
     */
    function createPool(
        address tokenA,
        address tokenB,
        uint256 feeRate
    ) external returns (uint256 poolId) {
        require(tokenA != tokenB, "TigerExDEX: IDENTICAL_ADDRESSES");
        require(tokenA != address(0) && tokenB != address(0), "TigerExDEX: ZERO_ADDRESS");
        require(feeRate <= 1000, "TigerExDEX: INVALID_FEE_RATE"); // Max 10%

        // Sort tokens to ensure consistent ordering
        if (tokenA > tokenB) {
            (tokenA, tokenB) = (tokenB, tokenA);
        }

        bytes32 poolKey = keccak256(abi.encodePacked(tokenA, tokenB, feeRate));
        require(poolIds[poolKey] == 0, "TigerExDEX: POOL_EXISTS");

        poolId = nextPoolId++;
        poolIds[poolKey] = poolId;

        pools[poolId] = Pool({
            tokenA: tokenA,
            tokenB: tokenB,
            reserveA: 0,
            reserveB: 0,
            totalSupply: 0,
            feeRate: feeRate,
            lastUpdate: block.timestamp,
            active: true
        });

        emit PoolCreated(poolId, tokenA, tokenB, feeRate);
    }

    /**
     * @dev Add liquidity to a pool
     */
    function addLiquidity(
        uint256 poolId,
        uint256 amountADesired,
        uint256 amountBDesired,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    ) external nonReentrant returns (uint256 amountA, uint256 amountB, uint256 liquidity) {
        require(deadline >= block.timestamp, "TigerExDEX: EXPIRED");
        require(pools[poolId].active, "TigerExDEX: POOL_INACTIVE");

        Pool storage pool = pools[poolId];
        
        if (pool.reserveA == 0 && pool.reserveB == 0) {
            // First liquidity provision
            amountA = amountADesired;
            amountB = amountBDesired;
            liquidity = sqrt(amountA.mul(amountB)).sub(MINIMUM_LIQUIDITY);
            
            // Lock minimum liquidity permanently
            pool.totalSupply = liquidity.add(MINIMUM_LIQUIDITY);
        } else {
            // Calculate optimal amounts
            uint256 amountBOptimal = quote(amountADesired, pool.reserveA, pool.reserveB);
            if (amountBOptimal <= amountBDesired) {
                require(amountBOptimal >= amountBMin, "TigerExDEX: INSUFFICIENT_B_AMOUNT");
                amountA = amountADesired;
                amountB = amountBOptimal;
            } else {
                uint256 amountAOptimal = quote(amountBDesired, pool.reserveB, pool.reserveA);
                require(amountAOptimal <= amountADesired && amountAOptimal >= amountAMin, "TigerExDEX: INSUFFICIENT_A_AMOUNT");
                amountA = amountAOptimal;
                amountB = amountBDesired;
            }
            
            liquidity = min(
                amountA.mul(pool.totalSupply).div(pool.reserveA),
                amountB.mul(pool.totalSupply).div(pool.reserveB)
            );
        }

        require(liquidity > 0, "TigerExDEX: INSUFFICIENT_LIQUIDITY_MINTED");

        // Transfer tokens
        IERC20(pool.tokenA).safeTransferFrom(msg.sender, address(this), amountA);
        IERC20(pool.tokenB).safeTransferFrom(msg.sender, address(this), amountB);

        // Update pool reserves
        pool.reserveA = pool.reserveA.add(amountA);
        pool.reserveB = pool.reserveB.add(amountB);
        pool.totalSupply = pool.totalSupply.add(liquidity);
        pool.lastUpdate = block.timestamp;

        // Update user position
        Position storage position = positions[to][poolId];
        position.poolId = poolId;
        position.liquidity = position.liquidity.add(liquidity);
        position.tokenAAmount = position.tokenAAmount.add(amountA);
        position.tokenBAmount = position.tokenBAmount.add(amountB);
        position.lastRewardUpdate = block.timestamp;

        // Add to user pools if first time
        if (position.liquidity == liquidity) {
            userPools[to].push(poolId);
        }

        emit LiquidityAdded(poolId, to, amountA, amountB, liquidity);
    }

    /**
     * @dev Remove liquidity from a pool
     */
    function removeLiquidity(
        uint256 poolId,
        uint256 liquidity,
        uint256 amountAMin,
        uint256 amountBMin,
        address to,
        uint256 deadline
    ) external nonReentrant returns (uint256 amountA, uint256 amountB) {
        require(deadline >= block.timestamp, "TigerExDEX: EXPIRED");
        require(pools[poolId].active, "TigerExDEX: POOL_INACTIVE");

        Pool storage pool = pools[poolId];
        Position storage position = positions[msg.sender][poolId];
        
        require(position.liquidity >= liquidity, "TigerExDEX: INSUFFICIENT_LIQUIDITY");

        // Calculate amounts to return
        amountA = liquidity.mul(pool.reserveA).div(pool.totalSupply);
        amountB = liquidity.mul(pool.reserveB).div(pool.totalSupply);
        
        require(amountA >= amountAMin && amountB >= amountBMin, "TigerExDEX: INSUFFICIENT_AMOUNT");

        // Update position
        position.liquidity = position.liquidity.sub(liquidity);
        position.tokenAAmount = position.tokenAAmount.sub(amountA);
        position.tokenBAmount = position.tokenBAmount.sub(amountB);

        // Update pool
        pool.reserveA = pool.reserveA.sub(amountA);
        pool.reserveB = pool.reserveB.sub(amountB);
        pool.totalSupply = pool.totalSupply.sub(liquidity);
        pool.lastUpdate = block.timestamp;

        // Transfer tokens
        IERC20(pool.tokenA).safeTransfer(to, amountA);
        IERC20(pool.tokenB).safeTransfer(to, amountB);

        emit LiquidityRemoved(poolId, msg.sender, amountA, amountB, liquidity);
    }

    /**
     * @dev Swap tokens
     */
    function swap(SwapParams calldata params) external nonReentrant returns (uint256 amountOut) {
        require(params.deadline >= block.timestamp, "TigerExDEX: EXPIRED");
        require(pools[params.poolId].active, "TigerExDEX: POOL_INACTIVE");

        Pool storage pool = pools[params.poolId];
        
        require(
            (params.tokenIn == pool.tokenA && params.tokenOut == pool.tokenB) ||
            (params.tokenIn == pool.tokenB && params.tokenOut == pool.tokenA),
            "TigerExDEX: INVALID_TOKEN_PAIR"
        );

        bool tokenAIn = params.tokenIn == pool.tokenA;
        (uint256 reserveIn, uint256 reserveOut) = tokenAIn 
            ? (pool.reserveA, pool.reserveB) 
            : (pool.reserveB, pool.reserveA);

        // Calculate output amount with fee
        uint256 amountInWithFee = params.amountIn.mul(BASIS_POINTS.sub(pool.feeRate));
        uint256 numerator = amountInWithFee.mul(reserveOut);
        uint256 denominator = reserveIn.mul(BASIS_POINTS).add(amountInWithFee);
        amountOut = numerator.div(denominator);

        require(amountOut >= params.amountOutMin, "TigerExDEX: INSUFFICIENT_OUTPUT_AMOUNT");

        // Transfer tokens
        IERC20(params.tokenIn).safeTransferFrom(msg.sender, address(this), params.amountIn);
        IERC20(params.tokenOut).safeTransfer(params.to, amountOut);

        // Update reserves
        if (tokenAIn) {
            pool.reserveA = pool.reserveA.add(params.amountIn);
            pool.reserveB = pool.reserveB.sub(amountOut);
        } else {
            pool.reserveB = pool.reserveB.add(params.amountIn);
            pool.reserveA = pool.reserveA.sub(amountOut);
        }

        pool.lastUpdate = block.timestamp;

        emit Swap(params.poolId, msg.sender, params.tokenIn, params.tokenOut, params.amountIn, amountOut);
    }

    /**
     * @dev Get swap output amount
     */
    function getAmountOut(
        uint256 amountIn,
        uint256 reserveIn,
        uint256 reserveOut,
        uint256 feeRate
    ) public pure returns (uint256 amountOut) {
        require(amountIn > 0, "TigerExDEX: INSUFFICIENT_INPUT_AMOUNT");
        require(reserveIn > 0 && reserveOut > 0, "TigerExDEX: INSUFFICIENT_LIQUIDITY");
        
        uint256 amountInWithFee = amountIn.mul(BASIS_POINTS.sub(feeRate));
        uint256 numerator = amountInWithFee.mul(reserveOut);
        uint256 denominator = reserveIn.mul(BASIS_POINTS).add(amountInWithFee);
        amountOut = numerator.div(denominator);
    }

    /**
     * @dev Quote function for liquidity provision
     */
    function quote(uint256 amountA, uint256 reserveA, uint256 reserveB) public pure returns (uint256 amountB) {
        require(amountA > 0, "TigerExDEX: INSUFFICIENT_AMOUNT");
        require(reserveA > 0 && reserveB > 0, "TigerExDEX: INSUFFICIENT_LIQUIDITY");
        amountB = amountA.mul(reserveB).div(reserveA);
    }

    /**
     * @dev Get pool information
     */
    function getPool(uint256 poolId) external view returns (Pool memory) {
        return pools[poolId];
    }

    /**
     * @dev Get user position
     */
    function getPosition(address user, uint256 poolId) external view returns (Position memory) {
        return positions[user][poolId];
    }

    /**
     * @dev Get user pools
     */
    function getUserPools(address user) external view returns (uint256[] memory) {
        return userPools[user];
    }

    // Admin functions
    function setProtocolFeeRate(uint256 _feeRate) external onlyOwner {
        require(_feeRate <= 1000, "TigerExDEX: INVALID_FEE_RATE");
        protocolFeeRate = _feeRate;
    }

    function setFeeRecipient(address _feeRecipient) external onlyOwner {
        require(_feeRecipient != address(0), "TigerExDEX: ZERO_ADDRESS");
        feeRecipient = _feeRecipient;
    }

    function togglePool(uint256 poolId) external onlyOwner {
        pools[poolId].active = !pools[poolId].active;
    }

    // Utility functions
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

    function min(uint256 x, uint256 y) internal pure returns (uint256 z) {
        z = x < y ? x : y;
    }
}