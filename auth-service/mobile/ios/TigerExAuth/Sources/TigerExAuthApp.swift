import SwiftUI
import FirebaseAuth
import GoogleSignIn
import FacebookLogin

struct TigerExAuthApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

// ==================== CONTENT VIEW ====================
struct ContentView: View {
    @State private var currentView = "login"
    
    var body: some View {
        Group {
            switch currentView {
            case "login": LoginView(onLoginSuccess: { currentView = "dashboard" }, onSwitch: { currentView = "register" })
            case "register": RegisterView(onRegisterSuccess: { currentView = "verify" }, onSwitch: { currentView = "login" })
            case "verify": VerificationView()
            case "bind": BindEmailPhoneView(onBindSuccess: { currentView = "dashboard" })
            case "dashboard": DashboardView(onLogout: { currentView = "login" })
            case "forgot": ForgotPasswordView(onSwitch: { currentView = "login" })
            default: LoginView(onLoginSuccess: {}, onSwitch: {})
            }
        }
        .preferredColorScheme(.dark)
    }
}

// ==================== LOGIN VIEW ====================
struct LoginView: View {
    var onLoginSuccess: () -> Void
    var onSwitch: () -> Void
    
    @State private var email = ""
    @State private var password = ""
    @State private var stayLogged = false
    @State private var showPassword = false
    @State private var showToast = false
    @State private var toastMessage = ""
    
    var body: some View {
        VStack(spacing: 20) {
            // Logo
            Text("🐯 TigerEx")
                .font(.system(size: 40, weight: .bold))
                .foregroundColor(.yellow)
            
            Text("Welcome Back")
                .font(.title2)
                .foregroundColor(.white)
            
            // Social Login
            HStack(spacing: 12) {
                SocialButton(icon: "g", color: .red) { socialLogin("google") }
                SocialButton(icon: "f", color: .blue) { socialLogin("facebook") }
                SocialButton(icon: "X", color: .black) { socialLogin("twitter") }
                SocialButton(icon: "🍎", color: .gray) { socialLogin("apple") }
            }
            
            Text("or")
                .foregroundColor(.gray)
            
            // Email/Phone
            VStack(alignment: .leading) {
                Text("Email or Phone")
                    .foregroundColor(.gray)
                    .font(.caption)
                TextField("Enter email or phone", text: $email)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .foregroundColor(.white)
            }
            
            // Password
            VStack(alignment: .leading) {
                Text("Password")
                    .foregroundColor(.gray)
                    .font(.caption)
                HStack {
                    SecureField("Enter password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .foregroundColor(.white)
                    Button(action: { showPassword.toggle() }) {
                        Image(systemName: showPassword ? "eye.slash" : "eye")
                            .foregroundColor(.gray)
                    }
                }
            }
            
            // Stay logged & Forgot
            HStack {
                Toggle("Stay logged in (30 days)", isOn: $stayLogged)
                    .foregroundColor(.gray)
                    .font(.caption)
                Spacer()
                Button("Forgot Password?") {
                    // Show forgot password
                }
                .foregroundColor(.yellow)
                .font(.caption)
            }
            
            // Login Button
            Button(action: handleLogin) {
                Text("Login")
                    .font(.headline)
                    .foregroundColor(.black)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.yellow)
                    .cornerRadius(10)
            }
            
            // Switch
            Button(action: onSwitch) {
                HStack {
                    Text("Don't have an account? ")
                    Text("Sign Up")
                        .foregroundColor(.yellow)
                }
            }
            .foregroundColor(.gray)
        }
        .padding()
        .background(Color.gray.opacity(0.2))
        .cornerRadius(20)
        .alert(toastMessage, isPresented: $showToast) {
            Button("OK", role: .cancel) {}
        }
    }
    
    func handleLogin() {
        if email.isEmpty || password.isEmpty {
            toastMessage = "Please fill all fields"
            showToast = true
            return
        }
        
        // Check user exists
        if !checkUserExists(email) {
            toastMessage = "User not found. Please register."
            showToast = true
            return
        }
        
        // Check 2FA
        if is2FAEnabled(email) {
            toastMessage = "Enter 2FA code"
            showToast = true
            return
        }
        
        toastMessage = "Login successful!"
        showToast = true
        onLoginSuccess()
    }
    
    func socialLogin(_ provider: String) {
        toastMessage = "Login with \(provider)..."
        showToast = true
        // In production: use OAuth SDK
        onLoginSuccess()
    }
}

struct SocialButton: View {
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(icon)
                .font(.system(size: 20))
                .foregroundColor(.white)
                .frame(width: 50, height: 50)
                .background(color)
                .clipShape(Circle())
        }
    }
}

// ==================== REGISTER VIEW ====================
struct RegisterView: View {
    var onRegisterSuccess: () -> Void
    var onSwitch: () -> Void
    
    @State private var email = ""
    @State private var phone = ""
    @State private var countryCode = "+1"
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var agreeTerms = false
    @State private var showToast = false
    @State private var toastMessage = ""
    
    let countries = [
        ("+1", "🇺🇸", "US"),
        ("+1", "🇨🇦", "CA"),
        ("+44", "🇬🇧", "UK"),
        ("+91", "🇮🇳", "IN"),
        ("+86", "🇨🇳", "CN"),
        ("+81", "🇯🇵", "JP"),
        ("+49", "🇩🇪", "DE"),
        ("+33", "🇫🇷", "FR"),
    ]
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                Text("Create Account")
                    .font(.title2)
                    .foregroundColor(.white)
                
                // Social Register
                HStack(spacing: 12) {
                    SocialButton(icon: "g", color: .red) {}
                    SocialButton(icon: "f", color: .blue) {}
                    SocialButton(icon: "X", color: .black) {}
                    SocialButton(icon: "🍎", color: .gray) {}
                }
                
                Text("or")
                    .foregroundColor(.gray)
                
                // Email
                VStack(alignment: .leading) {
                    Text("Email")
                        .foregroundColor(.gray)
                        .font(.caption)
                    TextField("your@email.com", text: $email)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                // Phone
                VStack(alignment: .leading) {
                    Text("Phone")
                        .foregroundColor(.gray)
                        .font(.caption)
                    HStack {
                        Picker("Country", selection: $countryCode) {
                            ForEach(countries, id: \.0) { country in
                                Text(country.1 + " " + country.0).tag(country.0)
                            }
                        }
                        .pickerStyle(MenuPickerStyle())
                        .frame(width: 80)
                        
                        TextField("Phone number", text: $phone)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                    }
                }
                
                // Password
                VStack(alignment: .leading) {
                    Text("Password")
                        .foregroundColor(.gray)
                        .font(.caption)
                    SecureField("Create password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                // Confirm Password
                VStack(alignment: .leading) {
                    Text("Confirm Password")
                        .foregroundColor(.gray)
                        .font(.caption)
                    SecureField("Confirm password", text: $confirmPassword)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                // Terms
                Toggle(isOn: $agreeTerms) {
                    Text("I agree to TigerEx Terms & Conditions")
                        .font(.caption)
                        .foregroundColor(.gray)
                }
                
                // Register Button
                Button(action: handleRegister) {
                    Text("Continue")
                        .font(.headline)
                        .foregroundColor(.black)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.yellow)
                        .cornerRadius(10)
                }
                
                // Switch
                Button(action: onSwitch) {
                    HStack {
                        Text("Already have an account? ")
                        Text("Login")
                            .foregroundColor(.yellow)
                    }
                }
                .foregroundColor(.gray)
            }
            .padding()
        }
        .background(Color.gray.opacity(0.2))
        .cornerRadius(20)
    }
    
    func handleRegister() {
        if email.isEmpty || phone.isEmpty || password.isEmpty {
            toastMessage = "Please fill all fields"
            showToast = true
            return
        }
        
        if password != confirmPassword {
            toastMessage = "Passwords do not match"
            showToast = true
            return
        }
        
        if checkUserExists(email) {
            toastMessage = "User already exists. Login."
            showToast = true
            onSwitch()
            return
        }
        
        if !agreeTerms {
            toastMessage = "Accept terms"
            showToast = true
            return
        }
        
        // Send verification codes
        sendVerificationCode(email, "email")
        sendVerificationCode(phone, "phone")
        
        toastMessage = "Verification codes sent!"
        showToast = true
        onRegisterSuccess()
    }
}

// ==================== VERIFICATION VIEW ====================
struct VerificationView: View {
    @State private var emailCode = ""
    @State private var phoneCode = ""
    @State private var showToast = false
    @State private var toastMessage = ""
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Verify Your Account")
                .font(.title2)
                .foregroundColor(.white)
            
            // Phone Verification
            VStack {
                Text("Phone Verification")
                    .foregroundColor(.yellow)
                TextField("Enter 6-digit code", text: $phoneCode)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .keyboardType(.numberPad)
                Button("Verify Phone") {
                    verifyCode(phoneCode, "phone")
                }
            }
            
            // Email Verification
            VStack {
                Text("Email Verification")
                    .foregroundColor(.yellow)
                TextField("Enter 6-digit code", text: $emailCode)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                Button("Verify Email") {
                    verifyCode(emailCode, "email")
                }
            }
        }
        .padding()
        .background(Color.gray.opacity(0.2))
        .cornerRadius(20)
    }
    
    func verifyCode(_ code: String, _ type: String) {
        if code.count == 6 {
            toastMessage = type.capitalized + " verified!"
            showToast = true
        }
    }
}

// ==================== BIND EMAIL/PHONE ====================
struct BindEmailPhoneView: View {
    var onBindSuccess: () -> Void
    
    @State private var email = ""
    @State private var phone = ""
    @State private var code = ""
    @State private var showToast = false
    @State private var toastMessage = ""
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Complete Your Profile")
                .font(.title2)
                .foregroundColor(.white)
            
            Text("Please bind your email and phone")
                .foregroundColor(.gray)
            
            TextField("Email", text: $email)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            
            Button("Send Email Code") {
                toastMessage = "Email code sent!"
                showToast = true
            }
            
            TextField("Email code", text: $code)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            
            TextField("Phone", text: $phone)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            
            Button("Send Phone Code") {
                toastMessage = "Phone code sent!"
                showToast = true
            }
            
            Button("Verify & Continue") {
                onBindSuccess()
            }
            .foregroundColor(.yellow)
        }
        .padding()
    }
}

// ==================== DASHBOARD ====================
struct DashboardView: View {
    var onLogout: () -> Void
    
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "person.circle.fill")
                .resizable()
                .frame(width: 80, height: 80)
                .foregroundColor(.yellow)
            
            Text("My Account")
                .font(.title)
                .foregroundColor(.white)
            
            VStack(alignment: .leading, spacing: 16) {
                DashboardRow(icon: "envelope", title: "Email", value: "user@example.com")
                DashboardRow(icon: "phone", title: "Phone", value: "+1234567890")
                DashboardRow(icon: "shield", title: "2FA", value: "Disabled")
                DashboardRow(icon: "idcard", title: "KYC", value: "Not Verified")
            }
            
            Button("Logout", action: onLogout)
                .foregroundColor(.red)
        }
        .padding()
    }
}

struct DashboardRow: View {
    let icon: String
    let title: String
    let value: String
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.yellow)
            Text(title)
                .foregroundColor(.gray)
            Spacer()
            Text(value)
                .foregroundColor(.white)
        }
        .padding()
        .background(Color.gray.opacity(0.2))
        .cornerRadius(10)
    }
}

// ==================== FORGOT PASSWORD ====================
struct ForgotPasswordView: View {
    var onSwitch: () -> Void
    
    @State private var identifier = ""
    
    var body: some View {
        VStack(spacing: 20) {
            Button(action: onSwitch) {
                Image(systemName: "arrow.left")
                    .foregroundColor(.gray)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            
            Text("Reset Password")
                .font(.title2)
                .foregroundColor(.white)
            
            TextField("Email or Phone", text: $identifier)
                .textFieldStyle(RoundedBorderTextFieldStyle())
            
            Button("Continue") {
                // Handle forgot password
            }
            .foregroundColor(.yellow)
        }
        .padding()
    }
}

// ==================== HELPERS ====================
func checkUserExists(_ identifier: String) -> Bool {
    // Call backend API
    return false
}

func is2FAEnabled(_ identifier: String) -> Bool {
    // Call backend API
    return false
}

func sendVerificationCode(_ identifier: String, _ type: String) {
    // Call backend API - returns 6-digit code
}

#Preview {
    ContentView()
}