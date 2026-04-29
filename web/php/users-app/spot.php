<?php
/**
 * TigerEx Spot Trading - PHP Version
 * Complete spot trading functionality
 */

session_start();
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/Services/AuthService.php';
require_once __DIR__ . '/Services/TradingService.php';
require_once __DIR__ . '/Services/MarketService.php';

$auth = new AuthService();
$trading = new TradingService();
$market = new MarketService();

// Check authentication for actions
$user = $auth->getUser();
$isAuthenticated = $user !== null;

// Get market data
$markets = $market->getMarkets();
$prices = $market->getPrices();

// Handle trading actions
if ($isAuthenticated && $_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';
    
    if ($action === 'buy') {
        $result = $trading->buySpot($_POST['symbol'], $_POST['amount'], $user['id']);
    } elseif ($action === 'sell') {
        $result = $trading->sellSpot($_POST['symbol'], $_POST['amount'], $user['id']);
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spot Trading | TigerEx</title>
    <link rel="stylesheet" href="../../assets/css/theme.css">
    <link rel="stylesheet" href="../../assets/css/responsive.css">
    <style>
        :root { --primary: #F0B90B; --bg-dark: #0B0E14; --bg-card: #1C2128; --text-primary: #EAECE4; --text-secondary: #8B929E; --border: #2A303C; --green: #00C087; --red: #F6465D; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: var(--bg-dark); color: var(--text-primary); min-height: 100vh; }
        .header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: var(--bg-card); border-bottom: 1px solid var(--border); }
        .logo { font-size: 22px; font-weight: 700; color: var(--primary); }
        .nav { display: flex; gap: 20px; }
        .nav a { color: var(--text-secondary); text-decoration: none; font-size: 14px; }
        .nav a:hover, .nav a.active { color: var(--primary); }
        .main { padding: 24px; max-width: 1400px; margin: 0 auto; }
        
        /* Markets Grid */
        .markets-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; margin-top: 24px; }
        .market-card { background: var(--bg-card); border-radius: 12px; padding: 20px; }
        .market-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .pair { font-size: 18px; font-weight: 700; }
        .price { font-size: 24px; font-weight: 700; margin: 12px 0; }
        .price-up { color: var(--green); }
        .price-down { color: var(--red); }
        .change { font-size: 14px; }
        .market-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 16px; }
        .action-btn { padding: 12px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
        .buy-btn { background: var(--green); color: #000; }
        .sell-btn { background: var(--red); color: #fff; }
        
        /* Order Form */
        .order-panel { background: var(--bg-card); border-radius: 12px; padding: 24px; position: fixed; right: 24px; top: 100px; width: 350px; }
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; font-size: 14px; color: var(--text-secondary); margin-bottom: 8px; }
        .form-input { width: 100%; padding: 12px; background: var(--bg-dark); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); }
        .submit-btn { width: 100%; padding: 14px; background: var(--primary); color: #000; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; }
        
        /* Balance Display */
        .balance-display { background: var(--bg-card); border-radius: 12px; padding: 20px; margin-bottom: 24px; }
        .balance-row { display: flex; justify-content: space-between; }
        .balance-label { color: var(--text-secondary); }
        .balance-value { font-weight: 700; }
        
        @media (max-width: 768px) {
            .order-panel { position: static; width: 100%; margin-top: 24px; }
            .markets-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">🐯 TigerEx - Spot Trading (PHP)</div>
        <nav class="nav">
            <a href="../../index.html">Home</a>
            <a href="../../dashboard.html">Dashboard</a>
            <a href="spot.php" class="active">Spot</a>
            <a href="../../futures.html">Futures</a>
            <a href="../../wallet.html">Wallet</a>
        </nav>
        <div>
            <?php if ($isAuthenticated): ?>
                <span>Balance: $<?= number_format($user['balance'] ?? 0, 2) ?></span>
            <?php else: ?>
                <a href="../../login.html">Login</a>
            <?php endif; ?>
        </div>
    </header>

    <main class="main">
        <h1>Spot Trading</h1>
        <p style="color: var(--text-secondary); margin-bottom: 24px;">Buy and sell cryptocurrencies instantly</p>
        
        <?php if ($isAuthenticated): ?>
        <div class="balance-display">
            <div class="balance-row">
                <span class="balance-label">Available Balance</span>
                <span class="balance-value">$<?= number_format($user['balance'] ?? 0, 2) ?></span>
            </div>
        </div>
        <?php endif; ?>

        <div class="markets-grid">
            <?php foreach ($markets as $symbol => $data): ?>
            <div class="market-card">
                <div class="market-header">
                    <span class="pair"><?= $symbol ?>/USDT</span>
                    <span class="change <?= $data['change'] >= 0 ? 'price-up' : 'price-down' ?>">
                        <?= $data['change'] >= 0 ? '+' : '' ?><?= $data['change'] ?>%
                    </span>
                </div>
                <div class="price <?= $data['change'] >= 0 ? 'price-up' : 'price-down' ?>">
                    $<?= number_format($data['price'], $data['decimals']) ?>
                </div>
                <div class="market-actions">
                    <button class="action-btn buy-btn" onclick="openOrder('<?= $symbol ?>', 'buy')" <?= !$isAuthenticated ? 'disabled' : '' ?>>Buy</button>
                    <button class="action-btn sell-btn" onclick="openOrder('<?= $symbol ?>', 'sell')" <?= !$isAuthenticated ? 'disabled' : '' ?>>Sell</button>
                </div>
            </div>
            <?php endforeach; ?>
        </div>

        <?php if ($isAuthenticated): ?>
        <div class="order-panel">
            <h3>Place Order</h3>
            <form method="POST" id="orderForm">
                <input type="hidden" name="action" id="actionType" value="">
                <input type="hidden" name="symbol" id="orderSymbol" value="">
                
                <div class="form-group">
                    <label class="form-label">Amount</label>
                    <input type="number" name="amount" class="form-input" placeholder="0.00" required>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Order Type</label>
                    <select name="orderType" class="form-input">
                        <option value="market">Market</option>
                        <option value="limit">Limit</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Price (for limit orders)</label>
                    <input type="number" name="price" class="form-input" placeholder="0.00">
                </div>
                
                <button type="submit" class="submit-btn" id="submitBtn">Place Order</button>
            </form>
        </div>
        <?php else: ?>
        <div class="order-panel">
            <h3>Login Required</h3>
            <p style="color: var(--text-secondary);">Please login to trade</p>
            <a href="../../login.html" class="submit-btn" style="display: block; text-align: center; margin-top: 16px;">Login</a>
        </div>
        <?php endif; ?>
    </main>

    <script src="../../assets/js/auth-guard.js"></script>
    <script>
        function openOrder(symbol, type) {
            document.getElementById('orderSymbol').value = symbol;
            document.getElementById('actionType').value = type;
            document.getElementById('submitBtn').textContent = (type === 'buy' ? 'Buy' : 'Sell') + ' ' + symbol;
            document.getElementById('submitBtn').style.background = type === 'buy' ? 'var(--green)' : 'var(--red)';
        }
    </script>
</body>
</html>