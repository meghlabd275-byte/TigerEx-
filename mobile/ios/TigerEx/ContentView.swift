import SwiftUI
import Combine
import Foundation

// MARK: - Main Content View
struct ContentView: View {
    @StateObject private var authManager = AuthenticationManager()
    @StateObject private var tradingManager = TradingManager()
    @StateObject private var portfolioManager = PortfolioManager()
    @StateObject private var notificationManager = NotificationManager()
    
    var body: some View {
        Group {
            if authManager.isAuthenticated {
                MainTabView()
                    .environmentObject(authManager)
                    .environmentObject(tradingManager)
                    .environmentObject(portfolioManager)
                    .environmentObject(notificationManager)
            } else {
                AuthenticationView()
                    .environmentObject(authManager)
            }
        }
        .onAppear {
            authManager.checkAuthenticationStatus()
            notificationManager.requestPermissions()
        }
    }
}

// MARK: - Main Tab View
struct MainTabView: View {
    @EnvironmentObject var authManager: AuthenticationManager
    @EnvironmentObject var tradingManager: TradingManager
    @EnvironmentObject var portfolioManager: PortfolioManager
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Home/Dashboard
            DashboardView()
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("Home")
                }
                .tag(0)
            
            // Markets
            MarketsView()
                .tabItem {
                    Image(systemName: "chart.line.uptrend.xyaxis")
                    Text("Markets")
                }
                .tag(1)
            
            // Trading
            TradingView()
                .tabItem {
                    Image(systemName: "arrow.left.arrow.right")
                    Text("Trade")
                }
                .tag(2)
            
            // Portfolio
            PortfolioView()
                .tabItem {
                    Image(systemName: "briefcase.fill")
                    Text("Portfolio")
                }
                .tag(3)
            
            // More
            MoreView()
                .tabItem {
                    Image(systemName: "ellipsis")
                    Text("More")
                }
                .tag(4)
        }
        .accentColor(.orange)
        .onAppear {
            portfolioManager.loadPortfolio()
            tradingManager.connectWebSocket()
        }
    }
}

// MARK: - Dashboard View
struct DashboardView: View {
    @EnvironmentObject var portfolioManager: PortfolioManager
    @EnvironmentObject var tradingManager: TradingManager
    @State private var showingNotifications = false
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Header with balance and notifications
                    HStack {
                        VStack(alignment: .leading) {
                            Text("Total Balance")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            Text("$\(portfolioManager.totalBalance, specifier: "%.2f")")
                                .font(.title)
                                .fontWeight(.bold)
                        }
                        
                        Spacer()
                        
                        Button(action: { showingNotifications = true }) {
                            Image(systemName: "bell.fill")
                                .foregroundColor(.orange)
                        }
                    }
                    .padding(.horizontal)
                    
                    // Portfolio Performance Card
                    PortfolioPerformanceCard()
                    
                    // Quick Actions
                    QuickActionsView()
                    
                    // Market Overview
                    MarketOverviewCard()
                    
                    // Recent Transactions
                    RecentTransactionsCard()
                    
                    // News & Updates
                    NewsUpdatesCard()
                }
                .padding(.vertical)
            }
            .navigationTitle("TigerEx")
            .navigationBarTitleDisplayMode(.large)
            .sheet(isPresented: $showingNotifications) {
                NotificationsView()
            }
        }
    }
}

// MARK: - Portfolio Performance Card
struct PortfolioPerformanceCard: View {
    @EnvironmentObject var portfolioManager: PortfolioManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Portfolio Performance")
                    .font(.headline)
                Spacer()
                Text("24h")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            HStack {
                VStack(alignment: .leading) {
                    Text("P&L")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    HStack {
                        Text("$\(portfolioManager.totalPnL, specifier: "%.2f")")
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(portfolioManager.totalPnL >= 0 ? .green : .red)
                        Text("(\(portfolioManager.totalPnLPercentage, specifier: "%.2f")%)")
                            .font(.caption)
                            .foregroundColor(portfolioManager.totalPnL >= 0 ? .green : .red)
                    }
                }
                
                Spacer()
                
                // Mini chart placeholder
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gray.opacity(0.2))
                    .frame(width: 100, height: 50)
                    .overlay(
                        Text("Chart")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    )
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)
        .padding(.horizontal)
    }
}

// MARK: - Quick Actions View
struct QuickActionsView: View {
    var body: some View {
        VStack(alignment: .leading) {
            Text("Quick Actions")
                .font(.headline)
                .padding(.horizontal)
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 16) {
                    QuickActionButton(
                        icon: "plus.circle.fill",
                        title: "Deposit",
                        color: .green
                    ) {
                        // Handle deposit
                    }
                    
                    QuickActionButton(
                        icon: "minus.circle.fill",
                        title: "Withdraw",
                        color: .red
                    ) {
                        // Handle withdraw
                    }
                    
                    QuickActionButton(
                        icon: "arrow.left.arrow.right.circle.fill",
                        title: "Convert",
                        color: .blue
                    ) {
                        // Handle convert
                    }
                    
                    QuickActionButton(
                        icon: "person.2.circle.fill",
                        title: "P2P",
                        color: .purple
                    ) {
                        // Handle P2P
                    }
                    
                    QuickActionButton(
                        icon: "doc.text.circle.fill",
                        title: "Copy Trade",
                        color: .orange
                    ) {
                        // Handle copy trading
                    }
                }
                .padding(.horizontal)
            }
        }
    }
}

struct QuickActionButton: View {
    let icon: String
    let title: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
            .frame(width: 70, height: 70)
            .background(Color(.systemBackground))
            .cornerRadius(12)
            .shadow(color: .black.opacity(0.1), radius: 3, x: 0, y: 1)
        }
    }
}

// MARK: - Market Overview Card
struct MarketOverviewCard: View {
    @EnvironmentObject var tradingManager: TradingManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Market Overview")
                    .font(.headline)
                Spacer()
                NavigationLink("View All", destination: MarketsView())
                    .font(.caption)
                    .foregroundColor(.orange)
            }
            
            LazyVStack(spacing: 8) {
                ForEach(tradingManager.topMarkets.prefix(5), id: \.symbol) { market in
                    MarketRowView(market: market)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)
        .padding(.horizontal)
    }
}

struct MarketRowView: View {
    let market: Market
    
    var body: some View {
        HStack {
            // Coin icon and name
            HStack(spacing: 8) {
                AsyncImage(url: URL(string: market.iconURL)) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                } placeholder: {
                    Circle()
                        .fill(Color.gray.opacity(0.3))
                }
                .frame(width: 24, height: 24)
                
                VStack(alignment: .leading, spacing: 2) {
                    Text(market.symbol)
                        .font(.caption)
                        .fontWeight(.medium)
                    Text(market.name)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            
            Spacer()
            
            // Price and change
            VStack(alignment: .trailing, spacing: 2) {
                Text("$\(market.price, specifier: "%.2f")")
                    .font(.caption)
                    .fontWeight(.medium)
                
                HStack(spacing: 2) {
                    Image(systemName: market.priceChange >= 0 ? "arrow.up" : "arrow.down")
                        .font(.caption2)
                    Text("\(abs(market.priceChangePercentage), specifier: "%.2f")%")
                        .font(.caption2)
                }
                .foregroundColor(market.priceChange >= 0 ? .green : .red)
            }
        }
    }
}

// MARK: - Recent Transactions Card
struct RecentTransactionsCard: View {
    @EnvironmentObject var portfolioManager: PortfolioManager
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Recent Transactions")
                    .font(.headline)
                Spacer()
                NavigationLink("View All", destination: TransactionHistoryView())
                    .font(.caption)
                    .foregroundColor(.orange)
            }
            
            LazyVStack(spacing: 8) {
                ForEach(portfolioManager.recentTransactions.prefix(3), id: \.id) { transaction in
                    TransactionRowView(transaction: transaction)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)
        .padding(.horizontal)
    }
}

struct TransactionRowView: View {
    let transaction: Transaction
    
    var body: some View {
        HStack {
            // Transaction type icon
            Image(systemName: transaction.type.iconName)
                .foregroundColor(transaction.type.color)
                .frame(width: 24, height: 24)
            
            VStack(alignment: .leading, spacing: 2) {
                Text(transaction.type.displayName)
                    .font(.caption)
                    .fontWeight(.medium)
                Text(transaction.timestamp.formatted(.dateTime.month().day().hour().minute()))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 2) {
                Text("\(transaction.amount, specifier: "%.6f") \(transaction.symbol)")
                    .font(.caption)
                    .fontWeight(.medium)
                Text("$\(transaction.usdValue, specifier: "%.2f")")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
    }
}

// MARK: - News Updates Card
struct NewsUpdatesCard: View {
    @State private var newsItems: [NewsItem] = []
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("News & Updates")
                    .font(.headline)
                Spacer()
                NavigationLink("View All", destination: NewsView())
                    .font(.caption)
                    .foregroundColor(.orange)
            }
            
            LazyVStack(spacing: 8) {
                ForEach(newsItems.prefix(3), id: \.id) { news in
                    NewsRowView(news: news)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 5, x: 0, y: 2)
        .padding(.horizontal)
        .onAppear {
            loadNews()
        }
    }
    
    private func loadNews() {
        // Mock news data
        newsItems = [
            NewsItem(id: "1", title: "Bitcoin reaches new all-time high", summary: "BTC surpasses $50,000 mark", timestamp: Date()),
            NewsItem(id: "2", title: "Ethereum 2.0 update released", summary: "Major network upgrade completed", timestamp: Date().addingTimeInterval(-3600)),
            NewsItem(id: "3", title: "TigerEx adds new trading pairs", summary: "10 new altcoins now available", timestamp: Date().addingTimeInterval(-7200))
        ]
    }
}

struct NewsRowView: View {
    let news: NewsItem
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            RoundedRectangle(cornerRadius: 6)
                .fill(Color.orange.opacity(0.2))
                .frame(width: 40, height: 40)
                .overlay(
                    Image(systemName: "newspaper")
                        .foregroundColor(.orange)
                )
            
            VStack(alignment: .leading, spacing: 4) {
                Text(news.title)
                    .font(.caption)
                    .fontWeight(.medium)
                    .lineLimit(2)
                
                Text(news.summary)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(1)
                
                Text(news.timestamp.formatted(.relative(presentation: .named)))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
    }
}

// MARK: - Data Models
struct Market {
    let symbol: String
    let name: String
    let price: Double
    let priceChange: Double
    let priceChangePercentage: Double
    let volume: Double
    let iconURL: String
}

struct Transaction {
    let id: String
    let type: TransactionType
    let symbol: String
    let amount: Double
    let usdValue: Double
    let timestamp: Date
}

enum TransactionType {
    case buy, sell, deposit, withdraw, transfer
    
    var displayName: String {
        switch self {
        case .buy: return "Buy"
        case .sell: return "Sell"
        case .deposit: return "Deposit"
        case .withdraw: return "Withdraw"
        case .transfer: return "Transfer"
        }
    }
    
    var iconName: String {
        switch self {
        case .buy: return "arrow.up.circle.fill"
        case .sell: return "arrow.down.circle.fill"
        case .deposit: return "plus.circle.fill"
        case .withdraw: return "minus.circle.fill"
        case .transfer: return "arrow.left.arrow.right.circle.fill"
        }
    }
    
    var color: Color {
        switch self {
        case .buy: return .green
        case .sell: return .red
        case .deposit: return .blue
        case .withdraw: return .orange
        case .transfer: return .purple
        }
    }
}

struct NewsItem {
    let id: String
    let title: String
    let summary: String
    let timestamp: Date
}

// MARK: - Managers (ObservableObject classes)
class AuthenticationManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var user: User?
    
    func checkAuthenticationStatus() {
        // Check stored authentication token
        if let token = UserDefaults.standard.string(forKey: "auth_token") {
            // Validate token with server
            isAuthenticated = true
        }
    }
    
    func login(email: String, password: String) async {
        // Implement login logic
    }
    
    func logout() {
        UserDefaults.standard.removeObject(forKey: "auth_token")
        isAuthenticated = false
        user = nil
    }
}

class TradingManager: ObservableObject {
    @Published var topMarkets: [Market] = []
    @Published var isConnected = false
    
    func connectWebSocket() {
        // Implement WebSocket connection
        loadTopMarkets()
    }
    
    private func loadTopMarkets() {
        // Mock data
        topMarkets = [
            Market(symbol: "BTC", name: "Bitcoin", price: 43250.00, priceChange: 1250.00, priceChangePercentage: 2.98, volume: 1234567890, iconURL: ""),
            Market(symbol: "ETH", name: "Ethereum", price: 2650.00, priceChange: -45.50, priceChangePercentage: -1.69, volume: 987654321, iconURL: ""),
            Market(symbol: "BNB", name: "Binance Coin", price: 315.75, priceChange: 8.25, priceChangePercentage: 2.68, volume: 456789123, iconURL: ""),
            Market(symbol: "ADA", name: "Cardano", price: 0.485, priceChange: 0.012, priceChangePercentage: 2.54, volume: 234567890, iconURL: ""),
            Market(symbol: "SOL", name: "Solana", price: 98.45, priceChange: -2.15, priceChangePercentage: -2.14, volume: 345678901, iconURL: "")
        ]
    }
}

class PortfolioManager: ObservableObject {
    @Published var totalBalance: Double = 0
    @Published var totalPnL: Double = 0
    @Published var totalPnLPercentage: Double = 0
    @Published var recentTransactions: [Transaction] = []
    
    func loadPortfolio() {
        // Mock data
        totalBalance = 12450.75
        totalPnL = 1250.30
        totalPnLPercentage = 11.15
        
        recentTransactions = [
            Transaction(id: "1", type: .buy, symbol: "BTC", amount: 0.025, usdValue: 1081.25, timestamp: Date()),
            Transaction(id: "2", type: .sell, symbol: "ETH", amount: 1.5, usdValue: 3975.00, timestamp: Date().addingTimeInterval(-3600)),
            Transaction(id: "3", type: .deposit, symbol: "USDT", amount: 5000.00, usdValue: 5000.00, timestamp: Date().addingTimeInterval(-7200))
        ]
    }
}

class NotificationManager: ObservableObject {
    @Published var notifications: [NotificationItem] = []
    
    func requestPermissions() {
        // Request push notification permissions
    }
}

struct User {
    let id: String
    let email: String
    let username: String
}

struct NotificationItem {
    let id: String
    let title: String
    let message: String
    let timestamp: Date
    let isRead: Bool
}

// MARK: - Placeholder Views
struct AuthenticationView: View {
    var body: some View {
        Text("Authentication View")
    }
}

struct MarketsView: View {
    var body: some View {
        Text("Markets View")
    }
}

struct TradingView: View {
    var body: some View {
        Text("Trading View")
    }
}

struct PortfolioView: View {
    var body: some View {
        Text("Portfolio View")
    }
}

struct MoreView: View {
    var body: some View {
        Text("More View")
    }
}

struct NotificationsView: View {
    var body: some View {
        Text("Notifications View")
    }
}

struct TransactionHistoryView: View {
    var body: some View {
        Text("Transaction History View")
    }
}

struct NewsView: View {
    var body: some View {
        Text("News View")
    }
}

// MARK: - Preview
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}