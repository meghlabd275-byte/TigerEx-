import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

const RegisterScreen = ({ navigation }: any) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleRegister = async () => {
    // Validation
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.password) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      Alert.alert('Error', 'Password must be at least 8 characters');
      return;
    }

    if (!acceptTerms) {
      Alert.alert('Error', 'Please accept the terms and conditions');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('https://api.tigerex.com/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: formData.firstName,
          last_name: formData.lastName,
          email: formData.email,
          phone: formData.phone,
          password: formData.password,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        Alert.alert(
          'Success',
          'Account created successfully! Please verify your email.',
          [
            {
              text: 'OK',
              onPress: () => navigation.navigate('Login'),
            },
          ]
        );
      } else {
        Alert.alert('Error', data.message || 'Registration failed');
      }
    } catch (error) {
      Alert.alert('Error', 'Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        <ScrollView
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* Header */}
          <View style={styles.header}>
            <TouchableOpacity
              onPress={() => navigation.goBack()}
              style={styles.backButton}
            >
              <Icon name="arrow-left" size={24} color="#FFF" />
            </TouchableOpacity>
            <Text style={styles.title}>Create Account</Text>
            <Text style={styles.subtitle}>Join TigerEx today</Text>
          </View>

          {/* Form */}
          <View style={styles.formContainer}>
            {/* First Name */}
            <View style={styles.inputContainer}>
              <Icon name="account-outline" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="First Name"
                placeholderTextColor="#999"
                value={formData.firstName}
                onChangeText={(text) => setFormData({ ...formData, firstName: text })}
                autoCapitalize="words"
              />
            </View>

            {/* Last Name */}
            <View style={styles.inputContainer}>
              <Icon name="account-outline" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Last Name"
                placeholderTextColor="#999"
                value={formData.lastName}
                onChangeText={(text) => setFormData({ ...formData, lastName: text })}
                autoCapitalize="words"
              />
            </View>

            {/* Email */}
            <View style={styles.inputContainer}>
              <Icon name="email-outline" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Email"
                placeholderTextColor="#999"
                value={formData.email}
                onChangeText={(text) => setFormData({ ...formData, email: text })}
                keyboardType="email-address"
                autoCapitalize="none"
                autoComplete="email"
              />
            </View>

            {/* Phone */}
            <View style={styles.inputContainer}>
              <Icon name="phone-outline" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Phone Number (Optional)"
                placeholderTextColor="#999"
                value={formData.phone}
                onChangeText={(text) => setFormData({ ...formData, phone: text })}
                keyboardType="phone-pad"
              />
            </View>

            {/* Password */}
            <View style={styles.inputContainer}>
              <Icon name="lock-outline" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Password"
                placeholderTextColor="#999"
                value={formData.password}
                onChangeText={(text) => setFormData({ ...formData, password: text })}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
              />
              <TouchableOpacity
                onPress={() => setShowPassword(!showPassword)}
                style={styles.eyeIcon}
              >
                <Icon
                  name={showPassword ? 'eye-outline' : 'eye-off-outline'}
                  size={20}
                  color="#666"
                />
              </TouchableOpacity>
            </View>

            {/* Confirm Password */}
            <View style={styles.inputContainer}>
              <Icon name="lock-check-outline" size={20} color="#666" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="Confirm Password"
                placeholderTextColor="#999"
                value={formData.confirmPassword}
                onChangeText={(text) => setFormData({ ...formData, confirmPassword: text })}
                secureTextEntry={!showConfirmPassword}
                autoCapitalize="none"
              />
              <TouchableOpacity
                onPress={() => setShowConfirmPassword(!showConfirmPassword)}
                style={styles.eyeIcon}
              >
                <Icon
                  name={showConfirmPassword ? 'eye-outline' : 'eye-off-outline'}
                  size={20}
                  color="#666"
                />
              </TouchableOpacity>
            </View>

            {/* Password Requirements */}
            <View style={styles.requirementsContainer}>
              <Text style={styles.requirementsTitle}>Password must contain:</Text>
              <View style={styles.requirement}>
                <Icon
                  name={formData.password.length >= 8 ? 'check-circle' : 'circle-outline'}
                  size={16}
                  color={formData.password.length >= 8 ? '#4CAF50' : '#666'}
                />
                <Text style={styles.requirementText}>At least 8 characters</Text>
              </View>
              <View style={styles.requirement}>
                <Icon
                  name={/[A-Z]/.test(formData.password) ? 'check-circle' : 'circle-outline'}
                  size={16}
                  color={/[A-Z]/.test(formData.password) ? '#4CAF50' : '#666'}
                />
                <Text style={styles.requirementText}>One uppercase letter</Text>
              </View>
              <View style={styles.requirement}>
                <Icon
                  name={/[0-9]/.test(formData.password) ? 'check-circle' : 'circle-outline'}
                  size={16}
                  color={/[0-9]/.test(formData.password) ? '#4CAF50' : '#666'}
                />
                <Text style={styles.requirementText}>One number</Text>
              </View>
            </View>

            {/* Terms and Conditions */}
            <TouchableOpacity
              style={styles.checkboxContainer}
              onPress={() => setAcceptTerms(!acceptTerms)}
            >
              <Icon
                name={acceptTerms ? 'checkbox-marked' : 'checkbox-blank-outline'}
                size={24}
                color={acceptTerms ? '#FF6B00' : '#666'}
              />
              <Text style={styles.checkboxText}>
                I agree to the{' '}
                <Text style={styles.link}>Terms of Service</Text> and{' '}
                <Text style={styles.link}>Privacy Policy</Text>
              </Text>
            </TouchableOpacity>

            {/* Register Button */}
            <TouchableOpacity
              style={[styles.registerButton, loading && styles.registerButtonDisabled]}
              onPress={handleRegister}
              disabled={loading}
            >
              <Text style={styles.registerButtonText}>
                {loading ? 'Creating Account...' : 'Create Account'}
              </Text>
            </TouchableOpacity>

            {/* Login Link */}
            <View style={styles.loginContainer}>
              <Text style={styles.loginText}>Already have an account? </Text>
              <TouchableOpacity onPress={() => navigation.navigate('Login')}>
                <Text style={styles.loginLink}>Login</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0A0E27',
  },
  keyboardView: {
    flex: 1,
  },
  scrollContent: {
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  header: {
    marginTop: 20,
    marginBottom: 32,
  },
  backButton: {
    width: 40,
    height: 40,
    justifyContent: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#999',
  },
  formContainer: {
    flex: 1,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1A1F3A',
    borderRadius: 12,
    marginBottom: 16,
    paddingHorizontal: 16,
    height: 56,
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    color: '#FFF',
    fontSize: 16,
  },
  eyeIcon: {
    padding: 8,
  },
  requirementsContainer: {
    backgroundColor: '#1A1F3A',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  requirementsTitle: {
    color: '#FFF',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 12,
  },
  requirement: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  requirementText: {
    color: '#999',
    fontSize: 14,
    marginLeft: 8,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  checkboxText: {
    color: '#999',
    fontSize: 14,
    marginLeft: 12,
    flex: 1,
  },
  link: {
    color: '#FF6B00',
    textDecorationLine: 'underline',
  },
  registerButton: {
    backgroundColor: '#FF6B00',
    borderRadius: 12,
    height: 56,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16,
  },
  registerButtonDisabled: {
    opacity: 0.6,
  },
  registerButtonText: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loginContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginBottom: 24,
  },
  loginText: {
    color: '#999',
    fontSize: 14,
  },
  loginLink: {
    color: '#FF6B00',
    fontSize: 14,
    fontWeight: 'bold',
  },
});

export default RegisterScreen;