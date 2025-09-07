import SwiftUI
import Firebase
import UserNotifications

@main
struct TigerExApp: App {
    @StateObject private var appState = AppState()
    @StateObject private var authManager = AuthenticationManager()
    @StateObject private var tradingManager = TradingManager()
    @StateObject private var portfolioManager = PortfolioManager()
    @StateObject private var notificationManager = NotificationManager()
    @StateObject private var biometricManager = BiometricManager()
    @StateObject private var themeManager = ThemeManager()
    
    init() {
        // Configure Firebase
        FirebaseApp.configure()
        
        // Configure appearance
        configureAppearance()
        
        // Request notification permissions
        requestNotificationPermissions()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .environmentObject(authManager)
                .environmentObject(tradingManager)
                .environmentObject(portfolioManager)
                .environmentObject(notificationManager)
                .environmentObject(biometricManager)
                .environmentObject(themeManager)
                .preferredColorScheme(themeManager.colorScheme)
                .onAppear {
                    setupApp()
                }
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)) { _ in
                    handleAppBecomeActive()
                }
                .onReceive(NotificationCenter.default.publisher(for: UIApplication.willResignActiveNotification)) { _ in
                    handleAppWillResignActive()
                }
        }
    }
    
    private func configureAppearance() {
        // Configure navigation bar appearance
        let navBarAppearance = UINavigationBarAppearance()
        navBarAppearance.configureWithOpaqueBackground()
        navBarAppearance.backgroundColor = UIColor.systemBackground
        navBarAppearance.titleTextAttributes = [.foregroundColor: UIColor.label]
        navBarAppearance.largeTitleTextAttributes = [.foregroundColor: UIColor.label]
        
        UINavigationBar.appearance().standardAppearance = navBarAppearance
        UINavigationBar.appearance().compactAppearance = navBarAppearance
        UINavigationBar.appearance().scrollEdgeAppearance = navBarAppearance
        
        // Configure tab bar appearance
        let tabBarAppearance = UITabBarAppearance()
        tabBarAppearance.configureWithOpaqueBackground()
        tabBarAppearance.backgroundColor = UIColor.systemBackground
        
        UITabBar.appearance().standardAppearance = tabBarAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabBarAppearance
        
        // Configure tint colors
        UIView.appearance().tintColor = UIColor(named: "AccentColor")
    }
    
    private func requestNotificationPermissions() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, error in
            DispatchQueue.main.async {
                if granted {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        }
    }
    
    private func setupApp() {
        // Initialize app state
        appState.initialize()
        
        // Check for biometric authentication
        if authManager.isLoggedIn && biometricManager.isBiometricEnabled {
            biometricManager.authenticateWithBiometrics { success in
                if !success {
                    authManager.logout()
                }
            }
        }
        
        // Start real-time data connections
        if authManager.isLoggedIn {
            tradingManager.startRealTimeUpdates()
            portfolioManager.startRealTimeUpdates()
        }
        
        // Check for app updates
        checkForAppUpdates()
    }
    
    private func handleAppBecomeActive() {
        // Resume real-time connections
        if authManager.isLoggedIn {
            tradingManager.resumeRealTimeUpdates()
            portfolioManager.resumeRealTimeUpdates()
        }
        
        // Refresh data
        Task {
            await refreshAppData()
        }
    }
    
    private func handleAppWillResignActive() {
        // Pause real-time connections to save battery
        tradingManager.pauseRealTimeUpdates()
        portfolioManager.pauseRealTimeUpdates()
        
        // Enable app lock if configured
        if biometricManager.isAppLockEnabled {
            appState.isAppLocked = true
        }
    }
    
    private func refreshAppData() async {
        guard authManager.isLoggedIn else { return }
        
        await withTaskGroup(of: Void.self) { group in
            group.addTask {
                await portfolioManager.refreshPortfolio()
            }
            
            group.addTask {
                await tradingManager.refreshMarketData()
            }
            
            group.addTask {
                await notificationManager.refreshNotifications()
            }
        }
    }
    
    private func checkForAppUpdates() {
        // Check for app updates from App Store
        AppUpdateManager.shared.checkForUpdates { updateAvailable in
            if updateAvailable {
                DispatchQueue.main.async {
                    appState.showUpdateAlert = true
                }
            }
        }
    }
}

// MARK: - App State Management
class AppState: ObservableObject {
    @Published var isAppLocked = false
    @Published var showUpdateAlert = false
    @Published var isNetworkConnected = true
    @Published var currentTab: MainTab = .home
    @Published var showOnboarding = false
    
    func initialize() {
        // Check if first launch
        if UserDefaults.standard.bool(forKey: "isFirstLaunch") == false {
            showOnboarding = true
            UserDefaults.standard.set(true, forKey: "isFirstLaunch")
        }
        
        // Monitor network connectivity
        NetworkMonitor.shared.startMonitoring { [weak self] isConnected in
            DispatchQueue.main.async {
                self?.isNetworkConnected = isConnected
            }
        }
    }
}

// MARK: - Main Tab Enum
enum MainTab: String, CaseIterable {
    case home = "Home"
    case markets = "Markets"
    case trading = "Trading"
    case portfolio = "Portfolio"
    case profile = "Profile"
    
    var icon: String {
        switch self {
        case .home: return "house.fill"
        case .markets: return "chart.line.uptrend.xyaxis"
        case .trading: return "arrow.left.arrow.right"
        case .portfolio: return "briefcase.fill"
        case .profile: return "person.fill"
        }
    }
    
    var selectedIcon: String {
        switch self {
        case .home: return "house.fill"
        case .markets: return "chart.line.uptrend.xyaxis"
        case .trading: return "arrow.left.arrow.right"
        case .portfolio: return "briefcase.fill"
        case .profile: return "person.fill"
        }
    }
}