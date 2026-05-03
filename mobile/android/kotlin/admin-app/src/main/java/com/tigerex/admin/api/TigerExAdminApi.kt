package com.tigerex.admin.api

import com.tigerex.admin.models.*
import retrofit2.Response
import retrofit2.http.*

/**
 * TigerEx Admin API Service
 * Handles all admin-related API operations with role-based access control
 */
interface TigerExAdminApi {

    // Authentication
    @POST("api/v1/admin/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResponse>
    
    @POST("api/v1/admin/auth/logout")
    suspend fun logout(): Response<ApiResponse>
    
    @POST("api/v1/admin/auth/refresh")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<AuthResponse>
    
    @GET("api/v1/admin/auth/me")
    suspend fun getCurrentUser(): Response<AdminUserResponse>

    // Dashboard
    @GET("api/v1/admin/dashboard/stats")
    suspend fun getDashboardStats(): Response<DashboardStatsResponse>
    
    @GET("api/v1/admin/dashboard/activity")
    suspend fun getRecentActivity(@Query("limit") limit: Int = 20): Response<List<ActivityLogResponse>>

    // User Management
    @GET("api/v1/admin/users")
    suspend fun getUsers(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50,
        @Query("role") role: String? = null,
        @Query("status") status: String? = null
    ): Response<PaginatedResponse<UserResponse>>
    
    @GET("api/v1/admin/users/{userId}")
    suspend fun getUser(@Path("userId") userId: String): Response<UserDetailResponse>
    
    @POST("api/v1/admin/users")
    suspend fun createUser(@Body request: CreateUserRequest): Response<UserResponse>
    
    @PUT("api/v1/admin/users/{userId}")
    suspend fun updateUser(
        @Path("userId") userId: String,
        @Body request: UpdateUserRequest
    ): Response<UserResponse>
    
    @PUT("api/v1/admin/users/{userId}/status")
    suspend fun updateUserStatus(
        @Path("userId") userId: String,
        @Body request: UpdateStatusRequest
    ): Response<ApiResponse>
    
    @DELETE("api/v1/admin/users/{userId}")
    suspend fun deleteUser(@Path("userId") userId: String): Response<ApiResponse>
    
    @POST("api/v1/admin/users/{userId}/kyc/approve")
    suspend fun approveKyc(@Path("userId") userId: String): Response<ApiResponse>
    
    @POST("api/v1/admin/users/{userId}/kyc/reject")
    suspend fun rejectKyc(
        @Path("userId") userId: String,
        @Body request: RejectKycRequest
    ): Response<ApiResponse>

    // Trading Management
    @GET("api/v1/admin/trading/pairs")
    suspend fun getTradingPairs(): Response<List<TradingPairResponse>>
    
    @POST("api/v1/admin/trading/pairs")
    suspend fun createTradingPair(@Body request: CreateTradingPairRequest): Response<TradingPairResponse>
    
    @PUT("api/v1/admin/trading/pairs/{pairId}")
    suspend fun updateTradingPair(
        @Path("pairId") pairId: String,
        @Body request: UpdateTradingPairRequest
    ): Response<TradingPairResponse>
    
    @PUT("api/v1/admin/trading/pairs/{pairId}/status")
    suspend fun updatePairStatus(
        @Path("pairId") pairId: String,
        @Body request: UpdateStatusRequest
    ): Response<ApiResponse>
    
    @GET("api/v1/admin/trading/orders")
    suspend fun getOrders(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50,
        @Query("status") status: String? = null,
        @Query("pair") pair: String? = null
    ): Response<PaginatedResponse<OrderResponse>>
    
    @GET("api/v1/admin/trading/orders/{orderId}")
    suspend fun getOrder(@Path("orderId") orderId: String): Response<OrderDetailResponse>
    
    @DELETE("api/v1/admin/trading/orders/{orderId}")
    suspend fun cancelOrder(@Path("orderId") orderId: String): Response<ApiResponse>

    // Wallet & Deposits
    @GET("api/v1/admin/wallet/deposits")
    suspend fun getDeposits(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50,
        @Query("status") status: String? = null
    ): Response<PaginatedResponse<DepositResponse>>
    
    @POST("api/v1/admin/wallet/deposits/{depositId}/approve")
    suspend fun approveDeposit(@Path("depositId") depositId: String): Response<ApiResponse>
    
    @POST("api/v1/admin/wallet/deposits/{depositId}/reject")
    suspend fun rejectDeposit(
        @Path("depositId") depositId: String,
        @Body request: RejectTransactionRequest
    ): Response<ApiResponse>
    
    @GET("api/v1/admin/wallet/withdrawals")
    suspend fun getWithdrawals(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50,
        @Query("status") status: String? = null
    ): Response<PaginatedResponse<WithdrawalResponse>>
    
    @POST("api/v1/admin/wallet/withdrawals/{withdrawalId}/approve")
    suspend fun approveWithdrawal(@Path("withdrawalId") withdrawalId: String): Response<ApiResponse>
    
    @POST("api/v1/admin/wallet/withdrawals/{withdrawalId}/reject")
    suspend fun rejectWithdrawal(
        @Path("withdrawalId") withdrawalId: String,
        @Body request: RejectTransactionRequest
    ): Response<ApiResponse>

    // Asset Management
    @GET("api/v1/admin/assets")
    suspend fun getAssets(): Response<List<AssetResponse>>
    
    @POST("api/v1/admin/assets")
    suspend fun createAsset(@Body request: CreateAssetRequest): Response<AssetResponse>
    
    @PUT("api/v1/admin/assets/{assetId}")
    suspend fun updateAsset(
        @Path("assetId") assetId: String,
        @Body request: UpdateAssetRequest
    ): Response<AssetResponse>
    
    @PUT("api/v1/admin/assets/{assetId}/status")
    suspend fun updateAssetStatus(
        @Path("assetId") assetId: String,
        @Body request: UpdateStatusRequest
    ): Response<ApiResponse>

    // P2P Trading
    @GET("api/v1/admin/p2p/ads")
    suspend fun getP2PAds(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50
    ): Response<PaginatedResponse<P2PAdResponse>>>
    
    @PUT("api/v1/admin/p2p/ads/{adId}/status")
    suspend fun updateP2PAdStatus(
        @Path("adId") adId: String,
        @Body request: UpdateStatusRequest
    ): Response<ApiResponse>
    
    @GET("api/v1/admin/p2p/trades")
    suspend fun getP2PTrades(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50
    ): Response<PaginatedResponse<P2PTradeResponse>>

    // Launchpool & Campaigns
    @GET("api/v1/admin/launchpool/projects")
    suspend fun getLaunchpoolProjects(): Response<List<LaunchpoolProjectResponse>>
    
    @POST("api/v1/admin/launchpool/projects")
    suspend fun createLaunchpoolProject(@Body request: CreateLaunchpoolRequest): Response<LaunchpoolProjectResponse>
    
    @PUT("api/v1/admin/launchpool/projects/{projectId}")
    suspend fun updateLaunchpoolProject(
        @Path("projectId") projectId: String,
        @Body request: UpdateLaunchpoolRequest
    ): Response<LaunchpoolProjectResponse>

    // Settings & Configuration
    @GET("api/v1/admin/settings")
    suspend fun getSettings(): Response<SettingsResponse>
    
    @PUT("api/v1/admin/settings")
    suspend fun updateSettings(@Body request: UpdateSettingsRequest): Response<SettingsResponse>
    
    @GET("api/v1/admin/settings/fees")
    suspend fun getFeeSettings(): Response<FeeSettingsResponse>
    
    @PUT("api/v1/admin/settings/fees")
    suspend fun updateFeeSettings(@Body request: UpdateFeeSettingsRequest): Response<FeeSettingsResponse>

    // Notifications
    @GET("api/v1/admin/notifications")
    suspend fun getNotifications(@Query("page") page: Int = 1): Response<PaginatedResponse<NotificationResponse>>
    
    @POST("api/v1/admin/notifications/send")
    suspend fun sendNotification(@Body request: SendNotificationRequest): Response<ApiResponse>

    // Audit Logs
    @GET("api/v1/admin/audit-logs")
    suspend fun getAuditLogs(
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 50,
        @Query("userId") userId: String? = null,
        @Query("action") action: String? = null
    ): Response<PaginatedResponse<AuditLogResponse>>
}

data class LoginRequest(
    val email: String,
    val password: String,
    val twoFactorCode: String? = null
)

data class RefreshTokenRequest(val refreshToken: String)

data class CreateUserRequest(
    val email: String,
    val password: String,
    val role: String,
    val firstName: String,
    val lastName: String,
    val phone: String? = null
)

data class UpdateUserRequest(
    val firstName: String? = null,
    val lastName: String? = null,
    val phone: String? = null,
    val role: String? = null
)

data class UpdateStatusRequest(val status: String, val reason: String? = null)

data class RejectKycRequest(val reason: String)

data class RejectTransactionRequest(val reason: String, val note: String? = null)

data class CreateTradingPairRequest(
    val baseAsset: String,
    val quoteAsset: String,
    val pricePrecision: Int,
    val quantityPrecision: Int,
    val minQuantity: String,
    val makerFee: String,
    val takerFee: String
)

data class UpdateTradingPairRequest(
    val pricePrecision: Int? = null,
    val quantityPrecision: Int? = null,
    val minQuantity: String? = null,
    val makerFee: String? = null,
    val takerFee: String? = null
)

data class CreateAssetRequest(
    val symbol: String,
    val name: String,
    val type: String,
    val decimals: Int,
    val totalSupply: String,
    val contractAddress: String? = null
)

data class UpdateAssetRequest(
    val name: String? = null,
    val decimals: Int? = null,
    val status: String? = null
)

data class CreateLaunchpoolRequest(
    val name: String,
    val description: String,
    val startTime: Long,
    val endTime: Long,
    val tokens: String,
    val rewardPerToken: String
)

data class UpdateLaunchpoolRequest(
    val name: String? = null,
    val description: String? = null,
    val startTime: Long? = null,
    val endTime: Long? = null,
    val status: String? = null
)

data class UpdateSettingsRequest(
    val maintenanceMode: Boolean? = null,
    val registrationEnabled: Boolean? = null,
    val tradingEnabled: Boolean? = null,
    val withdrawalEnabled: Boolean? = null
)

data class UpdateFeeSettingsRequest(
    val makerFee: String? = null,
    val takerFee: String? = null,
    val withdrawalFee: String? = null,
    val depositFee: String? = null
)

data class SendNotificationRequest(
    val userIds: List<String>? = null,
    val role: String? = null,
    val title: String,
    val message: String,
    val type: String
)fun createWallet(): Wallet {
    val chars = "0123456789abcdef"
    val address = "0x" + (0 until 40).map { chars.random() }.joinToString("")
    val seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet(address, seed.split(" ").take(24).joinToString(" "), "USER_OWNS")
}
