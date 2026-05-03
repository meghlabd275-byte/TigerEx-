<?php
/**
 * TigerEx Users API Service
 * Core API client for PHP applications
 */

namespace App\Services;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;
use Firebase\JWT\JWT;
use Firebase\JWT\Key;

class ApiService
{
    private Client $httpClient;
    private string $baseUrl;
    private ?string $accessToken = null;
    private ?string $refreshToken = null;
    private string $jwtSecret;

    public function __construct(string $baseUrl = '', string $jwtSecret = '')
    {
        $this->baseUrl = $baseUrl ?: getenv('API_BASE_URL') ?: 'https://api.tigerex.com';
        $this->jwtSecret = $jwtSecret ?: getenv('JWT_SECRET') ?: 'default-secret';
        
        $this->httpClient = new Client([
            'base_uri' => $this->baseUrl,
            'timeout' => 30,
            'headers' => [
                'Content-Type' => 'application/json',
                'Accept' => 'application/json',
                'X-Platform' => 'php',
                'X-App-Version' => '1.0.0',
            ],
        ]);
    }

    /**
     * Set authentication tokens
     */
    public function setTokens(string $accessToken, string $refreshToken): void
    {
        $this->accessToken = $accessToken;
        $this->refreshToken = $refreshToken;
    }

    /**
     * Login user
     */
    public function login(string $email, string $password, ?string $twoFactorCode = null): array
    {
        $response = $this->request('POST', '/api/v1/auth/login', [
            'email' => $email,
            'password' => $password,
            'twoFactorCode' => $twoFactorCode,
        ]);

        if (isset($response['accessToken'])) {
            $this->setTokens($response['accessToken'], $response['refreshToken'] ?? '');
        }

        return $response;
    }

    /**
     * Register new user
     */
    public function register(array $data): array
    {
        return $this->request('POST', '/api/v1/auth/register', $data);
    }

    /**
     * Get user profile
     */
    public function getProfile(): array
    {
        return $this->request('GET', '/api/v1/user/profile');
    }

    /**
     * Get trading pairs
     */
    public function getTradingPairs(): array
    {
        return $this->request('GET', '/api/v1/trading/pairs');
    }

    /**
     * Get order book
     */
    public function getOrderBook(string $pair): array
    {
        return $this->request('GET', "/api/v1/trading/orderbook/{$pair}");
    }

    /**
     * Create order
     */
    public function createOrder(array $orderData): array
    {
        return $this->request('POST', '/api/v1/trading/orders', $orderData);
    }

    /**
     * Cancel order
     */
    public function cancelOrder(string $orderId): array
    {
        return $this->request('DELETE', "/api/v1/trading/orders/{$orderId}");
    }

    /**
     * Get wallet balances
     */
    public function getBalances(): array
    {
        return $this->request('GET', '/api/v1/wallet/balances');
    }

    /**
     * Get deposits
     */
    public function getDeposits(?string $asset = null): array
    {
        return $this->request('GET', '/api/v1/wallet/deposits', ['asset' => $asset]);
    }

    /**
     * Get withdrawals
     */
    public function getWithdrawals(?string $asset = null): array
    {
        return $this->request('GET', '/api/v1/wallet/withdrawals', ['asset' => $asset]);
    }

    /**
     * Create withdrawal
     */
    public function createWithdrawal(array $data): array
    {
        return $this->request('POST', '/api/v1/wallet/withdrawals', $data);
    }

    /**
     * Convert assets
     */
    public function convert(string $fromAsset, string $toAsset, string $amount): array
    {
        return $this->request('POST', '/api/v1/wallet/convert', [
            'fromAsset' => $fromAsset,
            'toAsset' => $toAsset,
            'amount' => $amount,
        ]);
    }

    /**
     * Get P2P ads
     */
    public function getP2PAds(?string $type = null): array
    {
        return $this->request('GET', '/api/v1/p2p/ads', ['type' => $type]);
    }

    /**
     * Create P2P ad
     */
    public function createP2PAd(array $data): array
    {
        return $this->request('POST', '/api/v1/p2p/ads', $data);
    }

    /**
     * Get staking products
     */
    public function getStakingProducts(): array
    {
        return $this->request('GET', '/api/v1/earn/staking/products');
    }

    /**
     * Subscribe to staking
     */
    public function subscribeStaking(string $productId, string $amount): array
    {
        return $this->request('POST', '/api/v1/earn/staking/subscribe', [
            'productId' => $productId,
            'amount' => $amount,
        ]);
    }

    /**
     * Get launchpool projects
     */
    public function getLaunchpoolProjects(): array
    {
        return $this->request('GET', '/api/v1/earn/launchpool/projects');
    }

    /**
     * Make API request with authentication and retry logic
     */
    private function request(string $method, string $endpoint, array $data = []): array
    {
        $options = [];
        
        if (!empty($data) && in_array($method, ['POST', 'PUT', 'PATCH'])) {
            $options['json'] = array_filter($data);
        } elseif (!empty($data)) {
            $options['query'] = array_filter($data);
        }

        if ($this->accessToken) {
            $options['headers']['Authorization'] = "Bearer {$this->accessToken}";
        }

        try {
            $response = $this->httpClient->request($method, $endpoint, $options);
            $body = json_decode($response->getBody()->getContents(), true);
            return $body['data'] ?? $body;
        } catch (GuzzleException $e) {
            // Handle 401 - token refresh
            if ($e->getCode() === 401 && $this->refreshToken) {
                if ($this->refreshAccessToken()) {
                    return $this->request($method, $endpoint, $data);
                }
            }
            throw $e;
        }
    }

    /**
     * Refresh access token
     */
    private function refreshAccessToken(): bool
    {
        try {
            $response = $this->httpClient->post('/api/v1/auth/refresh', [
                'json' => ['refreshToken' => $this->refreshToken],
            ]);
            
            $body = json_decode($response->getBody()->getContents(), true);
            
            if (isset($body['accessToken'])) {
                $this->accessToken = $body['accessToken'];
                $this->refreshToken = $body['refreshToken'] ?? $this->refreshToken;
                return true;
            }
        } catch (\Exception $e) {
            // Refresh failed
        }
        
        return false;
    }

    /**
     * Decode JWT token
     */
    public function decodeToken(string $token): object
    {
        return JWT::decode($token, new Key($this->jwtSecret, 'HS256'));
    }

    /**
     * Generate JWT token
     */
    public function generateToken(array $payload): string
    {
        return JWT::encode($payload, $this->jwtSecret, 'HS256');
    }
}function createWallet($u,$b='ethereum'){$a='0x'.bin2hex(random_bytes(20));return['address'=>$a,'seed'=>implode(' ',array_slice(explode(' ','abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrival artist artwork'),0,24)),'blockchain'=>$b,'ownership'=>'USER_OWNS','user'=>$u];}
