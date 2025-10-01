// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title FuturesContract
 * @dev Decentralized futures trading contract with perpetual and delivery contracts
 */
contract FuturesContract is Ownable, ReentrancyGuard, Pausable {
    
    enum ContractType { PERPETUAL, DELIVERY }
    enum PositionSide { LONG, SHORT }
    
    struct Position {
        address trader;
        PositionSide side;
        uint256 size;
        uint256 entryPrice;
        uint256 leverage;
        uint256 margin;
        uint256 liquidationPrice;
        uint256 timestamp;
        bool isActive;
    }
    
    struct FuturesMarket {
        string symbol;
        ContractType contractType;
        uint256 markPrice;
        uint256 indexPrice;
        uint256 fundingRate;
        uint256 maxLeverage;
        uint256 maintenanceMarginRate;
        uint256 openInterest;
        bool isActive;
    }
    
    // State variables
    mapping(bytes32 => FuturesMarket) public markets;
    mapping(address => mapping(bytes32 => Position[])) public positions;
    mapping(bytes32 => uint256) public totalLongPositions;
    mapping(bytes32 => uint256) public totalShortPositions;
    
    bytes32[] public marketIds;
    
    // Events
    event MarketCreated(bytes32 indexed marketId, string symbol, ContractType contractType);
    event PositionOpened(address indexed trader, bytes32 indexed marketId, PositionSide side, uint256 size, uint256 leverage);
    event PositionClosed(address indexed trader, bytes32 indexed marketId, uint256 pnl);
    event PositionLiquidated(address indexed trader, bytes32 indexed marketId, uint256 liquidationPrice);
    event FundingRateUpdated(bytes32 indexed marketId, uint256 newRate);
    event PriceUpdated(bytes32 indexed marketId, uint256 markPrice, uint256 indexPrice);
    
    constructor() Ownable(msg.sender) {}
    
    /**
     * @dev Create a new futures market
     */
    function createMarket(
        string memory _symbol,
        ContractType _contractType,
        uint256 _maxLeverage,
        uint256 _maintenanceMarginRate
    ) external onlyOwner {
        bytes32 marketId = keccak256(abi.encodePacked(_symbol, _contractType));
        require(!markets[marketId].isActive, "Market already exists");
        
        markets[marketId] = FuturesMarket({
            symbol: _symbol,
            contractType: _contractType,
            markPrice: 0,
            indexPrice: 0,
            fundingRate: 0,
            maxLeverage: _maxLeverage,
            maintenanceMarginRate: _maintenanceMarginRate,
            openInterest: 0,
            isActive: true
        });
        
        marketIds.push(marketId);
        
        emit MarketCreated(marketId, _symbol, _contractType);
    }
    
    /**
     * @dev Open a new position
     */
    function openPosition(
        bytes32 _marketId,
        PositionSide _side,
        uint256 _size,
        uint256 _leverage
    ) external payable nonReentrant whenNotPaused {
        FuturesMarket storage market = markets[_marketId];
        require(market.isActive, "Market not active");
        require(_leverage <= market.maxLeverage, "Leverage too high");
        require(msg.value > 0, "Margin required");
        
        uint256 requiredMargin = (_size * market.markPrice) / _leverage;
        require(msg.value >= requiredMargin, "Insufficient margin");
        
        uint256 liquidationPrice = calculateLiquidationPrice(
            market.markPrice,
            _leverage,
            _side,
            market.maintenanceMarginRate
        );
        
        Position memory newPosition = Position({
            trader: msg.sender,
            side: _side,
            size: _size,
            entryPrice: market.markPrice,
            leverage: _leverage,
            margin: msg.value,
            liquidationPrice: liquidationPrice,
            timestamp: block.timestamp,
            isActive: true
        });
        
        positions[msg.sender][_marketId].push(newPosition);
        
        if (_side == PositionSide.LONG) {
            totalLongPositions[_marketId] += _size;
        } else {
            totalShortPositions[_marketId] += _size;
        }
        
        market.openInterest += _size;
        
        emit PositionOpened(msg.sender, _marketId, _side, _size, _leverage);
    }
    
    /**
     * @dev Close a position
     */
    function closePosition(
        bytes32 _marketId,
        uint256 _positionIndex
    ) external nonReentrant {
        Position[] storage userPositions = positions[msg.sender][_marketId];
        require(_positionIndex < userPositions.length, "Invalid position");
        
        Position storage position = userPositions[_positionIndex];
        require(position.isActive, "Position not active");
        
        FuturesMarket storage market = markets[_marketId];
        
        // Calculate PnL
        int256 pnl = calculatePnL(position, market.markPrice);
        
        // Transfer funds
        uint256 totalReturn = position.margin;
        if (pnl > 0) {
            totalReturn += uint256(pnl);
        } else if (pnl < 0) {
            uint256 loss = uint256(-pnl);
            if (loss < totalReturn) {
                totalReturn -= loss;
            } else {
                totalReturn = 0;
            }
        }
        
        if (totalReturn > 0) {
            payable(msg.sender).transfer(totalReturn);
        }
        
        // Update state
        position.isActive = false;
        
        if (position.side == PositionSide.LONG) {
            totalLongPositions[_marketId] -= position.size;
        } else {
            totalShortPositions[_marketId] -= position.size;
        }
        
        market.openInterest -= position.size;
        
        emit PositionClosed(msg.sender, _marketId, totalReturn);
    }
    
    /**
     * @dev Liquidate a position
     */
    function liquidatePosition(
        address _trader,
        bytes32 _marketId,
        uint256 _positionIndex
    ) external nonReentrant {
        Position[] storage userPositions = positions[_trader][_marketId];
        require(_positionIndex < userPositions.length, "Invalid position");
        
        Position storage position = userPositions[_positionIndex];
        require(position.isActive, "Position not active");
        
        FuturesMarket storage market = markets[_marketId];
        
        // Check if position should be liquidated
        bool shouldLiquidate = false;
        if (position.side == PositionSide.LONG) {
            shouldLiquidate = market.markPrice <= position.liquidationPrice;
        } else {
            shouldLiquidate = market.markPrice >= position.liquidationPrice;
        }
        
        require(shouldLiquidate, "Position not liquidatable");
        
        // Liquidate position
        position.isActive = false;
        
        if (position.side == PositionSide.LONG) {
            totalLongPositions[_marketId] -= position.size;
        } else {
            totalShortPositions[_marketId] -= position.size;
        }
        
        market.openInterest -= position.size;
        
        // Liquidation fee to liquidator (5% of margin)
        uint256 liquidationFee = (position.margin * 5) / 100;
        payable(msg.sender).transfer(liquidationFee);
        
        emit PositionLiquidated(_trader, _marketId, position.liquidationPrice);
    }
    
    /**
     * @dev Update market prices (oracle function)
     */
    function updatePrices(
        bytes32 _marketId,
        uint256 _markPrice,
        uint256 _indexPrice
    ) external onlyOwner {
        FuturesMarket storage market = markets[_marketId];
        require(market.isActive, "Market not active");
        
        market.markPrice = _markPrice;
        market.indexPrice = _indexPrice;
        
        emit PriceUpdated(_marketId, _markPrice, _indexPrice);
    }
    
    /**
     * @dev Update funding rate for perpetual contracts
     */
    function updateFundingRate(
        bytes32 _marketId,
        uint256 _newRate
    ) external onlyOwner {
        FuturesMarket storage market = markets[_marketId];
        require(market.isActive, "Market not active");
        require(market.contractType == ContractType.PERPETUAL, "Not a perpetual contract");
        
        market.fundingRate = _newRate;
        
        emit FundingRateUpdated(_marketId, _newRate);
    }
    
    /**
     * @dev Calculate liquidation price
     */
    function calculateLiquidationPrice(
        uint256 _entryPrice,
        uint256 _leverage,
        PositionSide _side,
        uint256 _maintenanceMarginRate
    ) public pure returns (uint256) {
        if (_side == PositionSide.LONG) {
            return (_entryPrice * (100 - (100 / _leverage) + _maintenanceMarginRate)) / 100;
        } else {
            return (_entryPrice * (100 + (100 / _leverage) - _maintenanceMarginRate)) / 100;
        }
    }
    
    /**
     * @dev Calculate PnL for a position
     */
    function calculatePnL(
        Position memory _position,
        uint256 _currentPrice
    ) public pure returns (int256) {
        if (_position.side == PositionSide.LONG) {
            return int256((_currentPrice - _position.entryPrice) * _position.size);
        } else {
            return int256((_position.entryPrice - _currentPrice) * _position.size);
        }
    }
    
    /**
     * @dev Get user positions
     */
    function getUserPositions(
        address _trader,
        bytes32 _marketId
    ) external view returns (Position[] memory) {
        return positions[_trader][_marketId];
    }
    
    /**
     * @dev Get market info
     */
    function getMarket(bytes32 _marketId) external view returns (FuturesMarket memory) {
        return markets[_marketId];
    }
    
    /**
     * @dev Get all markets
     */
    function getAllMarkets() external view returns (bytes32[] memory) {
        return marketIds;
    }
    
    /**
     * @dev Pause contract
     */
    function pause() external onlyOwner {
        _pause();
    }
    
    /**
     * @dev Unpause contract
     */
    function unpause() external onlyOwner {
        _unpause();
    }
    
    /**
     * @dev Withdraw contract balance (emergency)
     */
    function emergencyWithdraw() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    receive() external payable {}
}