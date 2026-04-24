package com.tigerex.app

import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

/**
 * TigerEx Android App - Kotlin
 * Login, Register, KYC, 2FA, Trading
 */
class MainActivity : AppCompatActivity() {

    private lateinit var emailPhoneInput: EditText
    private lateinit var passwordInput: EditText
    private lateinit var otpInput: EditText
    private lateinit var loginBtn: Button
    private lateinit var verifyBtn: Button
    private lateinit var progressBar: ProgressBar
    private lateinit var loginLayout: LinearLayout
    private lateinit var otpLayout: LinearLayout
    private lateinit var mainLayout: LinearLayout

    companion object {
        const val TEST_CODE = "727752"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        initViews()
        setupListeners()
    }

    private fun initViews() {
        emailPhoneInput = findViewById(R.id.emailPhoneInput)
        passwordInput = findViewById(R.id.passwordInput)
        otpInput = findViewById(R.id.otpInput)
        loginBtn = findViewById(R.id.loginBtn)
        verifyBtn = findViewById(R.id.verifyBtn)
        progressBar = findViewById(R.id.progressBar)
        loginLayout = findViewById(R.id.loginLayout)
        otpLayout = findViewById(R.id.otpLayout)
        mainLayout = findViewById(R.id.mainLayout)
    }

    private fun setupListeners() {
        loginBtn.setOnClickListener { handleLogin() }
        verifyBtn.setOnClickListener { handleVerification() }

        findViewById<Button>(R.id.tabEmail).setOnClickListener { switchTab("email") }
        findViewById<Button>(R.id.tabPhone).setOnClickListener { switchTab("phone") }
        findViewById<TextView>(R.id.forgotPassword).setOnClickListener { showOTP() }
    }

    private fun switchTab(tab: String) {
        when (tab) {
            "email" -> {
                emailPhoneInput.hint = "Enter your email"
                emailPhoneInput.inputType = android.text.InputType.TYPE_CLASS_TEXT or 
                    android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS
            }
            "phone" -> {
                emailPhoneInput.hint = "Phone number"
                emailPhoneInput.inputType = android.text.InputType.TYPE_CLASS_PHONE
            }
        }
    }

    private fun handleLogin() {
        val identifier = emailPhoneInput.text.toString().trim()
        val password = passwordInput.text.toString().trim()

        if (identifier.isEmpty() || password.isEmpty()) {
            showToast("Please enter email/phone and password")
            return
        }

        progressBar.visibility = View.VISIBLE
        loginBtn.isEnabled = false

        // Simulate login API call
        android.os.Handler(mainLooper).postDelayed({
            progressBar.visibility = View.GONE
            loginBtn.isEnabled = true
            showOTP()
        }, 1500)
    }

    private fun showOTP() {
        loginLayout.visibility = View.GONE
        otpLayout.visibility = View.VISIBLE
    }

    private fun handleVerification() {
        val code = otpInput.text.toString().trim()

        if (code.isEmpty()) {
            showToast("Please enter verification code")
            return
        }

        if (code == TEST_CODE) {
            showToast("✓ Verification successful!")
            showMainScreen()
        } else {
            showToast("Invalid code. Use: $TEST_CODE")
        }
    }

    private fun showMainScreen() {
        otpLayout.visibility = View.GONE
        mainLayout.visibility = View.VISIBLE
    }

    private fun showToast(message: String) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
    }
}
