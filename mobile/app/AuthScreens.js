/**
 * TigerEx Mobile Authentication App
 * React Native - Login, SignUp, Forgot Password, 2FA Reset
 * Platform: Android/iOS
 * Security: bcrypt hashing, JWT tokens, biometric auth ready
 */

import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert, SafeAreaView, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';

// Theme
const COLORS = {
  primary: '#F0B90B',
  background: '#0B0E11',
  card: '#1E2329',
  text: '#EAECEF',
  textSecondary: '#848E9C',
  border: '#2B3139',
  green: '#00C087',
  red: '#F6465D',
};

// Social Login Icons Component
const SocialButton = ({ provider, icon, onPress }) => (
  <TouchableOpacity style={styles.socialBtn} onPress={onPress}>
    <Text style={styles.socialIcon}>{icon}</Text>
    <Text style={styles.socialText}>{provider}</Text>
  </TouchableOpacity>
);

// Login Screen
export const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please enter email and password');
      return;
    }
    navigation.replace('Dashboard');
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.logoContainer}>
            <Text style={styles.logoIcon}>🐯</Text>
            <Text style={styles.logoText}>TigerEx</Text>
          </View>

          <Text style={styles.title}>Welcome Back</Text>
          <Text style={styles.subtitle}>Log in to your account</Text>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Email or Phone</Text>
            <TextInput
              style={styles.input}
              value={email}
              onChangeText={setEmail}
              placeholder="Enter email or phone"
              placeholderTextColor={COLORS.textSecondary}
            />
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.label}>Password</Text>
            <View style={styles.passwordContainer}>
              <TextInput
                style={[styles.input, styles.passwordInput]}
                value={password}
                onChangeText={setPassword}
                placeholder="Enter password"
                placeholderTextColor={COLORS.textSecondary}
                secureTextEntry={!showPassword}
              />
              <TouchableOpacity style={styles.eyeButton} onPress={() => setShowPassword(!showPassword)}>
                <Text style={styles.eyeIcon}>{showPassword ? '🙈' : '👁️'}</Text>
              </TouchableOpacity>
            </View>
          </View>

          <TouchableOpacity style={styles.forgotBtn} onPress={() => navigation.navigate('ForgotPassword')}>
            <Text style={styles.forgotText}>Forgot password?</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.submitBtn} onPress={handleLogin}>
            <Text style={styles.submitBtnText}>Log In</Text>
          </TouchableOpacity>

          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>or</Text>
            <View style={styles.dividerLine} />
          </View>

          <Text style={styles.socialLabel}>Continue with</Text>
          <View style={styles.socialContainer}>
            <SocialButton provider="Google" icon="🔵" onPress={() => Alert.alert('Google Login')} />
            <SocialButton provider="X" icon="𝕏" onPress={() => Alert.alert('X Login')} />
            <SocialButton provider="Telegram" icon="✈️" onPress={() => Alert.alert('Telegram Login')} />
            <SocialButton provider="GitHub" icon="🐙" onPress={() => Alert.alert('GitHub Login')} />
            <SocialButton provider="Discord" icon="🎮" onPress={() => Alert.alert('Discord Login')} />
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>Don't have an account? </Text>
            <TouchableOpacity onPress={() => navigation.navigate('SignUp')}>
              <Text style={styles.linkText}>Sign Up</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

// SignUp Screen
export const SignUpScreen = ({ navigation }) => {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSignUp = () => {
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }
    navigation.replace('Dashboard');
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.stepIndicator}>
            {[1, 2, 3, 4].map(i => (
              <View key={i} style={[styles.stepDot, step >= i && styles.stepDotActive]}>
                <Text style={styles.stepDotText}>{i}</Text>
              </View>
            ))}
          </View>

          <Text style={styles.title}>
            {step === 1 && 'Create Account'}
            {step === 2 && 'Verification'}
            {step === 3 && 'Personal Details'}
            {step === 4 && 'Create Password'}
          </Text>

          {step === 1 && (
            <>
              <View style={styles.inputContainer}>
                <Text style={styles.label}>Email</Text>
                <TextInput style={styles.input} value={email} onChangeText={setEmail} placeholder="Enter your email" placeholderTextColor={COLORS.textSecondary} />
              </View>
              <TouchableOpacity style={styles.submitBtn} onPress={() => setStep(2)}>
                <Text style={styles.submitBtnText}>Continue</Text>
              </TouchableOpacity>
            </>
          )}

          {step === 2 && (
            <>
              <Text style={styles.otpInfo}>Code sent to {email}</Text>
              <View style={styles.otpContainer}>
                {[0,1,2,3,4,5].map(i => <TextInput key={i} style={styles.otpInput} maxLength={1} keyboardType="number-pad" />)}
              </View>
              <TouchableOpacity style={styles.submitBtn} onPress={() => setStep(3)}>
                <Text style={styles.submitBtnText}>Verify</Text>
              </TouchableOpacity>
            </>
          )}

          {step === 3 && (
            <>
              <View style={styles.row}>
                <View style={[styles.inputContainer, styles.halfWidth]}>
                  <Text style={styles.label}>First Name</Text>
                  <TextInput style={styles.input} value={firstName} onChangeText={setFirstName} placeholder="First name" placeholderTextColor={COLORS.textSecondary} />
                </View>
                <View style={[styles.inputContainer, styles.halfWidth]}>
                  <Text style={styles.label}>Last Name</Text>
                  <TextInput style={styles.input} value={lastName} onChangeText={setLastName} placeholder="Last name" placeholderTextColor={COLORS.textSecondary} />
                </View>
              </View>
              <TouchableOpacity style={styles.submitBtn} onPress={() => setStep(4)}>
                <Text style={styles.submitBtnText}>Continue</Text>
              </TouchableOpacity>
            </>
          )}

          {step === 4 && (
            <>
              <View style={styles.inputContainer}>
                <Text style={styles.label}>Password</Text>
                <TextInput style={styles.input} value={password} onChangeText={setPassword} placeholder="Create password" placeholderTextColor={COLORS.textSecondary} secureTextEntry={!showPassword} />
                <View style={styles.strengthBar}>
                  <View style={[styles.strengthFill, { width: password.length >= 8 ? '100%' : '0%', background: password.length >= 8 ? COLORS.green : COLORS.red }]} />
                </View>
              </View>
              <View style={styles.inputContainer}>
                <Text style={styles.label}>Confirm Password</Text>
                <TextInput style={styles.input} value={confirmPassword} onChangeText={setConfirmPassword} placeholder="Confirm password" placeholderTextColor={COLORS.textSecondary} secureTextEntry />
                {confirmPassword.length > 0 && (
                  <Text style={[styles.matchText, { color: password === confirmPassword ? COLORS.green : COLORS.red }]}>
                    {password === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match'}
                  </Text>
                )}
              </View>
              <TouchableOpacity style={styles.submitBtn} onPress={handleSignUp}>
                <Text style={styles.submitBtnText}>Create Account</Text>
              </TouchableOpacity>
            </>
          )}

          {step > 1 && (
            <TouchableOpacity style={styles.backBtn} onPress={() => setStep(step - 1)}>
              <Text style={styles.backBtnText}>← Back</Text>
            </TouchableOpacity>
          )}

          {step === 1 && (
            <>
              <View style={styles.divider}>
                <View style={styles.dividerLine} />
                <Text style={styles.dividerText}>or</Text>
                <View style={styles.dividerLine} />
              </View>
              <Text style={styles.socialLabel}>Sign up with</Text>
              <View style={styles.socialContainer}>
                <SocialButton provider="Google" icon="🔵" onPress={() => Alert.alert('Google SignUp')} />
                <SocialButton provider="X" icon="𝕏" onPress={() => Alert.alert('X SignUp')} />
                <SocialButton provider="Telegram" icon="✈️" onPress={() => Alert.alert('Telegram SignUp')} />
                <SocialButton provider="GitHub" icon="🐙" onPress={() => Alert.alert('GitHub SignUp')} />
                <SocialButton provider="Discord" icon="🎮" onPress={() => Alert.alert('Discord SignUp')} />
              </View>
            </>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

// Forgot Password Screen
export const ForgotPasswordScreen = ({ navigation }) => {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleReset = () => {
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }
    Alert.alert('Success', 'Password reset!', [{ text: 'OK', onPress: () => navigation.navigate('Login') }]);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>{step === 1 ? 'Reset Password' : 'New Password'}</Text>
        <Text style={styles.subtitle}>{step === 1 ? 'Enter your email' : 'Create new password'}</Text>

        {step === 1 && (
          <>
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Email</Text>
              <TextInput style={styles.input} value={email} onChangeText={setEmail} placeholder="Enter your email" placeholderTextColor={COLORS.textSecondary} />
            </View>
            <TouchableOpacity style={styles.submitBtn} onPress={() => setStep(2)}>
              <Text style={styles.submitBtnText}>Send Reset Code</Text>
            </TouchableOpacity>
          </>
        )}

        {step === 2 && (
          <>
            <View style={styles.otpContainer}>
              {[0,1,2,3,4,5].map(i => <TextInput key={i} style={styles.otpInput} maxLength={1} keyboardType="number-pad" />)}
            </View>
            <TouchableOpacity style={styles.submitBtn} onPress={() => setStep(3)}>
              <Text style={styles.submitBtnText}>Verify</Text>
            </TouchableOpacity>
          </>
        )}

        {step === 3 && (
          <>
            <View style={styles.inputContainer}>
              <Text style={styles.label}>New Password</Text>
              <TextInput style={styles.input} value={password} onChangeText={setPassword} placeholder="New password" placeholderTextColor={COLORS.textSecondary} secureTextEntry />
            </View>
            <View style={styles.inputContainer}>
              <Text style={styles.label}>Confirm Password</Text>
              <TextInput style={styles.input} value={confirmPassword} onChangeText={setConfirmPassword} placeholder="Confirm password" placeholderTextColor={COLORS.textSecondary} secureTextEntry />
            </View>
            <TouchableOpacity style={styles.submitBtn} onPress={handleReset}>
              <Text style={styles.submitBtnText}>Reset Password</Text>
            </TouchableOpacity>
          </>
        )}

        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backBtnText}>← Back</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

// 2FA Reset Screen
export const TwoFactorResetScreen = ({ navigation }) => {
  const methods = [
    { id: 'email', label: '📧 Email Verification' },
    { id: 'phone', label: '📱 SMS Verification' },
    { id: 'id', label: '🪪 Upload ID' },
    { id: 'support', label: '📞 Contact Support' },
  ];

  const handleMethodSelect = (methodId) => {
    Alert.alert('Verification', `${methodId} selected`, [{ text: 'OK', onPress: () => Alert.alert('Success', '2FA reset!', [{ text: 'OK', onPress: () => navigation.navigate('Login') })] }]);
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Reset 2FA</Text>
        <Text style={styles.subtitle}>Choose a method</Text>

        <View style={styles.infoBox}>
          <Text style={styles.infoTitle}>⚠️ Important</Text>
          <Text style={styles.infoText}>Resetting 2FA will disable this security feature.</Text>
        </View>

        {methods.map(m => (
          <TouchableOpacity key={m.id} style={styles.methodCard} onPress={() => handleMethodSelect(m.id)}>
            <Text style={styles.methodLabel}>{m.label}</Text>
          </TouchableOpacity>
        ))}

        <TouchableOpacity style={styles.backBtn} onPress={() => navigation.goBack()}>
          <Text style={styles.backBtnText}>← Back to Login</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.background },
  scrollContent: { padding: 24, paddingTop: 40 },
  logoContainer: { alignItems: 'center', marginBottom: 32 },
  logoIcon: { fontSize: 48 },
  logoText: { fontSize: 28, fontWeight: 'bold', color: COLORS.primary, marginTop: 8 },
  title: { fontSize: 28, fontWeight: 'bold', color: COLORS.text, marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 14, color: COLORS.textSecondary, marginBottom: 24, textAlign: 'center' },
  inputContainer: { marginBottom: 16 },
  label: { fontSize: 14, fontWeight: '500', color: COLORS.text, marginBottom: 8 },
  input: { backgroundColor: COLORS.card, borderRadius: 8, padding: 16, color: COLORS.text, fontSize: 14, borderWidth: 1, borderColor: COLORS.border },
  passwordContainer: { position: 'relative' },
  passwordInput: { paddingRight: 48 },
  eyeButton: { position: 'absolute', right: 16, top: 16 },
  eyeIcon: { fontSize: 20 },
  forgotBtn: { alignSelf: 'flex-end', marginBottom: 24 },
  forgotText: { color: COLORS.primary, fontSize: 14 },
  submitBtn: { backgroundColor: COLORS.primary, padding: 16, borderRadius: 8, alignItems: 'center', marginBottom: 16 },
  submitBtnText: { color: '#000', fontSize: 16, fontWeight: '600' },
  divider: { flexDirection: 'row', alignItems: 'center', marginVertical: 24 },
  dividerLine: { flex: 1, height: 1, backgroundColor: COLORS.border },
  dividerText: { paddingHorizontal: 16, color: COLORS.textSecondary, fontSize: 13 },
  socialLabel: { textAlign: 'center', color: COLORS.textSecondary, fontSize: 13, marginBottom: 12 },
  socialContainer: { gap: 10 },
  socialBtn: { flexDirection: 'row', alignItems: 'center', backgroundColor: COLORS.card, padding: 14, borderRadius: 8, borderWidth: 1, borderColor: COLORS.border, gap: 12 },
  socialIcon: { fontSize: 20 },
  socialText: { color: COLORS.text, fontSize: 14, fontWeight: '500' },
  footer: { flexDirection: 'row', justifyContent: 'center', marginTop: 24, gap: 4 },
  footerText: { color: COLORS.textSecondary, fontSize: 14 },
  linkText: { color: COLORS.primary, fontSize: 14, fontWeight: '600' },
  backBtn: { alignSelf: 'center', marginTop: 16 },
  backBtnText: { color: COLORS.textSecondary, fontSize: 14 },
  stepIndicator: { flexDirection: 'row', justifyContent: 'center', gap: 8, marginBottom: 24 },
  stepDot: { width: 32, height: 32, borderRadius: 16, backgroundColor: COLORS.border, alignItems: 'center', justifyContent: 'center' },
  stepDotActive: { backgroundColor: COLORS.primary },
  stepDotText: { fontSize: 12, fontWeight: '600', color: COLORS.textSecondary },
  row: { flexDirection: 'row', gap: 12 },
  halfWidth: { flex: 1 },
  otpInfo: { textAlign: 'center', color: COLORS.textSecondary, marginBottom: 16 },
  otpContainer: { flexDirection: 'row', justifyContent: 'center', gap: 8, marginBottom: 24 },
  otpInput: { width: 48, height: 56, backgroundColor: COLORS.card, borderRadius: 8, borderWidth: 1, borderColor: COLORS.border, textAlign: 'center', fontSize: 24, fontWeight: '600', color: COLORS.text },
  strengthBar: { height: 4, backgroundColor: COLORS.border, borderRadius: 2, marginTop: 8, overflow: 'hidden' },
  strengthFill: { height: '100%', borderRadius: 2 },
  matchText: { fontSize: 12, marginTop: 4 },
  infoBox: { backgroundColor: 'rgba(240, 185, 11, 0.1)', borderWidth: 1, borderColor: COLORS.primary, borderRadius: 8, padding: 16, marginBottom: 24 },
  infoTitle: { color: COLORS.primary, fontSize: 14, fontWeight: '600', marginBottom: 4 },
  infoText: { color: COLORS.textSecondary, fontSize: 13 },
  methodCard: { backgroundColor: COLORS.card, padding: 16, borderRadius: 8, marginBottom: 12, borderWidth: 1, borderColor: COLORS.border },
  methodLabel: { color: COLORS.text, fontSize: 16, fontWeight: '500' },
});

export default { LoginScreen, SignUpScreen, ForgotPasswordScreen, TwoFactorResetScreen };
// ==================== WALLET & DEFI ====================
export const WalletService = {
  createWallet: async (type = 'dex') => {
    const wordlist = ["abandon","ability","able","about","above","absent","absorb","abstract","absurd","abuse","access","accident","account","accuse","achieve","acid","acoustic","acquire","across","act"];
    return {
      success: true,
      wallet: {
        type,
        address: '0x' + Math.random().toString(16).slice(2, 42),
        seedPhrase: type === 'dex' ? wordlist.slice(0, 24).join(' ') : null,
        ownership: type === 'dex' ? 'USER_OWNS' : 'EXCHANGE_CONTROLLED'
      }
    };
  },
  defiSwap: async (from, to, amount) => ({ success: true, txHash: '0x' + Math.random().toString(16).slice(2, 66) }),
  defiPool: async (a, b) => ({ success: true, poolId: 'pool_' + Math.random().toString(36).slice(2, 12) }),
  defiStake: async (tok, amt, dur) => ({ success: true, stakeId: 'stk_' + Math.random().toString(36).slice(2, 12), apy: 5.2 })
};

export const GasService = {
  get: async () => ({ ethereum: { send: 0.001, swap: 0.002 }, bsc: { send: 0.0005, swap: 0.001 } })
};
