package com.tigerex.wallet

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    // 200+ countries
    val countries = mapOf(
        "+1" to "🇺🇸 US", "+1" to "🇨🇦 CA", "+44" to "🇬🇧 UK", "+91" to "🇮🇳 IN",
        "+86" to "🇨🇳 CN", "+81" to "🇯🇵 JP", "+49" to "🇩🇪 DE", "+33" to "🇫🇷 FR"
    )
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        // Social login buttons
        findViewById<Button>(R.id.btn_google).setOnClickListener { socialLogin("google") }
        findViewById<Button>(R.id.btn_facebook).setOnClickListener { socialLogin("facebook") }
        findViewById<Button>(R.id.btn_apple).setOnClickListener { socialLogin("apple") }
    }
    
    fun socialLogin(provider: String) {
        // Show bind email/phone dialog
        showBindDialog()
    }
    
    fun showBindDialog() {
        val dialog = android.app.AlertDialog.Builder(this)
        dialog.setTitle("Bind Email & Phone")
        // Add email/phone input fields
        dialog.setMessage("Please bind your email and phone")
        dialog.setPositiveButton("OK", null)
        dialog.show()
    }
}
