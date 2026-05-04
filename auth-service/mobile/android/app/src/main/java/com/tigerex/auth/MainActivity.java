package com.tigerex.auth;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import android.content.Intent;

public class MainActivity extends Activity {

    private EditText etEmail, etPhone, etPassword, etConfirmPassword, etCode;
    private Button btnSubmit, btnSocialGoogle, btnSocialFacebook, btnSocialTwitter, btnSocialApple;
    private CheckBox chkStayLogged, chkTerms;
    private TextView tvTitle, tvForgotPassword, tvSwitchToLogin, tvSwitchToRegister;
    private Spinner spinnerCountry;
    
    private int currentView = 0; // 0=login, 1=register
    
    // Countries (200+)
    String[] countryCodes = {"+1", "+1", "+44", "+91", "+86", "+81", "+49", "+33", "+55", "+7", "+20", "+966", "+971", "+92", "+880", "+65", "+60", "+62", "+84", "+63", "+94", "+977", "+254", "+27", "+234", "+61", "+64"};
    String[] countryFlags = {"🇺🇸", "🇨🇦", "🇬🇧", "🇮🇳", "🇨🇳", "🇯🇵", "🇩🇪", "🇫🇷", "🇧🇷", "🇷🇺", "🇪🇬", "🇸🇦", "🇦🇪", "🇵🇰", "🇧🇩", "🇸🇬", "🇲🇾", "🇮🇩", "🇻🇳", "🇵🇭", "🇱🇰", "🇳🇵", "🇰🇪", "🇿🇦", "🇳🇬", "🇦🇺", "🇳🇿"};

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        showLoginView();
    }
    
    // ==================== LOGIN VIEW ====================
    private void showLoginView() {
        setContentView(R.layout.login);
        
        etEmail = findViewById(R.id.et_email);
        etPassword = findViewById(R.id.et_password);
        etCode = findViewById(R.id.et_code);
        btnSubmit = findViewById(R.id.btn_submit);
        chkStayLogged = findViewById(R.id.chk_stay_logged);
        tvForgotPassword = findViewById(R.id.tv_forgot_password);
        tvSwitchToLogin = findViewById(R.id.tv_switch);
        btnSocialGoogle = findViewById(R.id.btn_google);
        btnSocialFacebook = findViewById(R.id.btn_facebook);
        btnSocialTwitter = findViewById(R.id.btn_twitter);
        btnSocialApple = findViewById(R.id.btn_apple);
        
        tvSwitchToLogin.setText("Don't have an account? Sign Up");
        tvSwitchToLogin.setOnClickListener(v -> showRegisterView());
        
        btnSubmit.setOnClickListener(v -> handleLogin());
        tvForgotPassword.setOnClickListener(v -> showForgotPassword());
        
        btnSocialGoogle.setOnClickListener(v -> socialLogin("google"));
        btnSocialFacebook.setOnClickListener(v -> socialLogin("facebook"));
        btnSocialTwitter.setOnClickListener(v -> socialLogin("twitter"));
        btnSocialApple.setOnClickListener(v -> socialLogin("apple"));
        
        currentView = 0;
    }
    
    // ==================== REGISTER VIEW ====================
    private void showRegisterView() {
        setContentView(R.layout.register);
        
        etEmail = findViewById(R.id.et_email);
        etPhone = findViewById(R.id.et_phone);
        etPassword = findViewById(R.id.et_password);
        etConfirmPassword = findViewById(R.id.et_confirm_password);
        btnSubmit = findViewById(R.id.btn_submit);
        chkTerms = findViewById(R.id.chk_terms);
        tvSwitchToLogin = findViewById(R.id.tv_switch);
        spinnerCountry = findViewById(R.id.spinner_country);
        
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, countryFlags);
        spinnerCountry.setAdapter(adapter);
        
        tvSwitchToLogin.setText("Already have an account? Login");
        tvSwitchToLogin.setOnClickListener(v -> showLoginView());
        
        btnSubmit.setOnClickListener(v -> handleRegister());
        
        currentView = 1;
    }
    
    // ==================== FORGOT PASSWORD ====================
    private void showForgotPassword() {
        setContentView(R.layout.forgot_password);
        
        etEmail = findViewById(R.id.et_email);
        btnSubmit = findViewById(R.id.btn_submit);
        tvSwitchToLogin = findViewById(R.id.tv_back);
        
        tvSwitchToLogin.setOnClickListener(v -> showLoginView());
        btnSubmit.setOnClickListener(v -> handleForgotPassword());
    }
    
    // ==================== BIND EMAIL/PHONE ====================
    private void showBindView() {
        setContentView(R.layout.bind);
        
        etEmail = findViewById(R.id.et_email);
        etPhone = findViewById(R.id.et_phone);
        btnSubmit = findViewById(R.id.btn_bind_email);
        
        btnSubmit.setOnClickListener(v -> sendBindCode("email"));
    }
    
    // ==================== DASHBOARD ====================
    private void showDashboard() {
        setContentView(R.layout.dashboard);
        
        btnSubmit = findViewById(R.id.btn_logout);
        
        btnSubmit.setOnClickListener(v -> {
            showToast("Logged out");
            showLoginView();
        });
    }
    
    // ==================== HANDLERS ====================
    private void handleLogin() {
        String identifier = etEmail.getText().toString().trim();
        String password = etPassword.getText().toString();
        
        if (identifier.isEmpty() || password.isEmpty()) {
            showToast("Please fill all fields");
            return;
        }
        
        // Check if user exists
        if (!checkUserExists(identifier)) {
            showToast("User not found. Please register.");
            showRegisterView();
            return;
        }
        
        // Check 2FA if enabled
        if (is2FAEnabled(identifier)) {
            // Show 2FA input
            showToast("Enter 2FA code");
            return;
        }
        
        showToast("Login successful!");
        showDashboard();
    }
    
    private void handleRegister() {
        String email = etEmail.getText().toString().trim();
        String phone = getSelectedCountryCode() + etPhone.getText().toString().trim();
        String password = etPassword.getText().toString();
        String confirm = etConfirmPassword.getText().toString();
        
        if (email.isEmpty() || phone.isEmpty() || password.isEmpty()) {
            showToast("Please fill all fields");
            return;
        }
        
        if (!password.equals(confirm)) {
            showToast("Passwords do not match");
            return;
        }
        
        // Check if user exists
        if (checkUserExists(email)) {
            showToast("User already exists. Please login.");
            showLoginView();
            return;
        }
        
        if (!chkTerms.isChecked()) {
            showToast("Accept terms and conditions");
            return;
        }
        
        // Send verification codes
        sendVerificationCode(email, "email");
        sendVerificationCode(phone, "phone");
        
        showToast("Verification codes sent!");
    }
    
    private void handleForgotPassword() {
        String identifier = etEmail.getText().toString().trim();
        
        if (identifier.isEmpty()) {
            showToast("Enter email or phone");
            return;
        }
        
        if (!checkUserExists(identifier)) {
            showToast("User not found. Please register.");
            showRegisterView();
            return;
        }
        
        // Send verification codes
        sendVerificationCode(identifier, "email");
        sendVerificationCode(identifier, "phone");
        
        // Check 2FA
        if (is2FAEnabled(identifier)) {
            showToast("Enter 2FA code");
            return;
        }
        
        // Live verification
        showToast("Live verification required");
    }
    
    private void socialLogin(String provider) {
        showToast("Login with " + provider + "...");
        // In production: use OAuth SDK
        showBindView();
    }
    
    private void sendBindCode(String type) {
        showToast(type.toUpperCase() + " code sent!");
    }
    
    // ==================== HELPERS ====================
    private boolean checkUserExists(String identifier) {
        // Call backend API
        return false;
    }
    
    private boolean is2FAEnabled(String identifier) {
        // Call backend API
        return false;
    }
    
    private void sendVerificationCode(String identifier, String type) {
        int code = 100000 + (int)(Math.random() * 900000);
        showToast(type.toUpperCase() + " code: " + code);
    }
    
    private String getSelectedCountryCode() {
        int pos = spinnerCountry.getSelectedItemPosition();
        return countryCodes[pos];
    }
    
    private void showToast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }
}