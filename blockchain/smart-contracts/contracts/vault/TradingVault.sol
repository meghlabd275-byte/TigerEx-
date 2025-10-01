// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title TradingVault
 * @dev Yield-generating vault for trading strategies
 */
contract TradingVault is ERC20, ReentrancyGuard, Ownable, Pausable {
    
    IERC20 public immutable asset;
    
    uint256 public totalAssets;
    uint256 public performanceFee = 2000; // 20%
    uint256 public managementFee = 200; // 2% annual
    uint256 public constant FEE_DENOMINATOR = 10000;
    
    address public feeRecipient;
    uint256 public lastFeeCollection;
    
    mapping(address => uint256) public depositTimestamp;
    uint256 public lockPeriod = 7 days;
    
    event Deposit(address indexed user, uint256 assets, uint256 shares);
    event Withdraw(address indexed user, uint256 assets, uint256 shares);
    event FeesCollected(uint256 performanceFees, uint256 managementFees);
    event StrategyExecuted(uint256 profit, uint256 loss);
    
    constructor(
        address _asset,
        string memory _name,
        string memory _symbol,
        address _feeRecipient
    ) ERC20(_name, _symbol) Ownable(msg.sender) {
        asset = IERC20(_asset);
        feeRecipient = _feeRecipient;
        lastFeeCollection = block.timestamp;
    }
    
    /**
     * @dev Deposit assets and receive vault shares
     */
    function deposit(uint256 _assets) external nonReentrant whenNotPaused returns (uint256 shares) {
        require(_assets > 0, "Invalid amount");
        
        // Calculate shares
        uint256 _totalSupply = totalSupply();
        if (_totalSupply == 0) {
            shares = _assets;
        } else {
            shares = (_assets * _totalSupply) / totalAssets;
        }
        
        require(shares > 0, "Invalid shares");
        
        // Transfer assets
        asset.transferFrom(msg.sender, address(this), _assets);
        
        // Mint shares
        _mint(msg.sender, shares);
        totalAssets += _assets;
        depositTimestamp[msg.sender] = block.timestamp;
        
        emit Deposit(msg.sender, _assets, shares);
    }
    
    /**
     * @dev Withdraw assets by burning vault shares
     */
    function withdraw(uint256 _shares) external nonReentrant returns (uint256 assets) {
        require(_shares > 0, "Invalid shares");
        require(balanceOf(msg.sender) >= _shares, "Insufficient balance");
        require(
            block.timestamp >= depositTimestamp[msg.sender] + lockPeriod,
            "Lock period not expired"
        );
        
        // Calculate assets
        assets = (_shares * totalAssets) / totalSupply();
        require(assets > 0, "Invalid assets");
        
        // Burn shares
        _burn(msg.sender, _shares);
        totalAssets -= assets;
        
        // Transfer assets
        asset.transfer(msg.sender, assets);
        
        emit Withdraw(msg.sender, assets, _shares);
    }
    
    /**
     * @dev Execute trading strategy (owner only)
     */
    function executeStrategy(
        address _target,
        bytes calldata _data,
        uint256 _value
    ) external onlyOwner returns (bool success, bytes memory returnData) {
        require(_target != address(0), "Invalid target");
        
        (success, returnData) = _target.call{value: _value}(_data);
        require(success, "Strategy execution failed");
        
        // Update total assets based on current balance
        uint256 currentBalance = asset.balanceOf(address(this));
        
        if (currentBalance > totalAssets) {
            uint256 profit = currentBalance - totalAssets;
            emit StrategyExecuted(profit, 0);
        } else if (currentBalance < totalAssets) {
            uint256 loss = totalAssets - currentBalance;
            emit StrategyExecuted(0, loss);
        }
        
        totalAssets = currentBalance;
    }
    
    /**
     * @dev Collect management and performance fees
     */
    function collectFees() external onlyOwner {
        uint256 timeElapsed = block.timestamp - lastFeeCollection;
        
        // Calculate management fee
        uint256 managementFeeAmount = (totalAssets * managementFee * timeElapsed) / 
            (365 days * FEE_DENOMINATOR);
        
        // Calculate performance fee (on profits)
        uint256 currentValue = asset.balanceOf(address(this));
        uint256 performanceFeeAmount = 0;
        
        if (currentValue > totalAssets) {
            uint256 profit = currentValue - totalAssets;
            performanceFeeAmount = (profit * performanceFee) / FEE_DENOMINATOR;
        }
        
        uint256 totalFees = managementFeeAmount + performanceFeeAmount;
        
        if (totalFees > 0) {
            asset.transfer(feeRecipient, totalFees);
            totalAssets = asset.balanceOf(address(this));
        }
        
        lastFeeCollection = block.timestamp;
        
        emit FeesCollected(performanceFeeAmount, managementFeeAmount);
    }
    
    /**
     * @dev Get share price
     */
    function sharePrice() external view returns (uint256) {
        uint256 _totalSupply = totalSupply();
        if (_totalSupply == 0) {
            return 1e18;
        }
        return (totalAssets * 1e18) / _totalSupply;
    }
    
    /**
     * @dev Preview deposit
     */
    function previewDeposit(uint256 _assets) external view returns (uint256 shares) {
        uint256 _totalSupply = totalSupply();
        if (_totalSupply == 0) {
            return _assets;
        }
        return (_assets * _totalSupply) / totalAssets;
    }
    
    /**
     * @dev Preview withdraw
     */
    function previewWithdraw(uint256 _shares) external view returns (uint256 assets) {
        uint256 _totalSupply = totalSupply();
        if (_totalSupply == 0) {
            return 0;
        }
        return (_shares * totalAssets) / _totalSupply;
    }
    
    /**
     * @dev Set performance fee
     */
    function setPerformanceFee(uint256 _newFee) external onlyOwner {
        require(_newFee <= 5000, "Fee too high"); // Max 50%
        performanceFee = _newFee;
    }
    
    /**
     * @dev Set management fee
     */
    function setManagementFee(uint256 _newFee) external onlyOwner {
        require(_newFee <= 1000, "Fee too high"); // Max 10%
        managementFee = _newFee;
    }
    
    /**
     * @dev Set lock period
     */
    function setLockPeriod(uint256 _newPeriod) external onlyOwner {
        require(_newPeriod <= 30 days, "Period too long");
        lockPeriod = _newPeriod;
    }
    
    /**
     * @dev Set fee recipient
     */
    function setFeeRecipient(address _newRecipient) external onlyOwner {
        require(_newRecipient != address(0), "Invalid address");
        feeRecipient = _newRecipient;
    }
    
    /**
     * @dev Pause deposits
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause deposits
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Emergency withdraw (owner only)
     */
    function emergencyWithdraw() external onlyOwner {
        uint256 balance = asset.balanceOf(address(this));
        asset.transfer(owner(), balance);
    }
}