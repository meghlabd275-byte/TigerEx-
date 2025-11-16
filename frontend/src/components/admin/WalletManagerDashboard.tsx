import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const WalletManagerDashboard = () => {
    const [wallets, setWallets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [transferData, setTransferData] = useState({ from: '', to: '', amount: '', currency: '' });

    useEffect(() => {
        fetchWallets();
    }, []);

    const fetchWallets = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/wallets');
            setWallets(response.data);
            setLoading(false);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch wallets');
            setLoading(false);
        }
    };

    const handleCreateWallet = async (blockchain, walletType) => {
        try {
            await api.post(`/admin/wallets?blockchain=${blockchain}&wallet_type=${walletType}`);
            fetchWallets();
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create wallet');
        }
    };

    const handleTransfer = async (e) => {
        e.preventDefault();
        try {
            await api.post('/admin/wallets/transfer', null, {
                params: {
                    from_wallet_id: transferData.from,
                    to_wallet_id: transferData.to,
                    amount: transferData.amount,
                    currency: transferData.currency,
                }
            });
            fetchWallets();
            setTransferData({ from: '', to: '', amount: '', currency: '' });
        } catch (err) {
            setError(err.response?.data?.detail || 'Transfer failed');
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="wallet-manager-dashboard">
            <h2>Wallet Management</h2>
            <div>
                <h3>Create Wallet</h3>
                <button onClick={() => handleCreateWallet('ethereum', 'hot')}>Create Ethereum Hot Wallet</button>
                <button onClick={() => handleCreateWallet('ethereum', 'cold')}>Create Ethereum Cold Wallet</button>
            </div>
            <div>
                <h3>Wallets</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Blockchain</th>
                            <th>Address</th>
                            <th>Type</th>
                            <th>Balance</th>
                        </tr>
                    </thead>
                    <tbody>
                        {wallets.map(wallet => (
                            <tr key={wallet.wallet_id}>
                                <td>{wallet.wallet_id}</td>
                                <td>{wallet.blockchain}</td>
                                <td>{wallet.address}</td>
                                <td>{wallet.wallet_type}</td>
                                <td>{wallet.balance}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div>
                <h3>Transfer Funds</h3>
                <form onSubmit={handleTransfer}>
                    <input type="text" value={transferData.from} onChange={e => setTransferData({...transferData, from: e.target.value})} placeholder="From Wallet ID" />
                    <input type="text" value={transferData.to} onChange={e => setTransferData({...transferData, to: e.target.value})} placeholder="To Wallet ID" />
                    <input type="number" value={transferData.amount} onChange={e => setTransferData({...transferData, amount: e.target.value})} placeholder="Amount" />
                    <input type="text" value={transferData.currency} onChange={e => setTransferData({...transferData, currency: e.target.value})} placeholder="Currency" />
                    <button type="submit">Transfer</button>
                </form>
            </div>
        </div>
    );
};

export default WalletManagerDashboard;
