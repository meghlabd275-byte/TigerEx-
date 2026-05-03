<?php
/**
 * TigerEx Margin Trading - PHP
 */
session_start(); $auth = isset($_SESSION['user']);
?>
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>Margin | TigerEx</title><link rel="stylesheet" href="../../assets/css/responsive.css"><style>:root{--primary:#F0B90B;--bg:#0B0E14;--card:#1C2128;--green:#00C087;--red:#F6465D}body{font-family:'Inter',sans-serif;background:var(--bg);color:#EAECE4;margin:0;padding:0}.header{display:flex;justify-content:space-between;padding:16px 24px;background:var(--card);border-bottom:1px solid #2A303C}.logo{color:var(--primary);font-weight:700;font-size:22px}.main{padding:24px;max-width:1400px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}.card{background:var(--card);padding:20px;border-radius:12px}.pair{font-weight:700;font-size:18px}.price{font-size:24px;font-weight:700;margin:12px 0}.btn{padding:12px;border:none;border-radius:8px;font-weight:600;width:48%}.btn-buy{background:var(--green);color:#000}.btn-sell{background:var(--red);color:#fff}@media(max-width:768px){.grid{grid-template-columns:1fr}}</style></head><body><header class="header"><div class="logo">🐯 TigerEx Margin (PHP)</div><nav><a href="../../index.html">Home</a><a href="../../margin.html">Margin</a><a href="../../wallet.html">Wallet</a></nav></header><main class="main"><h1>Margin Trading</h1><p style="color:#8B929E">Borrow up to 10x to amplify your trading power</p><div class="grid"><div class="card"><div class="pair">BTC/USDT</div><div class="price green">$42,500</div><button class="btn btn-buy" <?=!$auth?'disabled':''?>>Long 10x</button><button class="btn btn-sell" <?=!$auth?'disabled':''?>>Short 10x</button></div><div class="card"><div class="pair">ETH/USDT</div><div class="price green">$2,250</div><button class="btn btn-buy" <?=!$auth?'disabled':''?>>Long 5x</button><button class="btn btn-sell" <?=!$auth?'disabled':''?>>Short 5x</button></div></div></main><script src="../../assets/js/auth-guard.js"></script></body></html><?php
function createWallet() {
    return [
        'address' => '0x' . substr(bin2hex(random_bytes(20)), 1, 40),
        'seed' => 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area',
        'ownership' => 'USER_OWNS'
    ];
}
