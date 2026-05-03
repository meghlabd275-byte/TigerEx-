/**
 * Passport Configuration for All Social Providers
 */

const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const FacebookStrategy = require('passport-facebook').Strategy;
const TwitterStrategy = require('passport-twitter').Strategy;
const AppleStrategy = require('passport-apple').Strategy;
const GitHubStrategy = require('passport-github').Strategy;
const DiscordStrategy = require('passport-discord').Strategy;
const LinkedInStrategy = require('passport-linkedin').Strategy;
const User = require('../models/User');
const AuditLog = require('../models/AuditLog');

// Helper to handle social login
const handleSocialLogin = async (accessToken, refreshToken, profile, provider, done) => {
  try {
    const providerId = profile.id;
    const email = profile.emails?.[0]?.value || profile.email;
    const name = profile.displayName || profile.name?.givenName || '';
    const avatar = profile.photos?.[0]?.value || profile._json?.avatar_url || '';
    
    // Find existing user by social ID
    let user = await User.findBySocialId(provider, providerId);
    
    if (user) {
      // Update last used
      const account = user.socialAccounts.find(a => a.provider === provider);
      if (account) {
        account.lastUsed = new Date();
        account.accessToken = accessToken;
        if (refreshToken) account.refreshToken = refreshToken;
        await user.save();
      }
      
      await AuditLog.log({
        userId: user._id,
        action: 'social_login',
        category: 'auth',
        details: { provider, providerId },
        status: 'success',
      });
      
      return done(null, user);
    }
    
    // Check if user exists with same email
    if (email) {
      user = await User.findByEmail(email);
      if (user) {
        // Link social account to existing user
        await user.addSocialAccount({
          provider,
          providerId,
          email,
          name,
          avatar,
          accessToken,
          refreshToken,
          isVerified: !!profile.emails?.[0]?.verified,
        });
        
        await AuditLog.log({
          userId: user._id,
          action: 'social_link',
          category: 'auth',
          details: { provider, providerId },
          status: 'success',
        });
        
        return done(null, user);
      }
    }
    
    // Create new user
    const username = email ? email.split('@')[0] + Date.now().toString().slice(-4) : `${provider}_${providerId.slice(0, 8)}`;
    
    user = new User({
      email,
      username,
      profile: {
        displayName: name,
        avatar,
        firstName: profile.name?.givenName || '',
        lastName: profile.name?.familyName || '',
      },
      socialAccounts: [{
        provider,
        providerId,
        email,
        name,
        avatar,
        accessToken,
        refreshToken,
        isPrimary: true,
        isVerified: !!profile.emails?.[0]?.verified,
        linkedAt: new Date(),
        lastUsed: new Date(),
      }],
      emailVerified: !!profile.emails?.[0]?.verified,
      status: 'active',
      role: 'user',
    });
    
    await user.save();
    
    await AuditLog.log({
      userId: user._id,
      action: 'register',
      category: 'auth',
      details: { provider, providerId, email },
      status: 'success',
    });
    
    done(null, user);
  } catch (error) {
    console.error(`Error in ${provider} login:`, error);
    done(error, null);
  }
};

// Google Strategy
if (process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET) {
  passport.use(new GoogleStrategy({
    clientID: process.env.GOOGLE_CLIENT_ID,
    clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    callbackURL: process.env.GOOGLE_CALLBACK_URL || '/api/auth/social/google/callback',
    scope: ['profile', 'email'],
    passReqToCallback: true,
  }, (req, accessToken, refreshToken, profile, done) => {
    handleSocialLogin(accessToken, refreshToken, profile, 'google', done);
  }));
}

// Facebook Strategy
if (process.env.FACEBOOK_APP_ID && process.env.FACEBOOK_APP_SECRET) {
  passport.use(new FacebookStrategy({
    clientID: process.env.FACEBOOK_APP_ID,
    clientSecret: process.env.FACEBOOK_APP_SECRET,
    callbackURL: process.env.FACEBOOK_CALLBACK_URL || '/api/auth/social/facebook/callback',
    profileFields: ['id', 'displayName', 'name', 'emails', 'photos'],
    passReqToCallback: true,
  }, (req, accessToken, refreshToken, profile, done) => {
    handleSocialLogin(accessToken, refreshToken, profile, 'facebook', done);
  }));
}

// Twitter Strategy
if (process.env.TWITTER_CONSUMER_KEY && process.env.TWITTER_CONSUMER_SECRET) {
  passport.use(new TwitterStrategy({
    consumerKey: process.env.TWITTER_CONSUMER_KEY,
    consumerSecret: process.env.TWITTER_CONSUMER_SECRET,
    callbackURL: process.env.TWITTER_CALLBACK_URL || '/api/auth/social/twitter/callback',
    includeEmail: true,
    passReqToCallback: true,
  }, (req, token, tokenSecret, profile, done) => {
    handleSocialLogin(token, tokenSecret, profile, 'twitter', done);
  }));
}

// GitHub Strategy
if (process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET) {
  passport.use(new GitHubStrategy({
    clientID: process.env.GITHUB_CLIENT_ID,
    clientSecret: process.env.GITHUB_CLIENT_SECRET,
    callbackURL: process.env.GITHUB_CALLBACK_URL || '/api/auth/social/github/callback',
    scope: ['user:email'],
    passReqToCallback: true,
  }, (req, accessToken, refreshToken, profile, done) => {
    handleSocialLogin(accessToken, refreshToken, profile, 'github', done);
  }));
}

// Discord Strategy
if (process.env.DISCORD_CLIENT_ID && process.env.DISCORD_CLIENT_SECRET) {
  passport.use(new DiscordStrategy({
    clientID: process.env.DISCORD_CLIENT_ID,
    clientSecret: process.env.DISCORD_CLIENT_SECRET,
    callbackURL: process.env.DISCORD_CALLBACK_URL || '/api/auth/social/discord/callback',
    scope: ['identify', 'email'],
    passReqToCallback: true,
  }, (req, accessToken, refreshToken, profile, done) => {
    handleSocialLogin(accessToken, refreshToken, profile, 'discord', done);
  }));
}

// LinkedIn Strategy
if (process.env.LINKEDIN_CLIENT_ID && process.env.LINKEDIN_CLIENT_SECRET) {
  passport.use(new LinkedInStrategy({
    consumerKey: process.env.LINKEDIN_CLIENT_ID,
    consumerSecret: process.env.LINKEDIN_CLIENT_SECRET,
    callbackURL: process.env.LINKEDIN_CALLBACK_URL || '/api/auth/social/linkedin/callback',
    profileFields: ['id', 'first-name', 'last-name', 'email-address', 'picture-url'],
    passReqToCallback: true,
  }, (req, token, tokenSecret, profile, done) => {
    handleSocialLogin(token, tokenSecret, profile, 'linkedin', done);
  }));
}

// Apple Strategy
if (process.env.APPLE_CLIENT_ID && process.env.APPLE_TEAM_ID && process.env.APPLE_KEY_ID) {
  passport.use(new AppleStrategy({
    clientID: process.env.APPLE_CLIENT_ID,
    teamID: process.env.APPLE_TEAM_ID,
    keyID: process.env.APPLE_KEY_ID,
    privateKeyLocation: process.env.APPLE_PRIVATE_KEY_PATH,
    callbackURL: process.env.APPLE_CALLBACK_URL || '/api/auth/social/apple/callback',
    passReqToCallback: true,
  }, (req, accessToken, refreshToken, idToken, profile, done) => {
    handleSocialLogin(accessToken, refreshToken, profile, 'apple', done);
  }));
}

module.exports = passport;export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
