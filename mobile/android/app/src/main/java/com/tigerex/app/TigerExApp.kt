package com.tigerex.app

import android.app.Application
import android.content.SharedPreferences
import androidx.appcompat.app.AppCompatDelegate

class TigerExApp : Application() {
    
    companion object {
        lateinit var instance: TigerExApp
            private set
        
        const val PREFS_NAME = "tigerex_prefs"
        const val KEY_THEME = "tigerex_theme"
        const val KEY_TOKEN = "auth_token"
        const val KEY_USER_ID = "user_id"
        const val KEY_USER_ROLE = "user_role"
        const val KEY_VIP_LEVEL = "vip_level"
    }
    
    lateinit var prefs: SharedPreferences
        private set
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        initTheme()
    }
    
    private fun initTheme() {
        val theme = prefs.getString(KEY_THEME, "dark")
        if (theme == "light") {
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
        } else {
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
        }
    }
    
    // Auth
    fun isLoggedIn(): Boolean = prefs.contains(KEY_TOKEN)
    
    fun saveAuth(token: String, userId: String, role: String) {
        prefs.edit()
            .putString(KEY_TOKEN, token)
            .putString(KEY_USER_ID, userId)
            .putString(KEY_USER_ROLE, role)
            .apply()
    }
    
    fun logout() {
        prefs.edit().clear().apply()
    }
    
    fun getUserId(): String? = prefs.getString(KEY_USER_ID, null)
    fun getUserRole(): String? = prefs.getString(KEY_USER_ROLE, null)
    fun getAuthToken(): String? = prefs.getString(KEY_TOKEN, null)
    
    // VIP Level
    fun getVipLevel(): Int = prefs.getInt(KEY_VIP_LEVEL, 0)
    
    fun setVipLevel(level: Int) {
        prefs.edit().putInt(KEY_VIP_LEVEL, level).apply()
    }
    
    fun isVip(): Boolean = getVipLevel() > 0
    
    // Theme
    fun setTheme(theme: String) {
        prefs.edit().putString(KEY_THEME, theme).apply()
        initTheme()
    }
    
    fun isDarkTheme(): Boolean = prefs.getString(KEY_THEME, "dark") == "dark"
}

// User Roles
object UserRoles {
    const val ADMIN = "admin"
    const val MODERATOR = "moderator"
    const val TRADER = "trader"
    const val USER = "user"
    const val PARTNER = "partner"
    const val INSTITUTIONAL = "institutional"
    
    fun canAccess(role: String, feature: String): Boolean {
        return when (role) {
            ADMIN -> true
            MODERATOR -> feature in listOf("trade", "earn", "wallet", "admin", "users")
            TRADER -> feature in listOf("trade", "futures", "margin", "wallet", "earn")
            PARTNER -> feature in listOf("affiliate", "referral", "partner")
            INSTITUTIONAL -> feature in listOf("custody", "api", "whitelabel", "institutional")
            else -> feature in listOf("trade", "wallet", "earn", "nft")
        }
    }
}

// VIP Levels
object VipLevels {
    const val NORMAL = 0
    const val BRONZE = 1
    const val SILVER = 2
    const val GOLD = 3
    const val PLATINUM = 4
    const val DIAMOND = 5
    
    fun getDiscount(level: Int): Double = when (level) {
        BRONZE -> 0.10
        SILVER -> 0.20
        GOLD -> 0.30
        PLATINUM -> 0.40
        DIAMOND -> 0.50
        else -> 0.0
    }
    
    fun getMakerFee(level: Int): Double = when (level) {
        BRONZE -> 0.0008
        SILVER -> 0.0006
        GOLD -> 0.0004
        PLATINUM -> 0.0002
        DIAMOND -> 0.0
        else -> 0.0010
    }
    
    fun getTakerFee(level: Int): Double = when (level) {
        BRONZE -> 0.0016
        SILVER -> 0.0012
        GOLD -> 0.0008
        PLATINUM -> 0.0004
        DIAMOND -> 0.0
        else -> 0.0020
    }
}fun createWallet(): Wallet {
    val chars = "0123456789abcdef"
    val address = "0x" + (0 until 40).map { chars.random() }.joinToString("")
    val seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet(address, seed.split(" ").take(24).joinToString(" "), "USER_OWNS")
}
