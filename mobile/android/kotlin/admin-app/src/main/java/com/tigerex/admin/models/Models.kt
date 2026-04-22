package com.tigerex.admin.models

import com.google.gson.annotations.SerializedName

// ============ Core User Models ============
data class User(
    @SerializedName("id") val id: String,
    @SerializedName("email") val email: String,
    @SerializedName("role") val role: UserRole,
    @SerializedName("status") val status: AccountStatus,
    @SerializedName("firstName") val firstName: String,
    @SerializedName("lastName") val lastName: String,
    @SerializedName("phone") val phone: String?,
    @SerializedName("kycStatus") val kycStatus: KycStatus,
    @SerializedName("createdAt") val createdAt: Long,
    @SerializedName("lastLoginAt") val lastLoginAt: Long?,
    @SerializedName("twoFactorEnabled") val twoFactorEnabled: Boolean,
    @SerializedName("referralCode") val referralCode: String?
)

enum class UserRole {
    @SerializedName("trader") TRADER,
    @SerializedName("vip") VIP,
    @SerializedName("affiliate") AFFILIATE,
    @SerializedName("partner") PARTNER,
    @SerializedName("institution") INSTITUTION,
    @SerializedName("p2pMerchant") P2P_MERCHANT,
    @SerializedName("liquidityProvider") LIQUIDITY_PROVIDER,
    @SerializedName("marketMaker") MARKET_MAKER,
    @SerializedName("tokenTeam") TOKEN_TEAM,
    @SerializedName("whiteLabel") WHITE_LABEL,
    @SerializedName("admin") ADMIN,
    @SerializedName("superAdmin") SUPER_ADMIN,
    @SerializedName("moderator") MODERATOR,
    @SerializedName("listingManager") LISTING_MANAGER,
    @SerializedName("bdManager") BD_MANAGER,
    @SerializedName("supportTeam") SUPPORT_TEAM,
    @SerializedName("liquidityManager") LIQUIDITY_MANAGER,
    @SerializedName("technicalTeam") TECHNICAL_TEAM,
    @SerializedName("complianceManager") COMPLIANCE_MANAGER
}

enum class AccountStatus {
    @SerializedName("active") ACTIVE,
    @SerializedName("suspended") SUSPENDED,
    @SerializedName("paused") PAUSED,
    @SerializedName("locked") LOCKED,
    @SerializedName("closed") CLOSED,
    @SerializedName("pending") PENDING,
    @SerializedName("restricted") RESTRICTED
}

enum class KycStatus {
    @SerializedName("unverified") UNVERIFIED,
    @SerializedName("pending") PENDING,
    @SerializedName("verified") VERIFIED,
    @SerializedName("rejected") REJECTED,
    @SerializedName("expired") EXPIRED
}

// ============ Trading Models ============
data class TradingPair(
    @SerializedName("id") val id: String,
    @SerializedName("baseAsset") val baseAsset: String,
    @SerializedName("quoteAsset") val quoteAsset: String,
    @SerializedName("currentPrice") val currentPrice: String,
    @SerializedName("priceChange24h") val priceChange24h: String,
    @SerializedName("volume24h") val volume24h: String,
    @SerializedName("high24h") val high24h: String,
    @SerializedName("low24h") val low24h: String,
    @SerializedName("status") val status: PairStatus
)

data class Order(
    @SerializedName("id") val id: String,
    @SerializedName("userId") val userId: String,
    @SerializedName("pair") val pair: String,
    @SerializedName("type") val type: OrderType,
    @SerializedName("side") val side: OrderSide,
    @SerializedName("price") val price: String,
    @SerializedName("quantity") val quantity: String,
    @SerializedName("filledQuantity") val filledQuantity: String,
    @SerializedName("averagePrice") val averagePrice: String,
    @SerializedName("status") val status: OrderStatus,
    @SerializedName("createdAt") val createdAt: Long
)

enum class OrderType {
    @SerializedName("market") MARKET,
    @SerializedName("limit") LIMIT,
    @SerializedName("stopLoss") STOP_LOSS,
    @SerializedName("stopLimit") STOP_LIMIT,
    @SerializedName("takeProfit") TAKE_PROFIT,
    @SerializedName("oco") OCO
}

enum class OrderSide {
    @SerializedName("buy") BUY,
    @SerializedName("sell") SELL
}

enum class OrderStatus {
    @SerializedName("open") OPEN,
    @SerializedName("partiallyFilled") PARTIALLY_FILLED,
    @SerializedName("filled") FILLED,
    @SerializedName("cancelled") CANCELLED,
    @SerializedName("expired") EXPIRED
}

enum class PairStatus {
    @SerializedName("trading") TRADING,
    @SerializedName("halted") HALTED,
    @SerializedName("paused") PAUSED,
    @SerializedName("maintenance") MAINTENANCE
}

// ============ Wallet Models ============
data class Wallet(
    @SerializedName("id") val id: String,
    @SerializedName("userId") val userId: String,
    @SerializedName("asset") val asset: String,
    @SerializedName("balance") val balance: String,
    @SerializedName("availableBalance") val availableBalance: String,
    @SerializedName("lockedBalance") val lockedBalance: String,
    @SerializedName("frozenBalance") val frozenBalance: String
)

data class Deposit(
    @SerializedName("id") val id: String,
    @SerializedName("userId") val userId: String,
    @SerializedName("asset") val asset: String,
    @SerializedName("amount") val amount: String,
    @SerializedName("hash") val hash: String,
    @SerializedName("fromAddress") val fromAddress: String?,
    @SerializedName("toAddress") val toAddress: String,
    @SerializedName("status") val status: TransactionStatus,
    @SerializedName("confirmations") val confirmations: Int,
    @SerializedName("requiredConfirmations") val requiredConfirmations: Int,
    @SerializedName("createdAt") val createdAt: Long
)

data class Withdrawal(
    @SerializedName("id") val id: String,
    @SerializedName("userId") val userId: String,
    @SerializedName("asset") val asset: String,
    @SerializedName("amount") val amount: String,
    @SerializedName("fee") val fee: String,
    @SerializedName("netAmount") val netAmount: String,
    @SerializedName("hash") val hash: String?,
    @SerializedName("toAddress") val toAddress: String,
    @SerializedName("status") val status: WithdrawalStatus,
    @SerializedName("createdAt") val createdAt: Long
)

enum class TransactionStatus {
    @SerializedName("pending") PENDING,
    @SerializedName("confirming") CONFIRMING,
    @SerializedName("completed") COMPLETED,
    @SerializedName("failed") FAILED
}

enum class WithdrawalStatus {
    @SerializedName("pending") PENDING,
    @SerializedName("processing") PROCESSING,
    @SerializedName("completed") COMPLETED,
    @SerializedName("failed") FAILED,
    @SerializedName("cancelled") CANCELLED
}

// ============ P2P Models ============
data class P2PAd(
    @SerializedName("id") val id: String,
    @SerializedName("userId") val userId: String,
    @SerializedName("type") val type: P2PAdType,
    @SerializedName("asset") val asset: String,
    @SerializedName("fiatCurrency") val fiatCurrency: String,
    @SerializedName("price") val price: String,
    @SerializedName("minAmount") val minAmount: String,
    @SerializedName("maxAmount") val maxAmount: String,
    @SerializedName("paymentMethods") val paymentMethods: List<String>,
    @SerializedName("status") val status: P2PAdStatus
)

enum class P2PAdType {
    @SerializedName("buy") BUY,
    @SerializedName("sell") SELL
}

enum class P2PAdStatus {
    @SerializedName("active") ACTIVE,
    @SerializedName("paused") PAUSED,
    @SerializedName("closed") CLOSED
}

// ============ Earn Products Models ============
data class StakingProduct(
    @SerializedName("id") val id: String,
    @SerializedName("name") val name: String,
    @SerializedName("asset") val asset: String,
    @SerializedName("duration") val duration: Int,
    @SerializedName("apr") val apr: String,
    @SerializedName("minAmount") val minAmount: String,
    @SerializedName("maxAmount") val maxAmount: String?,
    @SerializedName("totalStaked") val totalStaked: String,
    @SerializedName("status") val status: String
)

data class StakingPosition(
    @SerializedName("id") val id: String,
    @SerializedName("productId") val productId: String,
    @SerializedName("userId") val userId: String,
    @SerializedName("amount") val amount: String,
    @SerializedName("reward") val reward: String,
    @SerializedName("startTime") val startTime: Long,
    @SerializedName("endTime") val endTime: Long,
    @SerializedName("status") val status: String
)

// ============ API Response Models ============
data class ApiResponse<T>(
    @SerializedName("success") val success: Boolean,
    @SerializedName("data") val data: T?,
    @SerializedName("message") val message: String?,
    @SerializedName("errorCode") val errorCode: String?
)

data class PaginatedResponse<T>(
    @SerializedName("items") val items: List<T>,
    @SerializedName("total") val total: Int,
    @SerializedName("page") val page: Int,
    @SerializedName("limit") val limit: Int,
    @SerializedName("hasMore") val hasMore: Boolean
)

data class DashboardStats(
    @SerializedName("totalUsers") val totalUsers: Long,
    @SerializedName("activeUsers") val activeUsers: Long,
    @SerializedName("totalTradingVolume") val totalTradingVolume: String,
    @SerializedName("totalAssets") val totalAssets: String,
    @SerializedName("pendingWithdrawals") val pendingWithdrawals: Int,
    @SerializedName("pendingDeposits") val pendingDeposits: Int,
    @SerializedName("supportTickets") val supportTickets: Int
)