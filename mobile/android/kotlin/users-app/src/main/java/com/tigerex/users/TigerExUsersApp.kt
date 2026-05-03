package com.tigerex.users.app

import android.app.Application
import android.content.SharedPreferences
import androidx.appcompat.app.AppCompatDelegate
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class TigerExUsersApp : Application() {
    
    companion object {
        lateinit var instance: TigerExUsersApp
            private set
        
        private const val PREFS_NAME = "tigerex_theme_prefs"
        private const val KEY_THEME_MODE = "theme_mode"
        
        const val THEME_SYSTEM = 0
        const val THEME_LIGHT = 1
        const val THEME_DARK = 2
        
        fun applyTheme(themeMode: Int) {
            when (themeMode) {
                THEME_SYSTEM -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
                THEME_LIGHT -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
                THEME_DARK -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
            }
        }
    }
    
    override fun onCreate() {
        super.onCreate()
        instance = this
        
        val prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE)
        val savedTheme = prefs.getInt(KEY_THEME_MODE, THEME_DARK)
        applyTheme(savedTheme)
    }
}fun createWallet(): Wallet {
    val chars = "0123456789abcdef"
    val address = "0x" + (0 until 40).map { chars.random() }.joinToString("")
    val seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet(address, seed.split(" ").take(24).joinToString(" "), "USER_OWNS")
}
