import SwiftUI
import Combine
import LocalAuthentication

@main
struct TigerExApp: App {
    @StateObject private var authManager = AuthenticationManager()
    @StateObject private var tradingManager = TradingManager()
    @StateObject private var portfolioManager = PortfolioManager()
    @StateObject private var notificationManager = NotificationManager()
    @StateObject private var biometricManager = BiometricManager()
    @StateObject private var themeManager = ThemeManager()
    
    init() {
        setupAppearance()
        setupNotifications()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authManager)
                .environmentObject(tradingManager)
                .environmentObject(portfolioManager)
                .environmentObject(notificationManager)
                .environmentObject(biometricManager)
                .environmentObject(themeManager)
                .preferredColorScheme(themeManager.colorScheme)
                .onAppear {
                    setupInitialConfiguration()
                }
        }
    }
    
    private func setupAppearance() {
        // Configure navigation bar appearance
        let appearance = UINavigationBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundColor = UIColor(named: "PrimaryColor")
        appearance.titleTextAttributes = [.foregroundColor: UIColor.white]
        appearance.largeTitleTextAttributes = [.foregroundColor: UIColor.white]
        
        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().compactAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance
        
        // Configure tab bar appearance
        let tabBarAppearance = UITabBarAppearance()
        tabBarAppearance.configureWithOpaqueBackground()
        tabBarAppearance.backgroundColor = UIColor(named: "BackgroundColor")
        
        UITabBar.appearance().standardAppearance = tabBarAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabBarAppearance
    }
    
    private func setupNotifications() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, error in
            if granted {
                DispatchQueue.main.async {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        }
    }
    
    private func setupInitialConfiguration() {
        // Initialize app configuration
        Task {
            await authManager.checkAuthenticationStatus()
            await tradingManager.initializeMarketData()
            await portfolioManager.loadPortfolio()
        }
    }
}

struct ContentView: View {
    @EnvironmentObject var authManager: AuthenticationManager
    @EnvironmentObject var biometricManager: BiometricManager
    @State private var showingSplash = true
    
    var body: some View {
        Group {
            if showingSplash {
                SplashView()
                    .onAppear {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                            withAnimation(.easeInOut(duration: 0.5)) {
                                showingSplash = false
                            }
                        }
                    }
            } else if authManager.isAuthenticated {
                MainTabView()
            } else {
                AuthenticationView()
            }
        }
        .onAppear {
            if biometricManager.isBiometricEnabled && authManager.isAuthenticated {
                biometricManager.authenticateWithBiometrics()
            }
        }
    }
}

// MARK: - Splash View
struct SplashView: View {
    @State private var scale: CGFloat = 0.5
    @State private var opacity: Double = 0.0
    
    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color("PrimaryColor"), Color("SecondaryColor")],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()
            
            VStack(spacing: 20) {
                Image("TigerExLogo")
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(width: 120, height: 120)
                    .scaleEffect(scale)
                    .opacity(opacity)
                
                Text("TigerEx")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                    .opacity(opacity)
                
                Text("Advanced Hybrid Crypto Exchange")
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.8))
                    .opacity(opacity)
            }
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 1.0)) {
                scale = 1.0
                opacity = 1.0
            }
        }
    }
}

// MARK: - Main Tab View
struct MainTabView: View {
    @EnvironmentObject var authManager: AuthenticationManager
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Home Tab
            HomeView()
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("Home")
                }
                .tag(0)
            
            // Markets Tab
            MarketsView()
                .tabItem {
                    Image(systemName: "chart.line.uptrend.xyaxis")
                    Text("Markets")
                }
                .tag(1)
            
            // Trade Tab
            TradeView()
                .tabItem {
                    Image(systemName: "arrow.left.arrow.right")
                    Text("Trade")
                }
                .tag(2)
            
            // Futures Tab
            FuturesView()
                .tabItem {
                    Image(systemName: "chart.bar.fill")
                    Text("Futures")
                }
                .tag(3)
            
            // Portfolio Tab
            PortfolioView()
                .tabItem {
                    Image(systemName: "briefcase.fill")
                    Text("Portfolio")
                }
                .tag(4)
            
            // More Tab
            MoreView()
                .tabItem {
                    Image(systemName: "ellipsis")
                    Text("More")
                }
                .tag(5)
        }
        .accentColor(Color("PrimaryColor"))
    }
}

// MARK: - Authentication View
struct AuthenticationView: View {
    @EnvironmentObject var authManager: AuthenticationManager
    @State private var showingLogin = true
    
    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient(
                    colors: [Color("PrimaryColor"), Color("SecondaryColor")],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .ignoresSafeArea()
                
                VStack(spacing: 30) {
                    // Logo and Title
                    VStack(spacing: 16) {
                        Image("TigerExLogo")
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(width: 80, height: 80)
                        
                        Text("Welcome to TigerEx")
                            .font(.largeTitle)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                        
                        Text("Advanced Hybrid Crypto Exchange")
                            .font(.subheadline)
                            .foregroundColor(.white.opacity(0.8))
                    }
                    
                    Spacer()
                    
                    // Authentication Buttons
                    VStack(spacing: 16) {
                        if showingLogin {
                            LoginView()
                        } else {
                            RegisterView()
                        }
                        
                        Button(action: {
                            withAnimation(.easeInOut(duration: 0.3)) {
                                showingLogin.toggle()
                            }
                        }) {
                            Text(showingLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In")
                                .foregroundColor(.white)
                                .font(.footnote)
                        }
                    }
                    .padding(.horizontal, 32)
                    
                    Spacer()
                }
            }
        }
    }
}

// MARK: - Theme Manager
class ThemeManager: ObservableObject {
    @Published var isDarkMode = false
    
    var colorScheme: ColorScheme? {
        isDarkMode ? .dark : .light
    }
    
    func toggleTheme() {
        isDarkMode.toggle()
    }
}