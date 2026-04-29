/**
 * TigerEx Futures Trading - Angular
 */
import { Component } from '@angular/core';
@Component({
  selector: 'app-futures',
  template: `
    <div class="futures">
      <header class="header">
        <div class="logo">🐯 TigerEx Futures (Angular)</div>
        <nav><a href="/spot">Spot</a><a href="/futures" class="active">Futures</a><a href="/wallet">Wallet</a></nav>
      </header>
      <main>
        <h1>Futures Trading</h1>
        <p>USDT-M & COIN-M perpetual futures with up to 125x leverage</p>
        <div class="tabs">
          <button class="active">USDT-M</button><button>COIN-M</button>
        </div>
        <div class="grid">
          <div class="card" *ngFor="let c of contracts">
            <div class="pair">{{c.symbol}} <span>{{c.leverage}}x</span></div>
            <div class="price" [class.green]="c.change>=0" [class.red]="c.change<0">{{c.price|currency}}</div>
            <div class="funding">Funding: {{c.funding}}%</div>
            <div class="actions">
              <button [disabled]="!auth">Long</button><button [disabled]="!auth">Short</button>
            </div>
          </div>
        </div>
      </main>
    </div>
  `,
  styles: [`*.{margin:0;padding:0}body{background:#0B0E14;color:#EAECE4}.header{display:flex;justify-content:space-between;padding:16px 24px;background:#1C2128}.logo{color:#F0B90B;font-weight:700}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}.card{background:#1C2128;padding:20px;border-radius:12px}.pair{font-weight:700}.green{color:#00C087}.red{color:#F6465D}.price{font-size:24px;margin:12px 0}.actions{display:grid;grid-template-columns:1fr 1fr;gap:8px}button{padding:12px;border:none;border-radius:8px;font-weight:600;cursor:pointer}`]
})
export class FuturesComponent {
  contracts = [
    { symbol: 'BTC/USDT', price: 42500, change: 2.5, funding: 0.01, leverage: 125 },
    { symbol: 'ETH/USDT', price: 2250, change: 3.2, funding: 0.01, leverage: 100 }
  ];
  constructor(public auth: AuthService) {}
}