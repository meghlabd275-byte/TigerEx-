/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

package models

import (
	"database/sql/driver"
	"encoding/json"
	"time"

	"github.com/google/uuid"
)

type UserRole string

const (
	RoleUser              UserRole = "user"
	RoleVIP               UserRole = "vip"
	RoleInstitutional     UserRole = "institutional"
	RoleAffiliate         UserRole = "affiliate"
	RoleRegionalPartner   UserRole = "regional_partner"
	RoleSuperAdmin        UserRole = "super_admin"
	RoleKYCAdmin          UserRole = "kyc_admin"
	RoleCustomerSupport   UserRole = "customer_support"
	RoleP2PManager        UserRole = "p2p_manager"
	RoleAffiliateManager  UserRole = "affiliate_manager"
	RoleBDM               UserRole = "bdm"
	RoleTechnicalTeam     UserRole = "technical_team"
	RoleListingManager    UserRole = "listing_manager"
)

type KYCStatus string

const (
	KYCPending  KYCStatus = "pending"
	KYCApproved KYCStatus = "approved"
	KYCRejected KYCStatus = "rejected"
	KYCRequired KYCStatus = "required"
)

type UserStatus string

const (
	UserActive    UserStatus = "active"
	UserSuspended UserStatus = "suspended"
	UserBanned    UserStatus = "banned"
	UserPending   UserStatus = "pending"
)

type SecuritySettings struct {
	TwoFactorEnabled    bool   `json:"two_factor_enabled"`
	SMSEnabled          bool   `json:"sms_enabled"`
	EmailEnabled        bool   `json:"email_enabled"`
	BiometricEnabled    bool   `json:"biometric_enabled"`
	IPWhitelistEnabled  bool   `json:"ip_whitelist_enabled"`
	IPWhitelist         []string `json:"ip_whitelist"`
	SessionTimeout      int    `json:"session_timeout"`
	LoginNotifications  bool   `json:"login_notifications"`
	WithdrawWhitelist   []string `json:"withdraw_whitelist"`
}

func (s SecuritySettings) Value() (driver.Value, error) {
	return json.Marshal(s)
}

func (s *SecuritySettings) Scan(value interface{}) error {
	if value == nil {
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return nil
	}
	return json.Unmarshal(bytes, s)
}

type TradingPreferences struct {
	DefaultLeverage     float64 `json:"default_leverage"`
	RiskLevel          string  `json:"risk_level"`
	AutoStopLoss       bool    `json:"auto_stop_loss"`
	AutoTakeProfit     bool    `json:"auto_take_profit"`
	TradingNotifications bool   `json:"trading_notifications"`
	PreferredPairs     []string `json:"preferred_pairs"`
	TradingMode        string  `json:"trading_mode"`
}

func (t TradingPreferences) Value() (driver.Value, error) {
	return json.Marshal(t)
}

func (t *TradingPreferences) Scan(value interface{}) error {
	if value == nil {
		return nil
	}
	bytes, ok := value.([]byte)
	if !ok {
		return nil
	}
	return json.Unmarshal(bytes, t)
}

type User struct {
	ID                  uuid.UUID           `json:"id" db:"id"`
	Email               string              `json:"email" db:"email"`
	Username            string              `json:"username" db:"username"`
	PasswordHash        string              `json:"-" db:"password_hash"`
	FirstName           string              `json:"first_name" db:"first_name"`
	LastName            string              `json:"last_name" db:"last_name"`
	PhoneNumber         string              `json:"phone_number" db:"phone_number"`
	CountryCode         string              `json:"country_code" db:"country_code"`
	DateOfBirth         *time.Time          `json:"date_of_birth" db:"date_of_birth"`
	Role                UserRole            `json:"role" db:"role"`
	Status              UserStatus          `json:"status" db:"status"`
	KYCStatus           KYCStatus           `json:"kyc_status" db:"kyc_status"`
	KYCLevel            int                 `json:"kyc_level" db:"kyc_level"`
	EmailVerified       bool                `json:"email_verified" db:"email_verified"`
	PhoneVerified       bool                `json:"phone_verified" db:"phone_verified"`
	TwoFactorSecret     string              `json:"-" db:"two_factor_secret"`
	TwoFactorEnabled    bool                `json:"two_factor_enabled" db:"two_factor_enabled"`
	SecuritySettings    SecuritySettings    `json:"security_settings" db:"security_settings"`
	TradingPreferences  TradingPreferences  `json:"trading_preferences" db:"trading_preferences"`
	ReferralCode        string              `json:"referral_code" db:"referral_code"`
	ReferredBy          *uuid.UUID          `json:"referred_by" db:"referred_by"`
	VIPLevel            int                 `json:"vip_level" db:"vip_level"`
	TradingVolume30D    float64             `json:"trading_volume_30d" db:"trading_volume_30d"`
	LastLoginAt         *time.Time          `json:"last_login_at" db:"last_login_at"`
	LastLoginIP         string              `json:"last_login_ip" db:"last_login_ip"`
	FailedLoginAttempts int                 `json:"failed_login_attempts" db:"failed_login_attempts"`
	LockedUntil         *time.Time          `json:"locked_until" db:"locked_until"`
	CreatedAt           time.Time           `json:"created_at" db:"created_at"`
	UpdatedAt           time.Time           `json:"updated_at" db:"updated_at"`
}

type LoginRequest struct {
	Email      string `json:"email" binding:"required,email"`
	Password   string `json:"password" binding:"required,min=8"`
	TwoFactor  string `json:"two_factor"`
	RememberMe bool   `json:"remember_me"`
	IPAddress  string `json:"-"`
	UserAgent  string `json:"-"`
}

type RegisterRequest struct {
	Email           string `json:"email" binding:"required,email"`
	Username        string `json:"username" binding:"required,min=3,max=30"`
	Password        string `json:"password" binding:"required,min=8"`
	ConfirmPassword string `json:"confirm_password" binding:"required"`
	FirstName       string `json:"first_name" binding:"required"`
	LastName        string `json:"last_name" binding:"required"`
	PhoneNumber     string `json:"phone_number"`
	CountryCode     string `json:"country_code" binding:"required"`
	ReferralCode    string `json:"referral_code"`
	AcceptTerms     bool   `json:"accept_terms" binding:"required"`
	IPAddress       string `json:"-"`
	UserAgent       string `json:"-"`
}

type AuthResponse struct {
	User         *User  `json:"user"`
	AccessToken  string `json:"access_token"`
	RefreshToken string `json:"refresh_token"`
	ExpiresIn    int64  `json:"expires_in"`
}

type UserSession struct {
	ID           uuid.UUID `json:"id" db:"id"`
	UserID       uuid.UUID `json:"user_id" db:"user_id"`
	AccessToken  string    `json:"access_token" db:"access_token"`
	RefreshToken string    `json:"refresh_token" db:"refresh_token"`
	IPAddress    string    `json:"ip_address" db:"ip_address"`
	UserAgent    string    `json:"user_agent" db:"user_agent"`
	IsActive     bool      `json:"is_active" db:"is_active"`
	ExpiresAt    time.Time `json:"expires_at" db:"expires_at"`
	CreatedAt    time.Time `json:"created_at" db:"created_at"`
	UpdatedAt    time.Time `json:"updated_at" db:"updated_at"`
}

type UserDevice struct {
	ID           uuid.UUID `json:"id" db:"id"`
	UserID       uuid.UUID `json:"user_id" db:"user_id"`
	DeviceName   string    `json:"device_name" db:"device_name"`
	DeviceType   string    `json:"device_type" db:"device_type"`
	DeviceID     string    `json:"device_id" db:"device_id"`
	IPAddress    string    `json:"ip_address" db:"ip_address"`
	UserAgent    string    `json:"user_agent" db:"user_agent"`
	IsTrusted    bool      `json:"is_trusted" db:"is_trusted"`
	LastUsedAt   time.Time `json:"last_used_at" db:"last_used_at"`
	CreatedAt    time.Time `json:"created_at" db:"created_at"`
}

type LoginHistory struct {
	ID        uuid.UUID `json:"id" db:"id"`
	UserID    uuid.UUID `json:"user_id" db:"user_id"`
	IPAddress string    `json:"ip_address" db:"ip_address"`
	UserAgent string    `json:"user_agent" db:"user_agent"`
	Success   bool      `json:"success" db:"success"`
	Reason    string    `json:"reason" db:"reason"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}