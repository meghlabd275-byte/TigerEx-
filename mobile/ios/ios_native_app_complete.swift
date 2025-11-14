import SwiftUI
import Combine
import Foundation

// MARK: - Main App Structure
@main
struct TigerExApp: App {
    @StateObject private var authViewModel = AuthViewModel()
    @StateObject private var tradingViewModel = TradingViewModel()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authViewModel)
                .environmentObject(tradingViewModel)
                .preferredColorScheme(.dark)
        }
    }
}

// MARK: - Main Content View
struct ContentView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    
    var body: some View {
        Group {
            if authViewModel.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
        .animation(.easeInOut, value: authViewModel.isAuthenticated)
    }
}

// MARK: - Main Tab View
struct MainTabView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            TradingView()
                .tabItem {
                    Image(systemName: "chart.line.uptrend.xyaxis")
                    Text("Trade")
                }
                .tag(0)
            
            PortfolioView()
                .tabItem {
                    Image(systemName: "briefcase")
                    Text("Portfolio")
                }
                .tag(1)
            
            OrdersView()
                .tabItem {
                    Image(systemName: "list.bullet")
                    Text("Orders")
                }
                .tag(2)
            
            ProfileView()
                .tabItem {
                    Image(systemName: "person.circle")
                    Text("Profile")
                }
                .tag(3)
        }
        .accentColor(.yellow)
        .background(Color.black.ignoresSafeArea())
    }
}

// MARK: - Trading View
struct TradingView: View {
    @EnvironmentObject var tradingViewModel: TradingViewModel
    @State private var selectedTradingMode: TradingMode = .spot
    @State private var selectedOrderSide: OrderSide = .buy
    @State private var selectedOrderType: OrderType = .market
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Header
                TradingHeaderView()
                
                // Trading Mode Selector
                TradingModeSelector(selectedMode: $selectedTradingMode)
                    .onChange(of: selectedTradingMode) { mode in
                        tradingViewModel.updateTradingMode(mode)
                    }
                
                // Main Content
                GeometryReader { geometry in
                    HStack(spacing: 0) {
                        // Markets Panel
                        MarketsPanel()
                            .frame(width: 300)
                        
                        // Chart Section
                        ChartSection()
                            .frame(width: geometry.size.width - 300 - 320)
                        
                        // Trading Panel
                        TradingPanel(
                            selectedSide: $selectedOrderSide,
                            selectedType: $selectedOrderType
                        )
                        .frame(width: 320)
                    }
                }
            }
            .background(Color(red: 0.04, green: 0.05, blue: 0.07))
            .navigationBarHidden(true)
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }
}

// MARK: - Trading Header View
struct TradingHeaderView: View {
    var body: some View {
        HStack {
            // Logo
            HStack {
                Image(systemName: "tiger.fill")
                    .foregroundColor(.yellow)
                    .font(.title2)
                Text("TigerEx")
                    .foregroundColor(.yellow)
                    .font(.title2)
                    .fontWeight(.bold)
            }
            
            Spacer()
            
            // Notifications
            Button(action: {}) {
                Image(systemName: "bell")
                    .foregroundColor(.white)
                    .font(.title3)
            }
            
            // Profile
            Button(action: {}) {
                Image(systemName: "person.circle")
                    .foregroundColor(.white)
                    .font(.title3)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 12)
        .background(Color(red: 0.12, green: 0.14, blue: 0.16))
    }
}

// MARK: - Trading Mode Selector
struct TradingModeSelector: View {
    @Binding var selectedMode: TradingMode
    
    private let modes: [TradingMode] = [.spot, .futures, .margin, .options, .alpha, .etf, .tradex]
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 24) {
                ForEach(modes, id: \.self) { mode in
                    VStack(spacing: 4) {
                        Text(mode.rawValue.uppercased())
                            .font(.caption)
                            .fontWeight(selectedMode == mode ? .bold : .medium)
                            .foregroundColor(selectedMode == mode ? .yellow : .gray)
                        
                        Rectangle()
                            .fill(Color.yellow)
                            .frame(width: selectedMode == mode ? 20 : 0, height: 2)
                    }
                    .onTapGesture {
                        selectedMode = mode
                    }
                }
            }
            .padding(.horizontal, 16)
        }
        .padding(.vertical, 12)
        .background(Color(red: 0.12, green: 0.14, blue: 0.16))
    }
}

// MARK: - Markets Panel
struct MarketsPanel: View {
    @EnvironmentObject var tradingViewModel: TradingViewModel
    @State private var searchText = ""
    @State private var selectedMarketTab: MarketTab = .spot
    
    var body: some View {
        VStack(spacing: 0) {
            // Search Bar
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.gray)
                TextField("Search pairs...", text: $searchText)
                    .textFieldStyle(PlainTextFieldStyle())
                    .foregroundColor(.white)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color(red: 0.04, green: 0.05, blue: 0.07))
            .cornerRadius(8)
            .padding(16)
            
            // Market Tabs
            HStack(spacing: 16) {
                ForEach([MarketTab.spot, .futures, .margin], id: \.self) { tab in
                    Text(tab.rawValue.uppercased())
                        .font(.caption)
                        .fontWeight(selectedMarketTab == tab ? .bold : .medium)
                        .foregroundColor(selectedMarketTab == tab ? .yellow : .gray)
                        .onTapGesture {
                            selectedMarketTab = tab
                        }
                }
                Spacer()
            }
            .padding(.horizontal, 16)
            
            Divider()
                .background(Color.gray)
            
            // Markets List
            ScrollView {
                LazyVStack(spacing: 0) {
                    ForEach(filteredMarkets, id: \.symbol) { market in
                        MarketRow(market: market)
                            .onTapGesture {
                                tradingViewModel.selectMarket(market)
                            }
                    }
                }
            }
        }
        .background(Color(red: 0.12, green: 0.14, blue: 0.16))
        .cornerRadius(12)
        .padding()
    }
    
    private var filteredMarkets: [MarketData] {
        tradingViewModel.markets.filter { market in
            market.symbol.localizedCaseInsensitiveContains(searchText) &&
            market.category == selectedMarketTab.rawValue
        }
    }
}

// MARK: - Market Row
struct MarketRow: View {
    let market: MarketData
    
    var body: some View {
        VStack(spacing: 0) {
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text(market.symbol)
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.white)
                    
                    Text("Vol \(market.volume)")
                        .font(.system(size: 12))
                        .foregroundColor(.gray)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 2) {
                    Text(String(format: "%.4f", market.price))
                        .font(.system(size: 14, weight: .medium))
                        .foregroundColor(.white)
                    
                    Text("\(market.change >= 0 ? "+" : "")\(String(format: "%.2f", market.change))%")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(market.change >= 0 ? .green : .red)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            
            Divider()
                .background(Color(red: 0.17, green: 0.19, blue: 0.22))
        }
        .contentShape(Rectangle())
    }
}

// MARK: - Chart Section
struct ChartSection: View {
    @EnvironmentObject var tradingViewModel: TradingViewModel
    @State private var selectedTimeFrame: TimeFrame = .m15
    
    var body: some View {
        VStack(spacing: 0) {
            // Header with Price Info
            HStack {
                VStack(alignment: .leading) {
                    Text(tradingViewModel.selectedMarket?.symbol ?? "BTC/USDT")
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                    
                    HStack(alignment: .bottom, spacing: 12) {
                        Text(String(format: "%.2f", tradingViewModel.selectedMarket?.price ?? 67234.56))
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                        
                        Text("\(tradingViewModel.selectedMarket?.change >= 0 ? "+" : "")\(String(format: "%.2f", tradingViewModel.selectedMarket?.change ?? 0))%")
                            .font(.caption)
                            .fontWeight(.medium)
                            .foregroundColor(tradingViewModel.selectedMarket?.change ?? 0 >= 0 ? .green : .red)
                    }
                }
                
                Spacer()
                
                HStack(spacing: 12) {
                    Button(action: {}) {
                        Image(systemName: "gear")
                            .foregroundColor(.white)
                    }
                    
                    Button(action: {}) {
                        Image(systemName: "arrow.up.left.and.arrow.down.right")
                            .foregroundColor(.white)
                    }
                }
            }
            .padding(16)
            
            // Time Frame Selector
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach([TimeFrame.m1, .m5, .m15, .h1, .h4, .d1, .w1], id: \.self) { frame in
                        Text(frame.rawValue)
                            .font(.caption)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(selectedTimeFrame == frame ? Color.yellow : Color.clear)
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 4)
                                    .stroke(Color.gray, lineWidth: 1)
                            )
                            .foregroundColor(selectedTimeFrame == frame ? .black : .gray)
                            .onTapGesture {
                                selectedTimeFrame = frame
                            }
                    }
                }
                .padding(.horizontal, 16)
            }
            .padding(.bottom, 8)
            
            // Chart Placeholder
            RoundedRectangle(cornerRadius: 8)
                .fill(Color(red: 0.04, green: 0.05, blue: 0.07))
                .frame(height: 300)
                .overlay(
                    VStack {
                        Image(systemName: "chart.line.uptrend.xyaxis")
                            .font(.largeTitle)
                            .foregroundColor(.gray)
                        Text("Real-time Price Chart")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Text("Trading data visualization")
                            .font(.caption2)
                            .foregroundColor(.gray)
                    }
                )
                .padding(.horizontal, 16)
                .padding(.bottom, 16)
        }
        .background(Color(red: 0.12, green: 0.14, blue: 0.16))
        .cornerRadius(12)
        .padding()
    }
}

// MARK: - Trading Panel
struct TradingPanel: View {
    @EnvironmentObject var tradingViewModel: TradingViewModel
    @Binding var selectedSide: OrderSide
    @Binding var selectedType: OrderType
    @State private var amountText = ""
    @State private var priceText = ""
    @State private var leverage: Double = 10
    
    var body: some View {
        VStack(spacing: 0) {
            // Buy/Sell Tabs
            HStack(spacing: 0) {
                ForEach([OrderSide.buy, .sell], id: \.self) { side in
                    VStack {
                        Text(side.rawValue.uppercased())
                            .font(.caption)
                            .fontWeight(selectedSide == side ? .bold : .medium)
                            .foregroundColor(selectedSide == side ? .yellow : .gray)
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 48)
                    .background(
                        selectedSide == side ? Color(red: 0.04, green: 0.05, blue: 0.07) : Color.clear
                    )
                    .onTapGesture {
                        selectedSide = side
                    }
                }
            }
            .background(Color(red: 0.12, green: 0.14, blue: 0.16))
            
            VStack(spacing: 16) {
                // Order Type Buttons
                HStack(spacing: 8) {
                    ForEach([OrderType.market, .limit, .stop], id: \.self) { type in
                        Text(type.rawValue.uppercased())
                            .font(.caption)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(
                                RoundedRectangle(cornerRadius: 4)
                                    .fill(selectedType == type ? Color.yellow : Color.clear)
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 4)
                                    .stroke(Color.gray, lineWidth: 1)
                            )
                            .foregroundColor(selectedType == type ? .black : .gray)
                            .onTapGesture {
                                selectedType = type
                            }
                    }
                }
                
                // Price Input (for limit orders)
                if selectedType != .market {
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Price (USDT)")
                            .font(.caption)
                            .foregroundColor(.gray)
                        
                        TextField("0.00", text: $priceText)
                            .textFieldStyle(PlainTextFieldStyle())
                            .foregroundColor(.white)
                            .padding()
                            .background(Color(red: 0.04, green: 0.05, blue: 0.07))
                            .cornerRadius(8)
                    }
                }
                
                // Amount Input
                VStack(alignment: .leading, spacing: 4) {
                    Text("Amount (BTC)")
                        .font(.caption)
                        .foregroundColor(.gray)
                    
                    TextField("0.00", text: $amountText)
                        .textFieldStyle(PlainTextFieldStyle())
                        .foregroundColor(.white)
                        .padding()
                        .background(Color(red: 0.04, green: 0.05, blue: 0.07))
                        .cornerRadius(8)
                }
                
                // Leverage (for futures/margin)
                if tradingViewModel.currentTradingMode in ["futures", "margin"] {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text("Leverage")
                                .font(.caption)
                                .foregroundColor(.gray)
                            Spacer()
                            Text("\(Int(leverage))x")
                                .font(.caption)
                                .foregroundColor(.white)
                        }
                        
                        Slider(value: $leverage, in: 1...125, step: 1)
                            .accentColor(.yellow)
                    }
                }
                
                // Total Display
                HStack {
                    Text("Total (USDT)")
                        .font(.caption)
                        .foregroundColor(.gray)
                    Spacer()
                    Text("0.00")
                        .font(.caption)
                        .foregroundColor(.white)
                }
                
                // Buy/Sell Button
                Button(action: {
                    tradingViewModel.placeOrder(
                        side: selectedSide,
                        type: selectedType,
                        amount: Double(amountText) ?? 0,
                        price: Double(priceText)
                    )
                }) {
                    HStack {
                        Image(systemName: selectedSide == .buy ? "cart" : "arrow.up.square")
                        Text("\(selectedSide.rawValue.uppercased()) BTC")
                    }
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(selectedSide == .buy ? Color.green : Color.red)
                    .foregroundColor(.white)
                    .cornerRadius(8)
                    .fontWeight(.bold)
                }
                
                // Balance Info
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text("Available")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Spacer()
                        Text("10,000.00 USDT")
                            .font(.caption)
                            .foregroundColor(.white)
                    }
                    
                    HStack {
                        Text("Fee")
                            .font(.caption)
                            .foregroundColor(.gray)
                        Spacer()
                        Text("0.1%")
                            .font(.caption)
                            .foregroundColor(.white)
                    }
                }
            }
            .padding(16)
        }
        .background(Color(red: 0.12, green: 0.14, blue: 0.16))
        .cornerRadius(12)
        .padding()
    }
}

// MARK: - Order Book Panel
struct OrderBookPanel: View {
    @State private var sellOrders: [OrderBookEntry] = []
    @State private var buyOrders: [OrderBookEntry] = []
    
    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                Text("Order Book")
                    .font(.headline)
                    .foregroundColor(.white)
                Spacer()
                Text("Depth 0.01")
                    .font(.caption)
                    .foregroundColor(.gray)
            }
            .padding(16)
            
            Divider()
                .background(Color.gray)
            
            // Order Book Content
            HStack(spacing: 0) {
                // Sell Orders
                VStack(spacing: 0) {
                    Text("SELL")
                        .font(.caption)
                        .fontWeight(.bold)
                        .foregroundColor(.red)
                        .padding(8)
                    
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            ForEach(sellOrders, id: \.id) { order in
                                OrderBookRow(order: order, isSell: true)
                            }
                        }
                    }
                }
                .frame(maxWidth: .infinity)
                
                Divider()
                    .background(Color.gray)
                
                // Buy Orders
                VStack(spacing: 0) {
                    Text("BUY")
                        .font(.caption)
                        .fontWeight(.bold)
                        .foregroundColor(.green)
                        .padding(8)
                    
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            ForEach(buyOrders, id: \.id) { order in
                                OrderBookRow(order: order, isSell: false)
                            }
                        }
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .background(Color(red: 0.12, green: 0.14, blue: 0.16))
        .cornerRadius(12)
        .padding()
        .onAppear {
            generateOrderBookData()
        }
    }
    
    private func generateOrderBookData() {
        let basePrice = 67234.56
        
        // Generate sell orders
        sellOrders = (0..<10).map { index in
            let price = basePrice + Double(index + 1) * 10
            let amount = Double.random(in: 0.1...2.0)
            return OrderBookEntry(
                id: UUID(),
                price: price,
                amount: amount,
                total: price * amount
            )
        }.reversed()
        
        // Generate buy orders
        buyOrders = (0..<10).map { index in
            let price = basePrice - Double(index + 1) * 10
            let amount = Double.random(in: 0.1...2.0)
            return OrderBookEntry(
                id: UUID(),
                price: price,
                amount: amount,
                total: price * amount
            )
        }
    }
}

// MARK: - Order Book Row
struct OrderBookRow: View {
    let order: OrderBookEntry
    let isSell: Bool
    
    var body: some View {
        HStack {
            Text(String(format: "%.2f", order.price))
                .font(.caption)
                .foregroundColor(isSell ? .red : .green)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            Text(String(format: "%.4f", order.amount))
                .font(.caption)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
            
            Text(String(format: "%.2f", order.total))
                .font(.caption)
                .foregroundColor(isSell ? .red : .green)
                .frame(maxWidth: .infinity, alignment: .trailing)
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 6)
        .contentShape(Rectangle())
    }
}

// MARK: - Login View
struct LoginView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @State private var email = ""
    @State private var password = ""
    @State private var showingRegistration = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 32) {
                // Logo
                VStack(spacing: 8) {
                    Image(systemName: "tiger.fill")
                        .foregroundColor(.yellow)
                        .font(.system(size: 60))
                    Text("TigerEx")
                        .foregroundColor(.yellow)
                        .font(.largeTitle)
                        .fontWeight(.bold)
                }
                
                // Login Form
                VStack(spacing: 16) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Email")
                            .font(.caption)
                            .foregroundColor(.gray)
                        
                        TextField("Enter your email", text: $email)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .foregroundColor(.white)
                            .padding()
                            .background(Color(red: 0.12, green: 0.14, blue: 0.16))
                            .cornerRadius(8)
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Password")
                            .font(.caption)
                            .foregroundColor(.gray)
                        
                        SecureField("Enter your password", text: $password)
                            .textFieldStyle(RoundedBorderTextFieldStyle())
                            .foregroundColor(.white)
                            .padding()
                            .background(Color(red: 0.12, green: 0.14, blue: 0.16))
                            .cornerRadius(8)
                    }
                    
                    Button(action: {
                        authViewModel.login(email: email, password: password)
                    }) {
                        Text("Login")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.yellow)
                            .foregroundColor(.black)
                            .cornerRadius(8)
                            .fontWeight(.bold)
                    }
                    
                    Button(action: {
                        showingRegistration = true
                    }) {
                        Text("Don't have an account? Register")
                            .foregroundColor(.yellow)
                    }
                }
                
                Spacer()
            }
            .padding()
            .background(Color(red: 0.04, green: 0.05, blue: 0.07))
            .navigationBarHidden(true)
        }
        .sheet(isPresented: $showingRegistration) {
            RegisterView()
        }
    }
}

// MARK: - Register View
struct RegisterView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    @Environment(\.presentationMode) var presentationMode
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 32) {
                // Header
                VStack(spacing: 8) {
                    Text("Create Account")
                        .foregroundColor(.white)
                        .font(.title)
                        .fontWeight(.bold)
                    Text("Join TigerEx and start trading")
                        .foregroundColor(.gray)
                        .font(.caption)
                }
                
                // Registration Form
                VStack(spacing: 16) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Email")
                            .font(.caption)
                            .foregroundColor(.gray)
                        
                        TextField("Enter your email", text: $email)
                            .textFieldStyle(PlainTextFieldStyle())
                            .foregroundColor(.white)
                            .padding()
                            .background(Color(red: 0.12, green: 0.14, blue: 0.16))
                            .cornerRadius(8)
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Password")
                            .font(.caption)
                            .foregroundColor(.gray)
                        
                        SecureField("Enter your password", text: $password)
                            .textFieldStyle(PlainTextFieldStyle())
                            .foregroundColor(.white)
                            .padding()
                            .background(Color(red: 0.12, green: 0.14, blue: 0.16))
                            .cornerRadius(8)
                    }
                    
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Confirm Password")
                            .font(.caption)
                            .foregroundColor(.gray)
                        
                        SecureField("Confirm your password", text: $confirmPassword)
                            .textFieldStyle(PlainTextFieldStyle())
                            .foregroundColor(.white)
                            .padding()
                            .background(Color(red: 0.12, green: 0.14, blue: 0.16))
                            .cornerRadius(8)
                    }
                    
                    Button(action: {
                        if password == confirmPassword {
                            authViewModel.register(email: email, password: password)
                            presentationMode.wrappedValue.dismiss()
                        }
                    }) {
                        Text("Register")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.yellow)
                            .foregroundColor(.black)
                            .cornerRadius(8)
                            .fontWeight(.bold)
                    }
                    .disabled(password != confirmPassword)
                }
                
                Spacer()
            }
            .padding()
            .background(Color(red: 0.04, green: 0.05, blue: 0.07))
            .navigationBarHidden(true)
        }
    }
}

// MARK: - Placeholder Views
struct PortfolioView: View {
    var body: some View {
        VStack {
            Text("Portfolio")
                .font(.title)
                .foregroundColor(.white)
            Text("Coming Soon")
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(red: 0.04, green: 0.05, blue: 0.07))
    }
}

struct OrdersView: View {
    var body: some View {
        VStack {
            Text("Orders")
                .font(.title)
                .foregroundColor(.white)
            Text("Coming Soon")
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(red: 0.04, green: 0.05, blue: 0.07))
    }
}

struct ProfileView: View {
    @EnvironmentObject var authViewModel: AuthViewModel
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Profile")
                .font(.title)
                .foregroundColor(.white)
            
            Button("Logout") {
                authViewModel.logout()
            }
            .foregroundColor(.red)
            
            Spacer()
        }
        .padding()
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Color(red: 0.04, green: 0.05, blue: 0.07))
    }
}

// MARK: - Data Models
enum TradingMode: String, CaseIterable {
    case spot = "spot"
    case futures = "futures"
    case margin = "margin"
    case options = "options"
    case alpha = "alpha"
    case etf = "etf"
    case tradex = "tradex"
}

enum MarketTab: String, CaseIterable {
    case spot = "spot"
    case futures = "futures"
    case margin = "margin"
}

enum OrderSide: String, CaseIterable {
    case buy = "buy"
    case sell = "sell"
}

enum OrderType: String, CaseIterable {
    case market = "market"
    case limit = "limit"
    case stop = "stop"
}

enum TimeFrame: String, CaseIterable {
    case m1 = "1m"
    case m5 = "5m"
    case m15 = "15m"
    case h1 = "1h"
    case h4 = "4h"
    case d1 = "1d"
    case w1 = "1w"
}

struct MarketData {
    let symbol: String
    let price: Double
    let change: Double
    let volume: String
    let category: String
}

struct OrderBookEntry {
    let id: UUID
    let price: Double
    let amount: Double
    let total: Double
}

// MARK: - View Models
class AuthViewModel: ObservableObject {
    @Published var isAuthenticated = false
    
    func login(email: String, password: String) {
        // Simulate login
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.isAuthenticated = true
        }
    }
    
    func register(email: String, password: String) {
        // Simulate registration
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.isAuthenticated = true
        }
    }
    
    func logout() {
        isAuthenticated = false
    }
}

class TradingViewModel: ObservableObject {
    @Published var markets: [MarketData] = []
    @Published var selectedMarket: MarketData?
    @Published var currentTradingMode: String = "spot"
    
    init() {
        loadMarkets()
    }
    
    private func loadMarkets() {
        markets = [
            MarketData(symbol: "BTC/USDT", price: 67234.56, change: 2.34, volume: "1.2B", category: "spot"),
            MarketData(symbol: "ETH/USDT", price: 3456.78, change: -1.23, volume: "856M", category: "spot"),
            MarketData(symbol: "BNB/USDT", price: 567.89, change: 0.87, volume: "234M", category: "spot"),
            MarketData(symbol: "SOL/USDT", price: 123.45, change: 5.67, volume: "456M", category: "spot"),
            MarketData(symbol: "ADA/USDT", price: 0.456, change: -2.34, volume: "123M", category: "spot"),
            MarketData(symbol: "XRP/USDT", price: 0.789, change: 1.23, volume: "345M", category: "spot"),
            MarketData(symbol: "DOGE/USDT", price: 0.089, change: 8.90, volume: "567M", category: "spot"),
            MarketData(symbol: "AVAX/USDT", price: 34.56, change: -0.45, volume: "89M", category: "spot"),
            MarketData(symbol: "DOT/USDT", price: 7.89, change: 2.34, volume: "67M", category: "spot"),
            MarketData(symbol: "MATIC/USDT", price: 0.876, change: -1.56, volume: "234M", category: "spot")
        ]
        
        if !markets.isEmpty {
            selectedMarket = markets[0]
        }
    }
    
    func selectMarket(_ market: MarketData) {
        selectedMarket = market
    }
    
    func updateTradingMode(_ mode: TradingMode) {
        currentTradingMode = mode.rawValue
    }
    
    func placeOrder(side: OrderSide, type: OrderType, amount: Double, price: Double?) {
        // Simulate order placement
        print("Order placed: \(side.rawValue) \(type.rawValue) \(amount) @ \(price ?? 0)")
    }
}

// MARK: - Preview
struct TradingView_Previews: PreviewProvider {
    static var previews: some View {
        TradingView()
            .environmentObject(AuthViewModel())
            .environmentObject(TradingViewModel())
            .preferredColorScheme(.dark)
    }
}