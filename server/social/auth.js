/**
 * TigerEx Social Authentication API
 * Handles OAuth for all social platforms
 */
const express = require('express');
const axios = require('axios');
const jwt = require('jsonwebtoken');

const router = express.Router();

// Social OAuth Config
const SOCIAL_CONFIG = {
  google: {
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    tokenUrl: 'https://oauth2.googleapis.com/token',
    userInfoUrl: 'https://www.googleapis.com/oauth2/v2/userinfo',
    clientId: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET
  },
  apple: {
    authUrl: 'https://appleid.apple.com/auth/authorize',
    tokenUrl: 'https://appleid.apple.com/auth/token',
    clientId: process.env.APPLE_CLIENT_ID,
    clientSecret: process.env.APPLE_CLIENT_SECRET
  },
  facebook: {
    authUrl: 'https://www.facebook.com/v18.0/dialog/oauth',
    tokenUrl: 'https://graph.facebook.com/v18.0/oauth/access_token',
    userInfoUrl: 'https://graph.facebook.com/me',
    clientId: process.env.FACEBOOK_CLIENT_ID,
    clientSecret: process.env.FACEBOOK_CLIENT_SECRET
  },
  github: {
    authUrl: 'https://github.com/login/oauth/authorize',
    tokenUrl: 'https://github.com/login/oauth/access_token',
    userInfoUrl: 'https://api.github.com/user',
    clientId: process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET
  },
  discord: {
    authUrl: 'https://discord.com/api/oauth2/authorize',
    tokenUrl: 'https://discord.com/api/oauth2/token',
    userInfoUrl: 'https://discord.com/api/users/@me',
    clientId: process.env.DISCORD_CLIENT_ID,
    clientSecret: process.env.DISCORD_CLIENT_SECRET
  },
  twitter: {
    authUrl: 'https://twitter.com/i/oauth2/authorize',
    tokenUrl: 'https://api.twitter.com/2/oauth2/token',
    userInfoUrl: 'https://api.twitter.com/2/users/me',
    clientId: process.env.TWITTER_CLIENT_ID,
    clientSecret: process.env.TWITTER_CLIENT_SECRET
  }
};

// Generate OAuth URL
router.get('/auth-url/:provider', (req, res) => {
  const { provider } = req.params;
  const config = SOCIAL_CONFIG[provider];
  
  if (!config) {
    return res.status(400).json({ error: 'Invalid provider' });
  }
  
  const redirectUri = `${process.env.API_URL}/api/auth/social/callback/${provider}`;
  
  const authUrls = {
    google: `${config.authUrl}?client_id=${config.clientId}&redirect_uri=${redirectUri}&response_type=code&scope=email%20profile`,
    apple: `${config.authUrl}?client_id=${config.clientId}&redirect_uri=${redirectUri}&response_type=code&scope=name%20email`,
    facebook: `${config.authUrl}?client_id=${config.clientId}&redirect_uri=${redirectUri}&scope=email%20public_profile`,
    github: `${config.authUrl}?client_id=${config.clientId}&redirect_uri=${redirectUri}&scope=user:email`,
    discord: `${config.authUrl}?client_id=${config.clientId}&redirect_uri=${redirectUri}&scope=identify%20email&response_type=code`,
    twitter: `${config.authUrl}?client_id=${config.clientId}&redirect_uri=${redirectUri}&scope=tweet.read%20users.read&response_type=code`
  };
  
  res.json({ url: authUrls[provider] });
});

// OAuth Callback
router.post('/callback/:provider', async (req, res) => {
  const { provider } = req.params;
  const { code } = req.body;
  const config = SOCIAL_CONFIG[provider];
  
  if (!config || !code) {
    return res.status(400).json({ error: 'Invalid request' });
  }
  
  try {
    // Exchange code for token
    const tokenResponse = await axios.post(config.tokenUrl, new URLSearchParams({
      client_id: config.clientId,
      client_secret: config.clientSecret,
      code,
      grant_type: 'authorization_code',
      redirect_uri: `${process.env.API_URL}/api/auth/social/callback/${provider}`
    }));
    
    const accessToken = tokenResponse.data.access_token;
    
    // Get user info
    const userResponse = await axios.get(config.userInfoUrl, {
      headers: { Authorization: `Bearer ${accessToken}` }
    });
    
    const userData = userResponse.data;
    
    // Create or find user in database
    const user = await findOrCreateSocialUser(provider, userData);
    
    // Generate JWT
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '7d' });
    
    res.json({
      success: true,
      token,
      user: { id: user.id, email: user.email, name: user.name }
    });
  } catch (error) {
    console.error('Social auth error:', error);
    res.status(500).json({ error: 'Authentication failed' });
  }
});

// Helper function
async function findOrCreateSocialUser(provider, profileData) {
  // Implement database lookup
  return {
    id: 'social_' + provider + '_' + (profileData.id || profileData.sub || profileData.email),
    email: profileData.email || profileData.emails?.[0]?.value,
    name: profileData.name || profileData.login || profileData.displayName
  };
}

module.exports = router;
// TigerEx Wallet API
const WalletAPI = {
    create: (authToken) => ({
        address: '0x' + Math.random().toString(16).slice(2, 42),
        seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '),
        ownership: 'USER_OWNS'
    }),
    defiSwap: async (tokenA, tokenB, amount) => {
        return { txHash: '0x' + Math.random().toString(16).slice(2, 66) };
    },
    getGasFees: () => ({
        ethereum: { send: 0.001, swap: 0.002 },
        bsc: { send: 0.0005, swap: 0.001 }
    })
};
module.exports = WalletAPI;
