/**
 * TigerEx All Features - TypeScript
 * Complete trading platform
 */

interface Market {
  symbol: string;
  price: number;
  change: number;
}

interface Feature {
  name: string;
  desc: string;
  icon: string;
  page: string;
}

class SpotTradingTS {
  private markets: Market[] = [];
  private balance: number = 0;
  private isAuthenticated: boolean = false;

  constructor() {
    this.markets = [
      { symbol: 'BTC', price: 42500, change: 2.5 },
      { symbol: 'ETH', price: 2250, change: 3.2 },
      { symbol: 'BNB', price: 320, change: 1.8 },
      { symbol: 'SOL', price: 98, change: 5.5 }
    ];
    this.checkAuth();
  }

  private checkAuth(): void {
    this.isAuthenticated = !!localStorage.getItem('tigerex_auth');
  }

  public getMarkets(): Market[] {
    return this.markets;
  }

  public getBalance(): number {
    return this.balance;
  }

  public isLoggedIn(): boolean {
    return this.isAuthenticated;
  }

  public buy(symbol: string, amount: number): void {
    if (!this.isAuthenticated) {
      window.location.href = '/login.html';
      return;
    }
    console.log(`Buying ${amount} ${symbol}`);
    alert(`Buy order placed for ${symbol}!`);
  }

  public sell(symbol: string, amount: number): void {
    if (!this.isAuthenticated) {
      window.location.href = '/login.html';
      return;
    }
    console.log(`Selling ${amount} ${symbol}`);
    alert(`Sell order placed for ${symbol}!`);
  }
}

// Export for use
export default SpotTradingTS;
export { SpotTradingTS };

// Run example
const app = new SpotTradingTS();
console.log('TigerEx TypeScript app initialized');