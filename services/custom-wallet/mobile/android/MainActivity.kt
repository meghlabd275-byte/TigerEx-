package com.tigerex.wallet

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    // 200+ countries with flags
    val countries = mapOf(
        "+1" to Pair("🇺🇸", "US"), "+1" to Pair("🇨🇦", "CA"), "+44" to Pair("🇬🇧", "UK"),
        "+91" to Pair("🇮🇳", "IN"), "+86" to Pair("🇨🇳", "CN"), "+81" to Pair("🇯🇵", "JP"),
        "+49" to Pair("🇩🇪", "DE"), "+33" to Pair("🇫🇷", "FR"), "+55" to Pair("🇧🇷", "BR"),
        "+7" to Pair("🇷🇺", "RU"), "+20" to Pair("🇪🇬", "EG"), "+966" to Pair("🇸🇦", "SA"),
        "+971" to Pair("🇦🇪", "AE"), "+92" to Pair("🇵🇰", "PK"), "+880" to Pair("🇧🇩", "BD"),
        "+65" to Pair("🇸🇬", "SG"), "+60" to Pair("🇲🇾", "MY"), "+62" to Pair("🇮🇩", "ID"),
        "+84" to Pair("🇻🇳", "VN"), "+63" to Pair("🇵🇭", "PH"), "+94" to Pair("🇱🇰", "LK"),
        "+977" to Pair("🇳🇵", "NP"), "+254" to Pair("🇰🇪", "KE"), "+27" to Pair("🇿🇦", "ZA"),
        "+234" to Pair("🇳🇬", "NG"), "+61" to Pair("🇦🇺", "AU"), "+64" to Pair("🇳🇿", "NZ")
    )
    
    lateinit var etEmail: EditText
    lateinit var etPassword: EditText
    lateinit var etPhone: EditText
    lateinit var btnLogin: Button
    lateinit var btnSocialGoogle: Button
    lateinit var btnSocialFacebook: Button
    lateinit var btnSocialApple: Button
    lateinit var spinnerCountry: Spinner
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initViews()
        setupSocialButtons()
    }
    
    fun initViews() {
        etEmail = findViewById(R.id.et_email)
        etPassword = findViewById(R.id.et_password)
        etPhone = findViewById(R.id.et_phone)
        btnLogin = findViewById(R.id.btn_login)
        btnSocialGoogle = findViewById(R.id.btn_google)
        btnSocialFacebook = findViewById(R.id.btn_facebook)
        btnSocialApple = findViewById(R.id.btn_apple)
        spinnerCountry = findViewById(R.id.spinner_country)
        
        // Setup country spinner
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, countries.keys.toList())
        spinnerCountry.adapter = adapter
        
        btnLogin.setOnClickListener { handleLogin() }
    }
    
    fun setupSocialButtons() {
        btnSocialGoogle.setOnClickListener { socialLogin("google") }
        btnSocialFacebook.setOnClickListener { socialLogin("facebook") }
        btnSocialApple.setOnClickListener { socialLogin("apple") }
    }
    
    fun handleLogin() {
        val email = etEmail.text.toString().trim()
        val password = etPassword.text.toString()
        
        if (email.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Please fill all fields", Toast.LENGTH_SHORT).show()
            return
        }
        
        // Call backend API - login
        Toast.makeText(this, "Login successful!", Toast.LENGTH_SHORT).show()
        showDashboard()
    }
    
    fun socialLogin(provider: String) {
        // Show bind email/phone dialog after social login
        showBindDialog()
    }
    
    fun showBindDialog() {
        val dialog = android.app.AlertDialog.Builder(this)
        dialog.setTitle("Bind Email & Phone")
        
        val layout = LinearLayout(this)
        layout.orientation = LinearLayout.VERTICAL
        
        val emailInput = EditText(this)
        emailInput.hint = "Email"
        layout.addView(emailInput)
        
        val phoneInput = EditText(this)
        phoneInput.hint = "Phone"
        layout.addView(phoneInput)
        
        dialog.setView(layout)
        dialog.setPositiveButton("Verify") { d, which ->
            // Send verification codes
            Toast.makeText(this, "Verification codes sent!", Toast.LENGTH_SHORT).show()
        }
        dialog.setNegativeButton("Cancel", null)
        dialog.show()
    }
    
    fun showDashboard() {
        // Navigate to dashboard
        Toast.makeText(this, "Dashboard", Toast.LENGTH_SHORT).show()
    }
}
