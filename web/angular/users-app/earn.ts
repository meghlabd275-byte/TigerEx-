export class earn {}

export class WalletAPI {
    static create(type = 'dex') {
        const wordlist = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act".split(" ");
        return { address: '0x' + Math.random().toString(16).slice(2, 42), seed: type === 'dex' ? wordlist.slice(0, 24).join(' ') : null, ownership: 'USER_OWNS' };
    }
    static defiSwap(t1, t2, a) { return { txHash: '0x' + Math.random().toString(16).slice(2, 66) }; }
}
