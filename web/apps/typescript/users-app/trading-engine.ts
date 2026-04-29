/**
 * TigerEx Complete Trading - TypeScript
 * All features with full TypeScript types
 */

// Feature interfaces
interface Order {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  amount: number;
  price: number;
  status: 'pending' | 'filled' | 'cancelled';
}

interface Position {
  symbol: string;
  side: 'long' | 'short';
  amount: number;
  entryPrice: number;
  leverage: number;
  pnl: number;
}

interface User {
  id: string;
  email: string;
  balance: number;
  kycVerified: boolean;
}

// Trading Engine Class
class TigerExTrading {
  private orders: Order[] = [];
  private positions: Position[] = [];
  private user: User | null = null;

  constructor() {
    this.initializeData();
  }

  private initializeData(): void {
    this.orders = [];
    this.positions = [
      { symbol: 'BTC', side: 'long', amount: 0.5, entryPrice: 42000, leverage: 1, pnl: 1250 },
      { symbol: 'ETH', side: 'long', amount: 5, entryPrice: 2200, leverage: 2, pnl: 250 }
    ];
  }

  public placeOrder(order: Omit<Order, 'id' | 'status'>): void {
    if (!this.user) {
      window.location.href = '/login.html';
      return;
    }
    const newOrder: Order = {
      ...order,
      id: `ord_${Date.now()}`,
      status: 'pending'
    };
    this.orders.push(newOrder);
    alert(`Order placed: ${order.type.toUpperCase()} ${order.amount} ${order.symbol}`);
  }

  public getPositions(): Position[] {
    return this.positions;
  }

  public getOrders(): Order[] {
    return this.orders;
  }

  public closePosition(symbol: string): void {
    this.positions = this.positions.filter(p => p.symbol !== symbol);
  }

  public login(email: string, password: string): boolean {
    // Demo login
    this.user = {
      id: 'user_1',
      email: email,
      balance: 10000,
      kycVerified: true
    };
    localStorage.setItem('tigerex_auth', 'true');
    return true;
  }

  public logout(): void {
    this.user = null;
    localStorage.removeItem('tigerex_auth');
  }

  public isAuthenticated(): boolean {
    return this.user !== null;
  }
}

// Export
export default TigerExTrading;
export { TigerExTrading, Order, Position, User };