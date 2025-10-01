// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title MarginTradingContract
 * @dev Decentralized margin trading with isolated and cross margin
 */
contract MarginTradingContract is Ownable, ReentrancyGuard {
    
    enum MarginType { ISOLATED, CROSS }
    
    struct MarginAccount {
        MarginType marginType;
        mapping(address => uint256) assets;
        mapping(address => uint256) liabilities;
        uint256 totalAssetValue;
        uint256 totalLiabilityValue;
        bool isActive;
    }
    
    struct Loan {
        address borrower;
        address asset;
        uint256 principal;
        uint256 interestRate;
        uint256 timestamp;
        bool isActive;
    }
    
    struct MarginPair {
        address baseAsset;
        address quoteAsset;
        uint256 maxLeverage;
        uint256 maintenanceMarginRate;
        uint256 interestRateBase;
        uint256 interestRateQuote;
        bool isActive;
    }
    
    // State variables
    mapping(address => mapping(bytes32 => MarginAccount)) public accounts;
    mapping(address => Loan[]) public loans;
    mapping(bytes32 => MarginPair) public pairs;
    mapping(address => uint256) public assetPrices;
    
    bytes32[] public pairIds;
    
    uint256 public constant LIQUIDATION_THRESHOLD = 110; // 110%
    uint256 public constant PRECISION = 10000;
    
    // Events
    event MarginAccountCreated(address indexed user, bytes32 indexed pairId, MarginType marginType);
    event AssetDeposited(address indexed user, address indexed asset, uint256 amount);
    event AssetBorrowed(address indexed user, address indexed asset, uint256 amount);
    event LoanRepaid(address indexed user, uint256 loanId, uint256 amount);
    event AccountLiquidated(address indexed user, bytes32 indexed pairId);
    event PairCreated(bytes32 indexed pairId, address baseAsset, address quoteAsset);
    
    constructor() Ownable(msg.sender) {}
    
    /**
     * @dev Create a new margin trading pair
     */
    function createPair(
        address _baseAsset,
        address _quoteAsset,
        uint256 _maxLeverage,
        uint256 _maintenanceMarginRate,
        uint256 _interestRateBase,
        uint256 _interestRateQuote
    ) external onlyOwner {
        bytes32 pairId = keccak256(abi.encodePacked(_baseAsset, _quoteAsset));
        require(!pairs[pairId].isActive, "Pair already exists");
        
        pairs[pairId] = MarginPair({
            baseAsset: _baseAsset,
            quoteAsset: _quoteAsset,
            maxLeverage: _maxLeverage,
            maintenanceMarginRate: _maintenanceMarginRate,
            interestRateBase: _interestRateBase,
            interestRateQuote: _interestRateQuote,
            isActive: true
        });
        
        pairIds.push(pairId);
        
        emit PairCreated(pairId, _baseAsset, _quoteAsset);
    }
    
    /**
     * @dev Create a margin account
     */
    function createMarginAccount(
        bytes32 _pairId,
        MarginType _marginType
    ) external {
        require(pairs[_pairId].isActive, "Pair not active");
        require(!accounts[msg.sender][_pairId].isActive, "Account already exists");
        
        MarginAccount storage account = accounts[msg.sender][_pairId];
        account.marginType = _marginType;
        account.isActive = true;
        
        emit MarginAccountCreated(msg.sender, _pairId, _marginType);
    }
    
    /**
     * @dev Deposit assets to margin account
     */
    function deposit(
        bytes32 _pairId,
        address _asset,
        uint256 _amount
    ) external nonReentrant {
        require(pairs[_pairId].isActive, "Pair not active");
        require(accounts[msg.sender][_pairId].isActive, "Account not active");
        
        IERC20(_asset).transferFrom(msg.sender, address(this), _amount);
        
        MarginAccount storage account = accounts[msg.sender][_pairId];
        account.assets[_asset] += _amount;
        
        uint256 assetValue = (_amount * assetPrices[_asset]) / PRECISION;
        account.totalAssetValue += assetValue;
        
        emit AssetDeposited(msg.sender, _asset, _amount);
    }
    
    /**
     * @dev Borrow assets for margin trading
     */
    function borrow(
        bytes32 _pairId,
        address _asset,
        uint256 _amount
    ) external nonReentrant {
        require(pairs[_pairId].isActive, "Pair not active");
        require(accounts[msg.sender][_pairId].isActive, "Account not active");
        
        MarginAccount storage account = accounts[msg.sender][_pairId];
        MarginPair storage pair = pairs[_pairId];
        
        // Check borrowing capacity
        uint256 maxBorrowValue = (account.totalAssetValue * pair.maxLeverage) / 10;
        uint256 borrowValue = (_amount * assetPrices[_asset]) / PRECISION;
        
        require(
            account.totalLiabilityValue + borrowValue <= maxBorrowValue,
            "Exceeds borrowing capacity"
        );
        
        // Determine interest rate
        uint256 interestRate;
        if (_asset == pair.baseAsset) {
            interestRate = pair.interestRateBase;
        } else {
            interestRate = pair.interestRateQuote;
        }
        
        // Create loan
        Loan memory newLoan = Loan({
            borrower: msg.sender,
            asset: _asset,
            principal: _amount,
            interestRate: interestRate,
            timestamp: block.timestamp,
            isActive: true
        });
        
        loans[msg.sender].push(newLoan);
        
        // Update account
        account.liabilities[_asset] += _amount;
        account.totalLiabilityValue += borrowValue;
        
        // Transfer borrowed assets
        IERC20(_asset).transfer(msg.sender, _amount);
        
        emit AssetBorrowed(msg.sender, _asset, _amount);
    }
    
    /**
     * @dev Repay a loan
     */
    function repay(
        uint256 _loanId,
        uint256 _amount
    ) external nonReentrant {
        require(_loanId < loans[msg.sender].length, "Invalid loan ID");
        
        Loan storage loan = loans[msg.sender][_loanId];
        require(loan.isActive, "Loan not active");
        
        // Calculate interest
        uint256 timeElapsed = block.timestamp - loan.timestamp;
        uint256 interest = (loan.principal * loan.interestRate * timeElapsed) / (365 days * PRECISION);
        uint256 totalDebt = loan.principal + interest;
        
        require(_amount <= totalDebt, "Amount exceeds debt");
        
        // Transfer repayment
        IERC20(loan.asset).transferFrom(msg.sender, address(this), _amount);
        
        // Update loan
        if (_amount >= totalDebt) {
            loan.isActive = false;
            loan.principal = 0;
        } else {
            loan.principal = totalDebt - _amount;
            loan.timestamp = block.timestamp;
        }
        
        emit LoanRepaid(msg.sender, _loanId, _amount);
    }
    
    /**
     * @dev Liquidate an undercollateralized account
     */
    function liquidate(
        address _user,
        bytes32 _pairId
    ) external nonReentrant {
        MarginAccount storage account = accounts[_user][_pairId];
        require(account.isActive, "Account not active");
        
        // Check if account is undercollateralized
        uint256 marginLevel = (account.totalAssetValue * 100) / account.totalLiabilityValue;
        require(marginLevel < LIQUIDATION_THRESHOLD, "Account not liquidatable");
        
        // Liquidate account
        account.isActive = false;
        
        // Transfer remaining assets to liquidator as reward
        // Implementation depends on specific liquidation logic
        
        emit AccountLiquidated(_user, _pairId);
    }
    
    /**
     * @dev Update asset price (oracle function)
     */
    function updateAssetPrice(
        address _asset,
        uint256 _price
    ) external onlyOwner {
        assetPrices[_asset] = _price;
    }
    
    /**
     * @dev Get account margin level
     */
    function getMarginLevel(
        address _user,
        bytes32 _pairId
    ) external view returns (uint256) {
        MarginAccount storage account = accounts[_user][_pairId];
        
        if (account.totalLiabilityValue == 0) {
            return type(uint256).max;
        }
        
        return (account.totalAssetValue * 100) / account.totalLiabilityValue;
    }
    
    /**
     * @dev Get user loans
     */
    function getUserLoans(address _user) external view returns (Loan[] memory) {
        return loans[_user];
    }
    
    /**
     * @dev Get all pairs
     */
    function getAllPairs() external view returns (bytes32[] memory) {
        return pairIds;
    }
    
    /**
     * @dev Emergency withdraw (owner only)
     */
    function emergencyWithdraw(address _asset) external onlyOwner {
        uint256 balance = IERC20(_asset).balanceOf(address(this));
        IERC20(_asset).transfer(owner(), balance);
    }
}