import React, { createContext, useContext, useState, useEffect } from 'react';

interface Wallet {
  address: string;
  type: 'imported' | 'created';
  seedPhrase?: string;
  privateKey?: string;
}

interface WalletContextType {
  wallet: Wallet | null;
  isConnected: boolean;
  exchangeMode: 'cex' | 'dex';
  connectWallet: (wallet: Wallet) => void;
  disconnectWallet: () => void;
  switchExchangeMode: (mode: 'cex' | 'dex') => void;
  createWallet: () => Promise<Wallet>;
  importWallet: (seedPhrase: string) => Promise<Wallet>;
}

const WalletContext = createContext<WalletContextType | undefined>(undefined);

export const useWallet = () => {
  const context = useContext(WalletContext);
  if (!context) {
    throw new Error('useWallet must be used within a WalletProvider');
  }
  return context;
};

export const WalletProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [exchangeMode, setExchangeMode] = useState<'cex' | 'dex'>('cex');

  useEffect(() => {
    // Load wallet from localStorage
    const savedWallet = localStorage.getItem('tigerex_wallet');
    if (savedWallet) {
      setWallet(JSON.parse(savedWallet));
    }

    // Load exchange mode from localStorage
    const savedMode = localStorage.getItem('tigerex_exchange_mode');
    if (savedMode) {
      setExchangeMode(savedMode as 'cex' | 'dex');
    }
  }, []);

  const generateSeedPhrase = (): string => {
    // Simple seed phrase generation (in production, use proper BIP39)
    const words = [
      'abandon', 'ability', 'able', 'about', 'above', 'absent', 'absorb', 'abstract',
      'absurd', 'abuse', 'access', 'accident', 'account', 'accuse', 'achieve', 'acid',
      'acoustic', 'acquire', 'across', 'act', 'action', 'actor', 'actress', 'actual',
    ];
    
    const seedPhrase: string[] = [];
    for (let i = 0; i < 12; i++) {
      const randomIndex = Math.floor(Math.random() * words.length);
      seedPhrase.push(words[randomIndex]);
    }
    
    return seedPhrase.join(' ');
  };

  const generateAddress = (): string => {
    // Generate a mock Ethereum-style address
    const chars = '0123456789abcdef';
    let address = '0x';
    for (let i = 0; i < 40; i++) {
      address += chars[Math.floor(Math.random() * chars.length)];
    }
    return address;
  };

  const createWallet = async (): Promise<Wallet> => {
    const seedPhrase = generateSeedPhrase();
    const address = generateAddress();
    
    const newWallet: Wallet = {
      address,
      type: 'created',
      seedPhrase,
    };

    return newWallet;
  };

  const importWallet = async (seedPhrase: string): Promise<Wallet> => {
    // Validate seed phrase (basic validation)
    const words = seedPhrase.trim().split(' ');
    if (words.length !== 12 && words.length !== 24) {
      throw new Error('Invalid seed phrase. Must be 12 or 24 words.');
    }

    const address = generateAddress();
    
    const importedWallet: Wallet = {
      address,
      type: 'imported',
      seedPhrase,
    };

    return importedWallet;
  };

  const connectWallet = (newWallet: Wallet) => {
    setWallet(newWallet);
    localStorage.setItem('tigerex_wallet', JSON.stringify(newWallet));
    
    // Automatically switch to DEX mode when wallet is connected
    setExchangeMode('dex');
    localStorage.setItem('tigerex_exchange_mode', 'dex');
  };

  const disconnectWallet = () => {
    setWallet(null);
    localStorage.removeItem('tigerex_wallet');
    
    // Switch back to CEX mode when wallet is disconnected
    setExchangeMode('cex');
    localStorage.setItem('tigerex_exchange_mode', 'cex');
  };

  const switchExchangeMode = (mode: 'cex' | 'dex') => {
    if (mode === 'dex' && !wallet) {
      throw new Error('Please connect a wallet to use DEX mode');
    }
    setExchangeMode(mode);
    localStorage.setItem('tigerex_exchange_mode', mode);
  };

  return (
    <WalletContext.Provider
      value={{
        wallet,
        isConnected: !!wallet,
        exchangeMode,
        connectWallet,
        disconnectWallet,
        switchExchangeMode,
        createWallet,
        importWallet,
      }}
    >
      {children}
    </WalletContext.Provider>
  );
};