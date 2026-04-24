package main

import (
"bufio"
"fmt"
"os"
"strings"
)

// Test code constant
const testCode = "727752"

func main() {
showLogo()
login()
}

func showLogo() {
fmt.Println("\033[36m")
fmt.Println("     ██████╗ ███████╗███████╗██╗     ██╗███╗   ██╗███████╗")
fmt.Println("     ██╔══██╗██╔════╝██╔════╝██║     ██║████╗  ██║██╔════╝")
fmt.Println("     ██║  ██║█████╗  ███████╗██║     ██║██╔██╗ ██║█████╗  ")
fmt.Println("     ██║  ██║██╔══╝  ╚════██║██║     ██║██║╚██╗██║██╔══╝  ")
fmt.Println("     ██████╔╝███████╗███████║███████╗██║██║ ╚████║███████╗")
fmt.Println("     ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝")
fmt.Println("\033[0m")
fmt.Println("\033[33m        Cryptocurrency Exchange Platform\033[0m")
fmt.Println()
}

func login() {
fmt.Println("========================================")
fmt.Println("           LOGIN TO TIGEREX")
fmt.Println("========================================")
fmt.Println()

reader := bufio.NewReader(os.Stdin)

fmt.Print("Email/Phone: ")
email, _ := reader.ReadString('\n')
email = strings.TrimSpace(email)

fmt.Print("Password: ")
password, _ := reader.ReadString('\n')
password = strings.TrimSpace(password)

if email != "" && password != "" {
tln("\033[32m\n✓ Login successful!\033[0m")
()
} else {
tln("\033[31m\n✗ Invalid credentials\033[0m")
}
}

func showOTPVerification() {
fmt.Println()
fmt.Println("========================================")
fmt.Println("        VERIFICATION (Test: 727752)")
fmt.Println("========================================")
fmt.Println()

reader := bufio.NewReader(os.Stdin)

fmt.Print("Enter 6-digit code: ")
code, _ := reader.ReadString('\n')
code = strings.TrimSpace(code)

if code == testCode {
tln("\033[32m\n✓ Verification successful!\033[0m")
else {
tf("\033[31m\n✗ Invalid code. Use: %s\033[0m\n", testCode)
}
}

func showDashboard() {
fmt.Println()
fmt.Println("\033[33m========================================")
fmt.Println("            TIGEREX DASHBOARD")
fmt.Println("========================================\033[0m")
fmt.Println()
fmt.Println("  1. 📊 Markets")
fmt.Println("  2. 💰 Wallet")
fmt.Println("  3. 📈 Trade")
fmt.Println("  4. 💎 Earn")
fmt.Println("  5. 🪪 KYC Verification")
fmt.Println("  6. 🔐 Security (2FA)")
fmt.Println("  7. 👤 Profile")
fmt.Println("  8. 🚪 Logout")
fmt.Println()

reader := bufio.NewReader(os.Stdin)
fmt.Print("Select option: ")
choice, _ := reader.ReadString('\n')
choice = strings.TrimSpace(choice)

switch choice {
case "1": showMarkets()
case "2": showWallet()
case "3": showTrade()
case "5": showKYC()
case "6": showSecurity()
case "8": fmt.Println("Logged out.")
default: fmt.Println("Invalid option.")
}
}

func showMarkets() {
fmt.Println("\n📊 MARKETS")
fmt.Println("-----------")
fmt.Println("BTC/USDT $67,234.50 (+2.34%)")
fmt.Println("ETH/USDT $3,456.78 (+1.56%)")
fmt.Println("BNB/USDT $567.89 (-0.45%)")
}

func showWallet() {
fmt.Println("\n💰 WALLET")
fmt.Println("-----------")
fmt.Println("BTC: 1.5000")
fmt.Println("USDT: 10,000.00")
}

func showTrade() {
fmt.Println("\n📈 TRADE")
fmt.Println("-----------")
fmt.Println("Spot Trading")
fmt.Println("Futures Trading")
fmt.Println("Margin Trading")
}

func showKYC() {
fmt.Println("\n🪪 KYC VERIFICATION")
fmt.Println("---------------------")
fmt.Println("1. Upload Document (Front)")
fmt.Println("2. Upload Document (Back)")
fmt.Println("3. Selfie with Document")
fmt.Println("4. Live Face Verification")
fmt.Printf("\nTest Code: %s\n", testCode)
}

func showSecurity() {
fmt.Println("\n🔐 SECURITY")
fmt.Println("--------------")
fmt.Println("1. Enable 2FA (Google Auth)")
fmt.Println("2. Reset 2FA")
fmt.Println("3. Change Password")
fmt.Printf("\nTest Code: %s\n", testCode)
}
