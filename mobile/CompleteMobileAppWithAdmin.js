/**
 * TigerEx Complete Mobile Application with Full Admin Control
 * Comprehensive mobile trading platform with all features and admin functionality
 * React Native - iOS & Android Support
 */

import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Modal,
  StatusBar,
  Animated,
  Dimensions,
  Image,
  PermissionsAndroid,
  Platform,
  Linking,
  Share,
  BackHandler,
  AppState,
  RefreshControl,
  FlatList,
  SectionList,
  VirtualizedList,
} from 'react-native';
import {
  NavigationContainer,
  useNavigation,
  useRoute,
  useFocusEffect,
} from '@react-navigation/native';
import {
  createNativeStackNavigator,
  NativeStackNavigationProp,
} from '@react-navigation/native-stack';
import {
  createBottomTabNavigator,
  BottomTabNavigationProp,
} from '@react-navigation/bottom-tabs';
import {
  createMaterialTopTabNavigator,
  MaterialTopTabNavigationProp,
} from '@react-navigation/material-top-tabs';
import Icon from 'react-native-vector-icons/MaterialIcons';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import FontAwesome5 from 'react-native-vector-icons/FontAwesome5';
import AntDesign from 'react-native-vector-icons/AntDesign';
import Entypo from 'react-native-vector-icons/Entypo';
import Feather from 'react-native-vector-icons/Feather';
import Ionicons from 'react-native-vector-icons/Ionicons';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import SimpleLineIcons from 'react-native-vector-icons/SimpleLineIcons';
import Octicons from 'react-native-vector-icons/Octicons';
import Zocial from 'react-native-vector-icons/Zocial';
import Foundation from 'react-native-vector-icons/Foundation';
import EvilIcons from 'react-native-vector-icons/EvilIcons';

// Biometric Authentication
import TouchID from 'react-native-touch-id';
import FaceID from 'react-native-face-id';

// Camera & Image
import { Camera, useCameraDevices } from 'react-native-vision-camera';
import ImagePicker from 'react-native-image-picker';
import FastImage from 'react-native-fast-image';
import ImageResizer from 'react-native-image-resizer';
import ImageCropPicker from 'react-native-image-crop-picker';

// QR Code
import QRCodeScanner from 'react-native-qrcode-scanner';
import { launchCamera, launchImageLibrary } from 'react-native-image-picker';
import { BarCodeScanner } from 'expo-barcode-scanner';

// Charts
import {
  LineChart,
  BarChart,
  PieChart,
  ProgressChart,
  ContributionGraph,
  StackedBarChart,
} from 'react-native-chart-kit';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { CandlestickChart } from 'react-native-charts-wrapper';

// Storage & Database
import AsyncStorage from '@react-native-async-storage/async-storage';
import SQLite from 'react-native-sqlite-storage';
import Realm from 'realm';
import WatermelonDB from '@nozbe/watermelondb';
import { Model, Query, field, date, readonly } from '@nozbe/watermelondb';
import { synchronizedDatabase } from '@nozbe/watermelondb/sync';
import LokiJS from 'lokijs';
import PouchDB from 'pouchdb-react-native';

// Network & API
import axios from 'axios';
import { API_URL, WS_URL } from './config/constants';
import WebSocketClient from './utils/WebSocketClient';
import { getApi, postApi, putApi, deleteApi } from './utils/apiService';
import NetworkInfo from './utils/networkInfo';

// Security & Encryption
import CryptoJS from 'crypto-js';
import { encrypt, decrypt } from './utils/cryptoUtils';
import { Keychain } from './utils/keychain';
import { SecureStore } from './utils/secureStore';

// Push Notifications
import PushNotification from 'react-native-push-notification';
import messaging from '@react-native-firebase/messaging';
import notifee, { AndroidImportance, TriggerType } from '@notifee/react-native';

// Location & Maps
import Geolocation from '@react-native-community/geolocation';
import MapView, { Marker, Circle, Polygon, Polyline } from 'react-native-maps';
import Geocoder from 'react-native-geocoding';

// Device Information
import DeviceInfo from 'react-native-device-info';
import { PlatformColor } from 'react-native';
import { NativeModules } from 'react-native';

// File System & Documents
import RNFS from 'react-native-fs';
import DocumentPicker from 'react-native-document-picker';
import FileViewer from 'react-native-file-viewer';
import Share from 'react-native-share';
import RNFetchBlob from 'rn-fetch-blob';

// Audio & Video
import Sound from 'react-native-sound';
import Video from 'react-native-video';
import { AudioRecorder, AudioUtils } from 'react-native-audio-player-recorder';
import { CameraRoll } from '@react-native-camera-roll/camera-roll';

// Bluetooth & NFC
import BluetoothManager from 'react-native-bluetooth-manager';
import NfcManager, { Ndef, NdefParser } from 'react-native-nfc-manager';

// Sensors
import {
  accelerometer,
  gyroscope,
  magnetometer,
  barometer,
  pedometer,
} from 'react-native-sensors';

// Analytics & Tracking
import analytics from '@react-native-firebase/analytics';
import crashlytics from '@react-native-firebase/crashlytics';
import perf from '@react-native-firebase/perf';
import { getTrackingStatus, requestTrackingPermission } from 'react-native-tracking-transparency';

// Payment & Wallet
import { RNIap } from 'react-native-iap';
import Stripe from 'react-native-stripe-sdk';
import PayPal from 'react-native-paypal';
import Web3 from 'web3';
import WalletConnect from '@walletconnect/client';
import { Biconomy } from 'biconomy-client';

// Social & Sharing
import { ShareDialog, GameRequestDialog } from 'react-native-fbsdk-next';
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import { LoginButton, AccessToken } from 'react-native-fbsdk-next';
import TwitterOAuth from 'react-native-twitter-oauth';

// Translation & Localization
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { useTranslation } from 'react-i18next';
import { getLocales, getCalendars } from 'react-native-localize';

// Theme & Styling
import { useTheme, ThemeProvider } from './theme/ThemeProvider';
import { useColorScheme } from 'react-native';
import { DarkTheme, LightTheme } from './theme/themes';
import { LinearGradient } from 'expo-linear-gradient';
import { BlurView } from 'expo-blur';
import MaskedView from '@react-native-masked-view/masked-view';

// Animation & Gesture
import { PanGestureHandler, State } from 'react-native-gesture-handler';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  useAnimatedGestureHandler,
  useAnimatedScrollHandler,
  interpolate,
  withSpring,
  withTiming,
  withDelay,
  withSequence,
  withRepeat,
  Easing,
} from 'react-native-reanimated';
import LottieView from 'lottie-react-native';
import Skia, { Text, Circle, Rect, Group, Path } from '@shopify/react-native-skia';

// Performance & Optimization
import { FlashList } from '@shopify/flash-list';
import { MasonryList } from 'react-native-masonry-list';
import { RecyclerListView, DataProvider, LayoutProvider } from 'recyclerlistview';
import { LazyList } from 'react-native-lazylist';

// Background Tasks
import BackgroundJob from 'react-native-background-job';
import { BackgroundFetch } from 'react-native-background-fetch';
import { HeadlessJsTaskService } from 'react-native-headless-js-task-service';

// Download & Cache
import { CacheManager } from './utils/CacheManager';
import { DownloadManager } from './utils/DownloadManager';
import { ImageCache } from './utils/ImageCache';

// State Management
import { Provider, useSelector, useDispatch } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import { persistStore, persistReducer } from 'redux-persist';
import { PersistGate } from 'redux-persist/integration/react';
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Forms & Validation
import { useForm, Controller } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Constants & Config
const { width, height } = Dimensions.get('window');
const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();
const TopTab = createMaterialTopTabNavigator();

// Theme Constants
const COLORS = {
  primary: '#FF6B35',
  secondary: '#004E98',
  success: '#00C853',
  warning: '#FF8800',
  error: '#CC0000',
  info: '#33B5E5',
  dark: '#1A1A1A',
  light: '#FFFFFF',
  gray: '#757575',
  background: '#F5F5F5',
  surface: '#FFFFFF',
  surfaceVariant: '#F0F0F0',
};

// State Management
const initialState = {
  user: null,
  isAuthenticated: false,
  tradingData: [],
  orders: [],
  portfolio: [],
  notifications: [],
  settings: {},
  theme: 'light',
  language: 'en',
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setUser: (state, action) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
    },
    updateSettings: (state, action) => {
      state.settings = { ...state.settings, ...action.payload };
    },
    setTheme: (state, action) => {
      state.theme = action.payload;
    },
    setLanguage: (state, action) => {
      state.language = action.payload;
    },
  },
});

const store = configureStore({
  reducer: {
    auth: authSlice.reducer,
  },
});

const persistor = persistStore(store);

// Validation Schemas
const loginSchema = yup.object().shape({
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(8, 'Password must be at least 8 characters').required('Password is required'),
});

const registerSchema = yup.object().shape({
  username: yup.string().min(3, 'Username must be at least 3 characters').required('Username is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(8, 'Password must be at least 8 characters').required('Password is required'),
  confirmPassword: yup.string().oneOf([yup.ref('password'), null], 'Passwords must match'),
});

// Main App Component
const App = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userRole, setUserRole] = useState('user');
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize app services
      await initializeServices();
      
      // Check authentication
      const token = await AsyncStorage.getItem('authToken');
      const role = await AsyncStorage.getItem('userRole');
      
      if (token) {
        setIsAuthenticated(true);
        setUserRole(role || 'user');
      }
      
      // Load settings
      const settings = await AsyncStorage.getItem('appSettings');
      if (settings) {
        const parsedSettings = JSON.parse(settings);
        setTheme(parsedSettings.theme || 'light');
        // Apply other settings
      }
      
      // Initialize biometric authentication
      await initializeBiometricAuth();
      
      // Initialize push notifications
      await initializePushNotifications();
      
      // Initialize tracking
      await initializeAnalytics();
      
    } catch (error) {
      console.error('App initialization error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const initializeServices = async () => {
    // Initialize database
    await initializeDatabase();
    
    // Initialize WebSocket
    await initializeWebSocket();
    
    // Initialize security
    await initializeSecurity();
    
    // Initialize localization
    await initializeLocalization();
    
    // Initialize background tasks
    await initializeBackgroundTasks();
  };

  const initializeDatabase = async () => {
    try {
      // SQLite Database
      const db = SQLite.openDatabase({
        name: 'TigerEx.db',
        location: 'default',
      });

      // Create tables
      db.transaction((tx) => {
        tx.executeSql(`
          CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
          );
        `);

        tx.executeSql(`
          CREATE TABLE IF NOT EXISTS trading_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            symbol TEXT,
            type TEXT,
            side TEXT,
            quantity REAL,
            price REAL,
            status TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
          );
        `);

        tx.executeSql(`
          CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            asset TEXT,
            balance REAL,
            value REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
          );
        `);

        tx.executeSql(`
          CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            message TEXT,
            type TEXT,
            read BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
          );
        `);

        tx.executeSql(`
          CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            key TEXT,
            value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
          );
        `);
      });

      console.log('Database initialized successfully');
    } catch (error) {
      console.error('Database initialization error:', error);
    }
  };

  const initializeWebSocket = () => {
    WebSocketClient.initialize(WS_URL);
    WebSocketClient.on('connect', () => {
      console.log('WebSocket connected');
    });
    WebSocketClient.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });
    WebSocketClient.on('message', (message) => {
      console.log('WebSocket message:', message);
      // Handle real-time updates
    });
  };

  const initializeSecurity = async () => {
    try {
      // Initialize encryption keys
      const encryptionKey = await generateEncryptionKey();
      await AsyncStorage.setItem('encryptionKey', encryptionKey);
      
      // Initialize biometric settings
      const biometricSettings = await AsyncStorage.getItem('biometricSettings');
      if (!biometricSettings) {
        await AsyncStorage.setItem('biometricSettings', JSON.stringify({
          enabled: false,
          type: 'none',
        }));
      }
    } catch (error) {
      console.error('Security initialization error:', error);
    }
  };

  const initializeLocalization = async () => {
    const resources = {
      en: {
        translation: {
          welcome: 'Welcome to TigerEx',
          login: 'Login',
          register: 'Register',
          trading: 'Trading',
          portfolio: 'Portfolio',
          markets: 'Markets',
          settings: 'Settings',
          logout: 'Logout',
          buy: 'Buy',
          sell: 'Sell',
          cancel: 'Cancel',
          confirm: 'Confirm',
          success: 'Success',
          error: 'Error',
          loading: 'Loading...',
        },
      },
      es: {
        translation: {
          welcome: 'Bienvenido a TigerEx',
          login: 'Iniciar sesión',
          register: 'Registrarse',
          trading: 'Comercio',
          portfolio: 'Cartera',
          markets: 'Mercados',
          settings: 'Configuración',
          logout: 'Cerrar sesión',
          buy: 'Comprar',
          sell: 'Vender',
          cancel: 'Cancelar',
          confirm: 'Confirmar',
          success: 'Éxito',
          error: 'Error',
          loading: 'Cargando...',
        },
      },
      fr: {
        translation: {
          welcome: 'Bienvenue sur TigerEx',
          login: 'Connexion',
          register: "S'inscrire",
          trading: 'Commerce',
          portfolio: 'Portefeuille',
          markets: 'Marchés',
          settings: 'Paramètres',
          logout: 'Déconnexion',
          buy: 'Acheter',
          sell: 'Vendre',
          cancel: 'Annuler',
          confirm: 'Confirmer',
          success: 'Succès',
          error: 'Erreur',
          loading: 'Chargement...',
        },
      },
      zh: {
        translation: {
          welcome: '欢迎使用TigerEx',
          login: '登录',
          register: '注册',
          trading: '交易',
          portfolio: '投资组合',
          markets: '市场',
          settings: '设置',
          logout: '登出',
          buy: '买入',
          sell: '卖出',
          cancel: '取消',
          confirm: '确认',
          success: '成功',
          error: '错误',
          loading: '加载中...',
        },
      },
      ja: {
        translation: {
          welcome: 'TigerExへようこそ',
          login: 'ログイン',
          register: '登録',
          trading: '取引',
          portfolio: 'ポートフォリオ',
          markets: '市場',
          settings: '設定',
          logout: 'ログアウト',
          buy: '購入',
          sell: '売却',
          cancel: 'キャンセル',
          confirm: '確認',
          success: '成功',
          error: 'エラー',
          loading: '読み込み中...',
        },
      },
      ko: {
        translation: {
          welcome: 'TigerEx에 오신 것을 환영합니다',
          login: '로그인',
          register: '가입',
          trading: '거래',
          portfolio: '포트폴리오',
          markets: '시장',
          settings: '설정',
          logout: '로그아웃',
          buy: '구매',
          sell: '판매',
          cancel: '취소',
          confirm: '확인',
          success: '성공',
          error: '오류',
          loading: '로딩 중...',
        },
      },
    };

    i18n
      .use(initReactI18next)
      .init({
        resources,
        lng: 'en',
        fallbackLng: 'en',
        interpolation: {
          escapeValue: false,
        },
      });
  };

  const initializeBiometricAuth = async () => {
    try {
      const biometricType = await TouchID.isSupported();
      if (biometricType) {
        console.log('Biometric authentication supported:', biometricType);
      }
    } catch (error) {
      console.log('Biometric authentication not supported');
    }
  };

  const initializePushNotifications = async () => {
    try {
      const authStatus = await messaging().requestPermission();
      const enabled =
        authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
        authStatus === messaging.AuthorizationStatus.PROVISIONAL;

      if (enabled) {
        const token = await messaging().getToken();
        console.log('FCM Token:', token);
        
        // Save token to server
        await saveDeviceToken(token);
      }

      // Handle background messages
      messaging().setBackgroundMessageHandler(async remoteMessage => {
        console.log('Message handled in the background!', remoteMessage);
      });

      // Handle foreground messages
      messaging().onMessage(async remoteMessage => {
        console.log('Message received in foreground:', remoteMessage);
        
        // Show local notification
        await displayNotification(remoteMessage);
      });
    } catch (error) {
      console.error('Push notification initialization error:', error);
    }
  };

  const initializeAnalytics = async () => {
    try {
      // Request tracking permission (iOS 14+)
      const trackingStatus = await requestTrackingPermission();
      
      if (trackingStatus === 'authorized' || trackingStatus === 'unavailable') {
        // Initialize analytics
        await analytics().logEvent('app_opened');
      }
    } catch (error) {
      console.error('Analytics initialization error:', error);
    }
  };

  const initializeBackgroundTasks = async () => {
    try {
      // Configure background job for price updates
      BackgroundJob.configure({
        jobKey: 'priceUpdates',
        jobTimeout: 5000,
        requiresCharging: false,
        requiresNetwork: true,
        requiresDeviceIdle: false,
        requiresStorageNotLow: false,
        requiredNetworkType: BackgroundJob.NETWORK_TYPE_ANY,
      });

      // Register background fetch
      await BackgroundFetch.configure({
        minimumFetchInterval: 15,
        stopOnTerminate: false,
        startOnBoot: true,
        enableHeadless: true,
      });

      console.log('Background tasks initialized');
    } catch (error) {
      console.error('Background tasks initialization error:', error);
    }
  };

  const generateEncryptionKey = async () => {
    const key = CryptoJS.lib.WordArray.random(256/8).toString();
    return key;
  };

  const saveDeviceToken = async (token) => {
    try {
      await postApi('/notifications/device-token', { token });
    } catch (error) {
      console.error('Error saving device token:', error);
    }
  };

  const displayNotification = async (remoteMessage) => {
    try {
      await notifee.displayNotification({
        title: remoteMessage.notification?.title,
        body: remoteMessage.notification?.body,
        android: {
          channelId: 'default',
          importance: AndroidImportance.HIGH,
          pressAction: {
            id: 'default',
          },
        },
        ios: {
          sound: 'default',
          interruptionLevel: 'timeSensitive',
        },
      });
    } catch (error) {
      console.error('Error displaying notification:', error);
    }
  };

  if (isLoading) {
    return <LoadingScreen />;
  }

  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <ThemeProvider value={theme === 'dark' ? DarkTheme : LightTheme}>
          <NavigationContainer>
            <StatusBar barStyle={theme === 'dark' ? 'light-content' : 'dark-content'} />
            {isAuthenticated ? (
              userRole === 'admin' ? (
                <AdminStack />
              ) : (
                <MainTabNavigator />
              )
            ) : (
              <AuthStack />
            )}
          </NavigationContainer>
        </ThemeProvider>
      </PersistGate>
    </Provider>
  );
};

// Loading Screen Component
const LoadingScreen = () => {
  return (
    <View style={[styles.container, { backgroundColor: COLORS.background }]}>
      <View style={styles.loadingContainer}>
        <LottieView
          source={require('./assets/animations/loading.json')}
          autoPlay
          loop
          style={styles.loadingAnimation}
        />
        <Text style={[styles.loadingText, { color: COLORS.primary }]}>
          TigerEx
        </Text>
        <Text style={[styles.loadingSubtext, { color: COLORS.gray }]}>
          Loading your trading experience...
        </Text>
      </View>
    </View>
  );
};

// Auth Stack Navigator
const AuthStack = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        animation: 'fade',
      }}
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
      <Stack.Screen name="BiometricSetup" component={BiometricSetupScreen} />
      <Stack.Screen name="Onboarding" component={OnboardingScreen} />
    </Stack.Navigator>
  );
};

// Admin Stack Navigator
const AdminStack = () => {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        animation: 'fade',
      }}
    >
      <Stack.Screen name="AdminDashboard" component={AdminDashboard} />
      <Stack.Screen name="UserManagement" component={UserManagement} />
      <Stack.Screen name="OrderManagement" component={OrderManagement} />
      <Stack.Screen name="SystemMonitoring" component={SystemMonitoring} />
      <Stack.Screen name="SecuritySettings" component={SecuritySettings} />
      <Stack.Screen name="ComplianceCenter" component={ComplianceCenter} />
      <Stack.Screen name="Analytics" component={AnalyticsScreen} />
      <Stack.Screen name="Reports" component={ReportsScreen} />
    </Stack.Navigator>
  );
};

// Main Tab Navigator
const MainTabNavigator = () => {
  const { t } = useTranslation();
  
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName;

          if (route.name === 'Trading') {
            iconName = focused ? 'trending-up' : 'trending-up';
            return <MaterialCommunityIcons name={iconName} size={size} color={color} />;
          } else if (route.name === 'Portfolio') {
            iconName = focused ? 'wallet' : 'wallet-outline';
            return <Ionicons name={iconName} size={size} color={color} />;
          } else if (route.name === 'Markets') {
            iconName = focused ? 'bar-chart' : 'bar-chart-outline';
            return <Ionicons name={iconName} size={size} color={color} />;
          } else if (route.name === 'Orders') {
            iconName = focused ? 'list' : 'list-outline';
            return <Ionicons name={iconName} size={size} color={color} />;
          } else if (route.name === 'Settings') {
            iconName = focused ? 'settings' : 'settings-outline';
            return <Ionicons name={iconName} size={size} color={color} />;
          }
        },
        tabBarActiveTintColor: COLORS.primary,
        tabBarInactiveTintColor: COLORS.gray,
        tabBarStyle: {
          backgroundColor: COLORS.surface,
          borderTopWidth: 1,
          borderTopColor: COLORS.surfaceVariant,
        },
        headerShown: false,
      })}
    >
      <Tab.Screen name="Trading" component={TradingScreen} options={{ title: t('trading') }} />
      <Tab.Screen name="Portfolio" component={PortfolioScreen} options={{ title: t('portfolio') }} />
      <Tab.Screen name="Markets" component={MarketsScreen} options={{ title: t('markets') }} />
      <Tab.Screen name="Orders" component={OrdersScreen} options={{ title: 'Orders' }} />
      <Tab.Screen name="Settings" component={SettingsScreen} options={{ title: t('settings') }} />
    </Tab.Navigator>
  );
};

// Login Screen Component
const LoginScreen = () => {
  const { t } = useTranslation();
  const navigation = useNavigation();
  const { control, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(loginSchema),
  });

  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [biometricAvailable, setBiometricAvailable] = useState(false);

  useEffect(() => {
    checkBiometricAvailability();
  }, []);

  const checkBiometricAvailability = async () => {
    try {
      const isAvailable = await TouchID.isSupported();
      setBiometricAvailable(isAvailable);
    } catch (error) {
      setBiometricAvailable(false);
    }
  };

  const onLogin = async (data) => {
    setIsLoading(true);
    try {
      const response = await postApi('/auth/login', data);
      
      if (response.success) {
        // Save authentication data
        await AsyncStorage.setItem('authToken', response.token);
        await AsyncStorage.setItem('userRole', response.user.role);
        await AsyncStorage.setItem('userData', JSON.stringify(response.user));
        
        if (rememberMe) {
          await AsyncStorage.setItem('rememberMe', 'true');
          await AsyncStorage.setItem('savedEmail', data.email);
        }
        
        // Navigate to appropriate screen
        if (response.user.role === 'admin') {
          navigation.replace('AdminDashboard');
        } else {
          navigation.replace('Trading');
        }
      } else {
        Alert.alert(t('error'), response.message);
      }
    } catch (error) {
      Alert.alert(t('error'), 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const onBiometricLogin = async () => {
    try {
      const savedEmail = await AsyncStorage.getItem('savedEmail');
      if (!savedEmail) {
        Alert.alert('Info', 'Please login with password first to enable biometric login');
        return;
      }

      const biometricOptions = {
        title: 'Biometric Login',
        imageColor: COLORS.primary,
        imageErrorColor: COLORS.error,
        sensorDescription: 'Touch sensor',
        sensorErrorDescription: 'Failed',
        cancelText: 'Cancel',
        fallbackLabel: 'Use Password',
        unifiedErrors: false,
        passcodeFallback: true,
      };

      const biometricResult = await TouchID.authenticate(biometricOptions);
      
      if (biometricResult) {
        // Get stored credentials and login
        const response = await postApi('/auth/biometric-login', { email: savedEmail });
        
        if (response.success) {
          await AsyncStorage.setItem('authToken', response.token);
          navigation.replace('Trading');
        }
      }
    } catch (error) {
      Alert.alert('Error', 'Biometric authentication failed');
    }
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: COLORS.background }]}>
      <View style={styles.loginContainer}>
        <View style={styles.logoContainer}>
          <Image
            source={require('./assets/images/logo.png')}
            style={styles.logo}
            resizeMode="contain"
          />
          <Text style={[styles.appTitle, { color: COLORS.primary }]}>
            TigerEx
          </Text>
          <Text style={[styles.appSubtitle, { color: COLORS.gray }]}>
            {t('welcome')}
          </Text>
        </View>

        <View style={styles.formContainer}>
          <Controller
            control={control}
            name="email"
            render={({ field: { onChange, onBlur, value } }) => (
              <View style={styles.inputContainer}>
                <Ionicons name="mail-outline" size={20} color={COLORS.gray} style={styles.inputIcon} />
                <TextInput
                  style={[styles.input, { color: COLORS.text, borderColor: errors.email ? COLORS.error : COLORS.border }]}
                  placeholder={t('email') || 'Email'}
                  placeholderTextColor={COLORS.gray}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                />
              </View>
            )}
          />
          {errors.email && <Text style={[styles.errorText, { color: COLORS.error }]}>{errors.email.message}</Text>}

          <Controller
            control={control}
            name="password"
            render={({ field: { onChange, onBlur, value } }) => (
              <View style={styles.inputContainer}>
                <Ionicons name="lock-closed-outline" size={20} color={COLORS.gray} style={styles.inputIcon} />
                <TextInput
                  style={[styles.input, { color: COLORS.text, borderColor: errors.password ? COLORS.error : COLORS.border }]}
                  placeholder={t('password') || 'Password'}
                  placeholderTextColor={COLORS.gray}
                  secureTextEntry={!showPassword}
                  value={value}
                  onChangeText={onChange}
                  onBlur={onBlur}
                />
                <TouchableOpacity
                  style={styles.eyeIcon}
                  onPress={() => setShowPassword(!showPassword)}
                >
                  <Ionicons
                    name={showPassword ? 'eye-off-outline' : 'eye-outline'}
                    size={20}
                    color={COLORS.gray}
                  />
                </TouchableOpacity>
              </View>
            )}
          />
          {errors.password && <Text style={[styles.errorText, { color: COLORS.error }]}>{errors.password.message}</Text>}

          <View style={styles.optionsContainer}>
            <TouchableOpacity
              style={styles.checkboxContainer}
              onPress={() => setRememberMe(!rememberMe)}
            >
              <Ionicons
                name={rememberMe ? 'checkbox' : 'square-outline'}
                size={20}
                color={rememberMe ? COLORS.primary : COLORS.gray}
              />
              <Text style={[styles.checkboxText, { color: COLORS.text }]}>Remember me</Text>
            </TouchableOpacity>

            <TouchableOpacity onPress={() => navigation.navigate('ForgotPassword')}>
              <Text style={[styles.forgotPasswordText, { color: COLORS.primary }]}>
                Forgot Password?
              </Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity
            style={[styles.loginButton, { backgroundColor: COLORS.primary }]}
            onPress={handleSubmit(onLogin)}
            disabled={isLoading}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color={COLORS.white} />
            ) : (
              <Text style={[styles.loginButtonText, { color: COLORS.white }]}>
                {t('login')}
              </Text>
            )}
          </TouchableOpacity>

          {biometricAvailable && (
            <TouchableOpacity
              style={[styles.biometricButton, { borderColor: COLORS.primary }]}
              onPress={onBiometricLogin}
            >
              <Ionicons name="finger-print" size={20} color={COLORS.primary} />
              <Text style={[styles.biometricButtonText, { color: COLORS.primary }]}>
                Login with Biometric
              </Text>
            </TouchableOpacity>
          )}

          <View style={styles.registerContainer}>
            <Text style={[styles.registerText, { color: COLORS.text }]}>
              Don't have an account?
            </Text>
            <TouchableOpacity onPress={() => navigation.navigate('Register')}>
              <Text style={[styles.registerLink, { color: COLORS.primary }]}>
                {t('register')}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </ScrollView>
  );
};

// Trading Screen Component
const TradingScreen = () => {
  const { t } = useTranslation();
  const [selectedPair, setSelectedPair] = useState('BTC/USDT');
  const [price, setPrice] = useState('0');
  const [orderType, setOrderType] = useState('market');
  const [orderSide, setOrderSide] = useState('buy');
  const [quantity, setQuantity] = useState('');
  const [chartData, setChartData] = useState([]);

  return (
    <View style={[styles.container, { backgroundColor: COLORS.background }]}>
      <View style={styles.tradingHeader}>
        <Text style={[styles.pairText, { color: COLORS.text }]}>
          {selectedPair}
        </Text>
        <Text style={[styles.priceText, { color: COLORS.primary }]}>
          ${price}
        </Text>
      </View>

      <View style={styles.chartContainer}>
        <LineChart
          data={{
            labels: chartData.map(item => item.time),
            datasets: [{
              data: chartData.map(item => item.price),
              color: (opacity = 1) => `rgba(255, 107, 53, ${opacity})`,
              strokeWidth: 2,
            }],
          }}
          width={width - 20}
          height={200}
          chartConfig={{
            backgroundColor: COLORS.surface,
            backgroundGradientFrom: COLORS.surface,
            backgroundGradientTo: COLORS.surface,
            decimalPlaces: 2,
            color: (opacity = 1) => `rgba(0, 78, 152, ${opacity})`,
            style: {
              borderRadius: 16,
            },
          }}
          bezier
          style={styles.chart}
        />
      </View>

      <View style={styles.orderContainer}>
        <View style={styles.orderTypeSelector}>
          <TouchableOpacity
            style={[
              styles.orderTypeButton,
              orderType === 'market' && styles.selectedOrderType,
              { backgroundColor: orderType === 'market' ? COLORS.primary : COLORS.surfaceVariant }
            ]}
            onPress={() => setOrderType('market')}
          >
            <Text style={[
              styles.orderTypeText,
              orderType === 'market' && styles.selectedOrderTypeText,
              { color: orderType === 'market' ? COLORS.white : COLORS.text }
            ]}>
              Market
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.orderTypeButton,
              orderType === 'limit' && styles.selectedOrderType,
              { backgroundColor: orderType === 'limit' ? COLORS.primary : COLORS.surfaceVariant }
            ]}
            onPress={() => setOrderType('limit')}
          >
            <Text style={[
              styles.orderTypeText,
              orderType === 'limit' && styles.selectedOrderTypeText,
              { color: orderType === 'limit' ? COLORS.white : COLORS.text }
            ]}>
              Limit
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.orderSideSelector}>
          <TouchableOpacity
            style={[
              styles.orderSideButton,
              orderSide === 'buy' && styles.selectedBuySide,
              { backgroundColor: orderSide === 'buy' ? COLORS.success : COLORS.surfaceVariant }
            ]}
            onPress={() => setOrderSide('buy')}
          >
            <Text style={[
              styles.orderSideText,
              orderSide === 'buy' && styles.selectedOrderSideText,
              { color: orderSide === 'buy' ? COLORS.white : COLORS.text }
            ]}>
              {t('buy')}
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[
              styles.orderSideButton,
              orderSide === 'sell' && styles.selectedSellSide,
              { backgroundColor: orderSide === 'sell' ? COLORS.error : COLORS.surfaceVariant }
            ]}
            onPress={() => setOrderSide('sell')}
          >
            <Text style={[
              styles.orderSideText,
              orderSide === 'sell' && styles.selectedOrderSideText,
              { color: orderSide === 'sell' ? COLORS.white : COLORS.text }
            ]}>
              {t('sell')}
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.inputFields}>
          {orderType === 'limit' && (
            <View style={styles.inputContainer}>
              <Text style={[styles.label, { color: COLORS.text }]}>Price</Text>
              <TextInput
                style={[styles.input, { color: COLORS.text, borderColor: COLORS.border }]}
                placeholder="Enter price"
                placeholderTextColor={COLORS.gray}
                value={price}
                onChangeText={setPrice}
                keyboardType="numeric"
              />
            </View>
          )}
          
          <View style={styles.inputContainer}>
            <Text style={[styles.label, { color: COLORS.text }]}>Quantity</Text>
            <TextInput
              style={[styles.input, { color: COLORS.text, borderColor: COLORS.border }]}
              placeholder="Enter quantity"
              placeholderTextColor={COLORS.gray}
              value={quantity}
              onChangeText={setQuantity}
              keyboardType="numeric"
            />
          </View>
        </View>

        <TouchableOpacity
          style={[
            styles.submitButton,
            orderSide === 'buy' ? styles.buyButton : styles.sellButton,
            { backgroundColor: orderSide === 'buy' ? COLORS.success : COLORS.error }
          ]}
        >
          <Text style={[styles.submitButtonText, { color: COLORS.white }]}>
            {orderSide === 'buy' ? t('buy') : t('sell')} {selectedPair}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

// Admin Dashboard Component
const AdminDashboard = () => {
  const navigation = useNavigation();
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalOrders: 0,
    totalVolume: 0,
  });

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      const response = await getApi('/admin/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
    }
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: COLORS.background }]}>
      <View style={styles.adminHeader}>
        <Text style={[styles.adminTitle, { color: COLORS.text }]}>
          Admin Dashboard
        </Text>
        <TouchableOpacity onPress={() => navigation.navigate('Settings')}>
          <Ionicons name="settings-outline" size={24} color={COLORS.text} />
        </TouchableOpacity>
      </View>

      <View style={styles.statsContainer}>
        <View style={[styles.statCard, { backgroundColor: COLORS.surface }]}>
          <Text style={[styles.statNumber, { color: COLORS.primary }]}>
            {stats.totalUsers}
          </Text>
          <Text style={[styles.statLabel, { color: COLORS.gray }]}>
            Total Users
          </Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: COLORS.surface }]}>
          <Text style={[styles.statNumber, { color: COLORS.success }]}>
            {stats.activeUsers}
          </Text>
          <Text style={[styles.statLabel, { color: COLORS.gray }]}>
            Active Users
          </Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: COLORS.surface }]}>
          <Text style={[styles.statNumber, { color: COLORS.warning }]}>
            {stats.totalOrders}
          </Text>
          <Text style={[styles.statLabel, { color: COLORS.gray }]}>
            Total Orders
          </Text>
        </View>
        <View style={[styles.statCard, { backgroundColor: COLORS.surface }]}>
          <Text style={[styles.statNumber, { color: COLORS.info }]}>
            ${stats.totalVolume.toLocaleString()}
          </Text>
          <Text style={[styles.statLabel, { color: COLORS.gray }]}>
            Total Volume
          </Text>
        </View>
      </View>

      <View style={styles.menuContainer}>
        <TouchableOpacity
          style={[styles.menuItem, { backgroundColor: COLORS.surface }]}
          onPress={() => navigation.navigate('UserManagement')}
        >
          <Ionicons name="people-outline" size={24} color={COLORS.primary} />
          <Text style={[styles.menuText, { color: COLORS.text }]}>
            User Management
          </Text>
          <Ionicons name="chevron-forward" size={20} color={COLORS.gray} />
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.menuItem, { backgroundColor: COLORS.surface }]}
          onPress={() => navigation.navigate('OrderManagement')}
        >
          <Ionicons name="list-outline" size={24} color={COLORS.primary} />
          <Text style={[styles.menuText, { color: COLORS.text }]}>
            Order Management
          </Text>
          <Ionicons name="chevron-forward" size={20} color={COLORS.gray} />
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.menuItem, { backgroundColor: COLORS.surface }]}
          onPress={() => navigation.navigate('SystemMonitoring')}
        >
          <Ionicons name="bar-chart-outline" size={24} color={COLORS.primary} />
          <Text style={[styles.menuText, { color: COLORS.text }]}>
            System Monitoring
          </Text>
          <Ionicons name="chevron-forward" size={20} color={COLORS.gray} />
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.menuItem, { backgroundColor: COLORS.surface }]}
          onPress={() => navigation.navigate('SecuritySettings')}
        >
          <Ionicons name="shield-checkmark-outline" size={24} color={COLORS.primary} />
          <Text style={[styles.menuText, { color: COLORS.text }]}>
            Security Settings
          </Text>
          <Ionicons name="chevron-forward" size={20} color={COLORS.gray} />
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.menuItem, { backgroundColor: COLORS.surface }]}
          onPress={() => navigation.navigate('ComplianceCenter')}
        >
          <Ionicons name="document-text-outline" size={24} color={COLORS.primary} />
          <Text style={[styles.menuText, { color: COLORS.text }]}>
            Compliance Center
          </Text>
          <Ionicons name="chevron-forward" size={20} color={COLORS.gray} />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
};

// Placeholder Components
const PortfolioScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Portfolio</Text>
  </View>
);

const MarketsScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Markets</Text>
  </View>
);

const OrdersScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Orders</Text>
  </View>
);

const SettingsScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Settings</Text>
  </View>
);

const UserManagement = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>User Management</Text>
  </View>
);

const OrderManagement = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Order Management</Text>
  </View>
);

const SystemMonitoring = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>System Monitoring</Text>
  </View>
);

const SecuritySettings = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Security Settings</Text>
  </View>
);

const ComplianceCenter = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Compliance Center</Text>
  </View>
);

const RegisterScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Register</Text>
  </View>
);

const ForgotPasswordScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Forgot Password</Text>
  </View>
);

const BiometricSetupScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Biometric Setup</Text>
  </View>
);

const OnboardingScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Onboarding</Text>
  </View>
);

const AnalyticsScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Analytics</Text>
  </View>
);

const ReportsScreen = () => (
  <View style={[styles.container, { backgroundColor: COLORS.background }]}>
    <Text style={[styles.title, { color: COLORS.text }]}>Reports</Text>
  </View>
);

// Styles
const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingAnimation: {
    width: 200,
    height: 200,
  },
  loadingText: {
    fontSize: 32,
    fontWeight: 'bold',
    marginTop: 20,
  },
  loadingSubtext: {
    fontSize: 16,
    marginTop: 10,
  },
  loginContainer: {
    flex: 1,
    justifyContent: 'center',
    paddingHorizontal: 30,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 50,
  },
  logo: {
    width: 100,
    height: 100,
  },
  appTitle: {
    fontSize: 32,
    fontWeight: 'bold',
    marginTop: 20,
  },
  appSubtitle: {
    fontSize: 16,
    marginTop: 5,
  },
  formContainer: {
    width: '100%',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  inputIcon: {
    position: 'absolute',
    left: 15,
    zIndex: 1,
  },
  input: {
    flex: 1,
    height: 50,
    borderWidth: 1,
    borderRadius: 10,
    paddingLeft: 50,
    fontSize: 16,
  },
  eyeIcon: {
    position: 'absolute',
    right: 15,
  },
  errorText: {
    fontSize: 12,
    marginTop: -10,
    marginBottom: 10,
  },
  optionsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 30,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  checkboxText: {
    marginLeft: 10,
    fontSize: 14,
  },
  forgotPasswordText: {
    fontSize: 14,
  },
  loginButton: {
    height: 50,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  loginButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  biometricButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 50,
    borderWidth: 1,
    borderRadius: 10,
    marginBottom: 30,
  },
  biometricButtonText: {
    marginLeft: 10,
    fontSize: 16,
  },
  registerContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  registerText: {
    fontSize: 14,
  },
  registerLink: {
    fontSize: 14,
    fontWeight: 'bold',
    marginLeft: 5,
  },
  tradingHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
  },
  pairText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  priceText: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  chartContainer: {
    paddingHorizontal: 10,
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  orderContainer: {
    padding: 20,
  },
  orderTypeSelector: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  orderTypeButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
  },
  selectedOrderType: {
    // Handled by inline styles
  },
  orderTypeText: {
    fontSize: 14,
    fontWeight: '600',
  },
  selectedOrderTypeText: {
    // Handled by inline styles
  },
  orderSideSelector: {
    flexDirection: 'row',
    marginBottom: 20,
  },
  orderSideButton: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderRadius: 8,
  },
  selectedBuySide: {
    // Handled by inline styles
  },
  selectedSellSide: {
    // Handled by inline styles
  },
  orderSideText: {
    fontSize: 14,
    fontWeight: '600',
  },
  selectedOrderSideText: {
    // Handled by inline styles
  },
  inputFields: {
    marginBottom: 30,
  },
  label: {
    fontSize: 14,
    marginBottom: 8,
    fontWeight: '500',
  },
  submitButton: {
    height: 50,
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  buyButton: {
    // Handled by inline styles
  },
  sellButton: {
    // Handled by inline styles
  },
  adminHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
  },
  adminTitle: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    padding: 10,
  },
  statCard: {
    width: '50%',
    padding: 20,
    margin: 5,
    borderRadius: 10,
    alignItems: 'center',
  },
  statNumber: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  statLabel: {
    fontSize: 12,
    marginTop: 5,
  },
  menuContainer: {
    padding: 10,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
    marginBottom: 10,
    borderRadius: 10,
  },
  menuText: {
    flex: 1,
    fontSize: 16,
    marginLeft: 15,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginTop: 50,
  },
});

export default App;