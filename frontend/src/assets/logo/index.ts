export const LOGO_PATH = '/assets/logo/tigerex-logo.png';
export const FAVICON_PATH = '/assets/logo/tigerex-logo.png';

// Logo sizes for different platforms
export const LOGO_SIZES = {
  favicon: 'favicon.png',
  appleTouch: 'apple-touch-icon.png',
  android192: 'android-chrome-192x192.png',
  android512: 'android-chrome-512x512.png',
};

export const APP_NAME = 'TigerEx';
export const APP_TAGLINE = 'Professional Crypto Trading Platform';export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
