using System;
using System.Collections.Generic;

namespace TigerExApp
{
    // Test code constant
    class Program
    {
        private const string TEST_CODE = "727752";
        
        static void Main(string[] args)
        {
            ShowLogo();
            Login();
        }
        
        static void ShowLogo()
        {
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine(@"
     ██████╗ ███████╗███████╗██╗     ██╗███╗   ██╗███████╗
     ██╔══██╗██╔════╝██╔════╝██║     ██║████╗  ██║██╔════╝
     ██║  ██║█████╗  ███████╗██║     ██║██╔██╗ ██║█████╗  
     ██║  ██║██╔══╝  ╚════██║██║     ██║██║╚██╗██║██╔══╝  
     ██████╔╝███████╗███████║███████╗██║██║ ╚████║███████╗
     ╚═════╝ ╚══════╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝
            ");
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine("        Cryptocurrency Exchange Platform");
            Console.ResetColor();
            Console.WriteLine();
        }
        
        static void Login()
        {
            Console.WriteLine("========================================");
            Console.WriteLine("           LOGIN TO TIGEREX");
            Console.WriteLine("========================================");
            Console.WriteLine();
            
            Console.Write("Email/Phone: ");
            string email = Console.ReadLine();
            
            Console.Write("Password: ");
            string password = Console.ReadLine();
            
            if (!string.IsNullOrEmpty(email) && !string.IsNullOrEmpty(password))
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("\n✓ Login successful!");
                Console.ResetColor();
                ShowOTPVerification();
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("\n✗ Invalid credentials");
                Console.ResetColor();
            }
        }
        
        static void ShowOTPVerification()
        {
            Console.WriteLine();
            Console.WriteLine("========================================");
            Console.WriteLine("        VERIFICATION (Test: 727752)");
            Console.WriteLine("========================================");
            Console.WriteLine();
            
            Console.Write("Enter 6-digit code: ");
            string code = Console.ReadLine();
            
            if (code == TEST_CODE)
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("\n✓ Verification successful!");
                Console.ResetColor();
                ShowDashboard();
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"\n✗ Invalid code. Use: {TEST_CODE}");
                Console.ResetColor();
            }
        }
        
        static void ShowDashboard()
        {
            Console.WriteLine();
            Console.ForegroundColor = ConsoleColor.Yellow;
            Console.WriteLine("========================================");
            Console.WriteLine("            TIGEREX DASHBOARD");
            Console.WriteLine("========================================");
            Console.ResetColor();
            Console.WriteLine();
            Console.WriteLine("  1. 📊 Markets");
            Console.WriteLine("  2. 💰 Wallet");
            Console.WriteLine("  3. 📈 Trade");
            Console.WriteLine("  4. 💎 Earn");
            Console.WriteLine("  5. 🪪 KYC Verification");
            Console.WriteLine("  6. 🔐 Security (2FA)");
            Console.WriteLine("  7. 👤 Profile");
            Console.WriteLine("  8. 🚪 Logout");
            Console.WriteLine();
            Console.Write("Select option: ");
            
            string choice = Console.ReadLine();
            
            switch(choice)
            {
                case "1": ShowMarkets(); break;
                case "2": ShowWallet(); break;
                case "3": ShowTrade(); break;
                case "5": ShowKYC(); break;
                case "6": ShowSecurity(); break;
                case "8": Console.WriteLine("Logged out."); break;
                default: Console.WriteLine("Invalid option."); break;
            }
        }
        
        static void ShowMarkets()
        {
            Console.WriteLine("\n📊 MARKETS");
            Console.WriteLine("-----------");
            Console.WriteLine("BTC/USDT $67,234.50 (+2.34%)");
            Console.WriteLine("ETH/USDT $3,456.78 (+1.56%)");
            Console.WriteLine("BNB/USDT $567.89 (-0.45%)");
        }
        
        static void ShowWallet()
        {
            Console.WriteLine("\n💰 WALLET");
            Console.WriteLine("-----------");
            Console.WriteLine("BTC: 1.5000");
            Console.WriteLine("USDT: 10,000.00");
        }
        
        static void ShowTrade()
        {
            Console.WriteLine("\n📈 TRADE");
            Console.WriteLine("-----------");
            Console.WriteLine("Spot Trading");
            Console.WriteLine("Futures Trading");
            Console.WriteLine("Margin Trading");
        }
        
        static void ShowKYC()
        {
            Console.WriteLine("\n🪪 KYC VERIFICATION");
            Console.WriteLine("---------------------");
            Console.WriteLine("1. Upload Document (Front)");
            Console.WriteLine("2. Upload Document (Back)");
            Console.WriteLine("3. Selfie with Document");
            Console.WriteLine("4. Live Face Verification");
            Console.WriteLine($"\nTest Code: {TEST_CODE}");
        }
        
        static void ShowSecurity()
        {
            Console.WriteLine("\n🔐 SECURITY");
            Console.WriteLine("--------------");
            Console.WriteLine("1. Enable 2FA (Google Auth)");
            Console.WriteLine("2. Reset 2FA");
            Console.WriteLine("3. Change Password");
            Console.WriteLine($"\nTest Code: {TEST_CODE}");
        }
    }
}
