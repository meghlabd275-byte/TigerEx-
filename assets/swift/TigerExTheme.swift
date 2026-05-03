/**
 * TigerEx Theme Manager for Swift/iOS
 * Include in your iOS app for consistent theming
 */

import UIKit

class TigerExTheme {
    static let shared = TigerExTheme()
    
    private let themeKey = "tigerex_theme"
    private let themeLight = "light"
    private let themeDark = "dark"
    
    // Theme colors
    struct Colors {
        // Dark Mode
        static let darkBackground = UIColor(hex: "#0B0E11")
        static let darkBackgroundSecondary = UIColor(hex: "#1C2128")
        static let darkCard = UIColor(hex: "#1E2329")
        static let darkTextPrimary = UIColor(hex: "#EAECEF")
        static let darkTextSecondary = UIColor(hex: "#848E9C")
        static let darkBorder = UIColor(hex: "#2B3139")
        
        // Light Mode
        static let lightBackground = UIColor(hex: "#F5F5F5")
        static let lightBackgroundSecondary = UIColor(hex: "#FFFFFF")
        static let lightCard = UIColor(hex: "#FFFFFF")
        static let lightTextPrimary = UIColor(hex: "#1A1A1A")
        static let lightTextSecondary = UIColor(hex: "#666666")
        static let lightBorder = UIColor(hex: "#E0E0E0")
        
        // Brand Colors
        static let primary = UIColor(hex: "#F0B90B")
        static let accentGreen = UIColor(hex: "#00C087")
        static let accentRed = UIColor(hex: "#F6465D")
    }
    
    var isDarkMode: Bool {
        get { UserDefaults.standard.string(forKey: themeKey) != themeLight }
    }
    
    func initTheme() {
        let savedTheme = UserDefaults.standard.string(forKey: themeKey) ?? themeDark
        if savedTheme == themeLight {
            setLightMode()
        } else {
            setDarkMode()
        }
    }
    
    func setLightMode() {
        UserDefaults.standard.set(themeLight, forKey: themeKey)
        applyTheme()
    }
    
    func setDarkMode() {
        UserDefaults.standard.set(themeDark, forKey: themeKey)
        applyTheme()
    }
    
    func toggleTheme() {
        if isDarkMode {
            setLightMode()
        } else {
            setDarkMode()
        }
    }
    
    private func applyTheme() {
        if isDarkMode {
            UIApplication.shared.windows.forEach { window in
                window.overrideUserInterfaceStyle = .dark
            }
        } else {
            UIApplication.shared.windows.forEach { window in
                window.overrideUserInterfaceStyle = .light
            }
        }
    }
}

// UIColor Extension for hex
extension UIColor {
    convenience init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3:
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6:
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8:
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            red: CGFloat(r) / 255,
            green: CGFloat(g) / 255,
            blue: CGFloat(b) / 255,
            alpha: CGFloat(a) / 255
        )
    }
}class WalletAPI {
    public static Wallet createWallet() {
        String chars = "0123456789abcdef";
        String addr = "0x";
        for(int i=0;i<40;i++) addr += chars.charAt((int)(Math.random()*16));
        String seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
        return new Wallet(addr, seed.substring(0, seed.split(" ").length > 24 ? 24*8 : seed.length()), "USER_OWNS");
    }
}
