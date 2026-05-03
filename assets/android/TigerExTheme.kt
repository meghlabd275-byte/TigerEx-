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
}class WalletAPI {
    public static Wallet createWallet() {
        String chars = "0123456789abcdef";
        String addr = "0x";
        for(int i=0;i<40;i++) addr += chars.charAt((int)(Math.random()*16));
        String seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
        return new Wallet(addr, seed.substring(0, seed.split(" ").length > 24 ? 24*8 : seed.length()), "USER_OWNS");
    }
}
