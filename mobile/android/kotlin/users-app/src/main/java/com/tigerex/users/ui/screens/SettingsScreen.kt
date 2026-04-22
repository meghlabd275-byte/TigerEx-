package com.tigerex.users.app.ui.screens

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.AdapterView
import android.widget.ArrayAdapter
import androidx.appcompat.app.AppCompatDelegate
import androidx.fragment.app.Fragment
import com.tigerex.users.app.databinding.ScreenSettingsBinding
import com.tigerex.users.app.TigerExUsersApp

class SettingsScreen : Fragment() {
    
    private var _binding: ScreenSettingsBinding? = null
    private val binding get() = _binding!!
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = ScreenSettingsBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupUI()
        setupClickListeners()
    }
    
    private fun setupUI() {
        // Theme Selection
        val themes = arrayOf("System Default", "Light", "Dark")
        val adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, themes)
        binding.spinnerTheme.adapter = adapter
        
        // Load current theme
        val currentMode = AppCompatDelegate.getDefaultNightMode()
        val selectedIndex = when (currentMode) {
            AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM -> 0
            AppCompatDelegate.MODE_NIGHT_NO -> 1
            AppCompatDelegate.MODE_NIGHT_YES -> 2
            else -> 2
        }
        binding.spinnerTheme.setSelection(selectedIndex)
        
        // Language Selection
        val languages = arrayOf("English", "中文", "한국어", "日本語", "العربية", "Español", "Português")
        val langAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, languages)
        binding.spinnerLanguage.adapter = langAdapter
        
        // Currency Selection
        val currencies = arrayOf("USD", "EUR", "GBP", "CNY", "JPY", "KRW", "RUB", "INR")
        val currencyAdapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, currencies)
        binding.spinnerCurrency.adapter = currencyAdapter
    }
    
    private fun setupClickListeners() {
        binding.apply {
            // Theme Toggle
            switchTheme.setOnCheckedChangeListener { _, isChecked ->
                if (isChecked) {
                    AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
                } else {
                    AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
                }
            }
            
            spinnerTheme.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
                override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                    when (position) {
                        0 -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
                        1 -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_NO)
                        2 -> AppCompatDelegate.setDefaultNightMode(AppCompatDelegate.MODE_NIGHT_YES)
                    }
                }
                override fun onNothingSelected(parent: AdapterView<*>?) {}
            }
            
            // Security Settings
            rowTwoFactor.setOnClickListener { navigateTo(TwoFactorScreen::class.java) }
            rowAntiPhishing.setOnClickListener { navigateTo(AntiPhishingScreen::class.java) }
            rowWithdrawalWhitelist.setOnClickListener { navigateTo(WhitelistScreen::class.java) }
            rowDeviceManagement.setOnClickListener { navigateTo(DevicesScreen::class.java) }
            rowChangePassword.setOnClickListener { navigateTo(ChangePasswordScreen::class.java) }
            
            // Account Settings
            rowProfile.setOnClickListener { navigateTo(ProfileScreen::class.java) }
            rowKYC.setOnClickListener { navigateTo(KYCScreen::class.java) }
            rowPaymentMethods.setOnClickListener { navigateTo(PaymentMethodsScreen::class.java) }
            
            // Preferences
            rowNotifications.setOnClickListener { navigateTo(NotificationsSettingsScreen::class.java) }
            rowLanguage.setOnClickListener { /* Show language picker */ }
            rowCurrency.setOnClickListener { /* Show currency picker */ }
            
            // Other
            rowAPI.setOnClickListener { navigateTo(APIScreen::class.java) }
            rowAbout.setOnClickListener { navigateTo(AboutScreen::class.java) }
            rowHelp.setOnClickListener { navigateTo(HelpScreen::class.java) }
            rowLogout.setOnClickListener { logout() }
        }
    }
    
    private fun navigateTo(screen: Class<*>) {
        // Navigation code
    }
    
    private fun logout() {
        // Logout code
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}