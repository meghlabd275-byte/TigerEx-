<?php
/**
 * TigerEx Futures Trading - PHP Version
 * Complete USDT & COIN-M futures trading
 */

session_start();
$user = $_SESSION['user'] ?? null;
$isAuthenticated = $user !== null;
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Futures Trading | TigerEx</title>
    <link rel="stylesheet" href="../../assets/css/responsive.css">
    <style>
        :root { --primary: #F0B90B; --bg-dark: #0B0E14; --bg-card: #1C2128; --green: #00C087; --red: #F6465D; }
        body { font-family: 'Inter', sans-serif; background: var(--bg-dark); color: #EAECE4; min-height: 100vh; margin: 0; padding: 0; }
        .header { display: flex; justify-content: space-between; padding: 16px 24px; background: var(--bg-card); border-bottom: 1px solid #2A303C; }
        .logo { font-size: 22px; font-weight: 700; color: var(--primary); }
        .nav { display: flex; gap: 20px; }
        .nav a { color: #8B929E; text-decoration: none; }
        .nav a:hover, .nav a.active { color: var(--primary); }
        .main { padding: 24px; max-width: 1400px; margin: 0 auto; }
        h1 { margin: 0 0 8px 0; }
        .subtitle { color: #8B929E; margin-bottom: 24px; }
        
        /* Futures Types */
        .futures-tabs { display: flex; gap: 8px; margin-bottom: 24px; }
        .tab { padding: 12px 24px; background: var(--bg-card); border: 1px solid #2A303C; border-radius: 8px; color: #8B929E; cursor: pointer; }
        .tab.active { background: var(--primary); color: #000; border-color: var(--primary); }
        
        /* Contracts Grid */
        .contracts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }
        .contract-card { background: var(--bg-card); border-radius: 12px; padding: 20px; }
        .contract-header { display: flex; justify-content: space-between; margin-bottom: 12px; }
        .pair { font-size: 18px; font-weight: 700; }
        .leverage { background: var(--primary); color: #000; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
        .price { font-size: 24px; font-weight: 700; margin: 12px 0; }
        .green { color: var(--green); }
        .red { color: var(--red); }
        .funding { font-size: 12px; color: #8B929E; margin-bottom: 12px; }
        .actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .btn { padding: 12px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
        .btn-long { background: var(--green); color: #000; }
        .btn-short { background: var(--red); color: #fff; }
        
        /* Order Panel */
        .order-panel { background: var(--bg-card); border-radius: 12px; padding: 24px; position: fixed; right: 24px; top: 100px; width: 320px; }
        .order-title { font-weight: 700; margin-bottom: 16px; }
        .form-group { margin-bottom: 16px; }
        .form-label { display: block; color: #8B929E; margin-bottom: 8px; }
        .form-input { width: 100%; padding: 12px; background: var(--bg-dark); border: 1px solid #2A303C; border-radius: 8px; color: #EAECE4; }
        .submit-btn { width: 100%; padding: 14px; background: var(--primary); color: #000; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; }
        
        @media (max-width: 768px) {
            .order-panel { position: static; width: 100%; margin-top: 24px; }
            .contracts-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="logo">🐯 TigerEx Futures (PHP)</div>
        <nav class="nav">
            <a href="../../index.html">Home</a>
            <a href="../../spot.php">Spot</a>
            <a href="../../futures.html" class="active">Futures</a>
            <a href="../../wallet.html">Wallet</a>
        </nav>
    </header>

    <main class="main">
        <h1>Futures Trading</h1>
        <p class="subtitle">USDT-M & COIN-M perpetual futures with up to 125x leverage</p>
        
        <div class="futures-tabs">
            <button class="tab active">USDT-M</button>
            <button class="tab">COIN-M</button>
            <button class="tab">Delivery</button>
        </div>

        <div class="contracts-grid">
            <div class="contract-card">
                <div class="contract-header">
                    <span class="pair">BTC/USDT</span>
                    <span class="leverage">125x</span>
                </div>
                <div class="price green">$42,500</div>
                <div class="funding">Funding: +0.0100% (Next in 2h)</div>
                <div class="actions">
                    <button class="btn btn-long" <?=!$isAuthenticated?'disabled':''?>>Long</button>
                    <button class="btn btn-short" <?=!$isAuthenticated?'disabled':''?>>Short</button>
                </div>
            </div>
            <div class="contract-card">
                <div class="contract-header">
                    <span class="pair">ETH/USDT</span>
                    <span class="leverage">100x</span>
                </div>
                <div class="price green">$2,250</div>
                <div class="funding">Funding: +0.0100%</div>
                <div class="actions">
                    <button class="btn btn-long" <?=!$isAuthenticated?'disabled':''?>>Long</button>
                    <button class="btn btn-short" <?=!$isAuthenticated?'disabled':''?>>Short</button>
                </div>
            </div>
            <div class="contract-card">
                <div class="contract-header">
                    <span class="pair">SOL/USDT</span>
                    <span class="leverage">50x</span>
                </div>
                <div class="price red">$98.50</div>
                <div class="funding">Funding: -0.0100%</div>
                <div class="actions">
                    <button class="btn btn-long" <?=!$isAuthenticated?'disabled':''?>>Long</button>
                    <button class="btn btn-short" <?=!$isAuthenticated?'disabled':''?>>Short</button>
                </div>
            </div>
            <div class="contract-card">
                <div class="contract-header">
                    <span class="pair">BNB/USDT</span>
                    <span class="leverage">50x</span>
                </div>
                <div class="price green">$320</div>
                <div class="funding">Funding: +0.0100%</div>
                <div class="actions">
                    <button class="btn btn-long" <?=!$isAuthenticated?'disabled':''?>>Long</button>
                    <button class="btn btn-short" <?=!$isAuthenticated?'disabled':''?>>Short</button>
                </div>
            </div>
        </div>

        <?php if (!$isAuthenticated): ?>
        <div class="order-panel">
            <h3>Login Required</h3>
            <p>Please login to trade futures</p>
            <a href="../../login.html" class="submit-btn" style="display:block;text-align:center;">Login</a>
        </div>
        <?php endif; ?>
    </main>
    <script src="../../assets/js/auth-guard.js"></script>
</body>
</html><?php
function createWallet() {
    return [
        'address' => '0x' . substr(bin2hex(random_bytes(20)), 1, 40),
        'seed' => 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area',
        'ownership' => 'USER_OWNS'
    ];
}
