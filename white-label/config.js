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
