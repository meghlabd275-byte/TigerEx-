// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title LiquidityPool
 * @dev Automated Market Maker (AMM) liquidity pool with LP tokens
 */
contract LiquidityPool is ERC20, ReentrancyGuard, Ownable {
    
    IERC20 public immutable token0;
    IERC20 public immutable token1;
    
    uint256 public reserve0;
    uint256 public reserve1;
    
    uint256 public constant MINIMUM_LIQUIDITY = 10**3;
    uint256 public constant FEE_DENOMINATOR = 10000;
    uint256 public tradingFee = 30; // 0.3%
    
    event LiquidityAdded(address indexed provider, uint256 amount0, uint256 amount1, uint256 liquidity);
    event LiquidityRemoved(address indexed provider, uint256 amount0, uint256 amount1, uint256 liquidity);
    event Swap(address indexed trader, uint256 amountIn, uint256 amountOut, address tokenIn, address tokenOut);
    event Sync(uint256 reserve0, uint256 reserve1);
    
    constructor(
        address _token0,
        address _token1,
        string memory _name,
        string memory _symbol
    ) ERC20(_name, _symbol) Ownable(msg.sender) {
        token0 = IERC20(_token0);
        token1 = IERC20(_token1);
    }
    
    /**
     * @dev Add liquidity to the pool
     */
    function addLiquidity(
        uint256 _amount0,
        uint256 _amount1,
        uint256 _minLiquidity
    ) external nonReentrant returns (uint256 liquidity) {
        require(_amount0 > 0 && _amount1 > 0, "Invalid amounts");
        
        // Transfer tokens
        token0.transferFrom(msg.sender, address(this), _amount0);
        token1.transferFrom(msg.sender, address(this), _amount1);
        
        uint256 _totalSupply = totalSupply();
        
        if (_totalSupply == 0) {
            // First liquidity provider
            liquidity = sqrt(_amount0 * _amount1) - MINIMUM_LIQUIDITY;
            _mint(address(1), MINIMUM_LIQUIDITY); // Lock minimum liquidity
        } else {
            // Subsequent liquidity providers
            liquidity = min(
                (_amount0 * _totalSupply) / reserve0,
                (_amount1 * _totalSupply) / reserve1
            );
        }
        
        require(liquidity >= _minLiquidity, "Insufficient liquidity minted");
        require(liquidity > 0, "Insufficient liquidity");
        
        _mint(msg.sender, liquidity);
        
        _update(_amount0, _amount1);
        
        emit LiquidityAdded(msg.sender, _amount0, _amount1, liquidity);
    }
    
    /**
     * @dev Remove liquidity from the pool
     */
    function removeLiquidity(
        uint256 _liquidity,
        uint256 _minAmount0,
        uint256 _minAmount1
    ) external nonReentrant returns (uint256 amount0, uint256 amount1) {
        require(_liquidity > 0, "Invalid liquidity");
        
        uint256 _totalSupply = totalSupply();
        
        amount0 = (_liquidity * reserve0) / _totalSupply;
        amount1 = (_liquidity * reserve1) / _totalSupply;
        
        require(amount0 >= _minAmount0 && amount1 >= _minAmount1, "Insufficient output");
        require(amount0 > 0 && amount1 > 0, "Insufficient liquidity burned");
        
        _burn(msg.sender, _liquidity);
        
        token0.transfer(msg.sender, amount0);
        token1.transfer(msg.sender, amount1);
        
        _update(reserve0 - amount0, reserve1 - amount1);
        
        emit LiquidityRemoved(msg.sender, amount0, amount1, _liquidity);
    }
    
    /**
     * @dev Swap tokens
     */
    function swap(
        uint256 _amountIn,
        uint256 _minAmountOut,
        address _tokenIn
    ) external nonReentrant returns (uint256 amountOut) {
        require(_amountIn > 0, "Invalid input amount");
        require(_tokenIn == address(token0) || _tokenIn == address(token1), "Invalid token");
        
        bool isToken0 = _tokenIn == address(token0);
        (IERC20 tokenIn, IERC20 tokenOut, uint256 reserveIn, uint256 reserveOut) = 
            isToken0 ? (token0, token1, reserve0, reserve1) : (token1, token0, reserve1, reserve0);
        
        // Transfer input tokens
        tokenIn.transferFrom(msg.sender, address(this), _amountIn);
        
        // Calculate output amount with fee
        uint256 amountInWithFee = _amountIn * (FEE_DENOMINATOR - tradingFee);
        amountOut = (amountInWithFee * reserveOut) / (reserveIn * FEE_DENOMINATOR + amountInWithFee);
        
        require(amountOut >= _minAmountOut, "Insufficient output amount");
        require(amountOut > 0, "Insufficient liquidity");
        
        // Transfer output tokens
        tokenOut.transfer(msg.sender, amountOut);
        
        // Update reserves
        if (isToken0) {
            _update(reserve0 + _amountIn, reserve1 - amountOut);
        } else {
            _update(reserve0 - amountOut, reserve1 + _amountIn);
        }
        
        emit Swap(msg.sender, _amountIn, amountOut, _tokenIn, address(tokenOut));
    }
    
    /**
     * @dev Get amount out for a given input
     */
    function getAmountOut(
        uint256 _amountIn,
        address _tokenIn
    ) external view returns (uint256 amountOut) {
        require(_tokenIn == address(token0) || _tokenIn == address(token1), "Invalid token");
        
        bool isToken0 = _tokenIn == address(token0);
        (uint256 reserveIn, uint256 reserveOut) = 
            isToken0 ? (reserve0, reserve1) : (reserve1, reserve0);
        
        uint256 amountInWithFee = _amountIn * (FEE_DENOMINATOR - tradingFee);
        amountOut = (amountInWithFee * reserveOut) / (reserveIn * FEE_DENOMINATOR + amountInWithFee);
    }
    
    /**
     * @dev Update reserves
     */
    function _update(uint256 _reserve0, uint256 _reserve1) private {
        reserve0 = _reserve0;
        reserve1 = _reserve1;
        emit Sync(reserve0, reserve1);
    }
    
    /**
     * @dev Set trading fee (owner only)
     */
    function setTradingFee(uint256 _newFee) external onlyOwner {
        require(_newFee <= 100, "Fee too high"); // Max 1%
        tradingFee = _newFee;
    }
    
    /**
     * @dev Square root function
     */
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
    
    /**
     * @dev Minimum function
     */
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
    
    /**
     * @dev Get reserves
     */
    function getReserves() external view returns (uint256, uint256) {
        return (reserve0, reserve1);
    }
}