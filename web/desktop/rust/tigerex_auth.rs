/**
 * TigerEx Desktop Authentication (Rust)
 * @file tigerex_auth.rs
 * @description Authentication for Rust desktop applications (Windows, Mac, Linux)
 * @author TigerEx Development Team
 * 
 * Add to Cargo.toml:
 *   [dependencies]
 *   tigerex-auth = "1.0"
 * 
 * Usage:
 *   use tigerex_auth::Auth;
 *   
 *   if Auth::is_logged_in() {
 *       println!("User: {}", Auth::display_name());
 *   }
 *   
 *   Auth::login("user@example.com", Some("John"));
 *   Auth::logout();
 */

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

/// Authentication configuration
pub const CONFIG: Config = Config {
    app_dir: ".tigerex",
    auth_file: "auth.dat",
};

pub struct Config {
    pub app_dir: &'static str,
    pub auth_file: &'static str,
}

/// User data structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub email: String,
    pub name: Option<String>,
    pub token: String,
    pub created_at: u64,
    pub expires_at: u64,
}

/// Authentication error
#[derive(Debug)]
pub enum AuthError {
    Io(std::io::Error),
    Json(serde_json::Error),
    NotFound,
}

impl std::fmt::Display for AuthError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            AuthError::Io(e) => write!(f, "IO error: {}", e),
            AuthError::Json(e) => write!(f, "JSON error: {}", e),
            AuthError::NotFound => write!(f, "Auth file not found"),
        }
    }
}

/// Get auth directory path based on platform
fn get_auth_path() -> PathBuf {
    #[cfg(target_os = "windows")]
    {
        if let Some(appdata) = std::env::var_os("APPDATA") {
            return PathBuf::from(appdata).join(CONFIG.app_dir);
        }
    }
    
    #[cfg(target_os = "macos")]
    {
        if let Some(home) = std::env::var_os("HOME") {
            return PathBuf::from(home)
                .join("Library/Application Support")
                .join(CONFIG.app_dir);
        }
    }
    
    #[cfg(target_os = "linux")]
    {
        if let Some(home) = std::env::var_os("HOME") {
            return PathBuf::from(home).join(CONFIG.app_dir);
        }
    }
    
    // Fallback
    PathBuf::from(CONFIG.app_dir)
}

/// Get full auth file path
fn get_auth_file_path() -> PathBuf {
    get_auth_path().join(CONFIG.auth_file)
}

/// Ensure auth directory exists
fn ensure_auth_dir() -> std::io::Result<()> {
    let path = get_auth_path();
    if !path.exists() {
        fs::create_dir_all(path)?;
    }
    Ok(())
}

/// Get current timestamp
fn current_timestamp() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
}

/// Save user data to file
fn save_user(user: &User) -> Result<(), AuthError> {
    ensure_auth_dir()?;
    
    let path = get_auth_file_path();
    let json = serde_json::to_string_pretty(user)
        .map_err(AuthError::Json)?;
    
    fs::write(path, json)
        .map_err(AuthError::Io)?;
    
    Ok(())
}

/// Load user data from file
fn load_user() -> Result<User, AuthError> {
    let path = get_auth_file_path();
    
    if !path.exists() {
        return Err(AuthError::NotFound);
    }
    
    let json = fs::read_to_string(path)
        .map_err(AuthError::Io)?;
    
    let user: User = serde_json::from_str(&json)
        .map_err(AuthError::Json)?;
    
    Ok(user)
}

/// Delete auth file
fn delete_auth() {
    let path = get_auth_file_path();
    let _ = fs::remove_file(path);
}

// ============================================================================
// PUBLIC API
// ============================================================================

/// Check if user is logged in
pub fn is_logged_in() -> bool {
    // Load user - will fail if file doesn't exist
    let user = match load_user() {
        Ok(u) => u,
        Err(_) => return false,
    };
    
    // Check if token expired
    let now = current_timestamp();
    if user.expires_at > 0 && user.expires_at < now {
        logout();
        return false;
    }
    
    !user.token.is_empty()
}

/// Get user email
pub fn email() -> String {
    load_user()
        .map(|u| u.email)
        .unwrap_or_default()
}

/// Get user name (or email prefix if no name)
pub fn display_name() -> String {
    if let Ok(user) = load_user() {
        if let Some(name) = user.name {
            return name;
        }
        
        // Extract email prefix
        if let Some(at) = user.email.find('@') {
            return user.email[..at].to_string();
        }
        
        return user.email;
    }
    
    "User".to_string()
}

/// Get avatar initial (first letter, uppercase)
pub fn avatar() -> String {
    let name = display_name();
    let first = name.chars().next().unwrap_or('U');
    
    if first.is_ascii_lowercase() {
        first.to_ascii_uppercase().to_string()
    } else {
        first.to_string()
    }
}

/// Get full user data
pub fn user() -> Option<User> {
    load_user().ok()
}

/// Login user
/// 
/// # Arguments
/// * `email` - User email (required)
/// * `name` - Display name (optional)
/// 
/// # Returns
/// true if login successful
pub fn login(email: &str, name: Option<&str>) -> bool {
    if email.is_empty() {
        return false;
    }
    
    let now = current_timestamp();
    let user = User {
        email: email.to_string(),
        name: name.map(|s| s.to_string()),
        token: format!("tigerex_token_{}", now),
        created_at: now,
        expires_at: now + (24 * 60 * 60), // 24 hours
    };
    
    save_user(&user).is_ok()
}

/// Login with just email
pub fn login_email(email: &str) -> bool {
    login(email, None)
}

/// Logout user - clear all auth data
pub fn logout() {
    delete_auth();
}

// ============================================================================
// EXAMPLE GTK APPLICATION
// ============================================================================

#[cfg(feature = "gtk")]
pub mod gtk_example {
    use crate::{login_email, logout};
    
    /// Initialize GTK application
    pub fn init() {
        // This would require gtk-rs setup
        // Shown for demonstration only
    }
}

// ============================================================================
// EXAMPLE WXWIDGETS APPLICATION  
// ============================================================================

#[cfg(feature = "wx")]
pub mod wx_example {
    use crate::{login_email, logout, email, display_name, is_logged_in};
    
    /// Check if logged in (for use in frame OnInit)
    pub fn check_auth(frame: &mut wxFrame) -> bool {
        if is_logged_in() {
            true
        } else {
            // Show login dialog
            false
        }
    }
}

// ============================================================================
// EXAMPLE QT APPLICATION
// ============================================================================

#[cfg(feature = "qt")]
pub mod qt_example {
    use crate::{login_email, logout, email, is_logged_in};
    
    /// Check authentication in Qt application
    pub fn check_auth() -> bool {
        is_logged_in()
    }
    
    /// Get user email for Qt label
    pub fn user_email() -> String {
        email()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_login_logout() {
        let result = login("test@example.com", Some("Test User"));
        assert!(result);
        
        assert!(is_logged_in());
        assert_eq!(email(), "test@example.com");
        assert_eq!(display_name(), "Test User");
        
        logout();
        assert!(!is_logged_in());
    }
}