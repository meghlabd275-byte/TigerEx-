/*
 * TigerEx Exchange Platform
 * Version: 7.0.0 - Consolidated Production Release
 * 
 * Complete cryptocurrency exchange platform with:
 * - CEX/DEX hybrid functionality
 * - 105+ exchange features
 * - Multi-platform support (Web, Mobile, Desktop)
 * - Enterprise-grade security
 * - White-label deployment ready
 * 
 * Production-ready implementation
 */

import { configureStore } from '@reduxjs/toolkit';
import { authSlice } from './slices/authSlice';
import { tradingSlice } from './slices/tradingSlice';
import { marketSlice } from './slices/marketSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice.reducer,
    trading: tradingSlice.reducer,
    market: marketSlice.reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
