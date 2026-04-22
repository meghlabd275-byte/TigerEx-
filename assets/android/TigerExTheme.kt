/**
 * TigerEx Theme Manager for Kotlin/Android
 * Include in your Android app for consistent theming
 */

package com.tigerex.theme

import android.content.Context
import android.content.SharedPreferences
import androidx.appcompat.app.AppCompatDelegate

object TigerExTheme {
    private const val PREFS_NAME = "tigerex_prefs"
    private const val THEME_KEY = "tigerex_theme"
    private const val THEME_LIGHT = "light"
    private const val THEME_DARK = "dark"
    
    fun init(context: Context) {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val savedTheme = prefs.getString(THEME_KEY, THEME_DARK)
        
        if (savedTheme == THEME_LIGHT) {
            setLightMode()
        } else {
            setDarkMode()
        }
    }
    
    fun setLightMode() {
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
    }
    
    fun setDarkMode() {
        AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
    }
    
    fun toggleTheme(context: Context) {
        val currentTheme = getCurrentTheme(context)
        if (currentTheme == THEME_LIGHT) {
            setDarkMode()
        } else {
            setLightMode()
        }
    }
    
    fun getCurrentTheme(context: Context): String {
        val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        return prefs.getString(THEME_KEY, THEME_DARK) ?: THEME_DARK
    }
}