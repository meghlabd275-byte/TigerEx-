import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    
    var window: UIWindow?
    
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        
        // Initialize theme
        ThemeManager.shared.initialize()
        
        // Initialize user defaults
        UserDefaultsManager.shared.initialize()
        
        // Check login status
        if UserDefaultsManager.shared.isLoggedIn() {
            showMainApp()
        } else {
            showLogin()
        }
        
        return true
    }
    
    func showMainApp() {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        window?.rootViewController = storyboard.instantiateInitialViewController()
    }
    
    func showLogin() {
        let storyboard = UIStoryboard(name: "Login", bundle: nil)
        window?.rootViewController = storyboard.instantiateInitialViewController()
    }
}

// MARK: - Theme Manager
class ThemeManager {
    static let shared = ThemeManager()
    
    private let themeKey = "tigerex_theme"
    private let themeLight = "light"
    private let themeDark = "dark"
    
    func initialize() {
        let theme = UserDefaults.standard.string(forKey: themeKey) ?? themeDark
        applyTheme(theme)
    }
    
    func setTheme(_ theme: String) {
        UserDefaults.standard.set(theme, forKey: themeKey)
        applyTheme(theme)
    }
    
    func isDarkMode() -> Bool {
        return UserDefaults.standard.string(forKey: themeKey) != themeLight
    }
    
    private func applyTheme(_ theme: String) {
        if theme == themeLight {
            UIApplication.shared.windows.forEach { window in
                window.overrideUserInterfaceStyle = .light
            }
        } else {
            UIApplication.shared.windows.forEach { window in
                window.overrideUserInterfaceStyle = .dark
            }
        }
    }
}

// MARK: - User Defaults Manager
class UserDefaultsManager {
    static let shared = UserDefaultsManager()
    
    private let tokenKey = "auth_token"
    private let userIdKey = "user_id"
    private let userRoleKey = "user_role"
    private let vipLevelKey = "vip_level"
    private let themeKey = "tigerex_theme"
    
    func initialize() {
        // Set defaults
        if UserDefaults.standard.string(forKey: themeKey) == nil {
            UserDefaults.standard.set("dark", forKey: themeKey)
        }
    }
    
    // Auth
    var isLoggedIn: Bool {
        return UserDefaults.standard.string(forKey: tokenKey) != nil
    }
    
    func saveAuth(token: String, userId: String, role: String) {
        UserDefaults.standard.set(token, forKey: tokenKey)
        UserDefaults.standard.set(userId, forKey: userIdKey)
        UserDefaults.standard.set(role, forKey: userRoleKey)
    }
    
    func logout() {
        UserDefaults.standard.removeObject(forKey: tokenKey)
        UserDefaults.standard.removeObject(forKey: userIdKey)
        UserDefaults.standard.removeObject(forKey: userRoleKey)
    }
    
    func getUserId() -> String? {
        return UserDefaults.standard.string(forKey: userIdKey)
    }
    
    func getUserRole() -> String? {
        return UserDefaults.standard.string(forKey: userRoleKey)
    }
    
    func getAuthToken() -> String? {
        return UserDefaults.standard.string(forKey: tokenKey)
    }
    
    // VIP
    var vipLevel: Int {
        get { UserDefaults.standard.integer(forKey: vipLevelKey) }
        set { UserDefaults.standard.set(newValue, forKey: vipLevelKey) }
    }
    
    var isVip: Bool {
        return vipLevel > 0
    }
}

// MARK: - User Roles
enum UserRole: String {
    case admin = "admin"
    case moderator = "moderator"
    case trader = "trader"
    case user = "user"
    case partner = "partner"
    case institutional = "institutional"
    
    static func canAccess(role: String, feature: String) -> Bool {
        switch role {
        case "admin": return true
        case "moderator": return ["trade", "earn", "wallet", "admin", "users"].contains(feature)
        case "trader": return ["trade", "futures", "margin", "wallet", "earn"].contains(feature)
        case "partner": return ["affiliate", "referral", "partner"].contains(feature)
        case "institutional": return ["custody", "api", "whitelabel", "institutional"].contains(feature)
        default: return ["trade", "wallet", "earn", "nft"].contains(feature)
        }
    }
}

// MARK: - VIP Levels
enum VipLevel: Int {
    case normal = 0
    case bronze = 1
    case silver = 2
    case gold = 3
    case platinum = 4
    case diamond = 5
    
    var discount: Double {
        switch self {
        case .bronze: return 0.10
        case .silver: return 0.20
        case .gold: return 0.30
        case .platinum: return 0.40
        case .diamond: return 0.50
        default: return 0.0
        }
    }
    
    var makerFee: Double {
        switch self {
        case .bronze: return 0.0008
        case .silver: return 0.0006
        case .gold: return 0.0004
        case .platinum: return 0.0002
        case .diamond: return 0.0
        default: return 0.0010
        }
    }
    
    var takerFee: Double {
        switch self {
        case .bronze: return 0.0016
        case .silver: return 0.0012
        case .gold: return 0.0008
        case .platinum: return 0.0004
        case .diamond: return 0.0
        default: return 0.0020
        }
    }
}