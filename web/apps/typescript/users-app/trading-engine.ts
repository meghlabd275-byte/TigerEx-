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
export { TigerExTrading, Order, Position, User };export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

export function createWallet(userId: number, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const words = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork'; return { address, seedPhrase: words.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId }; }
