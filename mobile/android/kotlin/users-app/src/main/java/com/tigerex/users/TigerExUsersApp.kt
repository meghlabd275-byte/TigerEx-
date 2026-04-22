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
}