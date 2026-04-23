# 2FA Reset Flow Specification

## Project Overview

**Project Name:** TigerExchange Platform  
**Type:** Two-Factor Authentication (2FA) Reset Flow  
**Core Functionality:** Secure 2FA reset process requiring sequential identity verification before allowing 2FA reset.  
**Target Users:** Platform users who have lost access to their 2FA device and need to reset their authentication method.

---

## Functionality Specification

### Core Features

#### 1. Sequential Verification Flow

The 2FA reset process follows a strict sequential verification order:

1. **Step 1: Email Verification**
   - User receives a verification code via email
   - Code must be entered to proceed
   - Verification code expires after 15 minutes
   - Rate limit: 3 attempts per hour

2. **Step 2: Phone Verification**
   - After email verification, user receives SMS code to registered phone
   - Phone number must match account records
   - Code expires after 10 minutes
   - Rate limit: 3 attempts per hour

3. **Step 3: Liveness Verification**
   - After both email and phone verified, user must complete liveness check
   - Selfie verification with face match technology
   - Must pass anti-spoofing checks
   - Camera permission required

4. **Step 4: 2FA Reset Confirmation**
   - Only after all three verifications pass, 2FA is reset
   - User receives confirmation email
   - 2FA must be re-enabled on next login

### User Interactions and Flows

#### Verification State Machine:
```
IDLE → EMAIL_VERIFIED → PHONE_VERIFIED → LIVENESS_PASSED → COMPLETE
         ↓                     ↓                   ↓
      [FAILED]             [FAILED]            [FAILED]
         ↓                     ↓                   ↓
      IDLE (restart)      IDLE (restart)      IDLE (restart)
```

#### Frontend Flow:
1. User initiates 2FA reset request
2. Email verification form displayed
3. After email verified, phone verification form shown
4. After phone verified, liveness/camera verification shown
5. Final confirmation and 2FA reset

#### Backend API Endpoints:
- `POST /api/2fa/reset/initiate` - Start 2FA reset process
- `POST /api/2fa/reset/verify-email` - Verify email code
- `POST /api/2fa/reset/verify-phone` - Verify phone code
- `POST /api/2fa/reset/verify-liveness` - Submit liveness check
- `GET /api/2fa/reset/status` - Get current verification status

### Data Handling

#### Stored Data:
- Verification session with expiration (24 hours)
- Sequential verification states (boolean flags)
- Timestamp of each verification step
- IP address logged for security audit

#### Security Measures:
- Session tokens required for all verification steps
- All verification codes are cryptographically random
- Failed attempts trigger security alerts
- Audit log for all verification attempts

### Edge Cases

1. **Email not verified within time limit** → Session expires, must restart
2. **Phone number not registered** → Show error, do not proceed
3. **Liveness check fails multiple times** → Account flagged for manual review
4. **User tries to skip verification step** → Rejected, verification order enforced
5. **Session expires during verification** → All progress lost, restart required
6. **Invalid or expired verification code** → Show error, allow retry within limits

---

## Acceptance Criteria

### Verification Order Enforcement
- [ ] Email verification MUST be completed before phone verification is enabled
- [ ] Phone verification MUST be completed before liveness check is enabled
- [ ] Liveness check MUST pass before 2FA reset is allowed
- [ ] Users cannot skip any verification step

### Security Requirements
- [ ] All verification codes expire appropriately
- [ ] Rate limiting prevents brute force attacks
- [ ] Session tokens prevent replay attacks
- [ ] All attempts are logged for audit

### User Experience
- [ ] Clear progress indicator shows current step
- [ ] Error messages explain what went wrong
- [ ] User can restart from beginning if needed
- [ ] Confirmation displayed after successful reset

### API Behavior
- [ ] Each endpoint validates previous steps are complete
- [ ] Invalid session state returns appropriate error
- [ ] Successful verification advances state machine
- [ ] 2FA reset only occurs after all verifications pass

---

## Technical Implementation Notes

### Frontend Files to Update/Create:
- `src/pages/2fa-reset.html` or component
- Update existing auth pages to include 2FA reset flow

### Backend Files to Update/Create:
- `backend/auth-service/` - Add 2FA reset endpoints
- `backend/binance-verify-service/` - Integrate verification logic
- Database migrations for verification state tracking

### Third-party Services:
- Email service for verification codes
- SMS service for phone verification
- Liveness/face match API integration