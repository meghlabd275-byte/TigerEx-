// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract DeFiHub is Ownable, ReentrancyGuard {
    struct Protocol {
        string name;
        address contractAddress;
        uint256 apy;
        uint256 tvl;
        uint256 riskLevel; // 1-10
        bool isActive;
        uint256 lastUpdated;
    }
    
    struct StakingPosition {
        address user;
        string protocolName;
        address assetAddress;
        uint256 stakedAmount;
        uint256 rewardAmount;
        uint256 apyAtStake;
        uint256 startTime;
        uint256 lastCompound;
        bool isActive;
        bool autoCompound;
    }
    
    struct YieldFarmingPosition {
        address user;
        string protocolName;
        string poolName;
        uint256 lpTokens;
        uint256 rewardTokens;
        uint256 apy;
        uint256 impermanentLoss;
        uint256 startTime;
        bool isActive;
    }
    
    mapping(string => Protocol) public protocols;
    mapping(uint256 => StakingPosition) public stakingPositions;
    mapping(uint256 => YieldFarmingPosition) public yieldFarmingPositions;
    
    uint256 public nextPositionId = 1;
    uint256 public nextFarmingId = 1;
    
    event ProtocolAdded(string indexed protocolName, address contractAddress, uint256 apy);
    event ProtocolUpdated(string indexed protocolName, uint256 apy, uint256 tvl, uint256 riskLevel);
    event StakingPositionCreated(uint256 indexed positionId, address indexed user, string protocolName, uint256 amount);
    event YieldFarmingPositionCreated(uint256 indexed farmingId, address indexed user, string protocolName, uint256 lpTokens);
    event RewardsClaimed(uint256 indexed positionId, address indexed user, uint256 amount);
    event Compounded(uint256 indexed positionId, address indexed user, uint256 amount);
    
    function addProtocol(
        string memory name,
        address contractAddress,
        uint256 apy,
        uint256 riskLevel
    ) external onlyOwner {
        protocols[name] = Protocol({
            name: name,
            contractAddress: contractAddress,
            apy: apy,
            tvl: 0,
            riskLevel: riskLevel,
            isActive: true,
            lastUpdated: block.timestamp
        });
        
        emit ProtocolAdded(name, contractAddress, apy);
    }
    
    function updateProtocol(
        string memory name,
        uint256 apy,
        uint256 tvl,
        uint256 riskLevel
    ) external onlyOwner {
        Protocol storage protocol = protocols[name];
        require(bytes(protocol.name).length > 0, "Protocol does not exist");
        
        protocol.apy = apy;
        protocol.tvl = tvl;
        protocol.riskLevel = riskLevel;
        protocol.lastUpdated = block.timestamp;
        
        emit ProtocolUpdated(name, apy, tvl, riskLevel);
    }
    
    function createStakingPosition(
        string memory protocolName,
        address assetAddress,
        uint256 amount,
        bool autoCompound
    ) external nonReentrant returns (uint256) {
        Protocol memory protocol = protocols[protocolName];
        require(protocol.isActive, "Protocol is not active");
        require(amount > 0, "Amount must be greater than 0");
        
        // Transfer tokens from user
        IERC20(assetAddress).transferFrom(msg.sender, address(this), amount);
        
        uint256 positionId = nextPositionId;
        stakingPositions[positionId] = StakingPosition({
            user: msg.sender,
            protocolName: protocolName,
            assetAddress: assetAddress,
            stakedAmount: amount,
            rewardAmount: 0,
            apyAtStake: protocol.apy,
            startTime: block.timestamp,
            lastCompound: block.timestamp,
            isActive: true,
            autoCompound: autoCompound
        });
        
        nextPositionId++;
        
        emit StakingPositionCreated(positionId, msg.sender, protocolName, amount);
        return positionId;
    }
    
    function createYieldFarmingPosition(
        string memory protocolName,
        string memory poolName,
        uint256 lpTokens,
        uint256 apy
    ) external nonReentrant returns (uint256) {
        Protocol memory protocol = protocols[protocolName];
        require(protocol.isActive, "Protocol is not active");
        require(lpTokens > 0, "LP tokens must be greater than 0");
        
        // Transfer LP tokens from user (assuming they have already provided liquidity)
        // In a real implementation, this would involve actual LP token transfers
        
        uint256 farmingId = nextFarmingId;
        yieldFarmingPositions[farmingId] = YieldFarmingPosition({
            user: msg.sender,
            protocolName: protocolName,
            poolName: poolName,
            lpTokens: lpTokens,
            rewardTokens: 0,
            apy: apy,
            impermanentLoss: 0,
            startTime: block.timestamp,
            isActive: true
        });
        
        nextFarmingId++;
        
        emit YieldFarmingPositionCreated(farmingId, msg.sender, protocolName, lpTokens);
        return farmingId;
    }
    
    function calculateRewards(uint256 positionId) public view returns (uint256) {
        StakingPosition memory position = stakingPositions[positionId];
        require(position.user != address(0), "Position does not exist");
        require(position.isActive, "Position is not active");
        
        uint256 timeElapsed = block.timestamp - position.startTime;
        uint256 dailyRate = position.apyAtStake / 365;
        uint256 rewards = (position.stakedAmount * dailyRate * timeElapsed) / 100;
        
        return rewards;
    }
    
    function compoundRewards(uint256 positionId) external nonReentrant {
        StakingPosition storage position = stakingPositions[positionId];
        require(position.user == msg.sender, "Not your position");
        require(position.isActive, "Position is not active");
        require(position.autoCompound, "Auto-compounding not enabled");
        
        uint256 rewards = calculateRewards(positionId);
        require(rewards > position.stakedAmount / 100, "Rewards too small to compound");
        
        position.stakedAmount += rewards;
        position.rewardAmount = 0;
        position.lastCompound = block.timestamp;
        
        emit Compounded(positionId, msg.sender, rewards);
    }
    
    function claimRewards(uint256 positionId) external nonReentrant {
        StakingPosition storage position = stakingPositions[positionId];
        require(position.user == msg.sender, "Not your position");
        require(position.isActive, "Position is not active");
        
        uint256 rewards = calculateRewards(positionId);
        require(rewards > 0, "No rewards to claim");
        
        position.rewardAmount = 0;
        position.startTime = block.timestamp;
        
        // Transfer rewards to user
        // In a real implementation, this would involve actual token transfers
        
        emit RewardsClaimed(positionId, msg.sender, rewards);
    }
    
    function getProtocol(string memory name) external view returns (Protocol memory) {
        return protocols[name];
    }
    
    function getStakingPosition(uint256 positionId) external view returns (StakingPosition memory) {
        return stakingPositions[positionId];
    }
    
    function getYieldFarmingPosition(uint256 farmingId) external view returns (YieldFarmingPosition memory) {
        return yieldFarmingPositions[farmingId];
    }
}