export class settings {}

export const TigerExService = {
    createWallet: (type = 'dex') => ({
        address: '0x' + Math.random().toString(16).slice(2, 42),
        seed: type === 'dex' ? "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act".split(" ").slice(0, 24).join(" ") : null,
        ownership: 'USER_OWNS'
    }),
    getGasFees: () => ({ ethereum: { send: 0.001, swap: 0.002 }, bsc: { send: 0.0005, swap: 0.001 } })
};
