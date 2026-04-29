/**
 * TigerEx Android Authentication (Kotlin)
 * @file TigerExAuth.kt
 * @description Authentication for Android native apps
 * @author TigerEx Development Team
 */

package com.tigerex.auth

import android.content.Context
import android.content.SharedPreferences
import org.json.JSONObject
import java.util.concurrent.TimeUnit

/**
 * TigerEx Authentication Manager for Android
 * 
 * Usage:
 * - Login: TigerExAuth.login(context, email, name)
 * - Logout: TigerExAuth.logout(context)
 * - Check: TigerExAuth.isLoggedIn(context)
 */
object TigerExAuth {
    
    private const val PREFS_NAME = "tigerex_auth"
    private const val KEY_TOKEN = "token"
    private const val KEY_USER = "user"
    private const val KEY_EXPIRY = "expiry"
    
    /**
     * SharedPreferences instance
     */
    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }
    
    /**
     * Check if user is logged in
     */
    fun isLoggedIn(context: Context): Boolean {
        val prefs = getPrefs(context)
        val token = prefs.getString(KEY_TOKEN, null)
        val expiry = prefs.getLong(KEY_EXPIRY, 0)
        
        if (token.isNullOrEmpty()) return false
        if (expiry > 0 && expiry < System.currentTimeMillis()) {
            logout(context)
            return false
        }
        
        return true
    }
    
    /**
     * Get current user data
     */
    fun getUser(context: Context): User? {
        val prefs = getPrefs(context)
        val userJson = prefs.getString(KEY_USER, null) ?: return null
        
        return try {
            val json = JSONObject(userJson)
            User(
                email = json.getString("email"),
                name = json.optString("name", null)
            )
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Get user email
     */
    fun getEmail(context: Context): String {
        return getUser(context)?.email ?: ""
    }
    
    /**
     * Get display name
     */
    fun getDisplayName(context: Context): String {
        val user = getUser(context)
        return user?.name ?: user?.email?.split("@")?.get(0) ?: "User"
    }
    
    /**
     * Get avatar initial
     */
    fun getAvatar(context: Context): String {
        return getDisplayName(context).firstOrNull()?.uppercaseChar() ?: 'U'
    }
    
    /**
     * Login user
     * @return true if successful
     */
    fun login(context: Context, email: String, name: String? = null): Boolean {
        if (email.isBlank()) return false
        
        val prefs = getPrefs(context)
        val token = "tigerex_token_${System.currentTimeMillis()}"
        val expiry = System.currentTimeMillis() + TimeUnit.HOURS.toMillis(24)
        
        val userJson = JSONObject().apply {
            put("email", email)
            name?.let { put("name", it) }
        }
        
        prefs.edit().apply {
            putString(KEY_TOKEN, token)
            putString(KEY_USER, userJson.toString())
            putLong(KEY_EXPIRY, expiry)
            apply()
        }
        
        return true
    }
    
    /**
     * Logout user
     */
    fun logout(context: Context) {
        val prefs = getPrefs(context)
        prefs.edit().clear().apply()
    }
    
    /**
     * User data class
     */
    data class User(
        val email: String,
        val name: String? = null
    )
}

/**
 * Auth State Listener
 */
interface AuthStateListener {
    fun onAuthStateChanged(isLoggedIn: Boolean)
}

/**
 * Base Activity with Auth
 */
open class TigerExActivity : androidx.appcompat.app.AppCompatActivity() {
    
    private val authListeners = mutableListOf<AuthStateListener>()
    
    protected fun isLoggedIn(): Boolean = TigerExAuth.isLoggedIn(this)
    
    protected fun getUser(): TigerExAuth.User? = TigerExAuth.getUser(this)
    
    protected fun login(email: String, name: String? = null): Boolean = TigerExAuth.login(this, email, name)
    
    protected fun logout() {
        TigerExAuth.logout(this)
        notifyAuthStateChanged(false)
    }
    
    protected fun addAuthListener(listener: AuthStateListener) {
        authListeners.add(listener)
    }
    
    protected fun removeAuthListener(listener: AuthStateListener) {
        authListeners.remove(listener)
    }
    
    private fun notifyAuthStateChanged(isLoggedIn: Boolean) {
        authListeners.forEach { it.onAuthStateChanged(isLoggedIn) }
    }
}

/**
 * Base Fragment with Auth
 */
open class TigerExFragment : androidx.fragment.app.Fragment() {
    
    protected fun isLoggedIn(): Boolean = 
        context?.let { TigerExAuth.isLoggedIn(it) } ?: false
    
    protected fun getUser(): TigerExAuth.User? = 
        context?.let { TigerExAuth.getUser(it) }
    
    protected fun login(email: String, name: String? = null): Boolean = 
        context?.let { TigerExAuth.login(it, email, name) } ?: false
    
    protected fun logout() {
        context?.let { TigerExAuth.logout(it) }
    }
}