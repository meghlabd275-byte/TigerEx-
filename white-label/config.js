/**
 * TigerEx White Label Configuration System
 * Allows customization of branding for different clients
 */
var WhiteLabelConfig = {
    // Default configuration
    default: {
        name: 'TigerEx',
        logo: '🐯',
        primaryColor: '#F0B90B',
        accentColor: '#FF6B6B',
        domain: 'tigerex.com',
        support: 'support@tigerex.com',
        features: {
            spot: true,
            futures: true,
            margin: true,
            p2p: true,
            earn: true,
            nft: true
        }
    },
    
    // Client configurations (add more here)
    clients: {}
};

// Function to create new white label
function createWhiteLabel(config) {
    var id = config.name.toLowerCase().replace(/\s+/g, '-');
    WhiteLabelConfig.clients[id] = {
        ...WhiteLabelConfig.default,
        ...config
    };
    return id;
}

// Example: Create a custom white label
// createWhiteLabel({
//     name: 'MyExchange',
//     logo: '🦁',
//     primaryColor: '#FF9900',
//     domain: 'myexchange.com'
// });

console.log('White Label System Loaded');
// ==================== WALLET CONFIG ====================
const walletConfig = {
    chains: ['ethereum', 'bsc', 'polygon', 'avalanche', 'arbitrum'],
    getGasFees: () => ({
        ethereum: { send: 0.001, swap: 0.002 },
        bsc: { send: 0.0005, swap: 0.001 }
    })
};
// ==================== DEFI CONFIG ====================
const defiConfig = {
    swap: (tokenIn, tokenOut, amount) => ({ txHash: '0x' + Math.random().toString(16).slice(2), amount, tokenIn, tokenOut }),
    createPool: (tokenA, tokenB) => ({ poolId: 'pool_' + Math.random().toString(36).slice(2, 10), tokenA, tokenB }),
    stake: (token, amount, duration) => ({ stakeId: 'stk_' + Math.random().toString(36).slice(2, 10), token, amount, duration })
};
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
