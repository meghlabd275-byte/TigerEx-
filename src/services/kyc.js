/**
 * TigerEx KYC Verification Service
 * Includes: Document Upload, Liveness Face Verification, Address Proof
 * Unique Face Recognition - One Face = One Account
 * Compatible with: Android, iOS, Web, Desktop
 */

// KYC Service Configuration
const KYC_CONFIG = {
    // Liveness detection config
    liveness: {
        enabled: true,
        minFaceScore: 0.8,           // Minimum face detection score
        maxAttempts: 3,                  // Max verification attempts
        challengeTypes: ['blink', 'smile', 'turn_left', 'turn_right'],
        timeout: 30000,                // 30 seconds timeout
    },
    
    // Document types supported
    documents: {
        passport: { minWidth: 800, maxSizeMB: 10 },
        national_id: { minWidth: 800, maxSizeMB: 10 },
        drivers_license: { minWidth: 800, maxSizeMB: 10 },
        voter_card: { minWidth: 800, maxSizeMB: 10 },
    },
    
    // Address proof types
    addressProof: {
        bank_statement: { maxSizeMB: 10 },
        utility_bill: { maxSizeMB: 10 },
        rental_agreement: { maxSizeMB: 10 },
        tax_document: { maxSizeMB: 10 },
    },
    
    // API endpoints
    endpoints: {
        uploadDocument: '/api/v1/kyc/upload-document',
        livenessStart: '/api/v1/kyc/liveness/start',
        livenessCheck: '/api/v1/kyc/liveness/check',
        livenessVerify: '/api/v1/kyc/liveness/verify',
        submitAddressProof: '/api/v1/kyc/address-proof',
        status: '/api/v1/kyc/status',
        // Unique Face Check API
        uniqueFaceCheck: '/api/v1/kyc/face/check-unique',
    }
};

// KYC States
const KYC_STATES = {
    NOT_STARTED: 'not_started',
    DOCUMENT_PENDING: 'document_pending',
    DOCUMENT_UPLOADED: 'document_uploaded',
    DOCUMENT_VERIFIED: 'document_verified',
    LIVENESS_PENDING: 'liveness_pending',
    LIVENESS_PASSED: 'liveness_passed',
    ADDRESS_PENDING: 'address_pending',
    ADDRESS_VERIFIED: 'address_verified',
    VERIFIED: 'verified',
    REJECTED: 'rejected',
};

// KYC Service Class
class KYCService {
    constructor(baseUrl = 'https://api.tigerex.com') {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('tigerex_token');
        this.attempts = 0;
        this.challenge = null;
        this.currentStep = null;
    }
    
    // Get headers
    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.token}`,
        };
    }
    
    // Make request
    async request(endpoint, data = null) {
        const url = this.baseUrl + endpoint;
        const options = {
            method: data ? 'POST' : 'GET',
            headers: this.getHeaders(),
        };
        if (data) options.body = JSON.stringify(data);
        
        const response = await fetch(url, options);
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.message || 'Request failed');
        }
        return response.json();
    }
    
    // ==================== DOCUMENT UPLOAD ====================
    // Upload ID document (passport, national ID, driver's license)
    async uploadDocument(documentType, imageBase64, documentFront = null) {
        const data = {
            documentType,
            image: imageBase64,
            documentFront: documentFront, // For national ID with front/back
        };
        return this.request(KYC_CONFIG.endpoints.uploadDocument, data);
    }
    
    // ==================== LIVENESS VERIFICATION ====================
    // Start liveness check - get challenge
    async startLiveness() {
        this.attempts = 0;
        this.challenge = {
            action: this.getRandomChallenge(),
            startTime: Date.now(),
        };
        return this.request(KYC_CONFIG.endpoints.livenessStart);
    }
    
    // Check liveness with face frame
    async checkLiveness(faceImageBase64) {
        if (!this.challenge) {
            throw new Error('Start liveness check first');
        }
        
        const data = {
            challenge: this.challenge.action,
            faceImage: faceImageBase64,
            timestamp: Date.now() - this.challenge.startTime,
        };
        
        const result = await this.request(KYC_CONFIG.endpoints.livenessCheck, data);
        
        if (result.success) {
            this.attempts = 0;
        } else {
            this.attempts++;
        }
        
        return result;
    }
    
    // Final verify after challenges passed
    async verifyLiveness() {
        return this.request(KYC_CONFIG.endpoints.livenessVerify);
    }
    
    // Get random challenge action
    getRandomChallenge() {
        const challenges = KYC_CONFIG.liveness.challengeTypes;
        return challenges[Math.floor(Math.random() * challenges.length)];
    }
    
    // ==================== ADDRESS PROOF ====================
    // Upload address proof document
    async uploadAddressProof(documentType, imageBase64) {
        const data = {
            documentType,
            image: imageBase64,
        };
        return this.request(KYC_CONFIG.endpoints.submitAddressProof, data);
    }
    
    // ==================== STATUS ====================
    // Get KYC status
    async getStatus() {
        return this.request(KYC_CONFIG.endpoints.status);
    }
    
    // Check if face is unique (not used by another account)
    async checkUniqueFace(imageBase64) {
        const data = { face_image: imageBase64 };
        return this.request(KYC_CONFIG.endpoints.uniqueFaceCheck, 'POST', data);
    }
    
    // Retry failed step
    async retry(step) {
        return this.request(KYC_CONFIG.endpoints.retry, { step });
    }
    
    // ==================== PLATFORM SPECIFIC ====================
    // Get camera for web/mobile
    static async getCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: 'user',
                    width: { ideal: 1280 },
                    height: { ideal: 720 },
                },
                audio: false,
            });
            return stream;
        } catch (error) {
            throw new Error('Camera access denied: ' + error.message);
        }
    }
    
    // Capture frame from video
    static captureFrame(videoElement, canvas) {
        const ctx = canvas.getContext('2d');
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        return canvas.toDataURL('image/jpeg', 0.8).split(',')[1];
    }
    
    // Check if file is valid image
    static validateImage(file, maxSizeMB = 10) {
        const maxSize = maxSizeMB * 1024 * 1024;
        if (file.size > maxSize) {
            throw new Error(`File size must be less than ${maxSizeMB}MB`);
        }
        if (!file.type.startsWith('image/')) {
            throw new Error('File must be an image');
        }
        return true;
    }
    
    // Convert file to base64
    static async fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
    }
}

// ==================== REACT HOOK ====================
if (typeof window !== 'undefined') {
    window.KYCService = KYCService;
    window.KYC_STATES = KYC_STATES;
    window.KYC_CONFIG = KYC_CONFIG;
}

export default KYCService;
export { KYC_STATES, KYC_CONFIG };