import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const UserManagementDashboard = () => {
    const [users, setUsers] = useState([]);
    const [selectedUser, setSelectedUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/users');
            setUsers(response.data);
            setLoading(false);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch users');
            setLoading(false);
        }
    };

    const fetchUserProfile = async (userId) => {
        try {
            const response = await api.get(`/admin/users/${userId}/profile`);
            setSelectedUser(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch user profile');
        }
    };

    const handleSuspendUser = async (userId) => {
        try {
            await api.put(`/admin/users/${userId}`, { status: 'suspended' });
            fetchUsers();
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to suspend user');
        }
    };

    if (loading) return <div>Loading...</div>;
    if (error) return <div className="error">{error}</div>;

    return (
        <div className="user-management-dashboard">
            <h2>User Management</h2>
            <div className="user-list">
                <h3>All Users</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(user => (
                            <tr key={user.id}>
                                <td>{user.id}</td>
                                <td>{user.username}</td>
                                <td>{user.email}</td>
                                <td>{user.status}</td>
                                <td>
                                    <button onClick={() => fetchUserProfile(user.id)}>View Profile</button>
                                    <button onClick={() => handleSuspendUser(user.id)}>Suspend</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            {selectedUser && (
                <div className="user-profile">
                    <h3>User Profile: {selectedUser.username}</h3>
                    <h4>Balances</h4>
                    <ul>
                        {selectedUser.balances.map(balance => (
                            <li key={balance.currency}>{balance.currency}: {balance.balance}</li>
                        ))}
                    </ul>
                    <h4>Order History</h4>
                    <ul>
                        {selectedUser.order_history.map(order => (
                            <li key={order.order_id}>{order.symbol}: {order.quantity} @ {order.price}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default UserManagementDashboard;
