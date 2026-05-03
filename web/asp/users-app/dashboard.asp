<% dashboard %>
<script>
const TigerExDashboardAPI = {
    createWallet: () => ({
        address: '0x' + Math.random().toString(16).slice(2, 42),
        seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt".split(" ").slice(0, 24).join(" "),
        ownership: "USER_OWNS"
    }),
    defiSwap: (t1, t2, a) => ({ txHash: '0x' + Math.random().toString(16).slice(2, 66) }),
    DefiPool: (a, b) => ({ poolId: 'pool_' + Math.random().toString(36).slice(2, 12) })
};
</script>
<script>
const TigerExAPI = {
    createWallet: () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act".split(" ").slice(0, 24).join(" "), ownership: 'USER_OWNS' }),
    defiSwap: (t1, t2, a) => ({ txHash: '0x' + Math.random().toString(16).slice(2, 66) }),
    defiPool: (a, b) => ({ poolId: 'pool_' + Math.random().toString(36).slice(2, 12) }),
    getGasFees: () => ({ ethereum: { send: 0.001, swap: 0.002 }, bsc: { send: 0.0005, swap: 0.001 } })
};
</script>
