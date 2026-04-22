package com.tigerex.admin.utils

object Constants {
    const val API_BASE_URL = "https://api.tigerex.com/"
    const val WS_BASE_URL = "wss://stream.tigerex.com/"
    
    const val DATABASE_NAME = "tigerex_admin_db"
    const val DATABASE_VERSION = 1
    
    const val PREFS_NAME = "tigerex_admin_prefs"
    
    const val SESSION_TIMEOUT = 30 * 60 * 1000L
    const val REFRESH_INTERVAL = 5 * 60 * 1000L
    
    const val MAX_FILE_SIZE = 10 * 1024 * 1024
    const val COMPRESSION_QUALITY = 85
}

object UserRoles {
    const val SUPER_ADMIN = "super_admin"
    const val ADMIN = "admin"
    const val MODERATOR = "moderator"
    const val LISTING_MANAGER = "listing_manager"
    const val BD_MANAGER = "bd_manager"
    const val SUPPORT_TEAM = "support_team"
    const val LIQUIDITY_MANAGER = "liquidity_manager"
    const val TECHNICAL_TEAM = "technical_team"
    const val COMPLIANCE_MANAGER = "compliance_manager"
}

object TransactionStatus {
    const val PENDING = "pending"
    const val PROCESSING = "processing"
    const val COMPLETED = "completed"
    const val FAILED = "failed"
    const val CANCELLED = "cancelled"
}

object OrderStatus {
    const val OPEN = "open"
    const val PARTIALLY_FILLED = "partially_filled"
    const val FILLED = "filled"
    const val CANCELLED = "cancelled"
    const val EXPIRED = "expired"
}

object KycStatus {
    const val UNVERIFIED = "unverified"
    const val PENDING = "pending"
    const val VERIFIED = "verified"
    const val REJECTED = "rejected"
}