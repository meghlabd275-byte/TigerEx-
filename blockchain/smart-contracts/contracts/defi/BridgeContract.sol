// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract BridgeContract is Ownable, ReentrancyGuard {
    using SafeMath for uint256;
    
    struct BridgePair {
        address tokenA;
        address tokenB;
        uint256 feePercentage; // in basis points (100 = 1%)
        bool isActive;
        uint256 totalBridged;
    }
    
    struct BridgeTransaction {
        uint256 id;
        address fromToken;
        address toToken;
        address fromChain;
        address toChain;
        address sender;
        address receiver;
        uint256 amount;
        uint256 fee;
        uint256 timestamp;
        string status; // pending, completed, failed
        bytes32 transactionHash;
    }
    
    mapping(bytes32 => BridgePair) public bridgePairs;
    mapping(uint256 => BridgeTransaction) public transactions;
    mapping(string => address) public chainAddresses;
    
    uint256 public nextTransactionId = 1;
    uint256 public totalVolume;
    uint256 public totalFees;
    
    event BridgePairAdded(bytes32 indexed pairId, address tokenA, address tokenB, uint256 feePercentage);
    event BridgePairUpdated(bytes32 indexed pairId, uint256 feePercentage, bool isActive);
    event BridgeInitiated(uint256 indexed transactionId, address fromToken, address toToken, uint256 amount);
    event BridgeCompleted(uint256 indexed transactionId, bytes32 transactionHash);
    event BridgeFailed(uint256 indexed transactionId, string reason);
    event ChainAddressAdded(string chainName, address chainAddress);
    
    function addBridgePair(
        address tokenA,
        address tokenB,
        uint256 feePercentage
    ) external onlyOwner returns (bytes32) {
        bytes32 pairId = keccak256(abi.encodePacked(tokenA, tokenB));
        
        bridgePairs[pairId] = BridgePair({
            tokenA: tokenA,
            tokenB: tokenB,
            feePercentage: feePercentage,
            isActive: true,
            totalBridged: 0
        });
        
        emit BridgePairAdded(pairId, tokenA, tokenB, feePercentage);
        return pairId;
    }
    
    function updateBridgePair(
        bytes32 pairId,
        uint256 feePercentage,
        bool isActive
    ) external onlyOwner {
        BridgePair storage pair = bridgePairs[pairId];
        require(pair.tokenA != address(0), "Bridge pair does not exist");
        
        pair.feePercentage = feePercentage;
        pair.isActive = isActive;
        
        emit BridgePairUpdated(pairId, feePercentage, isActive);
    }
    
    function addChainAddress(string memory chainName, address chainAddress) external onlyOwner {
        chainAddresses[chainName] = chainAddress;
        emit ChainAddressAdded(chainName, chainAddress);
    }
    
    function bridgeTokens(
        bytes32 pairId,
        uint256 amount,
        address receiver
    ) external nonReentrant returns (uint256) {
        BridgePair memory pair = bridgePairs[pairId];
        require(pair.isActive, "Bridge pair is not active");
        require(amount > 0, "Amount must be greater than 0");
        require(receiver != address(0), "Invalid receiver address");
        
        // Transfer tokens from sender
        IERC20(pair.tokenA).transferFrom(msg.sender, address(this), amount);
        
        // Calculate fee
        uint256 fee = amount.mul(pair.feePercentage).div(10000);
        uint256 netAmount = amount.sub(fee);
        
        uint256 transactionId = nextTransactionId;
        transactions[transactionId] = BridgeTransaction({
            id: transactionId,
            fromToken: pair.tokenA,
            toToken: pair.tokenB,
            fromChain: address(this),
            toChain: address(0), // Will be set when completed
            sender: msg.sender,
            receiver: receiver,
            amount: amount,
            fee: fee,
            timestamp: block.timestamp,
            status: "pending",
            transactionHash: bytes32(0)
        });
        
        nextTransactionId++;
        totalVolume += amount;
        totalFees += fee;
        bridgePairs[pairId].totalBridged += amount;
        
        emit BridgeInitiated(transactionId, pair.tokenA, pair.tokenB, amount);
        return transactionId;
    }
    
    function completeBridge(
        uint256 transactionId,
        bytes32 transactionHash
    ) external onlyOwner {
        BridgeTransaction storage tx = transactions[transactionId];
        require(tx.id > 0, "Transaction does not exist");
        require(keccak256(bytes(tx.status)) == keccak256(bytes("pending")), "Transaction not pending");
        
        // Transfer bridged tokens to receiver
        BridgePair memory pair = getBridgePairByTokens(tx.fromToken, tx.toToken);
        uint256 netAmount = tx.amount.sub(tx.fee);
        
        // In a real implementation, we would mint or transfer the destination token
        // For now, we'll just update the status
        tx.status = "completed";
        tx.transactionHash = transactionHash;
        tx.toChain = msg.sender;
        
        emit BridgeCompleted(transactionId, transactionHash);
    }
    
    function failBridge(
        uint256 transactionId,
        string memory reason
    ) external onlyOwner {
        BridgeTransaction storage tx = transactions[transactionId];
        require(tx.id > 0, "Transaction does not exist");
        require(keccak256(bytes(tx.status)) == keccak256(bytes("pending")), "Transaction not pending");
        
        tx.status = "failed";
        
        // Return tokens to sender
        IERC20(tx.fromToken).transfer(tx.sender, tx.amount);
        
        emit BridgeFailed(transactionId, reason);
    }
    
    function getBridgePairByTokens(address tokenA, address tokenB) public view returns (BridgePair memory) {
        bytes32 pairId = keccak256(abi.encodePacked(tokenA, tokenB));
        return bridgePairs[pairId];
    }
    
    function getBridgePair(bytes32 pairId) external view returns (BridgePair memory) {
        return bridgePairs[pairId];
    }
    
    function getTransaction(uint256 transactionId) external view returns (BridgeTransaction memory) {
        return transactions[transactionId];
    }
    
    function getChainAddress(string memory chainName) external view returns (address) {
        return chainAddresses[chainName];
    }
    
    function getBridgeFee(bytes32 pairId, uint256 amount) external view returns (uint256) {
        BridgePair memory pair = bridgePairs[pairId];
        return amount.mul(pair.feePercentage).div(10000);
    }
    
    function getTotalVolume() external view returns (uint256) {
        return totalVolume;
    }
    
    function getTotalFees() external view returns (uint256) {
        return totalFees;
    }
}