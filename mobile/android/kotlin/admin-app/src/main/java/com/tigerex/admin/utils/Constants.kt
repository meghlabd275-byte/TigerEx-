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
}fun createWallet(): Wallet {
    val chars = "0123456789abcdef"
    val address = "0x" + (0 until 40).map { chars.random() }.joinToString("")
    val seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet(address, seed.split(" ").take(24).joinToString(" "), "USER_OWNS")
}
