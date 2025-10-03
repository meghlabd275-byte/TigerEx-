import React, { useState } from 'react';
import { useWallet } from '../../contexts/WalletContext';
import { Copy, Eye, EyeOff, Check, AlertCircle, Wallet as WalletIcon, Download } from 'lucide-react';

const WalletSetup: React.FC = () => {
  const { createWallet, importWallet, connectWallet } = useWallet();
  const [mode, setMode] = useState<'choice' | 'create' | 'import'>('choice');
  const [step, setStep] = useState(1);
  const [seedPhrase, setSeedPhrase] = useState('');
  const [importSeedPhrase, setImportSeedPhrase] = useState('');
  const [confirmedWords, setConfirmedWords] = useState<{ [key: number]: string }>({});
  const [showSeedPhrase, setShowSeedPhrase] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');
  const [agreedToTerms, setAgreedToTerms] = useState(false);

  const handleCreateWallet = async () => {
    try {
      const wallet = await createWallet();
      setSeedPhrase(wallet.seedPhrase || '');
      setStep(2);
    } catch (err) {
      setError('Failed to create wallet. Please try again.');
    }
  };

  const handleImportWallet = async () => {
    try {
      setError('');
      const wallet = await importWallet(importSeedPhrase);
      connectWallet(wallet);
    } catch (err: any) {
      setError(err.message || 'Failed to import wallet. Please check your seed phrase.');
    }
  };

  const copySeedPhrase = () => {
    navigator.clipboard.writeText(seedPhrase);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const verifySeedPhrase = () => {
    const words = seedPhrase.split(' ');
    const randomIndices = [2, 5, 8]; // Verify 3rd, 6th, and 9th words
    
    let allCorrect = true;
    randomIndices.forEach(index => {
      if (confirmedWords[index] !== words[index]) {
        allCorrect = false;
      }
    });

    if (allCorrect) {
      const wallet = {
        address: '0x' + Math.random().toString(16).substr(2, 40),
        type: 'created' as const,
        seedPhrase,
      };
      connectWallet(wallet);
    } else {
      setError('Seed phrase verification failed. Please check the words.');
    }
  };

  if (mode === 'choice') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-yellow-400 rounded-full mb-4">
              <WalletIcon className="w-10 h-10 text-gray-900" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">Welcome to TigerEx</h1>
            <p className="text-gray-400">Create or import your wallet to get started</p>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => {
                setMode('create');
                setStep(1);
              }}
              className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold py-4 rounded-lg transition-colors flex items-center justify-center gap-3"
            >
              <WalletIcon className="w-5 h-5" />
              Create New Wallet
            </button>

            <button
              onClick={() => setMode('import')}
              className="w-full bg-gray-800 hover:bg-gray-700 text-white font-semibold py-4 rounded-lg transition-colors flex items-center justify-center gap-3"
            >
              <Download className="w-5 h-5" />
              Import Existing Wallet
            </button>
          </div>

          <div className="mt-8 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
            <div className="flex gap-3">
              <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-blue-300">
                <p className="font-semibold mb-1">Important:</p>
                <p>Your wallet gives you access to DEX trading. Keep your seed phrase safe and never share it with anyone.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (mode === 'create') {
    if (step === 1) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full">
            <button
              onClick={() => setMode('choice')}
              className="text-gray-400 hover:text-white mb-6 flex items-center gap-2"
            >
              ← Back
            </button>

            <div className="bg-gray-800 rounded-lg p-6 mb-6">
              <h2 className="text-2xl font-bold text-white mb-4">Create New Wallet</h2>
              
              <div className="space-y-4 mb-6">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center flex-shrink-0 text-gray-900 font-bold">
                    1
                  </div>
                  <div>
                    <h3 className="text-white font-semibold mb-1">Secure Your Wallet</h3>
                    <p className="text-gray-400 text-sm">You'll receive a 12-word seed phrase that you must keep safe.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0 text-white font-bold">
                    2
                  </div>
                  <div>
                    <h3 className="text-white font-semibold mb-1">Write It Down</h3>
                    <p className="text-gray-400 text-sm">Store your seed phrase in a safe place. Never share it with anyone.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center flex-shrink-0 text-white font-bold">
                    3
                  </div>
                  <div>
                    <h3 className="text-white font-semibold mb-1">Verify & Complete</h3>
                    <p className="text-gray-400 text-sm">Confirm your seed phrase to complete the setup.</p>
                  </div>
                </div>
              </div>

              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
                <div className="flex gap-3">
                  <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  <div className="text-sm text-red-300">
                    <p className="font-semibold mb-1">Warning:</p>
                    <p>If you lose your seed phrase, you will lose access to your wallet forever. TigerEx cannot recover it for you.</p>
                  </div>
                </div>
              </div>

              <label className="flex items-start gap-3 mb-6 cursor-pointer">
                <input
                  type="checkbox"
                  checked={agreedToTerms}
                  onChange={(e) => setAgreedToTerms(e.target.checked)}
                  className="mt-1"
                />
                <span className="text-sm text-gray-300">
                  I understand that I am responsible for keeping my seed phrase safe and that TigerEx cannot recover it if lost.
                </span>
              </label>

              <button
                onClick={handleCreateWallet}
                disabled={!agreedToTerms}
                className="w-full bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-700 disabled:text-gray-500 text-gray-900 font-semibold py-3 rounded-lg transition-colors"
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      );
    }

    if (step === 2) {
      const words = seedPhrase.split(' ');
      
      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
          <div className="max-w-2xl w-full">
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-2xl font-bold text-white mb-2">Your Seed Phrase</h2>
              <p className="text-gray-400 mb-6">Write down these 12 words in order and keep them safe.</p>

              <div className="bg-gray-900 rounded-lg p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <span className="text-sm text-gray-400">Click to {showSeedPhrase ? 'hide' : 'reveal'}</span>
                  <button
                    onClick={() => setShowSeedPhrase(!showSeedPhrase)}
                    className="text-yellow-400 hover:text-yellow-500"
                  >
                    {showSeedPhrase ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>

                {showSeedPhrase ? (
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    {words.map((word, index) => (
                      <div key={index} className="bg-gray-800 rounded p-3">
                        <span className="text-gray-500 text-xs">{index + 1}.</span>
                        <span className="text-white ml-2 font-mono">{word}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="grid grid-cols-3 gap-3 mb-4">
                    {words.map((_, index) => (
                      <div key={index} className="bg-gray-800 rounded p-3">
                        <span className="text-gray-500 text-xs">{index + 1}.</span>
                        <span className="text-gray-600 ml-2">••••••</span>
                      </div>
                    ))}
                  </div>
                )}

                <button
                  onClick={copySeedPhrase}
                  className="w-full bg-gray-800 hover:bg-gray-700 text-white py-2 rounded-lg flex items-center justify-center gap-2 transition-colors"
                >
                  {copied ? (
                    <>
                      <Check className="w-4 h-4" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-4 h-4" />
                      Copy to Clipboard
                    </>
                  )}
                </button>
              </div>

              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4 mb-6">
                <p className="text-sm text-yellow-300">
                  ⚠️ Never share your seed phrase with anyone. TigerEx will never ask for it.
                </p>
              </div>

              <button
                onClick={() => setStep(3)}
                className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold py-3 rounded-lg transition-colors"
              >
                I've Written It Down
              </button>
            </div>
          </div>
        </div>
      );
    }

    if (step === 3) {
      const words = seedPhrase.split(' ');
      const verifyIndices = [2, 5, 8]; // Verify 3rd, 6th, and 9th words

      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full">
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-2xl font-bold text-white mb-2">Verify Seed Phrase</h2>
              <p className="text-gray-400 mb-6">Enter the following words to verify you've saved your seed phrase correctly.</p>

              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
                  <p className="text-sm text-red-300">{error}</p>
                </div>
              )}

              <div className="space-y-4 mb-6">
                {verifyIndices.map((index) => (
                  <div key={index}>
                    <label className="block text-sm text-gray-400 mb-2">
                      Word #{index + 1}
                    </label>
                    <input
                      type="text"
                      value={confirmedWords[index] || ''}
                      onChange={(e) => setConfirmedWords({ ...confirmedWords, [index]: e.target.value.toLowerCase().trim() })}
                      className="w-full bg-gray-900 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-yellow-400"
                      placeholder="Enter word"
                    />
                  </div>
                ))}
              </div>

              <button
                onClick={verifySeedPhrase}
                className="w-full bg-yellow-400 hover:bg-yellow-500 text-gray-900 font-semibold py-3 rounded-lg transition-colors"
              >
                Verify & Complete
              </button>
            </div>
          </div>
        </div>
      );
    }
  }

  if (mode === 'import') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <button
            onClick={() => setMode('choice')}
            className="text-gray-400 hover:text-white mb-6 flex items-center gap-2"
          >
            ← Back
          </button>

          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-2xl font-bold text-white mb-2">Import Wallet</h2>
            <p className="text-gray-400 mb-6">Enter your 12 or 24 word seed phrase to import your wallet.</p>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
                <p className="text-sm text-red-300">{error}</p>
              </div>
            )}

            <div className="mb-6">
              <label className="block text-sm text-gray-400 mb-2">
                Seed Phrase
              </label>
              <textarea
                value={importSeedPhrase}
                onChange={(e) => setImportSeedPhrase(e.target.value)}
                rows={4}
                className="w-full bg-gray-900 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-yellow-400 font-mono text-sm"
                placeholder="Enter your seed phrase separated by spaces"
              />
              <p className="text-xs text-gray-500 mt-2">
                Separate each word with a space
              </p>
            </div>

            <button
              onClick={handleImportWallet}
              disabled={!importSeedPhrase.trim()}
              className="w-full bg-yellow-400 hover:bg-yellow-500 disabled:bg-gray-700 disabled:text-gray-500 text-gray-900 font-semibold py-3 rounded-lg transition-colors"
            >
              Import Wallet
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default WalletSetup;