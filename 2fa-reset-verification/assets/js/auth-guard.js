// TigerEx Auth Guard - Dynamic 2FA Verification
// Connects to backend for real verification

const API_BASE = 'https://api.tigerex.com';

// Send email verification code
async function sendEmailCode(email) {
  const res = await fetch(`${API_BASE}/2fa/email/send`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email})
  });
  return res.json();
}

// Verify email code
async function verifyEmailCode(email, code) {
  const res = await fetch(`${API_BASE}/2fa/email/verify`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email, code})
  });
  return res.json();
}

// Send phone verification
async function sendPhoneCode(phone) {
  const res = await fetch(`${API_BASE}/2fa/phone/send`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({phone})
  });
  return res.json();
}

// Verify phone code
async function verifyPhoneCode(phone, code) {
  const res = await fetch(`${API_BASE}/2fa/phone/verify`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({phone, code})
  });
  return res.json();
}

// Face verification with AI
async function verifyFace(imageData) {
  const res = await fetch(`${API_BASE}/2fa/face/verify`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({image: imageData})
  });
  return res.json();
}

// Complete 2FA reset
async function completeReset(userId, methods) {
  const res = await fetch(`${API_BASE}/2fa/reset/complete`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({user_id: userId, methods})
  });
  return res.json();
}

// Database logging
console.log('TigerEx Auth Guard loaded - connected to backend');
