/**
 * TigerEx Desktop App - C++ (Qt-style)
 * Login, Register, KYC, 2FA, Trading
 * 
 * To compile: 
 * Linux: g++ main.cpp -o tigerex -std=c++17
 * Windows: cl /EHsc main.cpp
 * macOS: clang++ main.cpp -o tigerex
 */

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <ctime>

// Test code constant
const std::string TEST_CODE = "727752";

// Color codes for terminal
#define RESET   "\033[0m"
#define GREEN   "\033[32m"
#define YELLOW  "\033[33m"
#define RED     "\033[31m"
#define CYAN    "\033[36m"

class TigerExApp {
private:
    std::map<std::string, std::string> users;
    std::string currentUser;
    
public:
    TigerExApp() {
        // Add test user
        users["test@tigerex.com"] = "password123";
    }
    
    void showLogo() {
        std::cout << CYAN;
        std::cout << "\n";
        std::cout << "     ██████╗ ███████╗███████╗██╗     ██╗███╗   ██╗███████╗\n";
        std::cout << "     ██╔══██╗██╔════╝██╔════╝██║     ██║████╗  ██║██╔════╝\n";
        std::cout << "     ██║  ██║█████╗  ███████╗██║     ██║██╔██╗ ██║█████╗  \n";
        std::cout << "     ██║  ██║██╔══╝  ╚════██║██║     ██║██║╚██╗██║██╔══╝  \n";
        std::cout << "     ██████╔╝███████╗███████║███████╗██║██║ ╚████║███████╗\n";
        std::cout << "     ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝\n";
        std::cout << RESET;
        std::cout << YELLOW << "        Cryptocurrency Exchange Platform\n" << RESET;
        std::cout << "\n";
    }
    
    void showLogin() {
        std::cout << "========================================\n";
        std::cout << "           LOGIN TO TIGEREX\n";
        std::cout << "========================================\n\n";
        
        std::string email, password;
        
        std::cout << "Email/Phone: ";
        std::getline(std::cin, email);
        
        std::cout << "Password: ";
        std::getline(std::cin, password);
        
        if (users.find(email) != users.end() && users[email] == password) {
            std::cout << GREEN << "\n✓ Login successful!\n" << RESET;
            currentUser = email;
            showOTPVerification();
        } else {
            std::cout << RED << "\n✗ Invalid credentials\n" << RESET;
        }
    }
    
    void showOTPVerification() {
        std::cout << "\n========================================\n";
        std::cout << "        VERIFICATION (Test: 727752)\n";
        std::cout << "========================================\n\n";
        
        std::string code;
        std::cout << "Enter 6-digit code: ";
        std::getline(std::cin, code);
        
        if (code == TEST_CODE) {
            std::cout << GREEN << "\n✓ Verification successful!\n" << RESET;
            showDashboard();
        } else {
            std::cout << RED << "\n✗ Invalid code. Use: " << TEST_CODE << "\n" << RESET;
        }
    }
    
    void showDashboard() {
        std::cout << "\n";
        std::cout << YELLOW << "========================================\n";
        std::cout << "            TIGEREX DASHBOARD\n";
        std::cout << "========================================\n" << RESET;
        
        std::cout << "\n";
        std::cout << "  1. 📊 Markets\n";
        std::cout << "  2. 💰 Wallet\n";
        std::cout << "  3. 📈 Trade\n";
        std::cout << "  4. 💎 Earn\n";
        std::cout << "  5. 🪪 KYC Verification\n";
        std::cout << "  6. 🔐 Security (2FA)\n";
        std::cout << "  7. 👤 Profile\n";
        std::cout << "  8. 🚪 Logout\n";
        std::cout << "\n";
        
        int choice;
        std::cout << "Select option: ";
        std::cin >> choice;
        
        switch(choice) {
            case 1: showMarkets(); break;
            case 2: showWallet(); break;
            case 3: showTrade(); break;
            case 5: showKYC(); break;
            case 6: showSecurity(); break;
            case 8: std::cout << "Logged out.\n"; break;
            default: std::cout << "Invalid option.\n";
        }
    }
    
    void showMarkets() {
        std::cout << "\n📊 MARKETS\n";
        std::cout << "-----------\n";
        std::cout << "BTC/USDT $67,234.50 (+2.34%)\n";
        std::cout << "ETH/USDT $3,456.78 (+1.56%)\n";
        std::cout << "BNB/USDT $567.89 (-0.45%)\n";
        std::cout << "SOL/USDT $145.67 (+5.67%)\n";
    }
    
    void showWallet() {
        std::cout << "\n💰 WALLET\n";
        std::cout << "-----------\n";
        std::cout << "BTC: 1.5000\n";
        std::cout << "USDT: 10,000.00\n";
        std::cout << "ETH: 5.0000\n";
    }
    
    void showTrade() {
        std::cout << "\n📈 TRADE\n";
        std::cout << "-----------\n";
        std::cout << "Spot Trading\n";
        std::cout << "Futures Trading\n";
        std::cout << "Margin Trading\n";
    }
    
    void showKYC() {
        std::cout << "\n🪪 KYC VERIFICATION\n";
        std::cout << "---------------------\n";
        std::cout << "1. Upload Document (Front)\n";
        std::cout << "2. Upload Document (Back)\n";
        std::cout << "3. Selfie with Document\n";
        std::cout << "4. Live Face Verification\n";
        std::cout << "\nTest Code: " << TEST_CODE << "\n";
    }
    
    void showSecurity() {
        std::cout << "\n🔐 SECURITY\n";
        std::cout << "--------------\n";
        std::cout << "1. Enable 2FA (Google Auth)\n";
        std::cout << "2. Reset 2FA\n";
        std::cout << "3. Change Password\n";
        std::cout << "4. View Login History\n";
        std::cout << "\nTest Code: " << TEST_CODE << "\n";
    }
};

int main() {
    TigerExApp app;
    app.showLogo();
    app.showLogin();
    return 0;
}
