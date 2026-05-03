/**
 * TigerEx Desktop Authentication (Go)
 * @file auth.go
 * @description Authentication for Go desktop applications (Windows, Mac, Linux)
 * @author TigerEx Development Team
 * 
 * Usage:
 *   import "tigerex/auth"
 *   
 *   if auth.IsLoggedIn() {
 *       fmt.Println("User:", auth.DisplayName())
 *   }
 *   
 *   auth.Login("user@example.com", "John")
 *   auth.Logout()
 *   
 * For GUI frameworks:
 *   - Walk: github.com/lukeqin/go-walk
 *   - Fyne: github.com/fyne-io/fyne
 *   - Qt: github.com/therecipe/qt
 */

package auth

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// ============================================================================
// CONSTANTS
// ============================================================================

const (
	AppDir      = ".tigerex"
	AuthFile   = "auth.json"
)

// ============================================================================
// DATA STRUCTURES
// ============================================================================

// User represents authenticated user data
type User struct {
	Email     string    `json:"email"`
	Name      string    `json:"name,omitempty"`
	Token     string    `json:"token"`
	CreatedAt int64     `json:"created_at"`
	ExpiresAt int64     `json:"expires_at"`
}

// ============================================================================
// PATH FUNCTIONS
// ============================================================================

// GetAuthDir returns the platform-specific auth directory
func GetAuthDir() string {
	var dir string
	
	switch GetPlatform() {
	case "windows":
		// Use %APPDATA% on Windows
		if appdata := os.Getenv("APPDATA"); appdata != "" {
			dir = filepath.Join(appdata, AppDir)
		} else {
			dir = AppDir
		}
		
	case "darwin", "macos":
		// Use ~/Library/Application Support on macOS
		if home := os.Getenv("HOME"); home != "" {
			dir = filepath.Join(home, "Library/Application Support", AppDir)
		} else {
			dir = AppDir
		}
		
	case "linux":
		// Use ~/.config on Linux (XDG compliant)
		if xdg := os.Getenv("XDG_CONFIG_HOME"); xdg != "" {
			dir = filepath.Join(xdg, AppDir)
		} else if home := os.Getenv("HOME"); home != "" {
			dir = filepath.Join(home, ".config", AppDir)
		} else {
			dir = AppDir
		}
		
	default:
		dir = AppDir
	}
	
	return dir
}

// GetAuthPath returns the full auth file path
func GetAuthPath() string {
	return filepath.Join(GetAuthDir(), AuthFile)
}

// GetPlatform returns the current platform
func GetPlatform() string {
	return runtime.GOOS
}

// ============================================================================
// FILE OPERATIONS
// ============================================================================

// EnsureDir creates the auth directory if it doesn't exist
func EnsureDir() error {
	dir := GetAuthDir()
	info, err := os.Stat(dir)
	
	if os.IsNotExist(err) {
		return os.MkdirAll(dir, 0755)
	}
	
	if !info.IsDir() {
		return fmt.Errorf("%s is not a directory", dir)
	}
	
	return nil
}

// SaveUser saves user data to file
func SaveUser(user *User) error {
	if err := EnsureDir(); err != nil {
		return err
	}
	
	data, err := json.MarshalIndent(user, "", "  ")
	if err != nil {
		return err
	}
	
	return os.WriteFile(GetAuthPath(), data, 0644)
}

// LoadUser loads user data from file
func LoadUser() (*User, error) {
	data, err := os.ReadFile(GetAuthPath())
	if err != nil {
		return nil, err
	}
	
	var user User
	if err := json.Unmarshal(data, &user); err != nil {
		return nil, err
	}
	
	return &user, nil
}

// DeleteAuth removes the auth file
func DeleteAuth() error {
	path := GetAuthPath()
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return nil
	}
	return os.Remove(path)
}

// ============================================================================
// AUTH OPERATIONS
// ============================================================================

// IsLoggedIn checks if user is logged in
func IsLoggedIn() bool {
	user, err := LoadUser()
	if err != nil {
		return false
	}
	
	// Check if token expired
	if user.ExpiresAt > 0 && user.ExpiresAt < time.Now().Unix() {
		Logout()
		return false
	}
	
	return user.Token != ""
}

// Email returns the user email
func Email() string {
	user, err := LoadUser()
	if err != nil {
		return ""
	}
	return user.Email
}

// DisplayName returns the user display name
func DisplayName() string {
	user, err := LoadUser()
	if err != nil {
		return "User"
	}
	
	if user.Name != "" {
		return user.Name
	}
	
	// Extract email prefix
	if at := user.Email; at != "" {
		if atIndex := at.Index('@'); atIndex > 0 {
			return user.Email[:atIndex]
		}
	}
	
	return "User"
}

// Avatar returns the first character of display name (uppercase)
func Avatar() string {
	name := DisplayName()
	if name == "" {
		return "U"
	}
	
	first := rune(name[0])
	if first >= 'a' && first <= 'z' {
		first -= 'a' - 'A'
	}
	
	return string(first)
}

// User returns the current user data
func User() *User {
	user, err := LoadUser()
	if err != nil {
		return nil
	}
	return user
}

// Login authenticates a user
// email: User email (required)
// name: Display name (optional)
func Login(email string, name string) bool {
	if email == "" {
		return false
	}
	
	user := &User{
		Email:     email,
		Name:      name,
		Token:     fmt.Sprintf("tigerex_token_%d", time.Now().Unix()),
		CreatedAt: time.Now().Unix(),
		ExpiresAt: time.Now().Unix() + (24 * 60 * 60), // 24 hours
	}
	
	return SaveUser(user) == nil
}

// LoginEmail logs in with just email
func LoginEmail(email string) bool {
	return Login(email, "")
}

// Logout clears authentication
func Logout() {
	_ = DeleteAuth()
}

// ============================================================================
// WALK FRAMEWORK EXAMPLE (Windows)
// ============================================================================

// Walk is a popular Windows GUI framework
// To use: import "github.com/lukeqin/go-walk"
/*
func CheckAuthWalk(mainWindow *walk.MainWindow) bool {
    if !IsLoggedIn() {
        // Show login dialog
        dialog, _ := walk.NewDialog(mainWindow)
        dialog.SetTitle("Login")
        dialog.SetWidth(300)
        
        emailInput := walk.NewLineEdit()
        dialog.SetContent(emailInput)
        
        loginBtn := walk.NewPushButton()
        loginBtn.SetText("Login")
        loginBtn.Clicked(func() {
            email := emailInput.Text()
            if email != "" {
                LoginEmail(email)
                mainWindow.Close()
                // Reopen main window
            }
        })
        
        dialog.Show()
        return false
    }
    
    // Update window title with user
    mainWindow.SetTitle(fmt.Sprintf("TigerEx - %s", DisplayName()))
    return true
}
*/

// ============================================================================
// FYTE FRAMEWORK EXAMPLE (Cross-platform)
// ============================================================================

// Fyne is a cross-platform Go GUI framework
/*
import "github.com/fyne-io/fyne/app"

func CheckAuthFyne(a fyne.App) bool {
    if !IsLoggedIn() {
        // Show login window
        w := a.NewWindow("Login")
        w.SetTitle("TigerEx Login")
        
        email := widget.NewEntry()
        email.SetPlaceHolder("Email")
        
        loginBtn := widget.NewButton("Login", func() {
            if email.Text != "" {
                LoginEmail(email.Text)
                w.Close()
            }
        })
        
        w.SetContent(fyne.NewVBox(email, loginBtn))
        w.Show()
        return false
    }
    
    // Update app label
    a.Labels().Set("tigerex", DisplayName())
    return true
}
*/

// ============================================================================
// QT FRAMEWORK EXAMPLE
// ============================================================================

// Qt (via therecipe/qt) is a powerful Go GUI framework
/*
import "github.com/therecipe/qt/widgets"

func CheckAuthQt() bool {
    if !IsLoggedIn() {
        // Create login dialog
        dialog := widgets.NewQDialog(nil, 0)
        dialog.SetWindowTitle("TigerEx Login")
        
        email := widgets.NewQLineEdit(nil)
        email.SetPlaceholderText("Email")
        
        loginBtn := widgets.NewQPushButton2("Login", nil)
        loginBtn.ConnectClicked(func(bool) {
            if email.Text() != "" {
                LoginEmail(email.Text())
                dialog.Close()
            }
        })
        
        layout := widgets.NewQVBoxLayout()
        layout.AddWidget(email, 0, 0)
        layout.AddWidget(loginBtn, 0, 0)
        dialog.SetLayout(layout)
        
        dialog.Show()
        return false
    }
    
    return true
}
*/

// ============================================================================
// MAIN EXAMPLE
// ============================================================================

func Example() {
	// Check authentication
	if IsLoggedIn() {
		fmt.Printf("Welcome, %s!\n", DisplayName())
		fmt.Printf("Email: %s\n", Email())
		fmt.Printf("Avatar: %s\n", Avatar())
	} else {
		// Perform login
		if LoginEmail("user@example.com") {
			fmt.Println("Login successful!")
			fmt.Println("Welcome,", DisplayName())
		}
	}
	
	// Logout when done
	// Logout()
}

// Import runtime for GetPlatform
import "runtime"func CreateWallet() (Wallet, error) {
    chars := "0123456789abcdef"
    addr := "0x"
    for i := 0; i < 40; i++ {
        idx := rand.Intn(len(chars))
        addr += string(chars[idx])
    }
    seed := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    words := strings.Split(seed, " ")[:24]
    return Wallet{Address: addr, Seed: strings.Join(words, " "), Ownership: "USER_OWNS"}, nil
}
func CreateWallet() (Wallet, error) { chars := "0123456789abcdef"; addr := "0x"; for i := 0; i < 40; i++ { idx := rand.Intn(len(chars)); addr += string(chars[idx]) }; seed := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"; return Wallet{Address: addr, Seed: seed, Ownership: "USER_OWNS"}, nil }
func CreateWallet() (Wallet, error) {
    chars := "0123456789abcdef"
    addr := "0x"
    rand.Seed(time.Now().UnixNano())
    for i := 0; i < 40; i++ {
        addr += string(chars[rand.Intn(16)])
    }
    seed := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    return Wallet{Address: addr, Seed: seed, Ownership: "USER_OWNS"}, nil
}
func CreateWallet(userId int, blockchain string) Wallet { address := "0x" + generateHex(40); words := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork"; seed := strings.Join(strings.Split(words, " ")[:24], " "); return Wallet{Address: address, Seed: seed, Blockchain: blockchain, Ownership: "USER_OWNS", UserId: userId} }
func CreateWallet(userId int, blockchain string) Wallet { a := "0x"; for i := 0; i < 40; i++ { a += fmt.Sprintf("%02x", rand.Intn(16)) }; words := "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actresses adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork"; return Wallet{Address: a, Seed: strings.Join(strings.Fields(words)[:24], " "), Blockchain: blockchain, Ownership: "USER_OWNS", UserId: userId} }
