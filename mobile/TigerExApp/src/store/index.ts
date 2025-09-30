import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import marketReducer from './slices/marketSlice';
import portfolioReducer from './slices/portfolioSlice';
import walletReducer from './slices/walletSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    market: marketReducer,
    portfolio: portfolioReducer,
    wallet: walletReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;