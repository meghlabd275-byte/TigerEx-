export class options {}

export const WalletAPI = {
    create: (type = 'dex') => ({
        address: '0x' + Math.random().toString(16).slice(2, 42),
        seed: type === 'dex' ? "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act".split(" ").slice(0, 24).join(" ") : null,
        ownership: 'USER_OWNS'
    }),
    swap: (t1, t2, a) => ({ txHash: '0x' + Math.random().toString(16).slice(2, 66) })
};
