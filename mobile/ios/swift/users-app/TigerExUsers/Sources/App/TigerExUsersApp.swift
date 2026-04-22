import SwiftUI

@main
struct TigerExUsersApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

@MainActor
final class AppState: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var selectedTab: Tab = .trade
    
    enum Tab: Int, CaseIterable {
        case trade, wallet, earn, p2p, settings
    }
    
    func logout() {
        isAuthenticated = false
        currentUser = nil
        UserDefaults.standard.removeObject(forKey: "accessToken")
    }
}

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        Group {
            if appState.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
    }
}

struct MainTabView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        TabView(selection: $appState.selectedTab) {
            TradeView()
                .tabItem { Label("Trade", systemImage: "chart.line.uptrend.xyaxis") }
                .tag(AppState.Tab.trade)
            
            WalletView()
                .tabItem { Label("Wallet", systemImage: "wallet.pass") }
                .tag(AppState.Tab.wallet)
            
            EarnView()
                .tabItem { Label("Earn", systemImage: "chart.bar") }
                .tag(AppState.Tab.earn)
            
            P2PView()
                .tabItem { Label("P2P", systemImage: "person.2") }
                .tag(AppState.Tab.p2p)
            
            SettingsView()
                .tabItem { Label("Settings", systemImage: "gear") }
                .tag(AppState.Tab.settings)
        }
    }
}

struct LoginView: View {
    @State private var email = ""
    @State private var password = ""
    @State private var twoFactorCode = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 24) {
                Spacer()
                
                Image(systemName: "chart.line.uptrend.xyaxis.circle.fill")
                    .resizable()
                    .scaledToFit()
                    .frame(width: 80, height: 80)
                    .foregroundStyle(.orange)
                
                Text("TigerEx")
                    .font(.largeTitle.bold())
                
                VStack(spacing: 16) {
                    TextField("Email", text: $email)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.emailAddress)
                        .autocapitalization(.none)
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(.roundedBorder)
                        .textContentType(.password)
                }
                .padding(.horizontal)
                
                Button(action: login) {
                    if isLoading {
                        ProgressView()
                    } else {
                        Text("Login")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.orange)
                .foregroundStyle(.white)
                .clipShape(RoundedRectangle(cornerRadius: 12))
                .padding(.horizontal)
                .disabled(isLoading)
                
                Button("Forgot Password?") {
                    // Handle forgot password
                }
                .foregroundStyle(.orange)
                
                Spacer()
                
                Text("Don't have an account? Register")
                    .foregroundStyle(.secondary)
            }
            .navigationBarTitleDisplayMode(.inline)
        }
    }
    
    private func login() {
        isLoading = true
        Task {
            do {
                let response = try await APIService.shared.login(email: email, password: password)
                UserDefaults.standard.set(response.accessToken, forKey: "accessToken")
                // Update app state
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoading = false
        }
    }
}

#Preview {
    LoginView()
        .environmentObject(AppState())
}