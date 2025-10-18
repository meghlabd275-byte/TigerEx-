// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

/**
 * @title AdminController
 * @dev Complete admin control system for TigerEx trading operations
 * Manages all trading contracts, user permissions, and emergency controls
 */
contract AdminController is AccessControl, ReentrancyGuard, Pausable {
    using EnumerableSet for EnumerableSet.AddressSet;
    using EnumerableSet for EnumerableSet.Bytes32Set;

    // Roles
    bytes32 public constant SUPER_ADMIN_ROLE = keccak256("SUPER_ADMIN_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant MODERATOR_ROLE = keccak256("MODERATOR_ROLE");
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

    // Trading Types
    enum TradingType {
        SPOT,
        FUTURES_PERPETUAL,
        FUTURES_CROSS,
        FUTURES_DELIVERY,
        MARGIN,
        MARGIN_CROSS,
        MARGIN_ISOLATED,
        OPTIONS,
        DERIVATIVES,
        COPY_TRADING,
        ETF,
        LEVERAGED_TOKENS,
        STRUCTURED_PRODUCTS
    }

    // Contract Status
    enum ContractStatus {
        PENDING,
        ACTIVE,
        PAUSED,
        SUSPENDED,
        DELISTED
    }

    // User Status
    enum UserStatus {
        ACTIVE,
        SUSPENDED,
        BANNED,
        PENDING_VERIFICATION
    }

    // Exchange IDs
    enum Exchange {
        BINANCE,
        KUCOIN,
        BYBIT,
        OKX,
        MEXC,
        BITGET,
        BITFINEX
    }

    // Structs
    struct TradingContract {
        bytes32 contractId;
        Exchange exchange;
        TradingType tradingType;
        string symbol;
        string baseAsset;
        string quoteAsset;
        ContractStatus status;
        uint256[] leverageOptions;
        uint256 minOrderSize;
        uint256 maxOrderSize;
        uint256 makerFee; // in basis points (1 = 0.01%)
        uint256 takerFee; // in basis points
        uint256 fundingRate; // for futures
        uint256 fundingInterval; // in seconds
        uint256 settlementDate; // for delivery futures
        uint256 strikePrice; // for options
        uint256 expiryDate; // for options
        uint256 createdAt;
        uint256 updatedAt;
        address createdBy;
        string metadata;
    }

    struct UserProfile {
        address userAddress;
        UserStatus status;
        bytes32 role;
        uint256 kycLevel;
        bool tradingEnabled;
        bool withdrawalEnabled;
        bool depositEnabled;
        uint256 maxDailyWithdrawal;
        uint256 maxSingleWithdrawal;
        mapping(TradingType => bool) tradingPermissions;
        mapping(Exchange => bool) exchangePermissions;
        uint256 createdAt;
        uint256 updatedAt;
        string metadata;
    }

    struct AuditLog {
        uint256 logId;
        uint256 timestamp;
        address admin;
        string action;
        string targetType;
        bytes32 targetId;
        string details;
    }

    struct EmergencyAction {
        uint256 actionId;
        uint256 timestamp;
        address executor;
        string actionType;
        string reason;
        bool isActive;
    }

    // State Variables
    mapping(bytes32 => TradingContract) public tradingContracts;
    mapping(address => UserProfile) public userProfiles;
    mapping(uint256 => AuditLog) public auditLogs;
    mapping(uint256 => EmergencyAction) public emergencyActions;

    EnumerableSet.Bytes32Set private contractIds;
    EnumerableSet.AddressSet private userAddresses;

    uint256 public contractCounter;
    uint256 public auditLogCounter;
    uint256 public emergencyActionCounter;

    bool public tradingHalted;
    bool public withdrawalsHalted;
    bool public depositsHalted;

    // Events
    event ContractCreated(bytes32 indexed contractId, address indexed creator, string symbol);
    event ContractLaunched(bytes32 indexed contractId, address indexed launcher);
    event ContractPaused(bytes32 indexed contractId, address indexed pauser, string reason);
    event ContractResumed(bytes32 indexed contractId, address indexed resumer);
    event ContractDeleted(bytes32 indexed contractId, address indexed deleter, string reason);
    event ContractUpdated(bytes32 indexed contractId, address indexed updater);

    event UserCreated(address indexed userAddress, address indexed creator, bytes32 role);
    event UserUpdated(address indexed userAddress, address indexed updater);
    event UserSuspended(address indexed userAddress, address indexed suspender, string reason);
    event UserActivated(address indexed userAddress, address indexed activator);
    event UserBanned(address indexed userAddress, address indexed banner, string reason);

    event TradingPermissionUpdated(address indexed userAddress, TradingType tradingType, bool enabled);
    event ExchangePermissionUpdated(address indexed userAddress, Exchange exchange, bool enabled);

    event EmergencyTradingHalt(address indexed executor, string reason);
    event EmergencyTradingResume(address indexed executor);
    event EmergencyWithdrawalHalt(address indexed executor, string reason);
    event EmergencyWithdrawalResume(address indexed executor);

    event AuditLogCreated(uint256 indexed logId, address indexed admin, string action);

    // Modifiers
    modifier onlySuperAdmin() {
        require(hasRole(SUPER_ADMIN_ROLE, msg.sender), "AdminController: Super admin required");
        _;
    }

    modifier onlyAdmin() {
        require(
            hasRole(SUPER_ADMIN_ROLE, msg.sender) || hasRole(ADMIN_ROLE, msg.sender),
            "AdminController: Admin required"
        );
        _;
    }

    modifier onlyModerator() {
        require(
            hasRole(SUPER_ADMIN_ROLE, msg.sender) || 
            hasRole(ADMIN_ROLE, msg.sender) || 
            hasRole(MODERATOR_ROLE, msg.sender),
            "AdminController: Moderator required"
        );
        _;
    }

    modifier contractExists(bytes32 contractId) {
        require(contractIds.contains(contractId), "AdminController: Contract does not exist");
        _;
    }

    modifier userExists(address userAddress) {
        require(userAddresses.contains(userAddress), "AdminController: User does not exist");
        _;
    }

    // Constructor
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(SUPER_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(MODERATOR_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);

        contractCounter = 1;
        auditLogCounter = 1;
        emergencyActionCounter = 1;
    }

    // ==================== CONTRACT MANAGEMENT ====================

    /**
     * @dev Create a new trading contract
     */
    function createContract(
        Exchange exchange,
        TradingType tradingType,
        string memory symbol,
        string memory baseAsset,
        string memory quoteAsset,
        uint256[] memory leverageOptions,
        uint256 minOrderSize,
        uint256 maxOrderSize,
        uint256 makerFee,
        uint256 takerFee,
        string memory metadata
    ) external onlyAdmin returns (bytes32) {
        bytes32 contractId = keccak256(
            abi.encodePacked(
                exchange,
                tradingType,
                symbol,
                block.timestamp,
                contractCounter++
            )
        );

        require(!contractIds.contains(contractId), "AdminController: Contract already exists");

        TradingContract storage newContract = tradingContracts[contractId];
        newContract.contractId = contractId;
        newContract.exchange = exchange;
        newContract.tradingType = tradingType;
        newContract.symbol = symbol;
        newContract.baseAsset = baseAsset;
        newContract.quoteAsset = quoteAsset;
        newContract.status = ContractStatus.PENDING;
        newContract.leverageOptions = leverageOptions;
        newContract.minOrderSize = minOrderSize;
        newContract.maxOrderSize = maxOrderSize;
        newContract.makerFee = makerFee;
        newContract.takerFee = takerFee;
        newContract.createdAt = block.timestamp;
        newContract.updatedAt = block.timestamp;
        newContract.createdBy = msg.sender;
        newContract.metadata = metadata;

        contractIds.add(contractId);

        _createAuditLog("CREATE_CONTRACT", "contract", contractId, 
            string(abi.encodePacked("Created contract: ", symbol)));

        emit ContractCreated(contractId, msg.sender, symbol);

        return contractId;
    }

    /**
     * @dev Launch a pending contract
     */
    function launchContract(bytes32 contractId) 
        external 
        onlyAdmin 
        contractExists(contractId) 
    {
        TradingContract storage contractData = tradingContracts[contractId];
        require(contractData.status == ContractStatus.PENDING, "AdminController: Contract not pending");

        contractData.status = ContractStatus.ACTIVE;
        contractData.updatedAt = block.timestamp;

        _createAuditLog("LAUNCH_CONTRACT", "contract", contractId, 
            string(abi.encodePacked("Launched contract: ", contractData.symbol)));

        emit ContractLaunched(contractId, msg.sender);
    }

    /**
     * @dev Pause an active contract
     */
    function pauseContract(bytes32 contractId, string memory reason) 
        external 
        onlyModerator 
        contractExists(contractId) 
    {
        TradingContract storage contractData = tradingContracts[contractId];
        require(contractData.status == ContractStatus.ACTIVE, "AdminController: Contract not active");

        contractData.status = ContractStatus.PAUSED;
        contractData.updatedAt = block.timestamp;

        _createAuditLog("PAUSE_CONTRACT", "contract", contractId, 
            string(abi.encodePacked("Paused contract: ", contractData.symbol, " - Reason: ", reason)));

        emit ContractPaused(contractId, msg.sender, reason);
    }

    /**
     * @dev Resume a paused contract
     */
    function resumeContract(bytes32 contractId) 
        external 
        onlyModerator 
        contractExists(contractId) 
    {
        TradingContract storage contractData = tradingContracts[contractId];
        require(contractData.status == ContractStatus.PAUSED, "AdminController: Contract not paused");

        contractData.status = ContractStatus.ACTIVE;
        contractData.updatedAt = block.timestamp;

        _createAuditLog("RESUME_CONTRACT", "contract", contractId, 
            string(abi.encodePacked("Resumed contract: ", contractData.symbol)));

        emit ContractResumed(contractId, msg.sender);
    }

    /**
     * @dev Delete a contract (soft delete)
     */
    function deleteContract(bytes32 contractId, string memory reason) 
        external 
        onlyAdmin 
        contractExists(contractId) 
    {
        TradingContract storage contractData = tradingContracts[contractId];
        contractData.status = ContractStatus.DELISTED;
        contractData.updatedAt = block.timestamp;

        _createAuditLog("DELETE_CONTRACT", "contract", contractId, 
            string(abi.encodePacked("Deleted contract: ", contractData.symbol, " - Reason: ", reason)));

        emit ContractDeleted(contractId, msg.sender, reason);
    }

    /**
     * @dev Update contract parameters
     */
    function updateContract(
        bytes32 contractId,
        uint256[] memory leverageOptions,
        uint256 minOrderSize,
        uint256 maxOrderSize,
        uint256 makerFee,
        uint256 takerFee,
        string memory metadata
    ) external onlyAdmin contractExists(contractId) {
        TradingContract storage contractData = tradingContracts[contractId];
        
        if (leverageOptions.length > 0) {
            contractData.leverageOptions = leverageOptions;
        }
        if (minOrderSize > 0) {
            contractData.minOrderSize = minOrderSize;
        }
        if (maxOrderSize > 0) {
            contractData.maxOrderSize = maxOrderSize;
        }
        if (makerFee > 0) {
            contractData.makerFee = makerFee;
        }
        if (takerFee > 0) {
            contractData.takerFee = takerFee;
        }
        if (bytes(metadata).length > 0) {
            contractData.metadata = metadata;
        }

        contractData.updatedAt = block.timestamp;

        _createAuditLog("UPDATE_CONTRACT", "contract", contractId, 
            string(abi.encodePacked("Updated contract: ", contractData.symbol)));

        emit ContractUpdated(contractId, msg.sender);
    }

    // ==================== USER MANAGEMENT ====================

    /**
     * @dev Create a new user profile
     */
    function createUser(
        address userAddress,
        bytes32 role,
        uint256 kycLevel
    ) external onlyAdmin {
        require(!userAddresses.contains(userAddress), "AdminController: User already exists");
        require(userAddress != address(0), "AdminController: Invalid user address");

        UserProfile storage newUser = userProfiles[userAddress];
        newUser.userAddress = userAddress;
        newUser.status = UserStatus.ACTIVE;
        newUser.role = role;
        newUser.kycLevel = kycLevel;
        newUser.tradingEnabled = true;
        newUser.withdrawalEnabled = true;
        newUser.depositEnabled = true;
        newUser.maxDailyWithdrawal = 100000 * 10**18; // 100k tokens
        newUser.maxSingleWithdrawal = 10000 * 10**18; // 10k tokens
        newUser.createdAt = block.timestamp;
        newUser.updatedAt = block.timestamp;

        userAddresses.add(userAddress);

        _createAuditLog("CREATE_USER", "user", bytes32(uint256(uint160(userAddress))), 
            "Created user profile");

        emit UserCreated(userAddress, msg.sender, role);
    }

    /**
     * @dev Update user profile
     */
    function updateUser(
        address userAddress,
        UserStatus status,
        bytes32 role,
        uint256 kycLevel,
        bool tradingEnabled,
        bool withdrawalEnabled,
        bool depositEnabled,
        uint256 maxDailyWithdrawal,
        uint256 maxSingleWithdrawal
    ) external onlyAdmin userExists(userAddress) {
        UserProfile storage user = userProfiles[userAddress];
        
        user.status = status;
        user.role = role;
        user.kycLevel = kycLevel;
        user.tradingEnabled = tradingEnabled;
        user.withdrawalEnabled = withdrawalEnabled;
        user.depositEnabled = depositEnabled;
        user.maxDailyWithdrawal = maxDailyWithdrawal;
        user.maxSingleWithdrawal = maxSingleWithdrawal;
        user.updatedAt = block.timestamp;

        _createAuditLog("UPDATE_USER", "user", bytes32(uint256(uint160(userAddress))), 
            "Updated user profile");

        emit UserUpdated(userAddress, msg.sender);
    }

    /**
     * @dev Suspend a user
     */
    function suspendUser(address userAddress, string memory reason) 
        external 
        onlyModerator 
        userExists(userAddress) 
    {
        UserProfile storage user = userProfiles[userAddress];
        require(user.status == UserStatus.ACTIVE, "AdminController: User not active");

        user.status = UserStatus.SUSPENDED;
        user.tradingEnabled = false;
        user.updatedAt = block.timestamp;

        _createAuditLog("SUSPEND_USER", "user", bytes32(uint256(uint160(userAddress))), 
            string(abi.encodePacked("Suspended user - Reason: ", reason)));

        emit UserSuspended(userAddress, msg.sender, reason);
    }

    /**
     * @dev Activate a suspended user
     */
    function activateUser(address userAddress) 
        external 
        onlyModerator 
        userExists(userAddress) 
    {
        UserProfile storage user = userProfiles[userAddress];
        require(user.status == UserStatus.SUSPENDED, "AdminController: User not suspended");

        user.status = UserStatus.ACTIVE;
        user.tradingEnabled = true;
        user.updatedAt = block.timestamp;

        _createAuditLog("ACTIVATE_USER", "user", bytes32(uint256(uint160(userAddress))), 
            "Activated user");

        emit UserActivated(userAddress, msg.sender);
    }

    /**
     * @dev Ban a user permanently
     */
    function banUser(address userAddress, string memory reason) 
        external 
        onlyAdmin 
        userExists(userAddress) 
    {
        UserProfile storage user = userProfiles[userAddress];
        
        user.status = UserStatus.BANNED;
        user.tradingEnabled = false;
        user.withdrawalEnabled = false;
        user.depositEnabled = false;
        user.updatedAt = block.timestamp;

        _createAuditLog("BAN_USER", "user", bytes32(uint256(uint160(userAddress))), 
            string(abi.encodePacked("Banned user - Reason: ", reason)));

        emit UserBanned(userAddress, msg.sender, reason);
    }

    /**
     * @dev Set trading permission for specific trading type
     */
    function setTradingPermission(
        address userAddress,
        TradingType tradingType,
        bool enabled
    ) external onlyAdmin userExists(userAddress) {
        UserProfile storage user = userProfiles[userAddress];
        user.tradingPermissions[tradingType] = enabled;
        user.updatedAt = block.timestamp;

        _createAuditLog("SET_TRADING_PERMISSION", "user", bytes32(uint256(uint160(userAddress))), 
            string(abi.encodePacked("Set trading permission for type: ", _tradingTypeToString(tradingType))));

        emit TradingPermissionUpdated(userAddress, tradingType, enabled);
    }

    /**
     * @dev Set exchange permission
     */
    function setExchangePermission(
        address userAddress,
        Exchange exchange,
        bool enabled
    ) external onlyAdmin userExists(userAddress) {
        UserProfile storage user = userProfiles[userAddress];
        user.exchangePermissions[exchange] = enabled;
        user.updatedAt = block.timestamp;

        _createAuditLog("SET_EXCHANGE_PERMISSION", "user", bytes32(uint256(uint160(userAddress))), 
            string(abi.encodePacked("Set exchange permission for: ", _exchangeToString(exchange))));

        emit ExchangePermissionUpdated(userAddress, exchange, enabled);
    }

    // ==================== EMERGENCY CONTROLS ====================

    /**
     * @dev Emergency halt all trading
     */
    function emergencyHaltTrading(string memory reason) external onlySuperAdmin {
        tradingHalted = true;

        uint256 actionId = emergencyActionCounter++;
        EmergencyAction storage action = emergencyActions[actionId];
        action.actionId = actionId;
        action.timestamp = block.timestamp;
        action.executor = msg.sender;
        action.actionType = "HALT_TRADING";
        action.reason = reason;
        action.isActive = true;

        _createAuditLog("EMERGENCY_HALT_TRADING", "system", bytes32(actionId), 
            string(abi.encodePacked("Emergency trading halt - Reason: ", reason)));

        emit EmergencyTradingHalt(msg.sender, reason);
    }

    /**
     * @dev Resume trading after emergency halt
     */
    function emergencyResumeTrading() external onlySuperAdmin {
        tradingHalted = false;

        uint256 actionId = emergencyActionCounter++;
        EmergencyAction storage action = emergencyActions[actionId];
        action.actionId = actionId;
        action.timestamp = block.timestamp;
        action.executor = msg.sender;
        action.actionType = "RESUME_TRADING";
        action.reason = "Emergency resolved";
        action.isActive = true;

        _createAuditLog("EMERGENCY_RESUME_TRADING", "system", bytes32(actionId), 
            "Emergency trading resumed");

        emit EmergencyTradingResume(msg.sender);
    }

    /**
     * @dev Emergency halt all withdrawals
     */
    function emergencyHaltWithdrawals(string memory reason) external onlySuperAdmin {
        withdrawalsHalted = true;

        uint256 actionId = emergencyActionCounter++;
        EmergencyAction storage action = emergencyActions[actionId];
        action.actionId = actionId;
        action.timestamp = block.timestamp;
        action.executor = msg.sender;
        action.actionType = "HALT_WITHDRAWALS";
        action.reason = reason;
        action.isActive = true;

        _createAuditLog("EMERGENCY_HALT_WITHDRAWALS", "system", bytes32(actionId), 
            string(abi.encodePacked("Emergency withdrawal halt - Reason: ", reason)));

        emit EmergencyWithdrawalHalt(msg.sender, reason);
    }

    /**
     * @dev Resume withdrawals after emergency halt
     */
    function emergencyResumeWithdrawals() external onlySuperAdmin {
        withdrawalsHalted = false;

        uint256 actionId = emergencyActionCounter++;
        EmergencyAction storage action = emergencyActions[actionId];
        action.actionId = actionId;
        action.timestamp = block.timestamp;
        action.executor = msg.sender;
        action.actionType = "RESUME_WITHDRAWALS";
        action.reason = "Emergency resolved";
        action.isActive = true;

        _createAuditLog("EMERGENCY_RESUME_WITHDRAWALS", "system", bytes32(actionId), 
            "Emergency withdrawals resumed");

        emit EmergencyWithdrawalResume(msg.sender);
    }

    // ==================== VIEW FUNCTIONS ====================

    /**
     * @dev Get contract details
     */
    function getContract(bytes32 contractId) 
        external 
        view 
        contractExists(contractId) 
        returns (TradingContract memory) 
    {
        return tradingContracts[contractId];
    }

    /**
     * @dev Get all contract IDs
     */
    function getAllContractIds() external view returns (bytes32[] memory) {
        return contractIds.values();
    }

    /**
     * @dev Get contracts by status
     */
    function getContractsByStatus(ContractStatus status) 
        external 
        view 
        returns (bytes32[] memory) 
    {
        bytes32[] memory allIds = contractIds.values();
        bytes32[] memory result = new bytes32[](allIds.length);
        uint256 count = 0;

        for (uint256 i = 0; i < allIds.length; i++) {
            if (tradingContracts[allIds[i]].status == status) {
                result[count] = allIds[i];
                count++;
            }
        }

        // Resize array
        bytes32[] memory finalResult = new bytes32[](count);
        for (uint256 i = 0; i < count; i++) {
            finalResult[i] = result[i];
        }

        return finalResult;
    }

    /**
     * @dev Get user profile
     */
    function getUserProfile(address userAddress) 
        external 
        view 
        userExists(userAddress) 
        returns (
            address,
            UserStatus,
            bytes32,
            uint256,
            bool,
            bool,
            bool,
            uint256,
            uint256,
            uint256,
            uint256
        ) 
    {
        UserProfile storage user = userProfiles[userAddress];
        return (
            user.userAddress,
            user.status,
            user.role,
            user.kycLevel,
            user.tradingEnabled,
            user.withdrawalEnabled,
            user.depositEnabled,
            user.maxDailyWithdrawal,
            user.maxSingleWithdrawal,
            user.createdAt,
            user.updatedAt
        );
    }

    /**
     * @dev Check if user has trading permission for specific type
     */
    function hasTradingPermission(address userAddress, TradingType tradingType) 
        external 
        view 
        returns (bool) 
    {
        if (!userAddresses.contains(userAddress)) {
            return false;
        }
        return userProfiles[userAddress].tradingPermissions[tradingType];
    }

    /**
     * @dev Check if user has exchange permission
     */
    function hasExchangePermission(address userAddress, Exchange exchange) 
        external 
        view 
        returns (bool) 
    {
        if (!userAddresses.contains(userAddress)) {
            return false;
        }
        return userProfiles[userAddress].exchangePermissions[exchange];
    }

    /**
     * @dev Get all user addresses
     */
    function getAllUserAddresses() external view returns (address[] memory) {
        return userAddresses.values();
    }

    /**
     * @dev Get system statistics
     */
    function getSystemStats() 
        external 
        view 
        returns (
            uint256 totalContracts,
            uint256 activeContracts,
            uint256 pausedContracts,
            uint256 totalUsers,
            uint256 activeUsers,
            uint256 suspendedUsers,
            uint256 totalAuditLogs,
            bool isTradingHalted,
            bool areWithdrawalsHalted
        ) 
    {
        bytes32[] memory allContractIds = contractIds.values();
        uint256 active = 0;
        uint256 paused = 0;

        for (uint256 i = 0; i < allContractIds.length; i++) {
            ContractStatus status = tradingContracts[allContractIds[i]].status;
            if (status == ContractStatus.ACTIVE) {
                active++;
            } else if (status == ContractStatus.PAUSED) {
                paused++;
            }
        }

        address[] memory allUserAddresses = userAddresses.values();
        uint256 activeUsersCount = 0;
        uint256 suspendedUsersCount = 0;

        for (uint256 i = 0; i < allUserAddresses.length; i++) {
            UserStatus status = userProfiles[allUserAddresses[i]].status;
            if (status == UserStatus.ACTIVE) {
                activeUsersCount++;
            } else if (status == UserStatus.SUSPENDED) {
                suspendedUsersCount++;
            }
        }

        return (
            allContractIds.length,
            active,
            paused,
            allUserAddresses.length,
            activeUsersCount,
            suspendedUsersCount,
            auditLogCounter - 1,
            tradingHalted,
            withdrawalsHalted
        );
    }

    /**
     * @dev Get audit log
     */
    function getAuditLog(uint256 logId) external view returns (AuditLog memory) {
        return auditLogs[logId];
    }

    /**
     * @dev Get emergency action
     */
    function getEmergencyAction(uint256 actionId) external view returns (EmergencyAction memory) {
        return emergencyActions[actionId];
    }

    // ==================== INTERNAL FUNCTIONS ====================

    /**
     * @dev Create audit log entry
     */
    function _createAuditLog(
        string memory action,
        string memory targetType,
        bytes32 targetId,
        string memory details
    ) internal {
        uint256 logId = auditLogCounter++;
        AuditLog storage log = auditLogs[logId];
        log.logId = logId;
        log.timestamp = block.timestamp;
        log.admin = msg.sender;
        log.action = action;
        log.targetType = targetType;
        log.targetId = targetId;
        log.details = details;

        emit AuditLogCreated(logId, msg.sender, action);
    }

    /**
     * @dev Convert trading type to string
     */
    function _tradingTypeToString(TradingType tradingType) internal pure returns (string memory) {
        if (tradingType == TradingType.SPOT) return "SPOT";
        if (tradingType == TradingType.FUTURES_PERPETUAL) return "FUTURES_PERPETUAL";
        if (tradingType == TradingType.FUTURES_CROSS) return "FUTURES_CROSS";
        if (tradingType == TradingType.FUTURES_DELIVERY) return "FUTURES_DELIVERY";
        if (tradingType == TradingType.MARGIN) return "MARGIN";
        if (tradingType == TradingType.MARGIN_CROSS) return "MARGIN_CROSS";
        if (tradingType == TradingType.MARGIN_ISOLATED) return "MARGIN_ISOLATED";
        if (tradingType == TradingType.OPTIONS) return "OPTIONS";
        if (tradingType == TradingType.DERIVATIVES) return "DERIVATIVES";
        if (tradingType == TradingType.COPY_TRADING) return "COPY_TRADING";
        if (tradingType == TradingType.ETF) return "ETF";
        if (tradingType == TradingType.LEVERAGED_TOKENS) return "LEVERAGED_TOKENS";
        if (tradingType == TradingType.STRUCTURED_PRODUCTS) return "STRUCTURED_PRODUCTS";
        return "UNKNOWN";
    }

    /**
     * @dev Convert exchange to string
     */
    function _exchangeToString(Exchange exchange) internal pure returns (string memory) {
        if (exchange == Exchange.BINANCE) return "BINANCE";
        if (exchange == Exchange.KUCOIN) return "KUCOIN";
        if (exchange == Exchange.BYBIT) return "BYBIT";
        if (exchange == Exchange.OKX) return "OKX";
        if (exchange == Exchange.MEXC) return "MEXC";
        if (exchange == Exchange.BITGET) return "BITGET";
        if (exchange == Exchange.BITFINEX) return "BITFINEX";
        return "UNKNOWN";
    }

    // ==================== ADMIN FUNCTIONS ====================

    /**
     * @dev Grant admin role
     */
    function grantAdminRole(address account, bytes32 role) external onlySuperAdmin {
        grantRole(role, account);
        
        _createAuditLog("GRANT_ROLE", "admin", bytes32(uint256(uint160(account))), 
            string(abi.encodePacked("Granted role: ", _roleToString(role))));
    }

    /**
     * @dev Revoke admin role
     */
    function revokeAdminRole(address account, bytes32 role) external onlySuperAdmin {
        revokeRole(role, account);
        
        _createAuditLog("REVOKE_ROLE", "admin", bytes32(uint256(uint160(account))), 
            string(abi.encodePacked("Revoked role: ", _roleToString(role))));
    }

    /**
     * @dev Convert role to string
     */
    function _roleToString(bytes32 role) internal pure returns (string memory) {
        if (role == SUPER_ADMIN_ROLE) return "SUPER_ADMIN";
        if (role == ADMIN_ROLE) return "ADMIN";
        if (role == MODERATOR_ROLE) return "MODERATOR";
        if (role == OPERATOR_ROLE) return "OPERATOR";
        return "UNKNOWN";
    }

    /**
     * @dev Pause contract (emergency)
     */
    function pause() external onlySuperAdmin {
        _pause();
        
        _createAuditLog("PAUSE_CONTRACT", "system", bytes32(0), 
            "Emergency contract pause");
    }

    /**
     * @dev Unpause contract
     */
    function unpause() external onlySuperAdmin {
        _unpause();
        
        _createAuditLog("UNPAUSE_CONTRACT", "system", bytes32(0), 
            "Contract unpaused");
    }
}