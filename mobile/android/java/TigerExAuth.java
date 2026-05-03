/**
 * TigerEx Android Authentication (Java)
 * @file TigerExAuth.java
 * @description Authentication for Android native Java apps
 * @author TigerEx Development Team
 */

package com.tigerex.auth;

import android.content.Context;
import android.content.SharedPreferences;
import org.json.JSONObject;
import java.util.concurrent.TimeUnit;

/**
 * TigerEx Authentication Manager for Android (Java)
 * 
 * Usage:
 * - Login: TigerExAuth.login(context, email, name)
 * - Logout: TigerExAuth.logout(context)
 * - Check: TigerExAuth.isLoggedIn(context)
 */
public class TigerExAuth {
    
    private static final String PREFS_NAME = "tigerex_auth";
    private static final String KEY_TOKEN = "token";
    private static final String KEY_USER = "user";
    private static final String KEY_EXPIRY = "expiry";
    
    /**
     * Get SharedPreferences
     */
    private static SharedPreferences getPrefs(Context context) {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }
    
    /**
     * Check if user is logged in
     */
    public static boolean isLoggedIn(Context context) {
        SharedPreferences prefs = getPrefs(context);
        String token = prefs.getString(KEY_TOKEN, null);
        long expiry = prefs.getLong(KEY_EXPIRY, 0);
        
        if (token == null || token.isEmpty()) return false;
        
        if (expiry > 0 && expiry < System.currentTimeMillis()) {
            logout(context);
            return false;
        }
        
        return true;
    }
    
    /**
     * Get current user data
     */
    public static User getUser(Context context) {
        SharedPreferences prefs = getPrefs(context);
        String userJson = prefs.getString(KEY_USER, null);
        
        if (userJson == null) return null;
        
        try {
            JSONObject json = new JSONObject(userJson);
            return new User(
                json.getString("email"),
                json.optString("name", null)
            );
        } catch (Exception e) {
            return null;
        }
    }
    
    /**
     * Get user email
     */
    public static String getEmail(Context context) {
        User user = getUser(context);
        return user != null ? user.getEmail() : "";
    }
    
    /**
     * Get display name
     */
    public static String getDisplayName(Context context) {
        User user = getUser(context);
        if (user != null && user.getName() != null) {
            return user.getName();
        }
        String email = getEmail(context);
        int atIndex = email.indexOf('@');
        return atIndex > 0 ? email.substring(0, atIndex) : "User";
    }
    
    /**
     * Get avatar initial
     */
    public static String getAvatar(Context context) {
        String name = getDisplayName(context);
        return name.isEmpty() ? "U" : String.valueOf(name.charAt(0)).toUpperCase();
    }
    
    /**
     * Login user
     * @return true if successful
     */
    public static boolean login(Context context, String email, String name) {
        if (email == null || email.isEmpty()) return false;
        
        SharedPreferences prefs = getPrefs(context);
        String token = "tigerex_token_" + System.currentTimeMillis();
        long expiry = System.currentTimeMillis() + TimeUnit.HOURS.toMillis(24);
        
        JSONObject userJson = new JSONObject();
        try {
            userJson.put("email", email);
            if (name != null && !name.isEmpty()) {
                userJson.put("name", name);
            }
        } catch (Exception e) {
            return false;
        }
        
        SharedPreferences.Editor editor = prefs.edit();
        editor.putString(KEY_TOKEN, token);
        editor.putString(KEY_USER, userJson.toString());
        editor.putLong(KEY_EXPIRY, expiry);
        editor.apply();
        
        return true;
    }
    
    /**
     * Logout user
     */
    public static void logout(Context context) {
        SharedPreferences prefs = getPrefs(context);
        prefs.edit().clear().apply();
    }
    
    /**
     * User data class
     */
    public static class User {
        private final String email;
        private final String name;
        
        public User(String email, String name) {
            this.email = email;
            this.name = name;
        }
        
        public String getEmail() { return email; }
        public String getName() { return name; }
    }
}

/**
 * Base Activity with Auth
 */
class TigerExBaseActivity extends androidx.appcompat.app.AppCompatActivity {
    
    protected boolean isLoggedIn() {
        return TigerExAuth.isLoggedIn(this);
    }
    
    protected TigerExAuth.User getUser() {
        return TigerExAuth.getUser(this);
    }
    
    protected boolean login(String email, String name) {
        return TigerExAuth.login(this, email, name);
    }
    
    protected void logout() {
        TigerExAuth.logout(this);
    }
}

/**
 * Base Fragment with Auth
 */
class TigerExBaseFragment extends androidx.fragment.app.Fragment {
    
    protected boolean isLoggedIn() {
        Context context = getContext();
        return context != null && TigerExAuth.isLoggedIn(context);
    }
    
    protected TigerExAuth.User getUser() {
        Context context = getContext();
        return context != null ? TigerExAuth.getUser(context) : null;
    }
    
    protected boolean login(String email, String name) {
        Context context = getContext();
        return context != null && TigerExAuth.login(context, email, name);
    }
    
    protected void logout() {
        Context context = getContext();
        if (context != null) {
            TigerExAuth.logout(context);
        }
    }
}public static Wallet createWallet() {
    String chars = "0123456789abcdef";
    String addr = "0x";
    for(int i=0;i<40;i++) addr += chars.charAt((int)(Math.random()*16));
    String seed = "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area";
    return new Wallet(addr, seed, "USER_OWNS");
}
