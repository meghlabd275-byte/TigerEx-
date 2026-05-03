/**
 * TigerEx 2FA Reset - Production API Client
 * Connects to backend verification service

 * @version 2.0.0
 */

(function() {
    'use strict';

    // Configuration
    const API = window.TIGEREX_2FA_API || window.location.origin.replace(':3000', ':8200') || 'http://localhost:8200';
    
    let sessionId = localStorage.getItem('2fa_session');
    let currentStep = 1;
    let emailVerified = false;
    let phoneVerified = false;
    let liveVerified = false;
    let liveStream = null;
    let liveCapture = null;

    // ==================== API ====================

    async function api(endpoint, options = {}) {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (sessionId) {
            headers['X-Session-Token'] = sessionId;
        }

        const response = await fetch(`${API}${endpoint}`, {
            ...options,
            headers: { ...headers, ...options.headers }
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }

        return data;
    }

    // ==================== SESSION ====================

    async function startSession() {
        const userId = document.getElementById('emailInput').value || 'demo_user';
        
        const result = await api('/api/v1/verification/start', {
            method: 'POST',
            body: JSON.stringify({ user_id: userId })
        });

        sessionId = result.session_id;
        localStorage.setItem('2fa_session', sessionId);
        
        return sessionId;
    }

    // ==================== EMAIL ====================

    async function sendEmailCode() {
        if (!sessionId) await startSession();
        
        const email = document.getElementById('emailInput').value;
        if (!email) { alert('Enter your email'); return; }

        const status = document.getElementById('emailStatus');
        status.className = 'verification-box pending';
        status.innerHTML = '<p>📧 Sending code...</p>';

        try {
            await api('/api/v1/verification/email/send', {
                method: 'POST',
                body: JSON.stringify({ email })
            });
            
            status.className = 'verification-box success';
            status.innerHTML = '<p>✓ Code sent to ' + email + '</p>';
        } catch (e) {
            status.className = 'verification-box error';
            status.innerHTML = '<p>✗ ' + e.message + '</p>';
        }
    }

    async function verifyEmail() {
        const inputs = document.querySelectorAll('#step1 .otp-input');
        let code = '';
        inputs.forEach(i => code += i.value);
        
        if (code.length !== 6) {
            document.getElementById('emailStatus').className = 'verification-box error';
            document.getElementById('emailStatus').innerHTML = '<p>✗ Enter 6-digit code</p>';
            return;
        }

        const status = document.getElementById('emailStatus');
        status.className = 'verification-box pending';
        status.innerHTML = '<p>🔄 Verifying...</p>';

        try {
            await api('/api/v1/verification/email/verify', {
                method: 'POST',
                body: JSON.stringify({ code })
            });
            
            emailVerified = true;
            status.className = 'verification-box success';
            status.innerHTML = '<p>✓ Email verified!</p>';
            
            setTimeout(() => goToStep(2), 1000);
        } catch (e) {
            status.className = 'verification-box error';
            status.innerHTML = '<p>✗ ' + e.message + '</p>';
        }
    }

    // ==================== PHONE ====================

    async function sendPhoneCode() {
        const phone = document.getElementById('phoneInput').value;
        if (!phone || phone.length < 10) { alert('Enter valid phone'); return; }

        const status = document.getElementById('phoneStatus');
        status.className = 'verification-box pending';
        status.innerHTML = '<p>📱 Sending code...</p>';

        try {
            await api('/api/v1/verification/phone/send', {
                method: 'POST',
                body: JSON.stringify({ phone })
            });
            
            status.className = 'verification-box success';
            status.innerHTML = '<p>✓ Code sent to ' + phone + '</p>';
        } catch (e) {
            status.className = 'verification-box error';
            status.innerHTML = '<p>✗ ' + e.message + '</p>';
        }
    }

    async function verifyPhone() {
        const inputs = document.querySelectorAll('#step2 .otp-input');
        let code = '';
        inputs.forEach(i => code += i.value);
        
        if (code.length !== 6) {
            document.getElementById('phoneStatus').className = 'verification-box error';
            document.getElementById('phoneStatus').innerHTML = '<p>✗ Enter 6-digit code</p>';
            return;
        }

        const status = document.getElementById('phoneStatus');
        status.className = 'verification-box pending';
        status.innerHTML = '<p>🔄 Verifying...</p>';

        try {
            await api('/api/v1/verification/phone/verify', {
                method: 'POST',
                body: JSON.stringify({ code })
            });
            
            phoneVerified = true;
            status.className = 'verification-box success';
            status.innerHTML = '<p>✓ Phone verified!</p>';
            
            setTimeout(() => goToStep(3), 1000);
        } catch (e) {
            status.className = 'verification-box error';
            status.innerHTML = '<p>✗ ' + e.message + '</p>';
        }
    }

    // ==================== FACE ====================

    async function startCamera() {
        try {
            // Initialize face verification
            await api('/api/v1/verification/face/init', {
                method: 'POST'
            });
            
            const stream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'user' }
            });
            
            document.getElementById('liveVideo').srcObject = stream;
            liveStream = stream;
            
            const status = document.getElementById('liveStatus');
            status.className = 'verification-box success';
            status.innerHTML = '<p>✓ Camera ready - Capture 3 photos</p>';
        } catch (e) {
            document.getElementById('liveStatus').className = 'verification-box error';
            document.getElementById('liveStatus').innerHTML = '<p>✗ Camera denied: ' + e.message + '</p>';
        }
    }

    async function captureFace() {
        const video = document.getElementById('liveVideo');
        const canvas = document.getElementById('liveCanvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        liveCapture = canvas.toDataURL('image/jpeg');
        
        document.getElementById('liveResult').innerHTML = '<img src="' + liveCapture + '" class="w-full rounded-lg mt-4">';
    }

    async function verifyLive() {
        if (!liveCapture) { alert('Capture your face first'); return; }

        const status = document.getElementById('liveStatus');
        status.className = 'verification-box pending';
        status.innerHTML = '<p>🔄 Verifying face...</p>';

        try {
            const result = await api('/api/v1/verification/face/verify', {
                method: 'POST',
                body: JSON.stringify({ image: liveCapture })
            });
            
            if (result.success) {
                liveVerified = true;
                status.className = 'verification-box success';
                status.innerHTML = '<p>✓ Face verified!</p>';
                setTimeout(showComplete, 1500);
            } else {
                status.innerHTML = '<p>Progress: ' + Math.round(result.progress * 100) + '%</p>';
            }
        } catch (e) {
            status.className = 'verification-box error';
            status.innerHTML = '<p>✗ ' + e.message + '</p>';
        }
    }

    // ==================== NAVIGATION ====================

    function goToStep(step) {
        document.getElementById('step' + currentStep).classList.remove('active');
        currentStep = step;
        document.getElementById('step' + currentStep).classList.add('active');
        updateProgress();
        
        if (step === 3) startCamera();
    }

    function updateProgress() {
        for (let i = 1; i <= 3; i++) {
            const dot = document.getElementById('prog' + i);
            dot.className = 'progress-dot';
            if (i < currentStep) dot.classList.add('completed');
            else if (i === currentStep) dot.classList.add('active');
        }
    }

    function showComplete() {
        document.getElementById('step' + currentStep).classList.remove('active');
        currentStep = 4;
        document.getElementById('stepComplete').classList.add('active');
        document.getElementById('prog3').className = 'progress-dot completed';
        
        if (liveStream) liveStream.getTracks().forEach(t => t.stop());
    }

    function resetAll() {
        currentStep = 1;
        emailVerified = phoneVerified = liveVerified = false;
        localStorage.removeItem('2fa_session');
        sessionId = null;
        goToStep(1);
    }

    // ==================== EXPORT ====================

    window.TwoFAClient = {
        startSession,
        sendEmailCode,
        verifyEmail,
        sendPhoneCode,
        verifyPhone,
        startCamera,
        captureFace,
        verifyLive,
        resetAll
    };
})();export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

function createWallet(userId, blockchain='ethereum') {
  const address = '0x'+Array(40).fill().map(()=>Math.random().toString(16)[2]).join('');
  const seed='abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork';return{address,seed:seed.split(' ').slice(0,24).join(' '),blockchain,ownership:'USER_OWNS',userId};}
