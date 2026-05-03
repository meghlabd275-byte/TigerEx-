/**
 * TigerEx Spot Trading - Angular Component
 * Complete spot trading functionality
 */

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { TigerExService } from '../../services/tigerex.service';
import { AuthService } from '../../services/auth.service';

interface Market {
  symbol: string;
  price: number;
  change: number;
  volume: number;
}

@Component({
  selector: 'app-spot-trading',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="spot-trading">
      <!-- Header -->
      <header class="header">
        <div class="logo">🐯 TigerEx - Spot Trading (Angular)</div>
        <nav class="nav">
          <a routerLink="/dashboard">Dashboard</a>
          <a routerLink="/spot" class="active">Spot</a>
          <a routerLink="/futures">Futures</a>
          <a routerLink="/wallet">Wallet</a>
        </nav>
        <div class="user-info" *ngIf="auth.isAuthenticated()">
          <span>Balance: {{ balance | currency }}</span>
        </div>
      </header>

      <main class="main">
        <h1>Spot Trading</h1>
        <p class="subtitle">Buy and sell cryptocurrencies instantly</p>

        <!-- Balance Display -->
        <div class="balance-display" *ngIf="auth.isAuthenticated()">
          <div class="balance-item">
            <span class="label">Available Balance</span>
            <span class="value">{{ balance | currency }}</span>
          </div>
        </div>

        <!-- Markets Grid -->
        <div class="markets-grid">
          <div class="market-card" *ngFor="let market of markets">
            <div class="market-header">
              <span class="pair">{{ market.symbol }}/USDT</span>
              <span class="change" [class.positive]="market.change >= 0" [class.negative]="market.change < 0">
                {{ market.change >= 0 ? '+' : '' }}{{ market.change }}%
              </span>
            </div>
            <div class="price" [class.positive]="market.change >= 0" [class.negative]="market.change < 0">
              {{ market.price | currency }}
            </div>
            <div class="volume">Volume: {{ market.volume | number }}</div>
            <div class="market-actions">
              <button class="buy-btn" (click)="openOrder(market.symbol, 'buy')" [disabled]="!auth.isAuthenticated()">Buy</button>
              <button class="sell-btn" (click)="openOrder(market.symbol, 'sell')" [disabled]="!auth.isAuthenticated()">Sell</button>
            </div>
          </div>
        </div>

        <!-- Order Panel -->
        <div class="order-panel" *ngIf="selectedSymbol">
          <h3>Place Order - {{ orderType }} {{ selectedSymbol }}</h3>
          <form (ngSubmit)="placeOrder()">
            <div class="form-group">
              <label>Amount</label>
              <input type="number" [(ngModel)]="orderAmount" name="amount" required>
            </div>
            <div class="form-group">
              <label>Order Type</label>
              <select [(ngModel)]="orderTypeOption" name="orderType">
                <option value="market">Market</option>
                <option value="limit">Limit</option>
              </select>
            </div>
            <div class="form-group" *ngIf="orderTypeOption === 'limit'">
              <label>Price</label>
              <input type="number" [(ngModel)]="orderPrice" name="price">
            </div>
            <button type="submit" class="submit-btn" [class.buy]="orderType === 'buy'" [class.sell]="orderType === 'sell'">
              {{ orderType === 'buy' ? 'Buy' : 'Sell' }} {{ selectedSymbol }}
            </button>
          </form>
        </div>

        <!-- Login Required -->
        <div class="order-panel" *ngIf="!auth.isAuthenticated()">
          <h3>Login Required</h3>
          <p>Please login to trade</p>
          <a routerLink="/login" class="submit-btn">Login</a>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: #1C2128; border-bottom: 1px solid #2A303C; }
    .logo { font-size: 22px; font-weight: 700; color: #F0B90B; }
    .nav { display: flex; gap: 20px; }
    .nav a { color: #8B929E; text-decoration: none; }
    .nav a:hover, .nav a.active { color: #F0B90B; }
    .main { padding: 24px; max-width: 1400px; margin: 0 auto; }
    .subtitle { color: #8B929E; margin-bottom: 24px; }
    .balance-display { background: #1C2128; border-radius: 12px; padding: 20px; margin-bottom: 24px; }
    .balance-item { display: flex; justify-content: space-between; }
    .label { color: #8B929E; }
    .value { font-weight: 700; }
    .markets-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px; }
    .market-card { background: #1C2128; border-radius: 12px; padding: 20px; }
    .market-header { display: flex; justify-content: space-between; margin-bottom: 12px; }
    .pair { font-size: 18px; font-weight: 700; }
    .change.positive { color: #00C087; }
    .change.negative { color: #F6465D; }
    .price { font-size: 24px; font-weight: 700; margin: 12px 0; }
    .volume { font-size: 14px; color: #8B929E; }
    .market-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 16px; }
    .buy-btn, .sell-btn { padding: 12px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; }
    .buy-btn { background: #00C087; color: #000; }
    .sell-btn { background: #F6465D; color: #fff; }
    .order-panel { background: #1C2128; border-radius: 12px; padding: 24px; margin-top: 24px; }
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; font-size: 14px; color: #8B929E; margin-bottom: 8px; }
    .form-group input, .form-group select { width: 100%; padding: 12px; background: #0B0E14; border: 1px solid #2A303C; border-radius: 8px; color: #EAECE4; }
    .submit-btn { width: 100%; padding: 14px; border: none; border-radius: 8px; font-weight: 700; cursor: pointer; }
    .submit-btn.buy { background: #00C087; color: #000; }
    .submit-btn.sell { background: #F6465D; color: #fff; }
  `]
})
export class SpotTradingComponent implements OnInit {
  markets: Market[] = [];
  balance: number = 0;
  selectedSymbol: string = '';
  orderType: string = 'buy';
  orderAmount: number = 0;
  orderPrice: number = 0;
  orderTypeOption: string = 'market';

  constructor(
    private api: TigerExService,
    public auth: AuthService,
    private router: Router
  ) {}

  ngOnInit() {
    this.loadMarkets();
    if (this.auth.isAuthenticated()) {
      this.loadBalance();
    }
  }

  loadMarkets() {
    this.api.getMarkets().subscribe(data => {
      this.markets = data;
    });
  }

  loadBalance() {
    this.api.getBalance().subscribe(data => {
      this.balance = data.balance;
    });
  }

  openOrder(symbol: string, type: string) {
    if (!this.auth.isAuthenticated()) {
      this.router.navigate(['/login']);
      return;
    }
    this.selectedSymbol = symbol;
    this.orderType = type;
  }

  placeOrder() {
    if (!this.selectedSymbol || !this.orderAmount) return;
    
    const order = {
      symbol: this.selectedSymbol,
      side: this.orderType,
      amount: this.orderAmount,
      price: this.orderPrice,
      orderType: this.orderTypeOption
    };

    if (this.orderType === 'buy') {
      this.api.buySpot(order).subscribe(result => {
        alert('Order placed successfully!');
        this.loadBalance();
      });
    } else {
      this.api.sellSpot(order).subscribe(result => {
        alert('Order placed successfully!');
        this.loadBalance();
      });
    }
  }
}export class WalletAPI { createWallet() { return { address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }; } }
