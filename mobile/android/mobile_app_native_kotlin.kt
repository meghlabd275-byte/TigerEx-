package com.tigerex.mobile

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import kotlinx.coroutines.delay
import org.json.JSONObject
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*

/**
 * TigerEx Mobile Application - Advanced Trading Platform
 * Native Kotlin Implementation with Jetpack Compose
 */

data class Cryptocurrency(
    val symbol: String,
    val name: String,
    val price: Double,
    val change24h: Double,
    val volume24h: Double,
    val marketCap: Double,
    val icon: String
)

data class Order(
    val id: String,
    val type: String,
    val pair: String,
    val amount: Double,
    val price: Double,
    val total: Double,
    val status: String,
    val timestamp: String
)

data class Portfolio(
    val symbol: String,
    val balance: Double,
    val value: Double,
    val change24h: Double
)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TigerExMobileApp()
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TigerExMobileApp() {
    val navController = rememberNavController()
    var isDarkTheme by remember { mutableStateOf(true) }
    
    MaterialTheme(
        colorScheme = if (isDarkTheme) darkColorScheme() else lightColorScheme()
    ) {
        NavHost(
            navController = navController,
            startDestination = "dashboard"
        ) {
            composable("dashboard") {
                DashboardScreen(navController = navController)
            }
            composable("trading") {
                TradingScreen(navController = navController)
            }
            composable("portfolio") {
                PortfolioScreen(navController = navController)
            }
            composable("orders") {
                OrdersScreen(navController = navController)
            }
            composable("profile") {
                ProfileScreen(navController = navController)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(navController: NavController) {
    var cryptocurrencies by remember { mutableStateOf(listOf<Cryptocurrency>()) }
    var isLoading by remember { mutableStateOf(true) }
    var userBalance by remember { mutableStateOf(125000.50) }
    var todayProfit by remember { mutableStateOf(2500.75) }
    
    // Simulate loading data
    LaunchedEffect(Unit) {
        delay(2000)
        cryptocurrencies = getMockCryptocurrencies()
        isLoading = false
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0A0E1A))
            .padding(16.dp)
    ) {
        // Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "Welcome Back",
                    color = Color.Gray,
                    fontSize = 14.sp
                )
                Text(
                    text = "Trader",
                    color = Color.White,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            
            IconButton(onClick = { navController.navigate("profile") }) {
                Icon(
                    Icons.Default.AccountCircle,
                    contentDescription = "Profile",
                    tint = Color.White,
                    modifier = Modifier.size(32.dp)
                )
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Balance Card
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(16.dp)),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2139))
        ) {
            Column(
                modifier = Modifier.padding(20.dp)
            ) {
                Text(
                    text = "Total Balance",
                    color = Color.Gray,
                    fontSize = 14.sp
                )
                Text(
                    text = "$${String.format("%.2f", userBalance)}",
                    color = Color.White,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Row {
                    Icon(
                        Icons.Default.TrendingUp,
                        contentDescription = "Profit",
                        tint = Color(0xFF00D4AA),
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "+$${String.format("%.2f", todayProfit)} (2.1%)",
                        color = Color(0xFF00D4AA),
                        fontSize = 14.sp
                    )
                    Text(
                        text = " Today",
                        color = Color.Gray,
                        fontSize = 14.sp,
                        modifier = Modifier.padding(start = 4.dp)
                    )
                }
            }
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Quick Actions
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            ActionButton(
                icon = Icons.Default.Send,
                text = "Send",
                onClick = { navController.navigate("trading") }
            )
            ActionButton(
                icon = Icons.Default.CallReceived,
                text = "Receive",
                onClick = { navController.navigate("trading") }
            )
            ActionButton(
                icon = Icons.Default.SwapVert,
                text = "Trade",
                onClick = { navController.navigate("trading") }
            )
            ActionButton(
                icon = Icons.Default.AccountBalanceWallet,
                text = "Wallet",
                onClick = { navController.navigate("portfolio") }
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Market Overview
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "Market Overview",
                color = Color.White,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold
            )
            TextButton(onClick = { navController.navigate("trading") }) {
                Text(
                    text = "See All",
                    color = Color(0xFF3B82F6)
                )
            }
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        if (isLoading) {
            Box(
                modifier = Modifier.fillMaxWidth(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator(color = Color(0xFF3B82F6))
            }
        } else {
            LazyColumn {
                items(cryptocurrencies.take(5)) { crypto ->
                    CryptocurrencyItem(crypto = crypto) {
                        navController.navigate("trading")
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                }
            }
        }
        
        // Bottom Navigation
        BottomNavigationBar(navController = navController, currentRoute = "dashboard")
    }
}

@Composable
fun ActionButton(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    text: String,
    onClick: () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Button(
            onClick = onClick,
            modifier = Modifier
                .size(56.dp)
                .clip(RoundedCornerShape(16.dp)),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFF1E2139)
            ),
            contentPadding = PaddingValues(0.dp)
        ) {
            Icon(
                icon,
                contentDescription = text,
                tint = Color.White,
                modifier = Modifier.size(24.dp)
            )
        }
        Spacer(modifier = Modifier.height(8.dp))
        Text(
            text = text,
            color = Color.Gray,
            fontSize = 12.sp
        )
    }
}

@Composable
fun CryptocurrencyItem(
    crypto: Cryptocurrency,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp)),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2139)),
        onClick = onClick
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                // Icon placeholder
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(
                            Color(0xFF3B82F6),
                            RoundedCornerShape(20.dp)
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = crypto.symbol.take(2),
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        fontSize = 16.sp
                    )
                }
                Spacer(modifier = Modifier.width(12.dp))
                Column {
                    Text(
                        text = crypto.symbol,
                        color = Color.White,
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = crypto.name,
                        color = Color.Gray,
                        fontSize = 14.sp
                    )
                }
            }
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = "$${String.format("%.2f", crypto.price)}",
                    color = Color.White,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
                Row {
                    Icon(
                        if (crypto.change24h >= 0) Icons.Default.TrendingUp else Icons.Default.TrendingDown,
                        contentDescription = "Change",
                        tint = if (crypto.change24h >= 0) Color(0xFF00D4AA) else Color(0xFFEF4444),
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "${if (crypto.change24h >= 0) "+" else ""}${String.format("%.2f", crypto.change24h)}%",
                        color = if (crypto.change24h >= 0) Color(0xFF00D4AA) else Color(0xFFEF4444),
                        fontSize = 14.sp
                    )
                }
            }
        }
    }
}

@Composable
fun TradingScreen(navController: NavController) {
    // Enhanced trading screen implementation
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0A0E1A))
            .padding(16.dp)
    ) {
        Text(
            text = "Trading",
            color = Color.White,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        // Trading interface implementation
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .clip(RoundedCornerShape(16.dp)),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2139))
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Icon(
                    Icons.Default.SwapVert,
                    contentDescription = "Trading",
                    tint = Color(0xFF3B82F6),
                    modifier = Modifier.size(64.dp)
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Advanced Trading Interface",
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Real-time charts, order books, and trading tools",
                    color = Color.Gray,
                    fontSize = 14.sp
                )
            }
        }
        
        BottomNavigationBar(navController = navController, currentRoute = "trading")
    }
}

@Composable
fun PortfolioScreen(navController: NavController) {
    // Portfolio screen implementation
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0A0E1A))
            .padding(16.dp)
    ) {
        Text(
            text = "Portfolio",
            color = Color.White,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .clip(RoundedCornerShape(16.dp)),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2139))
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Icon(
                    Icons.Default.AccountBalanceWallet,
                    contentDescription = "Portfolio",
                    tint = Color(0xFF3B82F6),
                    modifier = Modifier.size(64.dp)
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Portfolio Management",
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Track your investments and performance",
                    color = Color.Gray,
                    fontSize = 14.sp
                )
            }
        }
        
        BottomNavigationBar(navController = navController, currentRoute = "portfolio")
    }
}

@Composable
fun OrdersScreen(navController: NavController) {
    // Orders screen implementation
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0A0E1A))
            .padding(16.dp)
    ) {
        Text(
            text = "Orders",
            color = Color.White,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .clip(RoundedCornerShape(16.dp)),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2139))
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Icon(
                    Icons.Default.List,
                    contentDescription = "Orders",
                    tint = Color(0xFF3B82F6),
                    modifier = Modifier.size(64.dp)
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Order History",
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "View and manage your trading orders",
                    color = Color.Gray,
                    fontSize = 14.sp
                )
            }
        }
        
        BottomNavigationBar(navController = navController, currentRoute = "orders")
    }
}

@Composable
fun ProfileScreen(navController: NavController) {
    // Profile screen implementation
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0A0E1A))
            .padding(16.dp)
    ) {
        Text(
            text = "Profile",
            color = Color.White,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .weight(1f)
                .clip(RoundedCornerShape(16.dp)),
            colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2139))
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Icon(
                    Icons.Default.AccountCircle,
                    contentDescription = "Profile",
                    tint = Color(0xFF3B82F6),
                    modifier = Modifier.size(64.dp)
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "User Profile",
                    color = Color.White,
                    fontSize = 18.sp,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Manage your account settings",
                    color = Color.Gray,
                    fontSize = 14.sp
                )
            }
        }
    }
}

@Composable
fun BottomNavigationBar(navController: NavController, currentRoute: String) {
    NavigationBar(
        containerColor = Color(0xFF1E2139)
    ) {
        NavigationBarItem(
            icon = { Icon(Icons.Default.Dashboard, contentDescription = "Dashboard") },
            label = { Text("Dashboard") },
            selected = currentRoute == "dashboard",
            onClick = { navController.navigate("dashboard") },
            colors = NavigationBarItemDefaults.colors(
                selectedIconColor = Color(0xFF3B82F6),
                selectedTextColor = Color(0xFF3B82F6),
                unselectedIconColor = Color.Gray,
                unselectedTextColor = Color.Gray
            )
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.SwapVert, contentDescription = "Trading") },
            label = { Text("Trading") },
            selected = currentRoute == "trading",
            onClick = { navController.navigate("trading") },
            colors = NavigationBarItemDefaults.colors(
                selectedIconColor = Color(0xFF3B82F6),
                selectedTextColor = Color(0xFF3B82F6),
                unselectedIconColor = Color.Gray,
                unselectedTextColor = Color.Gray
            )
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.AccountBalanceWallet, contentDescription = "Portfolio") },
            label = { Text("Portfolio") },
            selected = currentRoute == "portfolio",
            onClick = { navController.navigate("portfolio") },
            colors = NavigationBarItemDefaults.colors(
                selectedIconColor = Color(0xFF3B82F6),
                selectedTextColor = Color(0xFF3B82F6),
                unselectedIconColor = Color.Gray,
                unselectedTextColor = Color.Gray
            )
        )
        NavigationBarItem(
            icon = { Icon(Icons.Default.List, contentDescription = "Orders") },
            label = { Text("Orders") },
            selected = currentRoute == "orders",
            onClick = { navController.navigate("orders") },
            colors = NavigationBarItemDefaults.colors(
                selectedIconColor = Color(0xFF3B82F6),
                selectedTextColor = Color(0xFF3B82F6),
                unselectedIconColor = Color.Gray,
                unselectedTextColor = Color.Gray
            )
        )
    }
}

// Mock data functions
fun getMockCryptocurrencies(): List<Cryptocurrency> {
    return listOf(
        Cryptocurrency("BTC", "Bitcoin", 45234.56, 2.5, 28_500_000_000.0, 880_000_000_000.0, "₿"),
        Cryptocurrency("ETH", "Ethereum", 3124.78, 3.2, 15_200_000_000.0, 375_000_000_000.0, "Ξ"),
        Cryptocurrency("BNB", "Binance Coin", 524.12, 1.8, 1_800_000_000.0, 80_000_000_000.0, "BNB"),
        Cryptocurrency("ADA", "Cardano", 1.23, 4.1, 890_000_000.0, 43_000_000_000.0, "ADA"),
        Cryptocurrency("SOL", "Solana", 145.67, -1.2, 2_100_000_000.0, 65_000_000_000.0, "SOL")
    )
}

fun getMockOrders(): List<Order> {
    val dateFormat = SimpleDateFormat("HH:mm:ss", Locale.getDefault())
    return listOf(
        Order("1", "Buy", "BTC/USDT", 0.05, 45000.0, 2250.0, "Completed", dateFormat.format(Date())),
        Order("2", "Sell", "ETH/USDT", 1.2, 3150.0, 3780.0, "Completed", dateFormat.format(Date())),
        Order("3", "Buy", "BNB/USDT", 2.5, 520.0, 1300.0, "Pending", dateFormat.format(Date()))
    )
}

fun getMockPortfolio(): List<Portfolio> {
    return listOf(
        Portfolio("BTC", 0.15, 6785.18, 2.5),
        Portfolio("ETH", 2.8, 8749.38, 3.2),
        Portfolio("BNB", 5.2, 2725.42, 1.8),
        Portfolio("USDT", 12500.0, 12500.0, 0.0)
    )
}