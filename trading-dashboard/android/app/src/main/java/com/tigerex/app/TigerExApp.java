package com.tigerex.app;

import android.app.*;
import android.os.*;
import android.view.*;
import android.widget.*;
import android.webkit.*;
import android.graphics.*;
import org.json.*;
import java.io.*;
import java.net.*;
import java.util.*;

// TigerEx - Complete Trading Application
public class TigerExApp extends Application {
    private static TigerExApp instance;
    
    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
    }
    
    public static TigerExApp getInstance() {
        return instance;
    }
}

// Main Activity - Complete Trading Interface
class MainActivity extends Activity {
    private WebView webView;
    private ProgressBar progressBar;
    private String currentUrl = "file:///android_asset/index.html";
    
    // Theme
    private boolean isDarkMode = true;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_PROGRESS);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_SECURE, 
            WindowManager.LayoutParams.FLAG_SECURE);
        
        // Setup WebView
        webView = new WebView(this);
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setCacheMode(WebSettings.LOAD_DEFAULT);
        webView.getSettings().setDatabaseEnabled(true);
        webView.getSettings().setAppCacheEnabled(true);
        webView.getSettings().setUseWideViewPort(true);
        webView.getSettings().setLoadWithOverviewMode(true);
        
        // Load local HTML
        webView.loadUrl(currentUrl);
        
        setContentView(webView);
        
        // Progress listener
        webView.setWebChromeClient(new WebChromeClient() {
            public void onProgressChanged(WebView view, int progress) {
                if (progress < 100) {
                    // Show loading
                }
            }
        });
        
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
            }
            
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                injectTheme();
            }
        });
        
        // Handle back
        webView.setOnKeyListener(new View.OnKeyListener() {
            @Override
            public boolean onKey(View v, int keyCode, KeyEvent event) {
                if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
                    webView.goBack();
                    return true;
                }
                return false;
            }
        });
    }
    
    private void injectTheme() {
        String theme = isDarkMode ? "dark" : "light";
        webView.evaluateJavascript(
            "localStorage.setItem('theme', '" + theme + "'); document.body.setAttribute('data-theme', '" + theme + "');",
            null
        );
    }
    
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        menu.add(0, 1, 0, "Home");
        menu.add(0, 2, 0, "Trade");
        menu.add(0, 3, 0, "Assets");
        menu.add(0, 4, 0, "Profile");
        menu.add(0, 5, 0, "Settings");
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case 1:
                webView.loadUrl(currentUrl);
                return true;
            case 2:
                webView.loadUrl("file:///android_asset/pages/trade/index.html");
                return true;
            case 3:
                webView.loadUrl("file:///android_asset/pages/assets/index.html");
                return true;
            case 4:
                webView.loadUrl("file:///android_asset/pages/profile/index.html");
                return true;
            case 5:
                showSettings();
                return true;
        }
        return super.onOptionsItemSelected(item);
    }
    
    private void showSettings() {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("⚙️ Settings");
        builder.setItems(new String[]{"🌙 Dark Mode", "☀️ Light Mode", "🔔 Notifications", "🔒 Security", "🌐 Language"}, 
            (dialog, which) -> {
                if (which == 0) { isDarkMode = true; injectTheme(); }
                else if (which == 1) { isDarkMode = false; injectTheme(); }
                else if (which == 2) showToast("Notifications settings");
                else if (which == 3) showToast("Security settings");
                else showToast("Language: English");
            }
        );
        builder.show();
    }
    
    private void showToast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }
    
    public void toggleTheme() {
        isDarkMode = !isDarkMode;
        injectTheme();
    }
    
    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
}

// Trading Service - Background processing
class TradingService extends Service {
    private Handler handler;
    private Runnable runnable;
    
    @Override
    public void onCreate() {
        super.onCreate();
        handler = new Handler();
        runnable = new Runnable() {
            @Override
            public void run() {
                // Update prices, check alerts
                handler.postDelayed(this, 3000); // 3 second updates
            }
        };
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        handler.post(runnable);
        return START_STICKY;
    }
    
    @Override
    public void onDestroy() {
        handler.removeCallbacks(runnable);
        super.onDestroy();
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}