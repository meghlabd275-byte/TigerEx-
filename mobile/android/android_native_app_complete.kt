package com.tigerex.trading

import android.app.Application
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation.NavController
import androidx.navigation.NavHostController
import androidx.navigation.compose.*
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.delay
import kotlin.random.Random

// Main Application Class
class TigerExApp : Application() {
    override fun onCreate() {
        super.onCreate()
    }
}

// Main Activity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TigerExTradingApp()
        }
    }
}

// Main Compose App
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TigerExTradingApp() {
    val navController = rememberNavController()
    val viewModel: TradingViewModel = viewModel()
    
    TigerExTheme {
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            NavigationSetup(navController, viewModel)
        }
    }
}

// Navigation Setup
@Composable
fun NavigationSetup(navController: NavHostController, viewModel: TradingViewModel) {
    NavHost(
        navController = navController,
        startDestination = "trading"
    ) {
        composable("trading") {
            TradingScreen(navController, viewModel)
        }
        composable("portfolio") {
            PortfolioScreen(navController, viewModel)
        }
        composable("orders") {
            OrdersScreen(navController, viewModel)
        }
        composable("profile") {
            ProfileScreen(navController, viewModel)
        }
        composable("login") {
            LoginScreen(navController)
        }
        composable("register") {
            RegisterScreen(navController)
        }
    }
}

// Trading Screen - Main Interface
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TradingScreen(navController: NavController, viewModel: TradingViewModel) {
    var selectedTab by remember { mutableStateOf("spot") }
    var selectedOrderType by remember { mutableStateOf("market") }
    var selectedSide by remember { mutableStateOf("buy") }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0B0E11))
    ) {
        // Top Bar
        TopAppBar(
            title = {
                Text(
                    "TigerEx",
                    color = Color(0xFFFCD535),
                    fontWeight = FontWeight.Bold
                )
            },
            actions = {
                IconButton(onClick = { /* Notifications */ }) {
                    Icon(Icons.Default.Notifications, tint = Color.White)
                }
                IconButton(onClick = { /* Profile */ }) {
                    Icon(Icons.Default.Person, tint = Color.White)
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color(0xFF1E2329)
            )
        )
        
        // Trading Mode Tabs
        TradingModeTabs(selectedTab) { tab ->
            selectedTab = tab
            viewModel.updateTradingMode(tab)
        }
        
        // Main Content
        Row(
            modifier = Modifier
                .fillMaxSize()
                .weight(1f)
        ) {
            // Markets Panel
            MarketsPanel(
                modifier = Modifier.width(320.dp),
                viewModel = viewModel
            )
            
            // Chart and Trading Panel
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .weight(1f)
            ) {
                // Price Chart
                PriceChartSection(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(400.dp),
                    viewModel = viewModel
                )
                
                // Trading Panel
                TradingPanel(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f),
                    selectedSide = selectedSide,
                    selectedOrderType = selectedOrderType,
                    onSideChange = { selectedSide = it },
                    onOrderTypeChange = { selectedOrderType = it },
                    viewModel = viewModel
                )
            }
            
            // Order Book
            OrderBookPanel(
                modifier = Modifier.width(280.dp),
                viewModel = viewModel
            )
        }
        
        // Bottom Navigation
        BottomNavigationBar(navController)
    }
}

// Trading Mode Tabs
@Composable
fun TradingModeTabs(selectedTab: String, onTabSelected: (String) -> Unit) {
    val tabs = listOf("spot", "futures", "margin", "options", "alpha", "etf", "tradex")
    
    ScrollableRow(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFF1E2329))
            .padding(horizontal = 16.dp),
        horizontalArrangement = Arrangement.spacedBy(24.dp)
    ) {
        tabs.forEach { tab ->
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                modifier = Modifier
                    .clickable { onTabSelected(tab) }
                    .padding(vertical = 12.dp)
            ) {
                Text(
                    text = tab.uppercase(),
                    color = if (selectedTab == tab) Color(0xFFFCD535) else Color(0xFF848E9C),
                    fontWeight = if (selectedTab == tab) FontWeight.Bold else FontWeight.Normal,
                    fontSize = 14.sp
                )
                Spacer(modifier = Modifier.height(4.dp))
                Box(
                    modifier = Modifier
                        .width(if (selectedTab == tab) 20.dp else 0.dp)
                        .height(2.dp)
                        .background(Color(0xFFFCD535))
                )
            }
        }
    }
}

// Markets Panel
@Composable
fun MarketsPanel(
    modifier: Modifier = Modifier,
    viewModel: TradingViewModel
) {
    val markets by viewModel.markets.collectAsState()
    var searchText by remember { mutableStateOf("") }
    var selectedMarketTab by remember { mutableStateOf("spot") }
    
    Card(
        modifier = modifier.fillMaxHeight(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2329)),
        elevation = CardDefaults.cardElevation(0.dp)
    ) {
        Column {
            // Search Bar
            OutlinedTextField(
                value = searchText,
                onValueChange = { searchText = it },
                placeholder = { Text("Search pairs...", color = Color(0xFF848E9C)) },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedBorderColor = Color(0xFFFCD535),
                    unfocusedBorderColor = Color(0xFF2B3139),
                    containerColor = Color(0xFF0B0E11),
                    textColor = Color.White
                )
            )
            
            // Market Type Tabs
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                listOf("spot", "futures", "margin").forEach { tab ->
                    Text(
                        text = tab.uppercase(),
                        color = if (selectedMarketTab == tab) Color(0xFFFCD535) else Color(0xFF848E9C),
                        fontWeight = if (selectedMarketTab == tab) FontWeight.Bold else FontWeight.Normal,
                        modifier = Modifier
                            .clickable { selectedMarketTab = tab }
                            .padding(vertical = 8.dp)
                    )
                }
            }
            
            Divider(color = Color(0xFF2B3139))
            
            // Markets List
            LazyColumn(
                modifier = Modifier.fillMaxSize()
            ) {
                val filteredMarkets = markets.filter { 
                    it.symbol.contains(searchText, ignoreCase = true) &&
                    it.category == selectedMarketTab
                }
                
                items(filteredMarkets.size) { index ->
                    MarketItem(
                        market = filteredMarkets[index],
                        onMarketSelected = { viewModel.selectMarket(it) }
                    )
                }
            }
        }
    }
}

// Market Item Component
@Composable
fun MarketItem(
    market: MarketData,
    onMarketSelected: (MarketData) -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onMarketSelected(market) }
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = market.symbol,
                color = Color.White,
                fontWeight = FontWeight.Medium,
                fontSize = 14.sp
            )
            Text(
                text = "Vol ${market.volume}",
                color = Color(0xFF848E9C),
                fontSize = 12.sp
            )
        }
        
        Column(
            horizontalAlignment = Alignment.End
        ) {
            Text(
                text = market.price.toString(),
                color = Color.White,
                fontWeight = FontWeight.Medium,
                fontSize = 14.sp
            )
            Text(
                text = "${if (market.change >= 0) "+" else ""}${market.change}%",
                color = if (market.change >= 0) Color(0xFF0ECB81) else Color(0xFFF6465D),
                fontSize = 12.sp,
                fontWeight = FontWeight.Medium
            )
        }
    }
    
    Divider(color = Color(0xFF2B3139))
}

// Price Chart Section
@Composable
fun PriceChartSection(
    modifier: Modifier = Modifier,
    viewModel: TradingViewModel
) {
    val selectedMarket by viewModel.selectedMarket.collectAsState()
    var selectedTimeFrame by remember { mutableStateOf("15m") }
    
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2329)),
        elevation = CardDefaults.cardElevation(0.dp)
    ) {
        Column {
            // Header
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column {
                    Text(
                        text = selectedMarket?.symbol ?: "BTC/USDT",
                        color = Color.White,
                        fontSize = 20.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Row(
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = selectedMarket?.price?.toString() ?: "67234.56",
                            color = Color.White,
                            fontSize = 28.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            text = "${if (selectedMarket?.change ?: 0f >= 0) "+" else ""}${selectedMarket?.change ?: 0f}%",
                            color = if (selectedMarket?.change ?: 0f >= 0) Color(0xFF0ECB81) else Color(0xFFF6465D),
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
                
                Row {
                    IconButton(onClick = { /* Chart settings */ }) {
                        Icon(Icons.Default.Settings, tint = Color.White)
                    }
                    IconButton(onClick = { /* Fullscreen */ }) {
                        Icon(Icons.Default.Fullscreen, tint = Color.White)
                    }
                }
            }
            
            // Time Frames
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                val timeFrames = listOf("1m", "5m", "15m", "1h", "4h", "1d", "1w")
                timeFrames.forEach { frame ->
                    FilterChip(
                        onClick = { selectedTimeFrame = frame },
                        label = { Text(frame, fontSize = 12.sp) },
                        selected = selectedTimeFrame == frame,
                        colors = FilterChipDefaults.filterChipColors(
                            selectedContainerColor = Color(0xFFFCD535),
                            selectedLabelColor = Color.Black,
                            containerColor = Color.Transparent,
                            labelColor = Color(0xFF848E9C)
                        ),
                        border = FilterChipDefaults.filterChipBorder(
                            borderColor = Color(0xFF2B3139),
                            selectedBorderColor = Color(0xFFFCD535)
                        )
                    )
                }
            }
            
            // Chart Placeholder
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(300.dp)
                    .padding(16.dp),
                contentAlignment = Alignment.Center
            ) {
                // In a real app, this would be a chart library
                Text(
                    "📈 Price Chart\nReal-time trading data visualization",
                    color = Color(0xFF848E9C),
                    textAlign = TextAlign.Center
                )
            }
        }
    }
}

// Trading Panel
@Composable
fun TradingPanel(
    modifier: Modifier = Modifier,
    selectedSide: String,
    selectedOrderType: String,
    onSideChange: (String) -> Unit,
    onOrderTypeChange: (String) -> Unit,
    viewModel: TradingViewModel
) {
    var amount by remember { mutableStateOf("") }
    var price by remember { mutableStateOf("") }
    var leverage by remember { mutableStateOf(10) }
    
    Card(
        modifier = modifier,
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2329)),
        elevation = CardDefaults.cardElevation(0.dp)
    ) {
        Column {
            // Buy/Sell Tabs
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1E2329))
            ) {
                listOf("buy", "sell").forEach { side ->
                    Row(
                        modifier = Modifier
                            .weight(1f)
                            .clickable { onSideChange(side) }
                            .background(
                                if (selectedSide == side) Color(0xFF0B0E11) else Color.Transparent
                            )
                            .padding(vertical = 12.dp),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = side.uppercase(),
                            color = if (selectedSide == side) Color(0xFFFCD535) else Color(0xFF848E9C),
                            fontWeight = if (selectedSide == side) FontWeight.Bold else FontWeight.Medium
                        )
                    }
                }
            }
            
            Column(
                modifier = Modifier.padding(16.dp)
            ) {
                // Order Type Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    listOf("market", "limit", "stop").forEach { type ->
                        FilterChip(
                            onClick = { onOrderTypeChange(type) },
                            label = { Text(type.uppercase(), fontSize = 12.sp) },
                            selected = selectedOrderType == type,
                            colors = FilterChipDefaults.filterChipColors(
                                selectedContainerColor = Color(0xFFFCD535),
                                selectedLabelColor = Color.Black,
                                containerColor = Color.Transparent,
                                labelColor = Color(0xFF848E9C)
                            ),
                            border = FilterChipDefaults.filterChipBorder(
                                borderColor = Color(0xFF2B3139),
                                selectedBorderColor = Color(0xFFFCD535)
                            ),
                            modifier = Modifier.weight(1f)
                        )
                    }
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Price Input (for limit orders)
                if (selectedOrderType != "market") {
                    OutlinedTextField(
                        value = price,
                        onValueChange = { price = it },
                        label = { Text("Price (USDT)", color = Color(0xFF848E9C)) },
                        modifier = Modifier.fillMaxWidth(),
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = Color(0xFFFCD535),
                            unfocusedBorderColor = Color(0xFF2B3139),
                            containerColor = Color(0xFF0B0E11),
                            textColor = Color.White
                        )
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                }
                
                // Amount Input
                OutlinedTextField(
                    value = amount,
                    onValueChange = { amount = it },
                    label = { Text("Amount (BTC)", color = Color(0xFF848E9C)) },
                    modifier = Modifier.fillMaxWidth(),
                    colors = OutlinedTextFieldDefaults.colors(
                        focusedBorderColor = Color(0xFFFCD535),
                        unfocusedBorderColor = Color(0xFF2B3139),
                        containerColor = Color(0xFF0B0E11),
                        textColor = Color.White
                    )
                )
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Leverage (for futures/margin)
                if (viewModel.currentTradingMode.value in listOf("futures", "margin")) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "Leverage",
                            color = Color(0xFF848E9C),
                            fontSize = 14.sp
                        )
                        Text(
                            text = "${leverage}x",
                            color = Color.White,
                            fontWeight = FontWeight.Medium
                        )
                    }
                    
                    Slider(
                        value = leverage.toFloat(),
                        onValueChange = { leverage = it.toInt() },
                        valueRange = 1f..125f,
                        steps = 123,
                        colors = SliderDefaults.colors(
                            thumbColor = Color(0xFFFCD535),
                            activeTrackColor = Color(0xFFFCD535),
                            inactiveTrackColor = Color(0xFF2B3139)
                        ),
                        modifier = Modifier.fillMaxWidth()
                    )
                    
                    Spacer(modifier = Modifier.height(16.dp))
                }
                
                // Total Display
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "Total (USDT)",
                        color = Color(0xFF848E9C),
                        fontSize = 14.sp
                    )
                    Text(
                        text = "0.00",
                        color = Color.White,
                        fontWeight = FontWeight.Medium
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Buy/Sell Button
                Button(
                    onClick = { 
                        viewModel.placeOrder(
                            side = selectedSide,
                            type = selectedOrderType,
                            amount = amount.toFloatOrNull() ?: 0f,
                            price = price.toFloatOrNull()
                        )
                    },
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = if (selectedSide == "buy") Color(0xFF0ECB81) else Color(0xFFF6465D)
                    ),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Icon(
                        imageVector = if (selectedSide == "buy") Icons.Default.ShoppingCart else Icons.Default.Sell,
                        contentDescription = null,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "${selectedSide.uppercase()} BTC",
                        color = Color.White,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Spacer(modifier = Modifier.height(16.dp))
                
                // Available Balance
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Available",
                        color = Color(0xFF848E9C),
                        fontSize = 12.sp
                    )
                    Text(
                        text = "10,000.00 USDT",
                        color = Color.White,
                        fontSize = 12.sp
                    )
                }
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = "Fee",
                        color = Color(0xFF848E9C),
                        fontSize = 12.sp
                    )
                    Text(
                        text = "0.1%",
                        color = Color.White,
                        fontSize = 12.sp
                    )
                }
            }
        }
    }
}

// Order Book Panel
@Composable
fun OrderBookPanel(
    modifier: Modifier = Modifier,
    viewModel: TradingViewModel
) {
    Card(
        modifier = modifier.fillMaxHeight(),
        colors = CardDefaults.cardColors(containerColor = Color(0xFF1E2329)),
        elevation = CardDefaults.cardElevation(0.dp)
    ) {
        Column {
            // Header
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "Order Book",
                    color = Color.White,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "Depth 0.01",
                    color = Color(0xFF848E9C),
                    fontSize = 12.sp
                )
            }
            
            Divider(color = Color(0xFF2B3139))
            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .weight(1f)
            ) {
                // Sell Orders
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .background(Color(0xFF1E2329))
                ) {
                    Text(
                        text = "SELL",
                        color = Color(0xFFF6465D),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(8.dp)
                    )
                    
                    LazyColumn(
                        modifier = Modifier.weight(1f)
                    ) {
                        items(10) { index ->
                            OrderBookRow(
                                price = 67234.56f + (index + 1) * 10f,
                                amount = Random.nextFloat() * 2f,
                                isSell = true
                            )
                        }
                    }
                }
                
                Divider(
                    modifier = Modifier
                        .width(1.dp)
                        .fillMaxHeight(),
                    color = Color(0xFF2B3139)
                )
                
                // Buy Orders
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .background(Color(0xFF1E2329))
                ) {
                    Text(
                        text = "BUY",
                        color = Color(0xFF0ECB81),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(8.dp)
                    )
                    
                    LazyColumn(
                        modifier = Modifier.weight(1f)
                    ) {
                        items(10) { index ->
                            OrderBookRow(
                                price = 67234.56f - (index + 1) * 10f,
                                amount = Random.nextFloat() * 2f,
                                isSell = false
                            )
                        }
                    }
                }
            }
        }
    }
}

// Order Book Row
@Composable
fun OrderBookRow(
    price: Float,
    amount: Float,
    isSell: Boolean
) {
    val total = price * amount
    
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { /* Select price */ }
            .padding(horizontal = 16.dp, vertical = 6.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = price.toString(),
            color = if (isSell) Color(0xFFF6465D) else Color(0xFF0ECB81),
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium,
            modifier = Modifier.weight(1f)
        )
        
        Text(
            text = String.format("%.4f", amount),
            color = Color.White,
            fontSize = 12.sp,
            modifier = Modifier.weight(1f)
        )
        
        Text(
            text = String.format("%.2f", total),
            color = if (isSell) Color(0xFFF6465D) else Color(0xFF0ECB81),
            fontSize = 12.sp,
            fontWeight = FontWeight.Medium,
            modifier = Modifier.weight(1f)
        )
    }
}

// Bottom Navigation Bar
@Composable
fun BottomNavigationBar(navController: NavController) {
    NavigationBar(
        containerColor = Color(0xFF1E2329),
        contentColor = Color(0xFF848E9C)
    ) {
        val navBackStackEntry by navController.currentBackStackEntryAsState()
        val currentRoute = navBackStackEntry?.destination?.route
        
        listOf(
            "trading" to Icons.Default.BarChart,
            "portfolio" to Icons.Default.AccountBalanceWallet,
            "orders" to Icons.Default.List,
            "profile" to Icons.Default.Person
        ).forEach { (route, icon) ->
            NavigationBarItem(
                icon = { Icon(icon, contentDescription = route) },
                label = { Text(route.capitalize()) },
                selected = currentRoute == route,
                onClick = {
                    navController.navigate(route) {
                        popUpTo(navController.graph.startDestinationId)
                        launchSingleTop = true
                    }
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = Color(0xFFFCD535),
                    selectedTextColor = Color(0xFFFCD535),
                    unselectedIconColor = Color(0xFF848E9C),
                    unselectedTextColor = Color(0xFF848E9C),
                    indicatorColor = Color.Transparent
                )
            )
        }
    }
}

// Login Screen
@Composable
fun LoginScreen(navController: NavController) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0B0E11))
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "TigerEx",
            color = Color(0xFFFCD535),
            fontSize = 32.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 48.dp)
        )
        
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email", color = Color(0xFF848E9C)) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = Color(0xFFFCD535),
                unfocusedBorderColor = Color(0xFF2B3139),
                containerColor = Color(0xFF1E2329),
                textColor = Color.White
            )
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password", color = Color(0xFF848E9C)) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = Color(0xFFFCD535),
                unfocusedBorderColor = Color(0xFF2B3139),
                containerColor = Color(0xFF1E2329),
                textColor = Color.White
            )
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = { 
                navController.navigate("trading") {
                    popUpTo("login") { inclusive = true }
                }
            },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFCD535))
        ) {
            Text(
                text = "Login",
                color = Color.Black,
                fontWeight = FontWeight.Bold
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        TextButton(
            onClick = { navController.navigate("register") }
        ) {
            Text(
                text = "Don't have an account? Register",
                color = Color(0xFFFCD535)
            )
        }
    }
}

// Register Screen
@Composable
fun RegisterScreen(navController: NavController) {
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var confirmPassword by remember { mutableStateOf("") }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0B0E11))
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Create Account",
            color = Color.White,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 32.dp)
        )
        
        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email", color = Color(0xFF848E9C)) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = Color(0xFFFCD535),
                unfocusedBorderColor = Color(0xFF2B3139),
                containerColor = Color(0xFF1E2329),
                textColor = Color.White
            )
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password", color = Color(0xFF848E9C)) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = Color(0xFFFCD535),
                unfocusedBorderColor = Color(0xFF2B3139),
                containerColor = Color(0xFF1E2329),
                textColor = Color.White
            )
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        OutlinedTextField(
            value = confirmPassword,
            onValueChange = { confirmPassword = it },
            label = { Text("Confirm Password", color = Color(0xFF848E9C)) },
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = Color(0xFFFCD535),
                unfocusedBorderColor = Color(0xFF2B3139),
                containerColor = Color(0xFF1E2329),
                textColor = Color.White
            )
        )
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = { 
                navController.navigate("trading") {
                    popUpTo("login") { inclusive = true }
                }
            },
            modifier = Modifier.fillMaxWidth(),
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFFFCD535))
        ) {
            Text(
                text = "Register",
                color = Color.Black,
                fontWeight = FontWeight.Bold
            )
        }
        
        Spacer(modifier = Modifier.height(16.dp))
        
        TextButton(
            onClick = { navController.navigate("login") }
        ) {
            Text(
                text = "Already have an account? Login",
                color = Color(0xFFFCD535)
            )
        }
    }
}

// Placeholder Screens
@Composable
fun PortfolioScreen(navController: NavController, viewModel: TradingViewModel) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0B0E11)),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "Portfolio Screen\nComing Soon",
            color = Color.White,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
fun OrdersScreen(navController: NavController, viewModel: TradingViewModel) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0B0E11)),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "Orders Screen\nComing Soon",
            color = Color.White,
            textAlign = TextAlign.Center
        )
    }
}

@Composable
fun ProfileScreen(navController: NavController, viewModel: TradingViewModel) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xFF0B0E11)),
        contentAlignment = Alignment.Center
    ) {
        Text(
            text = "Profile Screen\nComing Soon",
            color = Color.White,
            textAlign = TextAlign.Center
        )
    }
}

// Theme
@Composable
fun TigerExTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = darkColorScheme(
            primary = Color(0xFFFCD535),
            secondary = Color(0xFF0ECB81),
            background = Color(0xFF0B0E11),
            surface = Color(0xFF1E2329),
            onPrimary = Color.Black,
            onSecondary = Color.White,
            onBackground = Color.White,
            onSurface = Color.White
        ),
        content = content
    )
}

// Data Models
data class MarketData(
    val symbol: String,
    val price: Float,
    val change: Float,
    val volume: String,
    val category: String = "spot"
)

// View Model
class TradingViewModel : androidx.lifecycle.ViewModel() {
    private val _markets = mutableStateListOf<MarketData>()
    private val _selectedMarket = mutableStateOf<MarketData?>(null)
    private val _currentTradingMode = mutableStateOf("spot")
    
    val markets: List<MarketData> = _markets
    val selectedMarket: MarketData? = _selectedMarket.value
    val currentTradingMode: String = _currentTradingMode.value
    
    init {
        loadMarkets()
    }
    
    private fun loadMarkets() {
        _markets.addAll(
            listOf(
                MarketData("BTC/USDT", 67234.56f, 2.34f, "1.2B"),
                MarketData("ETH/USDT", 3456.78f, -1.23f, "856M"),
                MarketData("BNB/USDT", 567.89f, 0.87f, "234M"),
                MarketData("SOL/USDT", 123.45f, 5.67f, "456M"),
                MarketData("ADA/USDT", 0.456f, -2.34f, "123M"),
                MarketData("XRP/USDT", 0.789f, 1.23f, "345M"),
                MarketData("DOGE/USDT", 0.089f, 8.90f, "567M"),
                MarketData("AVAX/USDT", 34.56f, -0.45f, "89M"),
                MarketData("DOT/USDT", 7.89f, 2.34f, "67M"),
                MarketData("MATIC/USDT", 0.876f, -1.56f, "234M")
            )
        )
        
        if (_markets.isNotEmpty()) {
            _selectedMarket.value = _markets[0]
        }
    }
    
    fun selectMarket(market: MarketData) {
        _selectedMarket.value = market
    }
    
    fun updateTradingMode(mode: String) {
        _currentTradingMode.value = mode
    }
    
    fun placeOrder(side: String, type: String, amount: Float, price: Float?) {
        // In a real app, this would send the order to the backend
        println("Order placed: $side $type $amount @ $price")
    }
}