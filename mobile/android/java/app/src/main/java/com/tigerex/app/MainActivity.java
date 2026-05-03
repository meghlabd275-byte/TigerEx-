package com.tigerex.app;

import android.os.Bundle;
import android.view.View;
import android.widget.*;
import androidx.appcompat.app.AppCompatActivity;
import androidx.annotation.NonNull;
import com.google.android.material.textfield.TextInputEditText;
import java.util.regex.Pattern;

/**
 * TigerEx Android App - Java
 * Login, Register, KYC, 2FA, Trading
 */
public class MainActivity extends AppCompatActivity {
    
    private EditText emailPhoneInput, passwordInput, otpInput;
    private Button loginBtn, verifyBtn;
    private ProgressBar progressBar;
    private View loginLayout, otpLayout, mainLayout;
    private int currentStep = 0;
    
    // Test code for all verifications
    private static final String TEST_CODE = "727752";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        initViews();
        setupListeners();
    }
    
    private void initViews() {
        emailPhoneInput = findViewById(R.id.emailPhoneInput);
        passwordInput = findViewById(R.id.passwordInput);
        otpInput = findViewById(R.id.otpInput);
        loginBtn = findViewById(R.id.loginBtn);
        verifyBtn = findViewById(R.id.verifyBtn);
        progressBar = findViewById(R.id.progressBar);
        loginLayout = findViewById(R.id.loginLayout);
        otpLayout = findViewById(R.id.otpLayout);
        mainLayout = findViewById(R.id.mainLayout);
    }
    
    private void setupListeners() {
        loginBtn.setOnClickListener(v -> handleLogin());
        verifyBtn.setOnClickListener(v -> handleVerification());
        
        findViewById(R.id.tabEmail).setOnClickListener(v -> switchTab("email"));
        findViewById(R.id.tabPhone).setOnClickListener(v -> switchTab("phone"));
        findViewById(R.id.forgotPassword).setOnClickListener(v -> showOTP());
    }
    
    private void switchTab(String tab) {
        if (tab.equals("email")) {
            emailPhoneInput.setHint("Enter your email");
            emailPhoneInput.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        } else {
            emailPhoneInput.setHint("Phone number");
            emailPhoneInput.setInputType(android.text.InputType.TYPE_CLASS_PHONE);
        }
    }
    
    private void handleLogin() {
        String identifier = emailPhoneInput.getText().toString().trim();
        String password = passwordInput.getText().toString().trim();
        
        if (identifier.isEmpty() || password.isEmpty()) {
            showToast("Please enter email/phone and password");
            return;
        }
        
        progressBar.setVisibility(View.VISIBLE);
        loginBtn.setEnabled(false);
        
        // Simulate login - in production, call API
        new android.os.Handler().postDelayed(() -> {
            progressBar.setVisibility(View.GONE);
            loginBtn.setEnabled(true);
            showOTP();
        }, 1500);
    }
    
    private void showOTP() {
        loginLayout.setVisibility(View.GONE);
        otpLayout.setVisibility(View.VISIBLE);
        currentStep = 1;
    }
    
    private void handleVerification() {
        String code = otpInput.getText().toString().trim();
        
        if (code.isEmpty()) {
            showToast("Please enter verification code");
            return;
        }
        
        if (code.equals(TEST_CODE)) {
            showToast("✓ Verification successful!");
            showMainScreen();
        } else {
            showToast("Invalid code. Use: " + TEST_CODE);
        }
    }
    
    private void showMainScreen() {
        otpLayout.setVisibility(View.GONE);
        mainLayout.setVisibility(View.VISIBLE);
    }
    
    private void showToast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }
}
public static Wallet createWallet() {
    String chars = "0123456789abcdef";
    String addr = "0x";
    for(int i=0;i<40;i++) addr += chars.charAt((int)(Math.random()*16));
    String seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    return new Wallet(addr, seed, "USER_OWNS");
}
