// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract RoyaltyDistributor is Ownable, ReentrancyGuard {
    using SafeMath for uint256;
    
    struct RoyaltyPayment {
        uint256 id;
        address creator;
        address buyer;
        address seller;
        uint256 salePrice;
        uint256 royaltyAmount;
        uint256 timestamp;
        bytes32 transactionHash;
        bool isDistributed;
    }
    
    struct CreatorRoyalty {
        address creator;
        uint256 totalRoyalties;
        uint256 distributedRoyalties;
        uint256 pendingRoyalties;
    }
    
    mapping(uint256 => RoyaltyPayment) public royaltyPayments;
    mapping(address => CreatorRoyalty) public creatorRoyalties;
    mapping(address => bool) public whitelistedTokens;
    
    uint256 public nextPaymentId = 1;
    uint256 public totalRoyaltyVolume;
    
    event RoyaltyRecorded(uint256 indexed paymentId, address indexed creator, uint256 salePrice, uint256 royaltyAmount);
    event RoyaltyDistributed(uint256 indexed paymentId, address indexed creator, uint256 amount);
    event TokenWhitelisted(address indexed token, bool isWhitelisted);
    event CreatorRegistered(address indexed creator);
    
    function whitelistToken(address token, bool isWhitelisted) external onlyOwner {
        whitelistedTokens[token] = isWhitelisted;
        emit TokenWhitelisted(token, isWhitelisted);
    }
    
    function recordRoyaltyPayment(
        address creator,
        address buyer,
        address seller,
        uint256 salePrice,
        uint256 royaltyPercentage
    ) external returns (uint256) {
        require(whitelistedTokens[msg.sender], "Caller not whitelisted");
        require(creator != address(0), "Invalid creator address");
        require(buyer != address(0), "Invalid buyer address");
        require(seller != address(0), "Invalid seller address");
        require(salePrice > 0, "Sale price must be greater than 0");
        require(royaltyPercentage <= 2000, "Royalty percentage too high (max 20%)");
        
        uint256 royaltyAmount = salePrice.mul(royaltyPercentage).div(10000);
        
        uint256 paymentId = nextPaymentId;
        royaltyPayments[paymentId] = RoyaltyPayment({
            id: paymentId,
            creator: creator,
            buyer: buyer,
            seller: seller,
            salePrice: salePrice,
            royaltyAmount: royaltyAmount,
            timestamp: block.timestamp,
            transactionHash: keccak256(abi.encodePacked(paymentId, block.timestamp)),
            isDistributed: false
        });
        
        // Update creator royalty tracking
        if (creatorRoyalties[creator].creator == address(0)) {
            creatorRoyalties[creator] = CreatorRoyalty({
                creator: creator,
                totalRoyalties: royaltyAmount,
                distributedRoyalties: 0,
                pendingRoyalties: royaltyAmount
            });
            emit CreatorRegistered(creator);
        } else {
            creatorRoyalties[creator].totalRoyalties = creatorRoyalties[creator].totalRoyalties.add(royaltyAmount);
            creatorRoyalties[creator].pendingRoyalties = creatorRoyalties[creator].pendingRoyalties.add(royaltyAmount);
        }
        
        nextPaymentId++;
        totalRoyaltyVolume = totalRoyaltyVolume.add(royaltyAmount);
        
        emit RoyaltyRecorded(paymentId, creator, salePrice, royaltyAmount);
        return paymentId;
    }
    
    function distributeRoyalty(uint256 paymentId) external nonReentrant {
        RoyaltyPayment storage payment = royaltyPayments[paymentId];
        require(payment.id > 0, "Payment does not exist");
        require(!payment.isDistributed, "Royalty already distributed");
        require(payment.creator == msg.sender || owner() == msg.sender, "Not authorized to distribute");
        
        // Transfer royalty amount to creator
        // In a real implementation, this would involve actual token transfers
        // For now, we'll just update the status
        
        payment.isDistributed = true;
        creatorRoyalties[payment.creator].distributedRoyalties = creatorRoyalties[payment.creator].distributedRoyalties.add(payment.royaltyAmount);
        creatorRoyalties[payment.creator].pendingRoyalties = creatorRoyalties[payment.creator].pendingRoyalties.sub(payment.royaltyAmount);
        
        emit RoyaltyDistributed(paymentId, payment.creator, payment.royaltyAmount);
    }
    
    function distributeRoyaltyToCreator(address creator) external nonReentrant {
        CreatorRoyalty storage royaltyInfo = creatorRoyalties[creator];
        require(royaltyInfo.creator != address(0), "Creator not registered");
        require(royaltyInfo.pendingRoyalties > 0, "No pending royalties");
        
        uint256 amount = royaltyInfo.pendingRoyalties;
        
        // Transfer pending royalties to creator
        // In a real implementation, this would involve actual token transfers
        
        royaltyInfo.distributedRoyalties = royaltyInfo.distributedRoyalties.add(amount);
        royaltyInfo.pendingRoyalties = 0;
        
        emit RoyaltyDistributed(0, creator, amount);
    }
    
    function getRoyaltyPayment(uint256 paymentId) external view returns (RoyaltyPayment memory) {
        return royaltyPayments[paymentId];
    }
    
    function getCreatorRoyalty(address creator) external view returns (CreatorRoyalty memory) {
        return creatorRoyalties[creator];
    }
    
    function getPendingRoyalties(address creator) external view returns (uint256) {
        return creatorRoyalties[creator].pendingRoyalties;
    }
    
    function getTotalRoyaltyVolume() external view returns (uint256) {
        return totalRoyaltyVolume;
    }
}