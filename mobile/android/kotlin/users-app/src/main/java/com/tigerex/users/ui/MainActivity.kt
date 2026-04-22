package com.tigerex.users.app.ui

import android.os.Bundle
import android.view.MenuItem
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentManager
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.tigerex.users.app.R
import com.tigerex.users.app.databinding.ActivityMainBinding
import com.tigerex.users.app.ui.fragments.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityMainBinding
    
    private val fragmentManager: FragmentManager by supportFragmentManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupBottomNavigation()
        
        if (savedInstanceState == null) {
            loadFragment(HomeFragment())
        }
    }
    
    private fun setupBottomNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> {
                    loadFragment(HomeFragment())
                    true
                }
                R.id.nav_markets -> {
                    loadFragment(MarketsFragment())
                    true
                }
                R.id.nav_trade -> {
                    loadFragment(TradeFragment())
                    true
                }
                R.id.nav_wallet -> {
                    loadFragment(WalletFragment())
                    true
                }
                R.id.nav_earn -> {
                    loadFragment(EarnFragment())
                    true
                }
                else -> false
            }
        }
    }
    
    private fun loadFragment(fragment: Fragment) {
        fragmentManager.beginTransaction()
            .replace(R.id.fragmentContainer, fragment)
            .commit()
    }
    
    override fun onBackPressed() {
        if (fragmentManager.backStackEntryCount > 0) {
            fragmentManager.popBackStack()
        } else {
            super.onBackPressed()
        }
    }
}