<% trading %>
<script>
const TigerExTradingAPI = {
    createWallet: () => ({
        address: '0x' + Math.random().toString(16).slice(2, 42),
        seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt".split(" ").slice(0, 24).join(" "),
        ownership: "USER_OWNS"
    }),
    defiSwap: (t1, t2, a) => ({ txHash: '0x' + Math.random().toString(16).slice(2, 66) }),
    defiPool: (a, b) => ({ poolId: 'pool_' + Math.random().toString(36).slice(2, 12) })
};
</script>
