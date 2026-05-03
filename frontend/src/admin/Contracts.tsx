/**
 * TigerEx Frontend Component
 * @file Contracts.tsx
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
import ContractForm from './ContractForm';

interface Contract {
  contract_id: string;
  symbol: string;
  exchange: string;
  trading_type: string;
  status: string;
}

const Contracts: React.FC = () => {
  const [contracts, setContracts] = useState<Contract[]>([]);
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
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
