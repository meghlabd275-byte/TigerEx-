import React, { useState, useEffect } from 'react';
import { 
  View, Text, TouchableOpacity, TextInput, 
  ScrollView, FlatList, Switch, Alert, Linking,
  StyleSheet, SafeAreaView, StatusBar, Platform,
  Image, Animated, Dimensions 
} from 'react-native';

// Theme colors
const darkTheme = {
  bgPrimary: '#050A12',
  bgSecondary: '#0D1B2A',
  bgTertiary: '#141E2B',
  textPrimary: '#E8EEF4',
  textSecondary: 'rgba(255,255,255,0.7)',
  textMuted: 'rgba(255,255,255,0.5)',
  border: 'rgba(255,255,255,0.08)',
  primary: '#F6821F',
  success: '#43A047',
  danger: '#E53935',
};

const lightTheme = {
  bgPrimary: '#F5F7FA',
  bgSecondary: '#FFFFFF',
  bgTertiary: '#F0F2F5',
  textPrimary: '#1A1A2E',
  textSecondary: '#666666',
  textMuted: '#999999',
  border: '#E0E0E0',
  primary: '#F6821F',
  success: '#43A047',
  danger: '#E53935',
};

// Context
export const ThemeContext = React.createContext(darkTheme);

// Main App Component
export default function App() {
  const [theme, setTheme] = useState('dark');
  const [currentScreen, setCurrentScreen] = useState('home');
  const colors = theme === 'dark' ? darkTheme : lightTheme;

  useEffect(() => {
    // Load saved theme
    const saved = 'dark'; // AsyncStorage.getItem('theme')
    setTheme(saved);
  }, []);

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  const navigate = (screen) => setCurrentScreen(screen);

  return (
    <ThemeContext.Provider value={colors}>
      <SafeAreaView style={[styles.container, { backgroundColor: colors.bgPrimary }]}>
        <StatusBar 
          barStyle={theme === 'dark' ? 'light-content' : 'dark-content'} 
          backgroundColor={colors.bgSecondary}
        />
        
        {/* Header */}
        <View style={[styles.header, { backgroundColor: colors.bgSecondary, borderBottomColor: colors.border }]}>
          <TouchableOpacity onPress={() => navigate('home')}>
            <View style={styles.logoRow}>
              <View style={[styles.logoIcon, { backgroundColor: colors.primary }]}>
                <Text style={styles.logoText}>🐯</Text>
              </View>
              <Text style={[styles.logoTitle, { color: colors.primary }]}>TigerEx</Text>
            </View>
          </TouchableOpacity>
          
          <View style={styles.headerRight}>
            <TouchableOpacity style={styles.headerBtn} onPress={() => Alert.alert('📷', 'QR Scanner')}>
              <Text>📷</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.headerBtn} onPress={() => navigate('notifications')}>
              <Text>🔔</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.headerBtn} onPress={() => Alert.alert('💬', 'Support')}>
              <Text>💬</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.themeBtn} onPress={toggleTheme}>
              <Text>{theme === 'dark' ? '🌙' : '☀️'}</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Main Content */}
        <ScrollView style={styles.content}>
          {currentScreen === 'home' && <HomeScreen colors={colors} />}
          {currentScreen === 'trade' && <TradeScreen colors={colors} />}
          {currentScreen === 'assets' && <AssetsScreen colors={colors} />}
          {currentScreen === 'profile' && <ProfileScreen colors={colors} />}
          {currentScreen === 'more' && <MoreScreen colors={colors} />}
          {currentScreen === 'notifications' && <NotificationsScreen colors={colors} />}
        </ScrollView>

        {/* Bottom Navigation */}
        <View style={[styles.bottomNav, { backgroundColor: colors.bgSecondary, borderTopColor: colors.border }]}>
          <TouchableOpacity style={styles.navItem} onPress={() => navigate('home')}>
            <Text style={[styles.navIcon, currentScreen === 'home' && { color: colors.primary }]}>🏠</Text>
            <Text style={[styles.navLabel, currentScreen === 'home' && { color: colors.primary }]}>Home</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.navItem} onPress={() => navigate('trade')}>
            <Text style={[styles.navIcon, currentScreen === 'trade' && { color: colors.primary }]}>📈</Text>
            <Text style={[styles.navLabel, currentScreen === 'trade' && { color: colors.primary }]}>Trade</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.navItem} onPress={() => navigate('assets')}>
            <Text style={[styles.navIcon, currentScreen === 'assets' && { color: colors.primary }]}>💰</Text>
            <Text style={[styles.navLabel, currentScreen === 'assets' && { color: colors.primary }]}>Assets</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.navItem} onPress={() => navigate('more')}>
            <Text style={[styles.navIcon, currentScreen === 'more' && { color: colors.primary }]}>📋</Text>
            <Text style={[styles.navLabel, currentScreen === 'more' && { color: colors.primary }]}>More</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.navItem} onPress={() => navigate('profile')}>
            <Text style={[styles.navIcon, currentScreen === 'profile' && { color: colors.primary }]}>👤</Text>
            <Text style={[styles.navLabel, currentScreen === 'profile' && { color: colors.primary }]}>Profile</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    </ThemeContext.Provider>
  );
}

// Home Screen
function HomeScreen({ colors }) {
  const stats = [
    { label: 'Balance', value: '$45,678', icon: '💰' },
    { label: "Today's P&L", value: '+$2,345', icon: '📈' },
    { label: 'Orders', value: '15', icon: '🤝' },
    { label: 'VIP', value: 'Level 3', icon: '⭐' },
  ];

  const markets = [
    { name: 'Bitcoin', symbol: 'BTC', price: '$67,432', change: '+2.3%' },
    { name: 'Ethereum', symbol: 'ETH', price: '$3,456', change: '+1.8%' },
    { name: 'Solana', symbol: 'SOL', price: '$138', change: '-3.2%' },
  ];

  const categories = [
    { name: 'Futures', icon: '📈', desc: '125x' },
    { name: 'Spot', icon: '💎', desc: '500+' },
    { name: 'P2P', icon: '🤝', desc: '0 fees' },
    { name: 'TradFi', icon: '📊', desc: 'CFD' },
    { name: 'Staking', icon: '🔒', desc: '20%' },
    { name: 'Card', icon: '💳', desc: '3%' },
  ];

  return (
    <View style={styles.screen}>
      <View style={styles.statsRow}>
        {stats.map((stat, i) => (
          <View key={i} style={[styles.statCard, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
            <Text style={styles.statIcon}>{stat.icon}</Text>
            <Text style={[styles.statValue, { color: colors.primary }]}>{stat.value}</Text>
            <Text style={[styles.statLabel, { color: colors.textMuted }]}>{stat.label}</Text>
          </View>
        ))}
      </View>

      <View style={styles.quickActions}>
        <TouchableOpacity style={[styles.actionBtn, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
          <Text style={styles.actionText}>📈 Trade</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.actionBtn, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
          <Text style={styles.actionText}>💰 Deposit</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.actionBtn, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
          <Text style={styles.actionText}>📤 Withdraw</Text>
        </TouchableOpacity>
      </View>

      <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>Top Markets</Text>
      {markets.map((market, i) => (
        <View key={i} style={[styles.marketCard, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
          <View style={styles.marketInfo}>
            <Text style={[styles.marketName, { color: colors.textPrimary }]}>{market.name}</Text>
            <Text style={[styles.marketSymbol, { color: colors.textMuted }]}>{market.symbol}/USDT</Text>
          </View>
          <View style={styles.marketPrice}>
            <Text style={[styles.price, { color: colors.textPrimary }]}>{market.price}</Text>
            <Text style={[styles.change, { color: market.change.startsWith('+') ? colors.success : colors.danger }]}>
              {market.change}
            </Text>
          </View>
        </View>
      ))}

      <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>Services</Text>
      <View style={styles.categoriesGrid}>
        {categories.map((cat, i) => (
          <TouchableOpacity key={i} style={[styles.categoryCard, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
            <Text style={styles.categoryIcon}>{cat.icon}</Text>
            <Text style={[styles.categoryName, { color: colors.textPrimary }]}>{cat.name}</Text>
            <Text style={[styles.categoryDesc, { color: colors.textMuted }]}>{cat.desc}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

// Trade Screen
function TradeScreen({ colors }) {
  const [orderType, setOrderType] = useState('limit');
  const [side, setSide] = useState('buy');

  return (
    <View style={styles.screen}>
      <View style={[styles.chart, { backgroundColor: colors.bgTertiary }]}>
        <Text style={[styles.chartText, { color: colors.textMuted }]}>📈 TradingView Chart</Text>
      </View>

      <View style={styles.orderTypeRow}>
        {['Limit', 'Market', 'Stop'].map((type) => (
          <TouchableOpacity 
            key={type}
            style={[styles.orderTypeBtn, orderType === type.toLowerCase() && { backgroundColor: colors.primary }]}
            onPress={() => setOrderType(type.toLowerCase())}
          >
            <Text style={[styles.orderTypeText, { color: orderType === type.toLowerCase() ? colors.bgSecondary : colors.textSecondary }]}>{type}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={styles.sideRow}>
        <TouchableOpacity 
          style={[styles.sideBtn, { backgroundColor: colors.success }, side === 'buy' && styles.sideActive]}
          onPress={() => setSide('buy')}
        >
          <Text style={styles.sideText}>Buy BTC</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.sideBtn, { backgroundColor: colors.danger }, side === 'sell' && styles.sideActive]}
          onPress={() => setSide('sell')}
        >
          <Text style={styles.sideText}>Sell BTC</Text>
        </TouchableOpacity>
      </View>

      <View style={[styles.input, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
        <Text style={[styles.inputLabel, { color: colors.textMuted }]}>Price</Text>
        <TextInput style={[styles.inputField, { color: colors.textPrimary }]} placeholder="67,432.50" placeholderTextColor={colors.textMuted} />
      </View>

      <View style={[styles.input, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
        <Text style={[styles.inputLabel, { color: colors.textMuted }]}>Amount</Text>
        <TextInput style={[styles.inputField, { color: colors.textPrimary }]} placeholder="0.00" placeholderTextColor={colors.textMuted} />
      </View>

      <View style={styles.percentRow}>
        {[25, 50, 75, 100].map((p) => (
          <TouchableOpacity key={p} style={[styles.percentBtn, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
            <Text style={[styles.percentText, { color: colors.textSecondary }]}>{p}%</Text>
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity style={[styles.submitBtn, { backgroundColor: side === 'buy' ? colors.success : colors.danger }]}>
        <Text style={styles.submitText}>{side === 'buy' ? 'Buy' : 'Sell'} BTC</Text>
      </TouchableOpacity>
    </View>
  );
}

// Assets Screen
function AssetsScreen({ colors }) {
  const wallets = [
    { name: 'Spot Wallet', balance: '$12,345', icon: '💵' },
    { name: 'Futures Wallet', balance: '$8,234', icon: '📈' },
    { name: 'P2P Wallet', balance: '$2,500', icon: '🤝' },
    { name: 'TigerPay', balance: '$5,000', icon: '🐯' },
    { name: 'TradFi', balance: '$15,678', icon: '📊' },
    { name: 'Crypto Card', balance: '$1,920', icon: '💳' },
  ];

  return (
    <View style={styles.screen}>
      <View style={[styles.totalCard, { backgroundColor: colors.primary }]}>
        <Text style={styles.totalLabel}>Total Balance</Text>
        <Text style={styles.totalValue}>$45,678.90</Text>
      </View>

      <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>Wallets</Text>
      {wallets.map((wallet, i) => (
        <View key={i} style={[styles.walletCard, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
          <Text style={styles.walletIcon}>{wallet.icon}</Text>
          <View style={styles.walletInfo}>
            <Text style={[styles.walletName, { color: colors.textPrimary }]}>{wallet.name}</Text>
            <Text style={[styles.walletBalance, { color: colors.primary }]}>{wallet.balance}</Text>
          </View>
        </View>
      ))}
    </View>
  );
}

// Profile Screen
function ProfileScreen({ colors }) {
  return (
    <View style={styles.screen}>
      <View style={[styles.profileCard, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
        <View style={[styles.avatar, { backgroundColor: colors.primary }]}>
          <Text style={styles.avatarText}>JD</Text>
        </View>
        <Text style={[styles.profileName, { color: colors.textPrimary }]}>John Doe</Text>
        <Text style={[styles.profileEmail, { color: colors.textMuted }]}>john.doe@email.com</Text>
        <View style={[styles.badge, { backgroundColor: `${colors.primary}20` }]}>
          <Text style={[styles.badgeText, { color: colors.primary }]}>⭐ VIP Level 3</Text>
        </View>
      </View>

      <View style={[styles.menuCard, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
        {[
          { icon: '🆔', name: 'KYC Verification', badge: 'Verified' },
          { icon: '🔑', name: 'API Keys', badge: '' },
          { icon: '📱', name: 'Devices', badge: '' },
          { icon: '🔐', name: 'Security', badge: '' },
          { icon: '⚙️', name: 'Preferences', badge: '' },
          { icon: '❓', name: 'Help Center', badge: '' },
          { icon: '💡', name: 'Feedback', badge: '' },
        ].map((item, i) => (
          <TouchableOpacity key={i} style={[styles.menuItem, { borderBottomColor: colors.border }]}>
            <Text style={styles.menuIcon}>{item.icon}</Text>
            <Text style={[styles.menuLabel, { color: colors.textPrimary }]}>{item.name}</Text>
            {item.badge && <View style={[styles.menuBadge, { backgroundColor: colors.success }]}><Text style={styles.menuBadgeText}>{item.badge}</Text></View>}
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity style={[styles.logoutBtn, { backgroundColor: `${colors.danger}20` }]}>
        <Text style={[styles.logoutText, { color: colors.danger }]}>🚪 Logout</Text>
      </TouchableOpacity>
    </View>
  );
}

// More Screen
function MoreScreen({ colors }) {
  const services = [
    { icon: '📈', name: 'Futures' },
    { icon: '💎', name: 'Spot' },
    { icon: '⚡', name: 'Margin' },
    { icon: '🤝', name: 'P2P' },
    { icon: '🔒', name: 'Staking' },
    { icon: '👥', name: 'Copy' },
    { icon: '💳', name: 'Card' },
    { icon: '🐯', name: 'TigerPay' },
    { icon: '📱', name: 'Top Up' },
    { icon: '🏦', name: 'Loans' },
    { icon: '💬', name: 'Support' },
    { icon: '❓', name: 'Help' },
  ];

  return (
    <View style={styles.screen}>
      <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>All Services</Text>
      <View style={styles.servicesGrid}>
        {services.map((service, i) => (
          <TouchableOpacity key={i} style={[styles.serviceCard, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
            <Text style={styles.serviceIcon}>{service.icon}</Text>
            <Text style={[styles.serviceName, { color: colors.textPrimary }]}>{service.name}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
}

// Notifications Screen
function NotificationsScreen({ colors }) {
  const notifications = [
    { title: 'BTC reached $67,000!', desc: 'Price alert triggered', icon: '📈' },
    { title: 'Order filled', desc: 'Bought 0.5 ETH', icon: '✅' },
    { title: 'Verification complete', desc: 'Level 2 verified', icon: '🆔' },
  ];

  return (
    <View style={styles.screen}>
      <Text style={[styles.sectionTitle, { color: colors.textPrimary }]}>Notifications</Text>
      {notifications.map((n, i) => (
        <View key={i} style={[styles.notifCard, { backgroundColor: colors.bgCard, borderColor: colors.border }]}>
          <Text style={styles.notifIcon}>{n.icon}</Text>
          <View style={styles.notifInfo}>
            <Text style={[styles.notifTitle, { color: colors.textPrimary }]}>{n.title}</Text>
            <Text style={[styles.notifDesc, { color: colors.textMuted }]}>{n.desc}</Text>
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  header: { 
    flexDirection: 'row', 
    justifyContent: 'space-between', 
    alignItems: 'center', 
    padding: 12, 
    paddingTop: Platform.OS === 'android' ? 40 : 50,
  },
  logoRow: { flexDirection: 'row', alignItems: 'center' },
  logoIcon: { width: 32, height: 32, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  logoText: { fontSize: 18 },
  logoTitle: { fontSize: 18, fontWeight: '800', marginLeft: 8 },
  headerRight: { flexDirection: 'row', alignItems: 'center' },
  headerBtn: { width: 36, height: 36, borderRadius: 8, alignItems: 'center', justifyContent: 'center', marginLeft: 8 },
  themeBtn: { paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8, marginLeft: 8 },
  content: { flex: 1 },
  screen: { padding: 16 },
  statsRow: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', marginBottom: 16 },
  statCard: { width: '48%', padding: 16, borderRadius: 12, borderWidth: 1, marginBottom: 8 },
  statIcon: { fontSize: 24, marginBottom: 4 },
  statValue: { fontSize: 18, fontWeight: '700' },
  statLabel: { fontSize: 12 },
  quickActions: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 16 },
  actionBtn: { flex: 1, padding: 14, borderRadius: 10, marginHorizontal: 4, alignItems: 'center' },
  actionText: { fontWeight: '600', fontSize: 14 },
  sectionTitle: { fontSize: 16, fontWeight: '600', marginBottom: 12, marginTop: 8 },
  marketCard: { flexDirection: 'row', justifyContent: 'space-between', padding: 14, borderRadius: 10, borderWidth: 1, marginBottom: 8 },
  marketInfo: {},
  marketName: { fontSize: 15, fontWeight: '600' },
  marketSymbol: { fontSize: 12 },
  marketPrice: { alignItems: 'flex-end' },
  price: { fontSize: 15, fontWeight: '600' },
  change: { fontSize: 12 },
  categoriesGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  categoryCard: { width: '31%', padding: 14, borderRadius: 10, borderWidth: 1, alignItems: 'center', marginBottom: 8 },
  categoryIcon: { fontSize: 24 },
  categoryName: { fontSize: 12, marginTop: 4 },
  categoryDesc: { fontSize: 10 },
  bottomNav: { 
    flexDirection: 'row', 
    justifyContent: 'space-around', 
    paddingVertical: 8, 
    borderTopWidth: 1,
  },
  navItem: { alignItems: 'center', padding: 4 },
  navIcon: { fontSize: 20 },
  navLabel: { fontSize: 10, marginTop: 2 },
  chart: { height: 250, borderRadius: 12, alignItems: 'center', justifyContent: 'center', marginBottom: 16 },
  chartText: { fontSize: 14 },
  orderTypeRow: { flexDirection: 'row', marginBottom: 12 },
  orderTypeBtn: { flex: 1, padding: 10, borderRadius: 8, alignItems: 'center', marginHorizontal: 2 },
  orderTypeText: { fontWeight: '600', fontSize: 13 },
  sideRow: { flexDirection: 'row', marginBottom: 12 },
  sideBtn: { flex: 1, padding: 14, borderRadius: 10, alignItems: 'center' },
  sideActive: { opacity: 0.8 },
  sideText: { color: 'white', fontWeight: '700' },
  input: { padding: 12, borderRadius: 10, borderWidth: 1, marginBottom: 8 },
  inputLabel: { fontSize: 12, marginBottom: 4 },
  inputField: { fontSize: 16 },
  percentRow: { flexDirection: 'row', marginBottom: 12 },
  percentBtn: { flex: 1, padding: 8, borderRadius: 6, alignItems: 'center', marginHorizontal: 2 },
  percentText: { fontSize: 12 },
  submitBtn: { padding: 16, borderRadius: 10, alignItems: 'center' },
  submitText: { color: 'white', fontWeight: '700', fontSize: 16 },
  totalCard: { padding: 20, borderRadius: 12, alignItems: 'center', marginBottom: 16 },
  totalLabel: { fontSize: 14, opacity: 0.8 },
  totalValue: { fontSize: 28, fontWeight: '700', color: '#050A12' },
  walletCard: { flexDirection: 'row', alignItems: 'center', padding: 14, borderRadius: 10, borderWidth: 1, marginBottom: 8 },
  walletIcon: { fontSize: 24, marginRight: 12 },
  walletInfo: { flex: 1 },
  walletName: { fontSize: 14 },
  walletBalance: { fontSize: 16, fontWeight: '700' },
  profileCard: { alignItems: 'center', padding: 24, borderRadius: 12, borderWidth: 1, marginBottom: 16 },
  avatar: { width: 70, height: 70, borderRadius: 35, alignItems: 'center', justifyContent: 'center', marginBottom: 12 },
  avatarText: { fontSize: 28, color: '#050A12', fontWeight: '700' },
  profileName: { fontSize: 20, fontWeight: '700' },
  profileEmail: { fontSize: 14, marginBottom: 8 },
  badge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  badgeText: { fontSize: 12, fontWeight: '600' },
  menuCard: { borderRadius: 12, borderWidth: 1, marginBottom: 16 },
  menuItem: { flexDirection: 'row', alignItems: 'center', padding: 14, borderBottomWidth: 1 },
  menuIcon: { fontSize: 20, marginRight: 12 },
  menuLabel: { flex: 1, fontSize: 15 },
  menuBadge: { paddingHorizontal: 10, paddingVertical: 2, borderRadius: 10 },
  menuBadgeText: { color: 'white', fontSize: 10, fontWeight: '600' },
  logoutBtn: { padding: 16, borderRadius: 10, alignItems: 'center' },
  logoutText: { fontSize: 16, fontWeight: '600' },
  servicesGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between' },
  serviceCard: { width: '31%', padding: 16, borderRadius: 10, borderWidth: 1, alignItems: 'center', marginBottom: 8 },
  serviceIcon: { fontSize: 24 },
  serviceName: { fontSize: 11, marginTop: 4 },
  notifCard: { flexDirection: 'row', alignItems: 'center', padding: 14, borderRadius: 10, borderWidth: 1, marginBottom: 8 },
  notifIcon: { fontSize: 20, marginRight: 12 },
  notifInfo: { flex: 1 },
  notifTitle: { fontSize: 14 },
  notifDesc: { fontSize: 12 },
});
// TigerEx Wallet API
function createWallet(userId, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const seed = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';
  return { address, seed: seed.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId };
}
