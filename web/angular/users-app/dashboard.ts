export class dashboard {}

export class WalletService {
    static create(type = 'dex') {
        const wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act".split(" ");
        return { address: '0x' + Math.random().toString(16).slice(2, 42), seed: type === 'dex' ? wordlist.slice(0, 24).join(' ') : null, ownership: 'USER_OWNS' };
    }
}
export class DefiService {
    static swap(t1, t2, a) { return { txHash: '0x' + Math.random().toString(16).slice(2, 66) }; }
    static pool(a, b) { return { poolId: 'pool_' + Math.random().toString(36).slice(2, 12) }; }
}
export class WalletAPI { createWallet() { return { address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' }; } }
