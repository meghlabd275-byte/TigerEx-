import SwiftUI

// MARK: - Theme Colors
struct ThemeColors {
    static let primary = Color(hex: "F6821F")
    static let accent = Color(hex: "00D4AA")
    
    struct Dark {
        static let background = Color(hex: "050A12")
        static let surface = Color(hex: "0D1B2A")
        static let card = Color(hex: "0D1B2A")
        static let textPrimary = Color(hex: "E8EEF4")
        static let textSecondary = Color.white.opacity(0.7)
    }
    
    struct Light {
        static let background = Color(hex: "F5F7FA")
        static let surface = Color.white
        static let card = Color.white
        static let textPrimary = Color(hex: "1A1A2E")
        static let textSecondary = Color(hex: "666666")
    }
}

// MARK: - Platform Links
struct PlatformLink: Identifiable {
    let id = UUID()
    let name: String
    let url: String
    let icon: String
    let description: String
}

struct PlatformData {
    static let homeLinks = [
        PlatformLink(name: "Bitget", url: "https://www.bitget.com/", icon: "🐯", description: "Main exchange")
    ]
    static let marketLinks = [
        PlatformLink(name: "Binance Markets", url: "https://www.binance.com/en/markets/overview", icon: "📊", description: "Markets overview")
    ]
    static let tradeLinks = [
        PlatformLink(name: "Futures", url: "https://www.bitget.com/futures/usdt/BTCUSDT", icon: "📈", description: "USDT-M Futures"),
        PlatformLink(name: "Spot", url: "https://www.bitget.com/spot/BTCUSDT", icon: "💎", description: "Spot trading"),
        PlatformLink(name: "Margin", url: "https://www.bitget.com/spot/BTCUSDT?type=cross", icon: "⚡", description: "Cross margin"),
        PlatformLink(name: "P2P", url: "https://p2p.binance.com/en", icon: "🤝", description: "P2P Trading"),
        PlatformLink(name: "On-Chain", url: "https://www.bitget.com/on-chain/sol/2pFFgMtw7GkE6Kr6Xpg81mqDvEihhoafg64HdheKpump", icon: "⛓️", description: "On-chain trading"),
        PlatformLink(name: "Alpha", url: "https://www.binance.com/en/alpha/bsc/0xd20fb09a49a8e75fef536a2dbc68222900287bac", icon: "🚀", description: "Alpha trading")
    ]
    static let tradfiLinks = [
        PlatformLink(name: "CFD", url: "https://www.bitgettradfi.com/tradfi/XAUUSD", icon: "📊", description: "CFD Trading"),
        PlatformLink(name: "Stocks", url: "https://www.bitget.com/on-chain/bnb/0xa9ee28c80f960b889dfbd1902055218cba016f75", icon: "🏢", description: "Stock tokens"),
        PlatformLink(name: "Stock Preps", url: "https://www.bitget.com/futures/usdt/NVDAUSDT", icon: "🧪", description: "NVDA futures")
    ]
    static let assetLinks = [
        PlatformLink(name: "Assets", url: "https://www.bitget.com/asset", icon: "💰", description: "All wallets"),
        PlatformLink(name: "Deposit", url: "https://www.bitget.com/asset", icon: "📥", description: "Deposit"),
        PlatformLink(name: "Withdrawal", url: "https://www.bitget.com/asset", icon: "📤", description: "Withdraw"),
        PlatformLink(name: "Spot Wallet", url: "https://www.bitget.com/asset", icon: "💵", description: "Spot balance"),
        PlatformLink(name: "Futures Wallet", url: "https://www.bitget.com/asset", icon: "📈", description: "Futures balance"),
        PlatformLink(name: "TigerPay", url: "https://www.bitget.com/asset", icon: "🐯", description: "Payment"),
        PlatformLink(name: "TradFi", url: "https://www.bitget.com/asset", icon: "📊", description: "CFD balance"),
        PlatformLink(name: "Crypto Card", url: "https://www.bitget.com/asset", icon: "💳", description: "Card")
    ]
}

// MARK: - Main View
struct ContentView: View {
    @State private var selectedTab = 0
    @State private var isDarkMode = true
    
    var body: some View {
        ZStack {
            (isDarkMode ? ThemeColors.Dark.background : ThemeColors.Light.background).ignoresSafeArea()
            TabView(selection: $selectedTab) {
                HomeView(isDarkMode: isDarkMode).tabItem { Label("Home", systemImage: "house.fill") }.tag(0)
                MarketsView(isDarkMode: isDarkMode).tabItem { Label("Markets", systemImage: "chart.bar.fill") }.tag(1)
                TradeView(isDarkMode: isDarkMode).tabItem { Label("Trade", systemImage: "arrow.left.arrow.right") }.tag(2)
                AssetsView(isDarkMode: isDarkMode).tabItem { Label("Assets", systemImage: "creditcard.fill") }.tag(3)
            }
            .accentColor(ThemeColors.primary)
        }
        .preferredColorScheme(.dark)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: { isDarkMode.toggle() }) {
                    Image(systemName: isDarkMode ? "moon.fill" : "sun.max.fill").foregroundColor(ThemeColors.primary)
                }
            }
        }
    }
}

// MARK: - View Components
struct HomeView: View {
    let isDarkMode: Bool
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                HStack { Text("🐯 TigerEx").font(.largeTitle).fontWeight(.bold).foregroundColor(ThemeColors.primary); Spacer() }.padding()
                HStack(spacing: 16) {
                    StatCard(value: "8+", label: "Platforms", isDarkMode: isDarkMode)
                    StatCard(value: "50+", label: "Markets", isDarkMode: isDarkMode)
                    StatCard(value: "24/7", label: "Support", isDarkMode: isDarkMode)
                }.padding(.horizontal)
                LazyVStack(spacing: 12) { ForEach(PlatformData.homeLinks) { link in LinkCard(link: link, isDarkMode: isDarkMode) } }.padding(.horizontal)
            }
        }
    }
}

struct MarketsView: View {
    let isDarkMode: Bool
    var body: some View {
        ScrollView { LazyVStack(spacing: 12) { ForEach(PlatformData.marketLinks) { link in LinkCard(link: link, isDarkMode: isDarkMode) } }.padding() }
    }
}

struct TradeView: View {
    let isDarkMode: Bool
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                Text("Trade").font(.title).fontWeight(.bold).foregroundColor(isDarkMode ? ThemeColors.Dark.textPrimary : ThemeColors.Light.textPrimary).padding(.horizontal)
                SectionView(title: "Trading", links: PlatformData.tradeLinks, isDarkMode: isDarkMode)
                SectionView(title: "TradFi", links: PlatformData.tradfiLinks, isDarkMode: isDarkMode)
            }.padding()
        }
    }
}

struct AssetsView: View {
    let isDarkMode: Bool
    var body: some View {
        ScrollView { LazyVStack(spacing: 12) { ForEach(PlatformData.assetLinks) { link in LinkCard(link: link, isDarkMode: isDarkMode) } }.padding() }
    }
}

struct SectionView: View {
    let title: String
    let links: [PlatformLink]
    let isDarkMode: Bool
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(title).font(.headline).foregroundColor(isDarkMode ? ThemeColors.Dark.textPrimary : ThemeColors.Light.textPrimary)
            ForEach(links) { link in LinkCard(link: link, isDarkMode: isDarkMode) }
        }
    }
}

struct StatCard: View {
    let value: String
    let label: String
    let isDarkMode: Bool
    var body: some View {
        VStack {
            Text(value).font(.title2).fontWeight(.bold).foregroundColor(ThemeColors.primary)
            Text(label).font(.caption).foregroundColor(isDarkMode ? ThemeColors.Dark.textSecondary : ThemeColors.Light.textSecondary)
        }.frame(maxWidth: .infinity).padding().background(isDarkMode ? ThemeColors.Dark.card : ThemeColors.Light.card).cornerRadius(12)
    }
}

struct LinkCard: View {
    let link: PlatformLink
    let isDarkMode: Bool
    var body: some View {
        Link(destination: URL(string: link.url)!) {
            HStack {
                Text(link.icon).font(.title2)
                VStack(alignment: .leading) {
                    Text(link.name).font(.headline).foregroundColor(isDarkMode ? ThemeColors.Dark.textPrimary : ThemeColors.Light.textPrimary)
                    Text(link.description).font(.caption).foregroundColor(isDarkMode ? ThemeColors.Dark.textSecondary : ThemeColors.Light.textSecondary)
                }
                Spacer()
                Image(systemName: "chevron.right").foregroundColor(isDarkMode ? ThemeColors.Dark.textSecondary : ThemeColors.Light.textSecondary)
            }.padding().background(isDarkMode ? ThemeColors.Dark.card : ThemeColors.Light.card).cornerRadius(12)
        }
    }
}

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default: (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(.sRGB, red: Double(r) / 255, green: Double(g) / 255, blue: Double(b) / 255, opacity: Double(a) / 255)
    }
}

@main
struct TradingDashboardApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
    }
}