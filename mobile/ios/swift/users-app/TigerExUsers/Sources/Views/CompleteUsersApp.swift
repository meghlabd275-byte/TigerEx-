import SwiftUI

@main
struct TigerExUsersApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .preferredColorScheme(.dark)
        }
    }
}

// MARK: - App State
@MainActor
final class AppState: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var selectedTab: Tab = .markets
    @Published var showLoading = false
    @Published var errorMessage: String?
    
    enum Tab: Int, CaseIterable {
        case home, markets, trade, wallet, earn
    }
}

// MARK: - Main Content View
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

// MARK: - Main Tab View
struct MainTabView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem { Label("Home", systemImage: "house.fill") }
                .tag(0)
            
            MarketsView()
                .tabItem { Label("Markets", systemImage: "chart.line.uptrend.xyaxis") }
                .tag(1)
            
            TradeView()
                .tabItem { Label("Trade", systemImage: "arrow.left.arrow.right") }
                .tag(2)
            
            WalletView()
                .tabItem { Label("Wallet", systemImage: "wallet.pass.fill") }
                .tag(3)
            
            EarnView()
                .tabItem { Label("Earn", systemImage: "chart.bar.fill") }
                .tag(4)
        }
        .tint(.orange)
    }
}

// MARK: - Home View (Dashboard)
struct HomeView: View {
    @EnvironmentObject var appState: AppState
    @State private var totalBalance = "$12,345.67"
    @State private var pnl24h = "+5.23%"
    @State private var watchlist: [Coin] = []
    
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Portfolio Card
                    VStack(spacing: 8) {
                        Text("Total Balance")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                        
                        Text(totalBalance)
                            .font(.system(size: 36, weight: .bold))
                        
                        Text(pnl24h)
                            .font(.headline)
                            .foregroundStyle(.green)
                    }
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.gray.opacity(0.2))
                    .clipShape(RoundedRectangle(cornerRadius: 16))
                    
                    // Quick Actions
                    HStack(spacing: 16) {
                        QuickActionButton(title: "Buy", icon: "arrow.down.circle.fill", color: .green) {
                            // Buy action
                        }
                        QuickActionButton(title: "Sell", icon: "arrow.up.circle.fill", color: .red) {
                            // Sell action
                        }
                        QuickActionButton(title: "Send", icon: "paperplane.fill", color: .blue) {
                            // Send action
                        }
                        QuickActionButton(title: "Convert", icon: "arrow.2.squarepath", color: .orange) {
                            // Convert action
                        }
                    }
                    
                    // Watchlist Section
                    VStack(alignment: .leading, spacing: 12) {
                        HStack {
                            Text("Watchlist")
                                .font(.headline)
                            Spacer()
                            Button("Edit") {}
                                .font(.subheadline)
                                .foregroundStyle(.orange)
                        }
                        
                        ForEach(watchlist) { coin in
                            CoinRow(coin: coin)
                        }
                    }
                    
                    // P2P Banner
                    NavigationLink {
                        P2PView()
                    } label: {
                        HStack {
                            Image(systemName: "person.2.fill")
                                .font(.title2)
                            VStack(alignment: .leading) {
                                Text("P2P Trading")
                                    .font(.headline)
                                Text("Buy & Sell Crypto")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                            Spacer()
                            Image(systemName: "chevron.right")
                                .foregroundStyle(.secondary)
                        }
                        .padding()
                        .background(Color.gray.opacity(0.2))
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                    .buttonStyle(.plain)
                    
                    // Services Grid
                    LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                        NavigationLink { DepositView() } label: {
                            ServiceCard(title: "Deposit", icon: "arrow.down.to.line", color: .green)
                        }
                        NavigationLink { WithdrawView() } label: {
                            ServiceCard(title: "Withdraw", icon: "arrow.up.from.line", color: .red)
                        }
                        NavigationLink { FuturesView() } label: {
                            ServiceCard(title: "Futures", icon: "chart.line.uptrend.xyaxis", color: .purple)
                        }
                        NavigationLink { StakingView() } label: {
                            ServiceCard(title: "Staking", icon: "lock.fill", color: .blue)
                        }
                        NavigationLink { LaunchpoolView() } label: {
                            ServiceCard(title: "Launchpool", icon: "flame.fill", color: .orange)
                        }
                        NavigationLink { CopyTradingView() } label: {
                            ServiceCard(title: "Copy Trading", icon: "person.2.fill", color: .cyan)
                        }
                        NavigationLink { MiningView() } label: {
                            ServiceCard(title: "Mining", icon: "pickaxe.fill", color: .yellow)
                        }
                        NavigationLink { CardView() } label: {
                            ServiceCard(title: "Card", icon: "creditcard.fill", color: .pink)
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("TigerEx")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    NavigationLink {
                        SettingsView()
                    } label: {
                        Image(systemName: "gearshape.fill")
                    }
                }
                ToolbarItem(placement: .topBarLeading) {
                    NavigationLink {
                        NotificationsView()
                    } label: {
                        Image(systemName: "bell.fill")
                    }
                }
            }
        }
    }
}

// MARK: - Markets View
struct MarketsView: View {
    @State private var searchText = ""
    @State private var selectedFilter = "All"
    @State private var coins: [Coin] = []
    
    let filters = ["All", "Favorites", "BTC", "ETH", "USDT", "BNB"]
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Search Bar
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundStyle(.secondary)
                    TextField("Search", text: $searchText)
                }
                .padding(10)
                .background(Color.gray.opacity(0.2))
                .clipShape(RoundedRectangle(cornerRadius: 10))
                .padding()
                
                // Filter Pills
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(filters, id: \.self) { filter in
                            Button {
                                selectedFilter = filter
                            } label: {
                                Text(filter)
                                    .font(.subheadline)
                                    .padding(.horizontal, 12)
                                    .padding(.vertical, 6)
                                    .background(selectedFilter == filter ? Color.orange : Color.gray.opacity(0.2))
                                    .clipShape(Capsule())
                            }
                            .foregroundStyle(selectedFilter == filter ? .white : .primary)
                        }
                    }
                    .padding(.horizontal)
                }
                .padding(.bottom, 8)
                
                // Coins List
                List(coins) { coin in
                    NavigationLink {
                        MarketDetailView(coin: coin)
                    } label: {
                        CoinRow(coin: coin)
                    }
                }
                .listStyle(.plain)
            }
            .navigationTitle("Markets")
        }
    }
}

// MARK: - Trade View
struct TradeView: View {
    @State private var selectedPair = "BTC/USDT"
    @State private var orderType: OrderType = .limit
    @State private var side: OrderSide = .buy
    @State private var price = ""
    @State private var amount = ""
    @State private var total = ""
    @State private var orderBook = OrderBook()
    
    enum OrderType: String, CaseIterable {
        case limit = "Limit"
        case market = "Market"
        case stopLimit = "Stop-Limit"
        case oco = "OCO"
    }
    
    enum OrderSide: String {
        case buy = "Buy"
        case sell = "Sell"
    }
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Pair Header
                HStack {
                    VStack(alignment: .leading) {
                        Text(selectedPair)
                            .font(.title2.bold())
                        Text("$43,250.00")
                            .font(.headline)
                            .foregroundStyle(.green)
                    }
                    Spacer()
                    VStack(alignment: .trailing) {
                        Text("+$1,050 (+2.5%)")
                            .foregroundStyle(.green)
                        Text("High: $44,300")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        Text("Vol: 12,345 BTC")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.2))
                
                // Buy/Sell Toggle
                HStack {
                    Button {
                        side = .buy
                    } label: {
                        Text("Buy")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(side == .buy ? Color.green : Color.clear)
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    }
                    Button {
                        side = .sell
                    } label: {
                        Text("Sell")
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(side == .sell ? Color.red : Color.clear)
                            .clipShape(RoundedRectangle(cornerRadius: 8))
                    }
                }
                .padding(.horizontal)
                .padding(.vertical, 8)
                
                // Order Type Picker
                Picker("Order Type", selection: $orderType) {
                    ForEach(OrderType.allCases, id: \.self) { type in
                        Text(type.rawValue).tag(type)
                    }
                }
                .pickerStyle(.segmented)
                .padding(.horizontal)
                
                // Order Form
                VStack(spacing: 12) {
                    // Price
                    HStack {
                        Text("Price")
                            .foregroundStyle(.secondary)
                        Spacer()
                        TextField("0.00", text: $price)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.decimalPad)
                        Text("USDT")
                            .foregroundStyle(.secondary)
                    }
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    
                    // Amount
                    HStack {
                        Text("Amount")
                            .foregroundStyle(.secondary)
                        Spacer()
                        TextField("0.00", text: $amount)
                            .multilineTextAlignment(.trailing)
                            .keyboardType(.decimalPad)
                        Text("BTC")
                            .foregroundStyle(.secondary)
                    }
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    
                    // Percentage Buttons
                    HStack(spacing: 8) {
                        ForEach(["25%", "50%", "75%", "100%"], id: \.self) { pct in
                            Button(pct) {
                                amount = "\(Double(pct.dropLast())! / 100 * 1.0)"
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 8)
                            .background(Color.gray.opacity(0.3))
                            .clipShape(RoundedRectangle(cornerRadius: 6))
                        }
                    }
                    
                    // Total
                    HStack {
                        Text("Total")
                            .foregroundStyle(.secondary)
                        Spacer()
                        Text(total.isEmpty ? "0.00" : total)
                            .multilineTextAlignment(.trailing)
                        Text("USDT")
                            .foregroundStyle(.secondary)
                    }
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    
                    // Place Order Button
                    Button {
                        // Place order
                    } label: {
                        Text(side == .buy ? "Buy BTC" : "Sell BTC")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(side == .buy ? Color.green : Color.red)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                }
                .padding()
                
                Spacer()
            }
            .navigationTitle("Trade")
            .navigationBarTitleDisplayMode(.inline)
        }
    }
}

// MARK: - Wallet View
struct WalletView: View {
    @State private var searchText = ""
    @State private var showZeroBalance = false
    @State private var balances: [Balance] = []
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Search Bar
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundStyle(.secondary)
                    TextField("Search", text: $searchText)
                }
                .padding(10)
                .background(Color.gray.opacity(0.2))
                .clipShape(RoundedRectangle(cornerRadius: 10))
                .padding()
                
                // Toggle
                Toggle("Show Zero Balance", isOn: $showZeroBalance)
                    .padding(.horizontal)
                    .tint(.orange)
                
                List(balances) { balance in
                    NavigationLink {
                        AssetDetailView(balance: balance)
                    } label: {
                        BalanceRow(balance: balance)
                    }
                }
                .listStyle(.plain)
            }
            .navigationTitle("Wallet")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    NavigationLink {
                        DepositView()
                    } label: {
                        Text("Deposit")
                            .foregroundStyle(.green)
                    }
                }
                ToolbarItem(placement: .topBarLeading) {
                    NavigationLink {
                        WithdrawView()
                    } label: {
                        Text("Withdraw")
                            .foregroundStyle(.red)
                    }
                }
            }
        }
    }
}

// MARK: - Earn View
struct EarnView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                // Tab Picker
                Picker("Earn Type", selection: $selectedTab) {
                    Text("Savings").tag(0)
                    Text("Staking").tag(1)
                    Text("Launchpool").tag(2)
                    Text("Megadrop").tag(3)
                }
                .pickerStyle(.segmented)
                .padding()
                
                TabView(selection: $selectedTab) {
                    SavingsProductsView().tag(0)
                    StakingProductsView().tag(1)
                    LaunchpoolProjectsView().tag(2)
                    MegadropProjectsView().tag(3)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))
            }
            .navigationTitle("Earn")
        }
    }
}

// MARK: - P2P View
struct P2PView: View {
    @State private var selectedTab = 0
    @State private var ads: [P2PAd] = []
    
    var body: some View {
        VStack(spacing: 0) {
            Picker("Buy/Sell", selection: $selectedTab) {
                Text("Buy").tag(0)
                Text("Sell").tag(1)
                Text("My Ads").tag(2)
                Text("Orders").tag(3)
            }
            .pickerStyle(.segmented)
            .padding()
            
            // Filters
            ScrollView(.horizontal, showsIndicators: false) {
                HStack {
                    FilterChip(title: "USDT", selected: true) {}
                    FilterChip(title: "BTC", selected: false) {}
                    FilterChip(title: "ETH", selected: false) {}
                    FilterChip(title: "BNB", selected: false) {}
                    FilterChip(title: "USD", selected: true) {}
                }
            }
            .padding(.horizontal)
            
            List(ads) { ad in
                P2PAdRow(ad: ad)
            }
            .listStyle(.plain)
        }
        .navigationTitle("P2P Trading")
        .toolbar {
            ToolbarItem(placement: .topBarTrailing) {
                Button {
                    // Create Ad
                } label: {
                    Image(systemName: "plus.circle.fill")
                        .foregroundStyle(.orange)
                }
            }
        }
    }
}

// MARK: - Deposit View
struct DepositView: View {
    @State private var selectedAsset = "BTC"
    @State private var selectedNetwork = "BTC"
    @State private var depositAddress = "bc1qxy2kgdygjrsqtzq2n0ye..." // truncated
    
    var body: some View {
        VStack(spacing: 20) {
            // Asset Picker
            VStack(alignment: .leading, spacing: 8) {
                Text("Select Asset")
                    .font(.headline)
                Picker("Asset", selection: $selectedAsset) {
                    Text("BTC").tag("BTC")
                    Text("ETH").tag("ETH")
                    Text("USDT").tag("USDT")
                    Text("BNB").tag("BNB")
                }
                .pickerStyle(.menu)
                .padding()
                .background(Color.gray.opacity(0.2))
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            
            // Network Selection
            VStack(alignment: .leading, spacing: 8) {
                Text("Select Network")
                    .font(.headline)
                ForEach(["BTC", "ETH", "TRC20"], id: \.self) { network in
                    Button {
                        selectedNetwork = network
                    } label: {
                        HStack {
                            Text(network)
                            Spacer()
                            if selectedNetwork == network {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundStyle(.orange)
                            }
                        }
                        .padding()
                        .background(selectedNetwork == network ? Color.orange.opacity(0.2) : Color.gray.opacity(0.2))
                        .clipShape(RoundedRectangle(cornerRadius: 8))
                    }
                    .foregroundStyle(.primary)
                }
            }
            
            // Deposit Address
            VStack(alignment: .leading, spacing: 8) {
                Text("Deposit Address")
                    .font(.headline)
                HStack {
                    Text(depositAddress)
                        .font(.system(.body, design: .monospaced))
                        .lineLimit(1)
                    Spacer()
                    Button {
                        UIPasteboard.general.string = depositAddress
                    } label: {
                        Image(systemName: "doc.on.doc")
                            .foregroundStyle(.orange)
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.2))
                .clipShape(RoundedRectangle(cornerRadius: 12))
                
                // QR Code Placeholder
                Image(systemName: "qrcode")
                    .font(.system(size: 120))
                    .padding()
                    .background(Color.white)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            
            Spacer()
        }
        .padding()
        .navigationTitle("Deposit")
    }
}

// MARK: - Withdraw View
struct WithdrawView: View {
    @State private var selectedAsset = "BTC"
    @State private var address = ""
    @State private var amount = ""
    @State private var fee = "0.0005 BTC"
    
    var body: some View {
        VStack(spacing: 20) {
            // Asset Picker
            VStack(alignment: .leading, spacing: 8) {
                Text("Select Asset")
                    .font(.headline)
                Picker("Asset", selection: $selectedAsset) {
                    Text("BTC").tag("BTC")
                    Text("ETH").tag("ETH")
                    Text("USDT").tag("USDT")
                }
                .pickerStyle(.menu)
                .padding()
                .background(Color.gray.opacity(0.2))
                .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            
            // Address
            VStack(alignment: .leading, spacing: 8) {
                Text("Recipient Address")
                    .font(.headline)
                TextField("Enter address", text: $address)
                    .padding()
                    .background(Color.gray.opacity(0.2))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            
            // Amount
            VStack(alignment: .leading, spacing: 8) {
                Text("Amount")
                    .font(.headline)
                HStack {
                    TextField("0.00", text: $amount)
                        .keyboardType(.decimalPad)
                    Button("MAX") {}
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.orange.opacity(0.3))
                        .clipShape(Capsule())
                }
                .padding()
                .background(Color.gray.opacity(0.2))
                .clipShape(RoundedRectangle(cornerRadius: 12))
                Text("Available: 1.2345 BTC")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            
            // Fee Display
            HStack {
                Text("Network Fee")
                Spacer()
                Text(fee)
                    .foregroundStyle(.secondary)
            }
            .padding()
            .background(Color.gray.opacity(0.2))
            .clipShape(RoundedRectangle(cornerRadius: 12))
            
            // Withdraw Button
            Button {
                // Withdraw
            } label: {
                Text("Withdraw")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.red)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            
            Spacer()
        }
        .padding()
        .navigationTitle("Withdraw")
    }
}

// MARK: - Market Detail View
struct MarketDetailView: View {
    let coin: Coin
    
    var body: some View {
        VStack(spacing: 0) {
            // Price Header
            VStack(spacing: 8) {
                Text(coin.price)
                    .font(.system(size: 32, weight: .bold))
                Text(coin.change24h)
                    .foregroundStyle(coin.isPositive ? .green : .red)
            }
            .padding()
            
            // Chart Placeholder
            Image(systemName: "chart.line.uptrend.xyaxis")
                .font(.system(size: 100))
                .frame(height: 250)
            
            // Order Book Preview
            VStack(spacing: 4) {
                ForEach(0..<5, id: \.self) { i in
                    HStack {
                        Text("43,\(250 + i)")
                            .foregroundStyle(.green)
                        Spacer()
                        ProgressView(value: Double.random(in: 0...1))
                            .tint(.green)
                        Text("1.2\(i)")
                            .foregroundStyle(.secondary)
                    }
                }
            }
            .padding()
            
            Spacer()
            
            // Trade Button
            Button {
                // Go to trade
            } label: {
                Text("Trade")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.orange)
                    .clipShape(RoundedRectangle(cornerRadius: 12))
            }
            .padding()
        }
        .navigationTitle(coin.symbol)
        .navigationBarTitleDisplayMode(.inline)
    }
}

// MARK: - Asset Detail View
struct AssetDetailView: View {
    let balance: Balance
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Balance Card
                VStack(spacing: 8) {
                    Text(balance.amount)
                        .font(.system(size: 32, weight: .bold))
                    Text("≈ $\(balance.usdValue)")
                        .foregroundStyle(.secondary)
                }
                .padding()
                .frame(maxWidth: .infinity)
                .background(Color.gray.opacity(0.2))
                .clipShape(RoundedRectangle(cornerRadius: 16))
                
                // Details
                VStack(spacing: 12) {
                    DetailRow(label: "Available", value: balance.available)
                    DetailRow(label: "Frozen", value: balance.frozen)
                    DetailRow(label: "Locked", value: balance.locked)
                    DetailRow(label: " USD Value", value: "$\(balance.usdValue)")
                }
                .padding()
                .background(Color.gray.opacity(0.2))
                .clipShape(RoundedRectangle(cornerRadius: 12))
                
                // Actions
                HStack(spacing: 12) {
                    NavigationLink {
                        DepositView()
                    } label: {
                        Text("Deposit")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                    NavigationLink {
                        WithdrawView()
                    } label: {
                        Text("Withdraw")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.red)
                            .clipShape(RoundedRectangle(cornerRadius: 12))
                    }
                }
            }
            .padding()
        }
        .navigationTitle(balance.asset)
    }
}

// MARK: - All Additional Views
struct WithdrawViewFull: View { var body: some View { WithdrawView() }}
struct FuturesView: View { var body: some View { Text("Futures").padding() }.navigationTitle("Futures") }
struct StakingView: View { var body: some View { Text("Staking").padding() }.navigationTitle("Staking") }
struct LaunchpoolView: View { var body: some View { Text("Launchpool").padding() }.navigationTitle("Launchpool") }
struct CopyTradingView: View { var body: some View { Text("Copy Trading").padding() }.navigationTitle("Copy Trading") }
struct MiningView: View { var body: some View { Text("Mining").padding() }.navigationTitle("Mining") }
struct CardView: View { var body: some View { Text("Card").padding() }.navigationTitle("Card") }
struct SettingsView: View { var body: some View { Text("Settings").padding() }.navigationTitle("Settings") }
struct NotificationsView: View { var body: some View { Text("Notifications").padding() }.navigationTitle("Notifications") }
struct SavingsProductsView: View { var body: some View { Text("Savings Products").padding() } }
struct StakingProductsView: View { var body: some View { Text("Staking Products").padding() } }
struct LaunchpoolProjectsView: View { var body: some View { Text("Launchpool Projects").padding() } }
struct MegadropProjectsView: View { var body: some View { Text("Megadrop Projects").padding() } }

// MARK: - Models
struct User: Identifiable {
    let id = UUID()
    let email: String
    let role: String
}

struct Coin: Identifiable {
    let id = UUID()
    let symbol: String
    let name: String
    let price: String
    let change24h: String
    let volume24h: String
    let isPositive: Bool = true
}

struct Balance: Identifiable {
    let id = UUID()
    let asset: String
    let amount: String
    let available: String
    let frozen: String
    let locked: String
    let usdValue: String
}

struct P2PAd: Identifiable {
    let id = UUID()
    let advertiser: String
    let price: String
    let available: String
    let paymentMethods: [String]
}

struct OrderBook {
    let bids: [(price: String, amount: String)] = []
    let asks: [(price: String, amount: String)] = []
}

// MARK: - Components
struct QuickActionButton: View {
    let title: String
    let icon: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundStyle(color)
                Text(title)
                    .font(.caption)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .background(Color.gray.opacity(0.2))
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
        .foregroundStyle(.primary)
    }
}

struct ServiceCard: View {
    let title: String
    let icon: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.title)
                .foregroundStyle(color)
            Text(title)
                .font(.caption)
                .foregroundStyle(.primary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.gray.opacity(0.2))
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

struct CoinRow: View {
    let coin: Coin
    
    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(coin.symbol)
                    .font(.headline)
                Text(coin.name)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            VStack(alignment: .trailing) {
                Text(coin.price)
                    .font(.headline)
                Text(coin.change24h)
                    .font(.caption)
                    .foregroundStyle(coin.isPositive ? .green : .red)
            }
        }
    }
}

struct BalanceRow: View {
    let balance: Balance
    
    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(balance.asset)
                    .font(.headline)
                Text("$\(balance.usdValue)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
            Spacer()
            VStack(alignment: .trailing) {
                Text(balance.amount)
                    .font(.headline)
                Text("Available: \(balance.available)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
    }
}

struct P2PAdRow: View {
    let ad: P2PAd
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(ad.advertiser)
                    .font(.headline)
                Spacer()
                Text("$\(ad.price)")
                    .font(.headline)
                    .foregroundStyle(.green)
            }
            HStack {
                ForEach(ad.paymentMethods, id: \.self) { method in
                    Text(method)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.gray.opacity(0.3))
                        .clipShape(Capsule())
                }
            }
        }
    }
}

struct FilterChip: View {
    let title: String
    let selected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.subheadline)
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(selected ? Color.orange : Color.gray.opacity(0.2))
                .clipShape(Capsule())
        }
        .foregroundStyle(selected ? .white : .primary)
    }
}

struct DetailRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .foregroundStyle(.secondary)
            Spacer()
            Text(value)
        }
    }
}

// MARK: - Login View
struct LoginView: View {
    @State private var email = ""
    @State private var password = ""
    @State private var twoFactorCode = ""
    
    var body: some View {
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
            
            Button("Login") {
                // Login
            }
            .frame(maxWidth: .infinity)
            .padding()
            .background(Color.orange)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .padding(.horizontal)
            
            Spacer()
        }
    }
}