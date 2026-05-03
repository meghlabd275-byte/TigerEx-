/**
 * TigerEx Frontend Component
 * @file Users.tsx
 * @description React component for TigerEx platform
 * @author TigerEx Development Team
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Button,
  Chip,
  ThemeProvider,
  createTheme,
  IconButton,
} from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';
import axios from 'axios';
import UserForm from './UserForm';

interface User {
  user_id: string;
  username: string;
  email: string;
  role: string;
  status: string;
}

const Users: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const theme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#1976d2',
      },
      secondary: {
        main: '#dc004e',
      },
      background: {
        default: '#121212',
        paper: '#1e1e1e',
      },
    },
  });

  const fetchUsers = async () => {
    try {
      const response = await axios.get('/api/admin/users');
      setUsers(response.data.users);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleFormOpen = (user: any = null) => {
    setSelectedUser(user);
    setIsFormOpen(true);
  };

  const handleFormClose = () => {
    setSelectedUser(null);
    setIsFormOpen(false);
  };

  const handleUserSaved = () => {
    fetchUsers();
  };

  const handleDeleteUser = async (userId: string) => {
    try {
      await axios.delete(`/api/admin/users/${userId}`);
      fetchUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
        <Container maxWidth="xl">
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h4" gutterBottom>
                    Users
                </Typography>
                <Button variant="contained" color="primary" onClick={() => handleFormOpen()}>
                    Create User
                </Button>
            </Box>
            <Paper>
                <List>
                    {users.map((user) => (
                        <ListItem key={user.user_id}>
                            <ListItemText 
                                primary={user.username} 
                                secondary={user.email} 
                            />
                            <Chip label={user.role} />
                            <Chip label={user.status} />
                            <IconButton onClick={() => handleFormOpen(user)}>
                                <Edit />
                            </IconButton>
                            <IconButton onClick={() => handleDeleteUser(user.user_id)}>
                                <Delete />
                            </IconButton>
                        </ListItem>
                    ))}
                </List>
            </Paper>
            <UserForm 
                open={isFormOpen} 
                onClose={handleFormClose} 
                onUserCreated={handleUserSaved} 
                user={selectedUser}
            />
        </Container>
    </ThemeProvider>
  );
};

export default Users;
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })

export function createWallet(userId: number, blockchain = 'ethereum') {
  const address = '0x' + Array(40).fill().map(() => Math.random().toString(16)[2]).join('');
  const words = 'abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork'; return { address, seedPhrase: words.split(' ').slice(0,24).join(' '), blockchain, ownership: 'USER_OWNS', userId }; }
