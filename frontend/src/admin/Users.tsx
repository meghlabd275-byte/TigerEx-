
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

const Users: React.FC = () => {
  const [users, setUsers] = useState([]);
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
