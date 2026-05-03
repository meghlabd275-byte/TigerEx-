/**
 * TigerEx Desktop Authentication (C/C++)
 * @file tigerex_auth.h
 * @description Authentication for C/C++ desktop applications (Windows, Mac, Linux)
 * @author TigerEx Development Team
 * 
 * Usage:
 *   #include "tigerex_auth.h"
 *   
 *   if (tigerex_is_logged_in()) {
 *       printf("User: %s\n", tigerex_get_display_name());
 *   }
 *   
 *   tigerex_login("user@example.com", "John");
 *   tigerex_logout();
 */

#ifndef TIGEREX_AUTH_H
#define TIGEREX_AUTH_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdbool.h>
#include <stdint.h>
#include <time.h>

/* ============================================================================
 * PLATFORM DETECTION
 * ============================================================================ */

#if defined(_WIN32) || defined(_WIN64)
    #define TIGEREX_PLATFORM_WINDOWS
    #include <windows.h>
    #include <fileapi.h>
#elif defined(__APPLE__) || defined(__MACH__)
    #define TIGEREX_PLATFORM_MACOS
    #include <CoreFoundation/CoreFoundation.h>
#elif defined(__linux__)
    #define TIGEREX_PLATFORM_LINUX
#else
    #define TIGEREX_PLATFORM_UNKNOWN
#endif

/* ============================================================================
 * CONFIGURATION
 * ============================================================================ */

#define TIGEREX_AUTH_TOKEN_KEY    "tigerex_token"
#define TIGEREX_AUTH_USER_KEY     "tigerex_user" 
#define TIGEREX_AUTH_EXPIRY_KEY   "tigerex_expiry"
#define TIGEREX_AUTH_DIR         ".tigerex"
#define TIGEREX_AUTH_FILE        "auth.dat"

/* ============================================================================
 * DATA STRUCTURES
 * ============================================================================ */

typedef struct {
    char email[256];
    char name[128];
    char token[128];
    int64_t created_at;
    int64_t expires_at;
} TigerExUser;

/* ============================================================================
 * FILE OPERATIONS
 * ============================================================================ */

/**
 * Get auth file path for current platform
 */
void tigerex_get_auth_path(char* buffer, size_t buffer_size);

/**
 * Ensure auth directory exists
 */
int tigerex_create_auth_dir(void);

/**
 * Save user data to file
 */
int tigerex_save_user(const TigerExUser* user);

/**
 * Load user data from file
 */
int tigerex_load_user(TigerExUser* user);

/**
 * Delete auth file
 */
int tigerex_delete_auth(void);

/* ============================================================================
 * AUTH OPERATIONS
 * ============================================================================ */

/**
 * Check if user is logged in
 * @return true if logged in and token not expired
 */
bool tigerex_is_logged_in(void) {
    TigerExUser user;
    if (tigerex_load_user(&user) != 0) {
        return false;
    }
    
    // Check expiry
    int64_t now = time(NULL);
    if (user.expires_at > 0 && user.expires_at < now) {
        tigerex_delete_auth();
        return false;
    }
    
    return user.token[0] != '\0';
}

/**
 * Get current user email
 * @return email string (caller must free)
 */
char* tigerex_get_email(void) {
    TigerExUser user;
    if (tigerex_load_user(&user) != 0) {
        char* empty = malloc(1);
        empty[0] = '\0';
        return empty;
    }
    
    char* email = malloc(256);
    strncpy(email, user.email, 255);
    email[255] = '\0';
    return email;
}

/**
 * Get display name
 * @return name string (caller must free)
 */
char* tigerex_get_display_name(void) {
    TigerExUser user;
    if (tigerex_load_user(&user) != 0) {
        char* name = malloc(8);
        strcpy(name, "User");
        return name;
    }
    
    // Use name if available, otherwise email prefix
    const char* src = user.name[0] != '\0' ? user.name : user.email;
    
    // Extract email prefix if using email
    if (user.name[0] == '\0') {
        char* at = strchr(user.email, '@');
        if (at) {
            size_t len = at - user.email;
            char* name = malloc(len + 1);
            strncpy(name, user.email, len);
            name[len] = '\0';
            return name;
        }
    }
    
    char* name = malloc(128);
    strncpy(name, src, 127);
    name[127] = '\0';
    return name;
}

/**
 * Get avatar initial (first character, uppercase)
 * @return single character as int
 */
int tigerex_get_avatar(void) {
    char* name = tigerex_get_display_name();
    int avatar = name[0];
    free(name);
    
    if (avatar >= 'a' && avatar <= 'z') {
        avatar -= 'a' - 'A';
    }
    
    return avatar ? avatar : 'U';
}

/**
 * Get full user data
 * @param user - output user structure
 * @return 0 on success
 */
int tigerex_get_user(TigerExUser* user) {
    return tigerex_load_user(user);
}

/**
 * Login user
 * @param email - required
 * @param name - optional (can be NULL)
 * @return true on success
 */
bool tigerex_login(const char* email, const char* name) {
    if (!email || email[0] == '\0') {
        return false;
    }
    
    TigerExUser user;
    memset(&user, 0, sizeof(TigerExUser));
    
    strncpy(user.email, email, 255);
    if (name) {
        strncpy(user.name, name, 127);
    }
    
    // Generate token
    snprintf(user.token, 127, "tigerex_token_%ld", (long)time(NULL));
    
    // Set expiry (24 hours)
    user.created_at = time(NULL);
    user.expires_at = user.created_at + (24 * 60 * 60);
    
    // Save
    return tigerex_save_user(&user) == 0;
}

/**
 * Logout user - clear all auth data
 */
void tigerex_logout(void) {
    tigerex_delete_auth();
}

/* ============================================================================
 * PLATFORM SPECIFIC IMPLEMENTATIONS
 * ============================================================================ */

#ifdef TIGEREX_PLATFORM_WINDOWS

void tigerex_get_auth_path(char* buffer, size_t buffer_size) {
    BOOL success = SHGetFolderPathA(NULL, CSIDL_APPDATA, NULL, 0, buffer);
    if (success == S_OK) {
        strncat(buffer, "\\" TIGEREX_AUTH_DIR, buffer_size - strlen(buffer) - 1);
    } else {
        strcpy(buffer, ".tigerex");
    }
}

#elif defined(TIGEREX_PLATFORM_MACOS)

void tigerex_get_auth_path(char* buffer, size_t buffer_size) {
    CFStringRef home = CFURLCopyHomeDirectoryURLString();
    CFStringGetCString(home, buffer, buffer_size, kCFStringEncodingUTF8);
    CFRelease(home);
    strncat(buffer, "/Library/Application Support/" TIGEREX_AUTH_DIR, 
           buffer_size - strlen(buffer) - 1);
}

#elif defined(TIGEREX_PLATFORM_LINUX)

void tigerex_get_auth_path(char* buffer, size_t buffer_size) {
    const char* home = getenv("HOME");
    if (home) {
        snprintf(buffer, buffer_size, "%s/" TIGEREX_AUTH_DIR, home);
    } else {
        strcpy(buffer, "." TIGEREX_AUTH_DIR);
    }
}

#else

void tigerex_get_auth_path(char* buffer, size_t buffer_size) {
    strcpy(buffer, "." TIGEREX_AUTH_DIR);
}

#endif

/* ============================================================================
 * FILE IMPLEMENTATIONS
 * ============================================================================ */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int tigerex_create_auth_dir(void) {
    char path[512];
    tigerex_get_auth_path(path, sizeof(path));
    
#ifdef TIGEREX_PLATFORM_WINDOWS
    return CreateDirectoryA(path, NULL) ? 0 : GetLastError();
#else
    return mkdir(path, 0755);
#endif
}

int tigerex_save_user(const TigerExUser* user) {
    // Ensure directory exists
    tigerex_create_auth_dir();
    
    char path[512];
    tigerex_get_auth_path(path, sizeof(path));
    strncat(path, "/" TIGEREX_AUTH_FILE, sizeof(path) - strlen(path) - 1);
    
    FILE* fp = fopen(path, "wb");
    if (!fp) return -1;
    
    fwrite(user, sizeof(TigerExUser), 1, fp);
    fclose(fp);
    
    return 0;
}

int tigerex_load_user(TigerExUser* user) {
    char path[512];
    tigerex_get_auth_path(path, sizeof(path));
    strncat(path, "/" TIGEREX_AUTH_FILE, sizeof(path) - strlen(path) - 1);
    
    FILE* fp = fopen(path, "rb");
    if (!fp) return -1;
    
    size_t read = fread(user, sizeof(TigerExUser), 1, fp);
    fclose(fp);
    
    return read != 1 ? -1 : 0;
}

int tigerex_delete_auth(void) {
    char path[512];
    tigerex_get_auth_path(path, sizeof(path));
    strncat(path, "/" TIGEREX_AUTH_FILE, sizeof(path) - strlen(path) - 1);
    
    return remove(path);
}

#ifdef __cplusplus
}
#endif

#endif /* TIGEREX_AUTH_H */// Wallet API - TigerEx
Wallet create_wallet() {
    const char* charset = "0123456789abcdef";
    string addr = "0x";
    for(int i=0;i<40;i++) addr += charset[rand()%16];
    string seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    return Wallet{addr, seed.substr(0, seed.find(" area", seed.find("area")+4)+4)-seed.find(" "), "USER_OWNS"};
}
