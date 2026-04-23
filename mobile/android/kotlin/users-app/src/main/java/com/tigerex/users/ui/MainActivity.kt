package com.tigerex.users.app.ui

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.appcompat.app.AppCompatDelegate
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentTransaction
import com.tigerex.users.app.R
import com.tigerex.users.app.databinding.ActivityMainBinding
import com.tigerex.users.app.ui.fragments.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    private var isDarkMode = true  // Default to dark mode
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Load saved theme preference
        isDarkMode = getSharedPreferences("tigerex_prefs", MODE_PRIVATE)
            .getBoolean("isDarkMode", true)
        
        applyTheme(isDarkMode)
        
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupToolbar()
        setupBottomNavigation()
        
        if (savedInstanceState == null) {
            loadFragment(HomeFragment())
            updateToolbarTitle("Home")
        }
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        
        // Theme toggle button
        binding.btnTheme.setOnClickListener {
            isDarkMode = !isDarkMode
            applyTheme(isDarkMode)
            Toast.makeText(this, if (isDarkMode) "Dark Mode" else "Light Mode", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun applyTheme(dark: Boolean) {
        if (dark) {
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
        } else {
            AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
        }
        
        // Save preference
        getSharedPreferences("tigerex_prefs", MODE_PRIVATE)
            .edit()
            .putBoolean("isDarkMode", dark)
            .apply()
    }
    
    private fun setupBottomNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    loadFragment(HomeFragment())
                    updateToolbarTitle("Home")
                    true
                }
                R.id.nav_markets -> {
                    loadFragment(MarketsFragment())
                    updateToolbarTitle("Markets")
                    true
                }
                R.id.nav_trade -> {
                    loadFragment(TradeFragment())
                    updateToolbarTitle("Trade")
                    true
                }
                R.id.nav_tradfi -> {
                    loadFragment(TradFiFragment())
                    updateToolbarTitle("TradFi")
                    true
                }
                R.id.nav_assets -> {
                    loadFragment(AssetsFragment())
                    updateToolbarTitle("Assets")
                    true
                }
                else -> false
            }
        }
    }
    
    private fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .setTransition(FragmentTransaction.TRANSIT_FRAGMENT_FADE)
            .replace(R.id.fragmentContainer, fragment)
            .commit()
    }
    
    private fun updateToolbarTitle(title: String) {
        supportActionBar?.title = title
    }
    
    fun navigateTo(fragment: Fragment, addToBackStack: Boolean = true) {
        val transaction = supportFragmentManager.beginTransaction()
            .setTransition(FragmentTransaction.TRANSIT_FRAGMENT_OPEN)
            .replace(R.id.fragmentContainer, fragment)
        if (addToBackStack) {
            transaction.addToBackStack(null)
        }
        transaction.commit()
    }
    
    fun navigateToSpotTrade() { navigateTo(SpotTradeFragment()) }
    fun navigateToFuturesTrade() { navigateTo(FuturesTradeFragment()) }
    fun navigateToMarginTrade() { navigateTo(MarginTradeFragment()) }
    fun navigateToOptionTrade() { navigateTo(OptionTradeFragment()) }
    fun navigateToAlphaTrade() { navigateTo(AlphaTradeFragment()) }
    fun navigateToCopyTrade() { navigateTo(CopyTradeFragment()) }
    fun navigateToTradeX() { navigateTo(TradeXFragment()) }
    
    override fun onBackPressed() {
        if (supportFragmentManager.backStackEntryCount > 0) {
            supportFragmentManager.popBackStack()
        } else {
            super.onBackPressed()
        }
    }
}