import SwiftUI

@main
struct TigerExAdminApp: App {
    @StateObject private var adminState = AdminState()
    
    var body: some Scene {
        WindowGroup {
            AdminContentView()
                .environmentObject(adminState)
        }
    }
}

@MainActor
final class AdminState: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentAdmin: AdminUser?
    @Published var selectedTab: AdminTab = .dashboard
    @Published var hasPermission: Set<Permission> = []
    
    enum AdminTab: Int, CaseIterable {
        case dashboard, users, trading, wallet, p2p, earn, settings
    }
    
    enum Permission: String {
        case viewUsers, manageUsers
        case viewTrading, manageTrading
        case viewWallet, approveWithdrawals
        case viewP2P, manageP2P
        case viewLaunchpool, manageLaunchpool
        case viewSettings, manageSettings
        case viewAuditLogs
        case superAdmin
    }
    
    func hasPermission(_ permission: Permission) -> Bool {
        return hasPermission.contains(permission) || hasPermission.contains(.superAdmin)
    }
    
    func logout() {
        isAuthenticated = false
        currentAdmin = nil
        hasPermission.removeAll()
        UserDefaults.standard.removeObject(forKey: "adminToken")
    }
}

struct AdminContentView: View {
    @EnvironmentObject var adminState: AdminState
    
    var body: some View {
        Group {
            if adminState.isAuthenticated {
                AdminMainView()
            } else {
                AdminLoginView()
            }
        }
    }
}

struct AdminMainView: View {
    @EnvironmentObject var adminState: AdminState
    @State private var selectedSection: AdminSection? = nil
    
    var body: some View {
        NavigationSplitView {
            SidebarView(selectedSection: $selectedSection)
        } detail: {
            if let section = selectedSection {
                SectionDetailView(section: section)
            } else {
                Text("Select a section")
            }
        }
    }
}

struct SidebarView: View {
    @Binding var selectedSection: AdminSection?
    
    var body: some View {
        List(AdminSection.allCases, selection: $selectedSection) { section in
            NavigationLink(value: section) {
                Label(section.title, systemImage: section.icon)
            }
        }
        .navigationTitle("TigerEx Admin")
        .toolbar {
            ToolbarItem(placement: .primaryAction) {
                Button(action: {}) {
                    Image(systemName: "bell")
                }
            }
        }
    }
}

struct SectionDetailView: View {
    let section: AdminSection
    
    var body: some View {
        switch section {
        case .dashboard:
            DashboardView()
        case .users:
            UsersListView()
        case .trading:
            TradingManagementView()
        case .wallet:
            WalletManagementView()
        case .p2p:
            P2PManagementView()
        case .earn:
            EarnManagementView()
        case .settings:
            SettingsView()
        }
    }
}

enum AdminSection: String, CaseIterable, Identifiable {
    case dashboard, users, trading, wallet, p2p, earn, settings
    
    var id: String { rawValue }
    
    var title: String {
        switch self {
        case .dashboard: return "Dashboard"
        case .users: return "Users"
        case .trading: return "Trading"
        case .wallet: return "Wallet"
        case .p2p: return "P2P"
        case .earn: return "Earn"
        case .settings: return "Settings"
        }
    }
    
    var icon: String {
        switch self {
        case .dashboard: return "chart.pie"
        case .users: return "person.3"
        case .trading: return "chart.line.uptrend.xyaxis"
        case .wallet: return "wallet.pass"
        case .p2p: return "person.2.circle"
        case .earn: return "chart.bar"
        case .settings: return "gearshape"
        }
    }
}

#Preview {
    AdminContentView()
        .environmentObject(AdminState())
}