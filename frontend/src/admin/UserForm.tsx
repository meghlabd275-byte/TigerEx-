/**
 * TigerEx Frontend Component
 * @file UserForm.tsx
 * @description React component for TigerEx platform
 * @author TigerEx Development Team
 */

import React, { useState, useEffect } from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  MenuItem,
} from '@mui/material';
import axios from 'axios';

const UserForm: React.FC<{ 
    open: boolean; 
    onClose: () => void; 
    onUserCreated: () => void; 
    user?: any; 
}> = ({ open, onClose, onUserCreated, user }) => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    role: 'trader',
    status: 'pending',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        email: user.email,
        username: user.username,
        role: user.role,
        status: user.status,
      });
    } else {
        setFormData({
            email: '',
            username: '',
            role: 'trader',
            status: 'pending',
        });
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    try {
      if (user) {
        await axios.put(`/api/admin/users/${user.user_id}`, formData);
      } else {
        await axios.post('/api/admin/users/create', formData);
      }
      onUserCreated();
      onClose();
    } catch (error) {
      console.error('Error saving user:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{user ? 'Edit' : 'Create'} User</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          name="email"
          label="Email Address"
          type="email"
          fullWidth
          variant="standard"
          onChange={handleChange}
          value={formData.email}
        />
        <TextField
          margin="dense"
          name="username"
          label="Username"
          type="text"
          fullWidth
          variant="standard"
          onChange={handleChange}
          value={formData.username}
        />
        <TextField
          margin="dense"
          name="role"
          label="Role"
          type="text"
          fullWidth
          variant="standard"
          onChange={handleChange}
          value={formData.role}
          select
        >
            <MenuItem value="super_admin">Super Admin</MenuItem>
            <MenuItem value="admin">Admin</MenuItem>
            <MenuItem value="moderator">Moderator</MenuItem>
            <MenuItem value="trader">Trader</MenuItem>
            <MenuItem value="viewer">Viewer</MenuItem>
        </TextField>
        <TextField
            margin="dense"
            name="status"
            label="Status"
            type="text"
            fullWidth
            variant="standard"
            onChange={handleChange}
            value={formData.status}
            select
            >
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="active">Active</MenuItem>
            <MenuItem value="suspended">Suspended</MenuItem>
            <MenuItem value="banned">Banned</MenuItem>
        </TextField>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit}>{user ? 'Save' : 'Create'}</Button>
      </DialogActions>
    </Dialog>
  );
};

export default UserForm;
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
