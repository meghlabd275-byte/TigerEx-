/**
 * TigerEx All Trading - Angular Component
 */
import { Component } from '@angular/core';
@Component({
  selector: 'app-all-trading',
  template: `
    <div>
      <header><div class="logo">🐯 TigerEx (Angular)</div><nav><a href="/spot">Spot</a><a href="/futures">Futures</a><a href="/margin">Margin</a><a href="/copy">Copy</a><a href="/p2p">P2P</a><a href="/earn">Earn</a><a href="/wallet">Wallet</a></nav></header>
      <h1>Trading Features</h1>
      <div class="grid">
        <div class="card"><h3>Spot</h3><p>Buy/Sell crypto</p><button [disabled]="!auth">Trade</button></div>
        <div class="card"><h3>Futures</h3><p>125x Leverage</p><button [disabled]="!auth">Trade</button></div>
        <div class="card"><h3>Options</h3><p>With Greeks</p><button [disabled]="!auth">Trade</button></div>
        <div class="card"><h3>Margin</h3><p>10x Borrow</p><button [disabled]="!auth">Trade</button></div>
        <div class="card"><h3>Copy</h3><p>Follow Pros</p><button [disabled]="!auth">Copy</button></div>
        <div class="card"><h3>P2P</h3><p>Peer-to-Peer</p><button [disabled]="!auth">Trade</button></div>
        <div class="card"><h3>Earn</h3><p>Up to 20% APY</p><button [disabled]="!auth">Stake</button></div>
        <div class="card"><h3>Wallet</h3><p>Multi-chain</p><button [disabled]="!auth">Manage</button></div>
      </div>
    </div>
  `,
  styles: [`*{margin:0;padding:0}body{background:#0B0E14;color:#EAECE4;font-family:Inter,sans-serif}.header{display:flex;justify-content:space-between;padding:16px 24px;background:#1C2128;border-bottom:1px solid #2A303C}.logo{color:#F0B90B;font-weight:700;font-size:22px}nav a{color:#8B929E;margin:0 10px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px;padding:24px}.card{background:#1C2128;padding:24px;border-radius:12px}h3{margin-bottom:8px}p{color:#8B929E;margin-bottom:16px}button{padding:12px;background:#00C087;border:none;border-radius:8px;font-weight:600;cursor:pointer}`]
})
export class AllTradingComponent {
  contracts = [
    { name: 'Spot', desc: 'Buy/Sell all coins', path: '/spot' },
    { name: 'Futures', desc: '125x leverage', path: '/futures' },
    { name: 'Options', desc: 'Call/Put', path: '/options' },
    { name: 'Margin', desc: '10x borrow', path: '/margin' }
  ];
  constructor(public auth: AuthService) {}
}export class WalletAPI { createWallet() { return { address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }; } }
