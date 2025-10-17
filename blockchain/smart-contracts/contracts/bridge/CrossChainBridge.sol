// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/**
 * @title CrossChainBridge
 * @dev Cross-chain bridge for TigerEx supporting multiple blockchain networks
 */
contract CrossChainBridge is ReentrancyGuard, AccessControl, Pausable {
    using SafeERC20 for IERC20;
    using ECDSA for bytes32;

    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    struct BridgeTransaction {
        bytes32 txId;
        address user;
        address token;
        uint256 amount;
        uint256 fromChainId;
        uint256 toChainId;
        address toAddress;
        uint256 timestamp;
        BridgeStatus status;
        uint256 fee;
        bytes32 merkleRoot;
    }

    struct ChainConfig {
        bool supported;
        uint256 minAmount;
        uint256 maxAmount;
        uint256 baseFee;
        uint256 feeRate; // in basis points
        address bridgeContract;
    }

    struct ValidatorInfo {
        address validator;
        bool active;
        uint256 stake;
        uint256 lastActivity;
    }

    enum BridgeStatus {
        Pending,
        Validated,
        Completed,
        Failed,
        Refunded
    }

    // State variables
    mapping(uint256 => ChainConfig) public chainConfigs;
    mapping(bytes32 => BridgeTransaction) public bridgeTransactions;
    mapping(address => bool) public supportedTokens;
    mapping(bytes32 => mapping(address => bool)) public validatorSignatures;
    mapping(bytes32 => uint256) public validationCount;
    mapping(address => ValidatorInfo) public validators;
    
    uint256[] public supportedChains;
    uint256 public currentChainId;
    uint256 public requiredValidations = 3;
    uint256 public constant BASIS_POINTS = 10000;
    uint256 public totalValidators;
    
    address public treasury;
    
    // Events
    event BridgeInitiated(
        bytes32 indexed txId,
        address indexed user,
        address indexed token,
        uint256 amount,
        uint256 fromChainId,
        uint256 toChainId,
        address toAddress
    );
    
    event BridgeValidated(
        bytes32 indexed txId,
        address indexed validator,
        uint256 validationCount
    );
    
    event BridgeCompleted(
        bytes32 indexed txId,
        address indexed user,
        uint256 amount
    );
    
    event BridgeFailed(
        bytes32 indexed txId,
        string reason
    );
    
    event ValidatorAdded(address indexed validator, uint256 stake);
    event ValidatorRemoved(address indexed validator);
    event ChainConfigUpdated(uint256 indexed chainId, bool supported);

    constructor(
        uint256 _chainId,
        address _treasury,
        address[] memory _initialValidators
    ) {
        currentChainId = _chainId;
        treasury = _treasury;
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
        
        // Add initial validators
        for (uint256 i = 0; i < _initialValidators.length; i++) {
            _addValidator(_initialValidators[i], 0);
        }
    }

    /**
     * @dev Initiate a cross-chain bridge transaction
     */
    function initiateBridge(
        address token,
        uint256 amount,
        uint256 toChainId,
        address toAddress
    ) external payable nonReentrant whenNotPaused returns (bytes32 txId) {
        require(supportedTokens[token], "CrossChainBridge: TOKEN_NOT_SUPPORTED");
        require(chainConfigs[toChainId].supported, "CrossChainBridge: CHAIN_NOT_SUPPORTED");
        require(toAddress != address(0), "CrossChainBridge: INVALID_TO_ADDRESS");
        
        ChainConfig memory config = chainConfigs[toChainId];
        require(amount >= config.minAmount && amount <= config.maxAmount, "CrossChainBridge: INVALID_AMOUNT");
        
        // Calculate fees
        uint256 fee = config.baseFee + (amount * config.feeRate / BASIS_POINTS);
        require(msg.value >= fee, "CrossChainBridge: INSUFFICIENT_FEE");
        
        // Generate transaction ID
        txId = keccak256(abi.encodePacked(
            msg.sender,
            token,
            amount,
            currentChainId,
            toChainId,
            toAddress,
            block.timestamp,
            block.number
        ));
        
        require(bridgeTransactions[txId].txId == bytes32(0), "CrossChainBridge: TX_EXISTS");
        
        // Lock tokens
        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);
        
        // Store transaction
        bridgeTransactions[txId] = BridgeTransaction({
            txId: txId,
            user: msg.sender,
            token: token,
            amount: amount,
            fromChainId: currentChainId,
            toChainId: toChainId,
            toAddress: toAddress,
            timestamp: block.timestamp,
            status: BridgeStatus.Pending,
            fee: fee,
            merkleRoot: bytes32(0)
        });
        
        // Send fee to treasury
        payable(treasury).transfer(fee);
        
        // Refund excess ETH
        if (msg.value > fee) {
            payable(msg.sender).transfer(msg.value - fee);
        }
        
        emit BridgeInitiated(txId, msg.sender, token, amount, currentChainId, toChainId, toAddress);
    }

    /**
     * @dev Validate a bridge transaction (called by validators)
     */
    function validateBridge(
        bytes32 txId,
        bytes32 merkleRoot,
        bytes calldata signature
    ) external onlyRole(VALIDATOR_ROLE) {
        require(bridgeTransactions[txId].txId != bytes32(0), "CrossChainBridge: TX_NOT_FOUND");
        require(bridgeTransactions[txId].status == BridgeStatus.Pending, "CrossChainBridge: INVALID_STATUS");
        require(!validatorSignatures[txId][msg.sender], "CrossChainBridge: ALREADY_VALIDATED");
        
        // Verify signature
        bytes32 messageHash = keccak256(abi.encodePacked(txId, merkleRoot));
        bytes32 ethSignedMessageHash = messageHash.toEthSignedMessageHash();
        address signer = ethSignedMessageHash.recover(signature);
        require(signer == msg.sender, "CrossChainBridge: INVALID_SIGNATURE");
        
        // Record validation
        validatorSignatures[txId][msg.sender] = true;
        validationCount[txId]++;
        
        // Update validator activity
        validators[msg.sender].lastActivity = block.timestamp;
        
        emit BridgeValidated(txId, msg.sender, validationCount[txId]);
        
        // Check if enough validations
        if (validationCount[txId] >= requiredValidations) {
            bridgeTransactions[txId].status = BridgeStatus.Validated;
            bridgeTransactions[txId].merkleRoot = merkleRoot;
        }
    }

    /**
     * @dev Complete bridge transaction (release tokens on destination chain)
     */
    function completeBridge(
        bytes32 txId,
        bytes32[] calldata merkleProof
    ) external nonReentrant whenNotPaused {
        BridgeTransaction storage bridgeTx = bridgeTransactions[txId];
        require(bridgeTx.txId != bytes32(0), "CrossChainBridge: TX_NOT_FOUND");
        require(bridgeTx.status == BridgeStatus.Validated, "CrossChainBridge: NOT_VALIDATED");
        require(bridgeTx.toChainId == currentChainId, "CrossChainBridge: WRONG_CHAIN");
        
        // Verify merkle proof (simplified - in production use proper merkle tree verification)
        bytes32 leaf = keccak256(abi.encodePacked(txId, bridgeTx.user, bridgeTx.amount));
        require(_verifyMerkleProof(merkleProof, bridgeTx.merkleRoot, leaf), "CrossChainBridge: INVALID_PROOF");
        
        // Update status
        bridgeTx.status = BridgeStatus.Completed;
        
        // Release tokens
        IERC20(bridgeTx.token).safeTransfer(bridgeTx.toAddress, bridgeTx.amount);
        
        emit BridgeCompleted(txId, bridgeTx.user, bridgeTx.amount);
    }

    /**
     * @dev Refund failed bridge transaction
     */
    function refundBridge(bytes32 txId) external onlyRole(OPERATOR_ROLE) {
        BridgeTransaction storage bridgeTx = bridgeTransactions[txId];
        require(bridgeTx.txId != bytes32(0), "CrossChainBridge: TX_NOT_FOUND");
        require(
            bridgeTx.status == BridgeStatus.Pending || bridgeTx.status == BridgeStatus.Failed,
            "CrossChainBridge: CANNOT_REFUND"
        );
        require(bridgeTx.fromChainId == currentChainId, "CrossChainBridge: WRONG_CHAIN");
        
        // Update status
        bridgeTx.status = BridgeStatus.Refunded;
        
        // Refund tokens
        IERC20(bridgeTx.token).safeTransfer(bridgeTx.user, bridgeTx.amount);
        
        emit BridgeCompleted(txId, bridgeTx.user, bridgeTx.amount);
    }

    /**
     * @dev Add a new validator
     */
    function addValidator(address validator, uint256 stake) external onlyRole(DEFAULT_ADMIN_ROLE) {
        _addValidator(validator, stake);
    }

    function _addValidator(address validator, uint256 stake) internal {
        require(validator != address(0), "CrossChainBridge: ZERO_ADDRESS");
        require(!validators[validator].active, "CrossChainBridge: VALIDATOR_EXISTS");
        
        validators[validator] = ValidatorInfo({
            validator: validator,
            active: true,
            stake: stake,
            lastActivity: block.timestamp
        });
        
        totalValidators++;
        _grantRole(VALIDATOR_ROLE, validator);
        
        emit ValidatorAdded(validator, stake);
    }

    /**
     * @dev Remove a validator
     */
    function removeValidator(address validator) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(validators[validator].active, "CrossChainBridge: VALIDATOR_NOT_FOUND");
        
        validators[validator].active = false;
        totalValidators--;
        _revokeRole(VALIDATOR_ROLE, validator);
        
        emit ValidatorRemoved(validator);
    }

    /**
     * @dev Configure supported chain
     */
    function configureChain(
        uint256 chainId,
        bool supported,
        uint256 minAmount,
        uint256 maxAmount,
        uint256 baseFee,
        uint256 feeRate,
        address bridgeContract
    ) external onlyRole(DEFAULT_ADMIN_ROLE) {
        chainConfigs[chainId] = ChainConfig({
            supported: supported,
            minAmount: minAmount,
            maxAmount: maxAmount,
            baseFee: baseFee,
            feeRate: feeRate,
            bridgeContract: bridgeContract
        });
        
        if (supported) {
            supportedChains.push(chainId);
        }
        
        emit ChainConfigUpdated(chainId, supported);
    }

    /**
     * @dev Add supported token
     */
    function addSupportedToken(address token) external onlyRole(DEFAULT_ADMIN_ROLE) {
        supportedTokens[token] = true;
    }

    /**
     * @dev Remove supported token
     */
    function removeSupportedToken(address token) external onlyRole(DEFAULT_ADMIN_ROLE) {
        supportedTokens[token] = false;
    }

    /**
     * @dev Set required validations
     */
    function setRequiredValidations(uint256 _requiredValidations) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_requiredValidations > 0 && _requiredValidations <= totalValidators, "CrossChainBridge: INVALID_COUNT");
        requiredValidations = _requiredValidations;
    }

    /**
     * @dev Emergency pause
     */
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }

    /**
     * @dev Unpause
     */
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }

    /**
     * @dev Get bridge transaction details
     */
    function getBridgeTransaction(bytes32 txId) external view returns (BridgeTransaction memory) {
        return bridgeTransactions[txId];
    }

    /**
     * @dev Get supported chains
     */
    function getSupportedChains() external view returns (uint256[] memory) {
        return supportedChains;
    }

    /**
     * @dev Verify merkle proof (simplified implementation)
     */
    function _verifyMerkleProof(
        bytes32[] memory proof,
        bytes32 root,
        bytes32 leaf
    ) internal pure returns (bool) {
        bytes32 computedHash = leaf;
        
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];
            if (computedHash <= proofElement) {
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }
        
        return computedHash == root;
    }

    /**
     * @dev Emergency withdrawal (only admin)
     */
    function emergencyWithdraw(address token, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        IERC20(token).safeTransfer(msg.sender, amount);
    }
}