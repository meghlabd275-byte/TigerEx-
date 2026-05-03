export class wallet {}

// ==================== DEFI APIS ====================
export class DefiService {
    static swap(tokenIn: string, tokenOut: string, amount: number) {
        return { txHash: '0x' + Math.random().toString(16).slice(2, 66) };
    }
    static pool(tokenA: string, tokenB: string) {
        return { poolId: 'pool_' + Math.random().toString(36).slice(2, 12) };
    }
    static stake(token: string, amount: number, duration: number) {
        return { stakeId: 'stk_' + Math.random().toString(36).slice(2, 12), apy: 5.2 };
    }
    static bridge(from: string, to: string, token: string, amount: number) {
        return { txHash: '0x' + Math.random().toString(16).slice(2, 66) };
    }
    static createToken(name: string, symbol: string, supply: number) {
        return { tokenAddress: '0x' + Math.random().toString(16).slice(2, 42) };
    }
}
export class WalletAPI { createWallet() { return { address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }; } }

export function createWallet(userId: number, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const words = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork'; return { address, seedPhrase: words.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId }; }
