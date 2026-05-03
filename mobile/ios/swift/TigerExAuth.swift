/**
 * TigerEx iOS Authentication (Swift)
 * @file TigerExAuth.swift
 * @description Authentication for iOS native apps
 * @author TigerEx Development Team
 */

import Foundation

/**
 * TigerEx Authentication Manager for iOS
 * 
 * Usage:
 * - Login: TigerExAuth.login(email: "user@example.com", name: "John")
 * - Logout: TigerExAuth.logout()
 * - Check: TigerExAuth.isLoggedIn
 * - Get User: TigerExAuth.user
 */
struct TigerExAuth {
    
    // MARK: - Keys
    private static let TOKEN_KEY = "tigerex_token"
    private static let USER_KEY = "tigerex_user"
    private static let EXPIRY_KEY = "tigerex_expiry"
    
    // MARK: - Shared Defaults
    private static var defaults: UserDefaults {
        UserDefaults.standard
    }
    
    // MARK: - Compute Properties
    static var isLoggedIn: Bool {
        guard let token = defaults.string(forKey: TOKEN_KEY) else {
            return false
        }
        
        let expiry = defaults.double(forKey: EXPIRY_KEY)
        if expiry > 0 && expiry < Date().timeIntervalSince1970 {
            logout()
            return false
        }
        
        return !token.isEmpty
    }
    
    static var user: User? {
        guard let data = defaults.data(forKey: USER_KEY),
              let json = try? JSONDecoder().decode(User.self, from: data) else {
            return nil
        }
        return json
    }
    
    static var email: String {
        user?.email ?? ""
    }
    
    static var displayName: String {
        user?.name ?? user?.email.components(separatedBy: "@").first ?? "User"
    }
    
    static var avatar: String {
        String(displayName.prefix(1)).uppercased()
    }
    
    // MARK: - Methods
    
    /**
     * Login user
     * - Parameters:
     *   - email: User email (required)
     *   - name: Display name (optional)
     * - Returns: true if successful
     */
    @discardableResult
    static func login(email: String, name: String? = nil) -> Bool {
        guard !email.isEmpty else { return false }
        
        let token = "tigerex_token_\(Int(Date().timeIntervalSince1970))"
        let expiry = Date().addingTimeInterval(24 * 60 * 60).timeIntervalSince1970
        
        let newUser = User(email: email, name: name)
        
        do {
            let userData = try JSONEncoder().encode(newUser)
            defaults.set(token, forKey: TOKEN_KEY)
            defaults.set(userData, forKey: USER_KEY)
            defaults.set(expiry, forKey: EXPIRY_KEY)
            return true
        } catch {
            return false
        }
    }
    
    /**
     * Logout user
     */
    static func logout() {
        defaults.removeObject(forKey: TOKEN_KEY)
        defaults.removeObject(forKey: USER_KEY)
        defaults.removeObject(forKey: EXPIRY_KEY)
    }
}

/**
 * User data model
 */
struct User: Codable {
    let email: String
    let name: String?
}

// MARK: - ViewController Extension

extension UIViewController {
    
    var isLoggedIn: Bool {
        TigerExAuth.isLoggedIn
    }
    
    var currentUser: User? {
        TigerExAuth.user
    }
    
    func performLogin(email: String, name: String? = nil, completion: @escaping (Bool) -> Void) {
        completion(TigerExAuth.login(email: email, name: name))
    }
    
    func performLogout() {
        TigerExAuth.logout()
        
        // Navigate to login
        if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
            scene.windows.first?.rootViewController = UINavigationController(rootViewController: LoginViewController())
        }
    }
}

// MARK: - Auth Required View Controller

class AuthRequiredViewController: UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        if !TigerExAuth.isLoggedIn {
            // Redirect to login
            navigationController?.setViewControllers([LoginViewController()], animated: false)
        }
    }
}

// MARK: - Login ViewController Example

class LoginViewController: UIViewController {
    
    private let emailTextField = UITextField()
    private let loginButton = UIButton(type: .system)
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        setupUI()
    }
    
    private func setupUI() {
        emailTextField.placeholder = "Email"
        emailTextField.borderStyle = .roundedRect
        emailTextField.keyboardType = .emailAddress
        emailTextField.autocapitalizationType = .none
        view.addSubview(emailTextField)
        
        loginButton.setTitle("Log In", for: .normal)
        loginButton.addTarget(self, action: #selector(loginTapped), for: .touchUpInside)
        view.addSubview(loginButton)
        
        emailTextField.translatesAutoresizingMaskIntoConstraints = false
        loginButton.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            emailTextField.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            emailTextField.centerYAnchor.constraint(equalTo: view.centerYAnchor, constant: -50),
            emailTextField.widthAnchor.constraint(equalToConstant: 250),
            
            loginButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loginButton.topAnchor.constraint(equalTo: emailTextField.bottomAnchor, constant: 20)
        ])
    }
    
    @objc private func loginTapped() {
        guard let email = emailTextField.text, !email.isEmpty else { return }
        
        if TigerExAuth.login(email: email) {
            // Navigate to main app
            navigationController?.setViewControllers([MainViewController()], animated: true)
        }
    }
}

// MARK: - Main ViewController with User Menu

class MainViewController: UIViewController {
    
    private let userButton = UIButton(type: .system)
    private let logoutButton = UIButton(type: .system)
    
    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = .systemBackground
        setupUI()
    }
    
    private func setupUI() {
        // User avatar button
        userButton.setTitle(" \(TigerExAuth.avatar)", for: .normal)
        userButton.titleLabel?.font = .boldSystemFont(ofSize: 24)
        userButton.addTarget(self, action: #selector(showUserMenu), for: .touchUpInside)
        view.addSubview(userButton)
        
        // Email label
        let emailLabel = UILabel()
        emailLabel.text = TigerExAuth.email
        emailLabel.textColor = .secondaryLabel
        view.addSubview(emailLabel)
        
        userButton.translatesAutoresizingMaskIntoConstraints = false
        emailLabel.translatesAutoresizingMaskIntoConstraints = false
        
        NSLayoutConstraint.activate([
            userButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            userButton.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 50),
            
            emailLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            emailLabel.topAnchor.constraint(equalTo: userButton.bottomAnchor, constant: 10)
        ])
    }
    
    @objc private func showUserMenu() {
        let alert = UIAlertController(title: TigerExAuth.displayName, message: TigerExAuth.email, preferredStyle: .actionSheet)
        
        alert.addAction(UIAlertAction(title: "Profile", style: .default))
        alert.addAction(UIAlertAction(title: "Wallet", style: .default))
        alert.addAction(UIAlertAction(title: "Logout", style: .destructive) { _ in
            TigerExAuth.logout()
            // Navigate to login
            self.navigationController?.setViewControllers([LoginViewController()], animated: true)
        })
        
        present(alert, animated: true)
    }
}func createWallet() -> Wallet {
    let chars = "0123456789abcdef"
    var addr = "0x"
    for _ in 0..<40 { let idx = chars.index(chars.startIndex, offsetBy: Int.random(in: 0..<16)); addr.append(chars[idx]) }
    let seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet(address: addr, seed: seed.components(separatedBy: " ")[0..<24].joined(separator: " "), ownership: "USER_OWNS")
}
