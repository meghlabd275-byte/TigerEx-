package com.tigerex.android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.core.content.ContextCompat
import androidx.core.splashscreen.SplashScreen.Companion.installSplashScreen
import androidx.fragment.app.FragmentActivity
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.lifecycleScope
import com.tigerex.android.presentation.navigation.TigerExNavigation
import com.tigerex.android.presentation.theme.TigerExTheme
import com.tigerex.android.presentation.viewmodel.AuthViewModel
import com.tigerex.android.presentation.viewmodel.BiometricViewModel
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch

@AndroidEntryPoint
class MainActivity : FragmentActivity() {

    private lateinit var biometricPrompt: BiometricPrompt
    private lateinit var promptInfo: BiometricPrompt.PromptInfo

    override fun onCreate(savedInstanceState: Bundle?) {
        val splashScreen = installSplashScreen()
        super.onCreate(savedInstanceState)
        
        enableEdgeToEdge()
        
        setupBiometricAuthentication()
        
        setContent {
            TigerExTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    TigerExApp()
                }
            }
        }
    }

    private fun setupBiometricAuthentication() {
        val executor = ContextCompat.getMainExecutor(this)
        biometricPrompt = BiometricPrompt(this, executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    // Handle authentication error
                }

                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    // Handle successful authentication
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    // Handle failed authentication
                }
            })

        promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Biometric Authentication")
            .setSubtitle("Log in using your biometric credential")
            .setNegativeButtonText("Use account password")
            .build()
    }

    fun showBiometricPrompt() {
        biometricPrompt.authenticate(promptInfo)
    }
}

@Composable
fun TigerExApp() {
    val authViewModel: AuthViewModel = hiltViewModel()
    val biometricViewModel: BiometricViewModel = hiltViewModel()
    
    var isAuthenticated by remember { mutableStateOf(false) }
    
    LaunchedEffect(Unit) {
        // Check if user is already authenticated
        isAuthenticated = authViewModel.isUserAuthenticated()
    }
    
    TigerExNavigation(
        isAuthenticated = isAuthenticated,
        onAuthenticationChanged = { isAuthenticated = it }
    )
}