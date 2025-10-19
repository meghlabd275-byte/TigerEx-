
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
import ContractForm from './ContractForm';

const Contracts: React.FC = () => {
  const [contracts, setContracts] = useState([]);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedContract, setSelectedContract] = useState(null);

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

  const fetchContracts = async () => {
    try {
      const response = await axios.get('/api/admin/contracts');
      setContracts(response.data.contracts);
    } catch (error) {
      console.error('Error fetching contracts:', error);
    }
  };

  useEffect(() => {
    fetchContracts();
  }, []);

  const handleFormOpen = (contract: any = null) => {
    setSelectedContract(contract);
    setIsFormOpen(true);
  };

  const handleFormClose = () => {
    setSelectedContract(null);
    setIsFormOpen(false);
  };

  const handleContractSaved = () => {
    fetchContracts();
  };

  const handleDeleteContract = async (contractId: string) => {
    try {
      await axios.delete(`/api/admin/contracts/${contractId}`);
      fetchContracts();
    } catch (error) {
      console.error('Error deleting contract:', error);
    }
  };

  return (
    <ThemeProvider theme={theme}>
        <Container maxWidth="xl">
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h4" gutterBottom>
                    Trading Contracts
                </Typography>
                <Button variant="contained" color="primary" onClick={() => handleFormOpen()}>
                    Create Contract
                </Button>
            </Box>
            <Paper>
                <List>
                    {contracts.map((contract) => (
                        <ListItem key={contract.contract_id}>
                            <ListItemText 
                                primary={contract.symbol} 
                                secondary={`${contract.exchange} - ${contract.trading_type}`} 
                            />
                            <Chip label={contract.status} />
                            <IconButton onClick={() => handleFormOpen(contract)}>
                                <Edit />
                            </IconButton>
                            <IconButton onClick={() => handleDeleteContract(contract.contract_id)}>
                                <Delete />
                            </IconButton>
                        </ListItem>
                    ))}
                </List>
            </Paper>
            <ContractForm 
                open={isFormOpen} 
                onClose={handleFormClose} 
                onContractCreated={handleContractSaved} 
                contract={selectedContract}
            />
        </Container>
    </ThemeProvider>
  );
};

export default Contracts;
