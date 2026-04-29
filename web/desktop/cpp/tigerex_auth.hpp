/**
 * TigerEx Desktop Authentication (C++)
 * @file tigerex_auth.hpp
 * @description Authentication for C++ desktop applications (Windows, Mac, Linux)
 * @author TigerEx Development Team
 * 
 * Usage:
 *   #include "tigerex_auth.hpp"
 *   
 *   if (TigerExAuth::isLoggedIn()) {
 *       std::cout << "User: " << TigerExAuth::getDisplayName() << std::endl;
 *   }
 *   
 *   TigerExAuth::login("user@example.com", "John");
 *   TigerExAuth::logout();
 */

#ifndef TIGEREX_AUTH_HPP
#define TIGEREX_AUTH_HPP

#include <string>
#include <fstream>
#include <chrono>
#include <ctime>

#ifdef _WIN32
    #include <windows.h>
    #include <shlobj.h>
#elif __APPLE__
    #include <CoreFoundation/CoreFoundation.h>
#elif __linux__
    #include <sys/stat.h>
    #include <unistd.h>
#endif

namespace TigerExAuth {
    
    // ============================================================================
    // DATA STRUCTURES
    // ============================================================================
    
    struct User {
        std::string email;
        std::string name;
        std::string token;
        int64_t created_at;
        int64_t expires_at;
        
        User() : created_at(0), expires_at(0) {}
    };
    
    // ============================================================================
    // CONFIGURATION
    // ============================================================================
    
    namespace Config {
        const std::string AUTH_DIR = ".tigerex";
        const std::string AUTH_FILE = "auth.dat";
    }
    
    // ============================================================================
    // PATH OPERATIONS
    // ============================================================================
    
    std::string getAuthPath() {
        std::string path;
        
#ifdef _WIN32
        char appdata[MAX_PATH];
        if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, appdata))) {
            path = appdata;
        } else {
            path = ".";
        }
        path += "\\" + Config::AUTH_DIR;
        
#elif __APPLE__
        CFStringRef home = CFURLCopyHomeDirectoryURLString();
        char homeStr[MAXPATHLEN];
        CFStringGetCString(home, homeStr, MAXPATHLEN, kCFStringEncodingUTF8);
        CFRelease(home);
        path = homeStr;
        path += "/Library/Application Support/" + Config::AUTH_DIR;
        
#elif __linux__
        const char* home = getenv("HOME");
        path = home ? std::string(home) : ".";
        path += "/" + Config::AUTH_DIR;
        
#else
        path = "." + Config::AUTH_DIR;
#endif
        
        return path;
    }
    
    // ============================================================================
    // FILE OPERATIONS
    // ============================================================================
    
    bool createAuthDir() {
        std::string path = getAuthPath();
        
#ifdef _WIN32
        return CreateDirectoryA(path.c_str(), NULL) != 0;
#elif __APPLE__
        return mkdir(path.c_str(), 0755) == 0;
#else
        return mkdir(path.c_str(), 0755) == 0;
#endif
    }
    
    bool saveUser(const User& user) {
        createAuthDir();
        
        std::string path = getAuthPath() + "/" + Config::AUTH_FILE;
        
        std::ofstream file(path, std::ios::binary);
        if (!file.is_open()) return false;
        
        // Write email
        size_t emailLen = user.email.size();
        file.write(reinterpret_cast<const char*>(&emailLen), sizeof(size_t));
        file.write(user.email.c_str(), emailLen);
        
        // Write name
        size_t nameLen = user.name.size();
        file.write(reinterpret_cast<const char*>(&nameLen), sizeof(size_t));
        if (nameLen > 0) {
            file.write(user.name.c_str(), nameLen);
        }
        
        // Write token
        size_t tokenLen = user.token.size();
        file.write(reinterpret_cast<const char*>(&tokenLen), sizeof(size_t));
        file.write(user.token.c_str(), tokenLen);
        
        // Write timestamps
        file.write(reinterpret_cast<const char*>(&user.created_at), sizeof(int64_t));
        file.write(reinterpret_cast<const char*>(&user.expires_at), sizeof(int64_t));
        
        file.close();
        return true;
    }
    
    bool loadUser(User& user) {
        std::string path = getAuthPath() + "/" + Config::AUTH_FILE;
        
        std::ifstream file(path, std::ios::binary);
        if (!file.is_open()) return false;
        
        // Read email
        size_t emailLen;
        file.read(reinterpret_cast<char*>(&emailLen), sizeof(size_t));
        user.email.resize(emailLen);
        file.read(&user.email[0], emailLen);
        
        // Read name
        size_t nameLen;
        file.read(reinterpret_cast<char*>(&nameLen), sizeof(size_t));
        if (nameLen > 0) {
            user.name.resize(nameLen);
            file.read(&user.name[0], nameLen);
        }
        
        // Read token
        size_t tokenLen;
        file.read(reinterpret_cast<char*>(&tokenLen), sizeof(size_t));
        user.token.resize(tokenLen);
        file.read(&user.token[0], tokenLen);
        
        // Read timestamps
        file.read(reinterpret_cast<char*>(&user.created_at), sizeof(int64_t));
        file.read(reinterpret_cast<char*>(&user.expires_at), sizeof(int64_t));
        
        file.close();
        return true;
    }
    
    bool deleteAuth() {
        std::string path = getAuthPath() + "/" + Config::AUTH_FILE;
        return remove(path.c_str()) == 0;
    }
    
    // ============================================================================
    // AUTH OPERATIONS
    // ============================================================================
    
    bool isLoggedIn() {
        User user;
        if (!loadUser(user)) {
            return false;
        }
        
        // Check expiry
        auto now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
        if (user.expires_at > 0 && user.expires_at < now) {
            logout();
            return false;
        }
        
        return !user.token.empty();
    }
    
    std::string getEmail() {
        User user;
        if (!loadUser(user)) {
            return "";
        }
        return user.email;
    }
    
    std::string getDisplayName() {
        User user;
        if (!loadUser(user)) {
            return "User";
        }
        
        if (!user.name.empty()) {
            return user.name;
        }
        
        // Extract email prefix
        size_t at = user.email.find('@');
        if (at != std::string::npos) {
            return user.email.substr(0, at);
        }
        
        return "User";
    }
    
    std::string getAvatar() {
        std::string name = getDisplayName();
        char first = name.empty() ? 'U' : name[0];
        if (first >= 'a' && first <= 'z') {
            first = first - 'a' + 'A';
        }
        return std::string(1, first);
    }
    
    bool login(const std::string& email, const std::string& name = "") {
        if (email.empty()) {
            return false;
        }
        
        User user;
        user.email = email;
        user.name = name;
        user.token = "tigerex_token_" + std::to_string(time(NULL));
        
        auto now = std::chrono::system_clock::now();
        user.created_at = std::chrono::system_clock::to_time_t(now);
        user.expires_at = user.created_at + (24 * 60 * 60); // 24 hours
        
        return saveUser(user);
    }
    
    void logout() {
        deleteAuth();
    }
    
    // Convenience getters
    static inline bool isLoggedInStatic() { return isLoggedIn(); }
    static inline std::string getEmailStatic() { return getEmail(); }
    static inline std::string getDisplayNameStatic() { return getDisplayName(); }
    static inline std::string getAvatarStatic() { return getAvatar(); }
    static inline void logoutStatic() { logout(); }
    
    // ============================================================================
    // EXAMPLE GTK APPLICATION
    // ============================================================================
    
#ifdef TIGEREX_GTK
    
#include <gtk/gtk.h>

    // GTK Login Window
    class GtkLoginWindow {
    private:
        GtkWidget* window;
        GtkWidget* emailEntry;
        GtkWidget* loginButton;
        
    public:
        GtkLoginWindow() {
            window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
            gtk_window_set_title(GTK_WINDOW(window), "TigerEx Login");
            gtk_window_set_default_size(GTK_WINDOW(window), 400, 300);
            
            GtkWidget* box = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
            gtk_container_add(GTK_CONTAINER(window), box);
            
            gtk_container_set_border_width(GTK_CONTAINER(box), 20);
            
            emailEntry = gtk_entry_new();
            gtk_entry_set_placeholder_text(GTK_ENTRY(emailEntry), "Email");
            gtk_box_pack_start(GTK_BOX(box), emailEntry, FALSE, FALSE, 0);
            
            loginButton = gtk_button_new_with_label("Log In");
            g_signal_connect(loginButton, "clicked", G_CALLBACK(onLoginClicked), this);
            gtk_box_pack_start(GTK_BOX(box), loginButton, FALSE, FALSE, 0);
            
            g_signal_connect(window, "destroy", G_CALLBACK(gtk_main_quit), NULL);
        }
        
        void show() {
            gtk_widget_show_all(window);
        }
        
    private:
        static void onLoginClicked(GtkWidget* widget, gpointer data) {
            auto* self = static_cast<GtkLoginWindow*>(data);
            const char* email = gtk_entry_get_text(GTK_ENTRY(self->emailEntry));
            
            if (email && strlen(email) > 0) {
                TigerExAuth::login(email);
                gtk_main_quit();
            }
        }
    };
    
#endif /* TIGEREX_GTK */
    
} /* namespace TigerExAuth */

#endif /* TIGEREX_AUTH_HPP */