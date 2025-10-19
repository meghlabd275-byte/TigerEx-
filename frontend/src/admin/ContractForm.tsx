
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

const ContractForm: React.FC<{ 
    open: boolean; 
    onClose: () => void; 
    onContractCreated: () => void; 
    contract?: any; 
}> = ({ open, onClose, onContractCreated, contract }) => {
  const [formData, setFormData] = useState({
    exchange: '',
    trading_type: '',
    symbol: '',
    base_asset: '',
    quote_asset: '',
    status: 'pending',
  });

  useEffect(() => {
    if (contract) {
      setFormData({
        exchange: contract.exchange,
        trading_type: contract.trading_type,
        symbol: contract.symbol,
        base_asset: contract.base_asset,
        quote_asset: contract.quote_asset,
        status: contract.status,
      });
    } else {
        setFormData({
            exchange: '',
            trading_type: '',
            symbol: '',
            base_asset: '',
            quote_asset: '',
            status: 'pending',
        });
    }
  }, [contract]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async () => {
    try {
      if (contract) {
        await axios.put(`/api/admin/contracts/${contract.contract_id}`, formData);
      } else {
        await axios.post('/api/admin/contracts/create', formData);
      }
      onContractCreated();
      onClose();
    } catch (error) {
      console.error('Error saving contract:', error);
    }
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{contract ? 'Edit' : 'Create'} Trading Contract</DialogTitle>
      <DialogContent>
        <TextField
          autoFocus
          margin="dense"
          name="exchange"
          label="Exchange"
          type="text"
          fullWidth
          variant="standard"
          onChange={handleChange}
          value={formData.exchange}
          select
        >
          <MenuItem value="binance">Binance</MenuItem>
          <MenuItem value="kucoin">Kucoin</MenuItem>
          <MenuItem value="bybit">Bybit</MenuItem>
          <MenuItem value="okx">OKX</MenuItem>
          <MenuItem value="mexc">MEXC</MenuItem>
          <MenuItem value="bitget">Bitget</MenuItem>
          <MenuItem value="bitfinex">Bitfinex</MenuItem>
        </TextField>
        <TextField
          margin="dense"
          name="trading_type"
          label="Trading Type"
          type="text"
          fullWidth
          variant="standard"
          onChange={handleChange}
          value={formData.trading_type}
          select
        >
            <MenuItem value="spot">Spot</MenuItem>
            <MenuItem value="futures_perpetual">Futures Perpetual</MenuItem>
            <MenuItem value="futures_cross">Futures Cross</MenuItem>
            <MenuItem value="futures_delivery">Futures Delivery</MenuItem>
            <MenuItem value="margin">Margin</MenuItem>
            <MenuItem value="margin_cross">Margin Cross</MenuItem>
            <MenuItem value="margin_isolated">Margin Isolated</MenuItem>
            <MenuItem value="options">Options</MenuItem>
            <MenuItem value="derivatives">Derivatives</MenuItem>
            <MenuItem value="copy_trading">Copy Trading</MenuItem>
            <MenuItem value="etf">ETF</MenuItem>
            <MenuItem value="leveraged_tokens">Leveraged Tokens</MenuItem>
            <MenuItem value="structured_products">Structured Products</MenuItem>
        </TextField>
        <TextField
          margin="dense"
          name="symbol"
          label="Symbol"
          type="text"
          fullWidth
          variant="standard"
          onChange={handleChange}
          value={formData.symbol}
        />
        <TextField
          margin="dense"
          name="base_asset"
          label="Base Asset"
          type="text"
          fullWidth
          variant="standard"
          onChange={handleChange}
          value={formData.base_asset}
        />
        <TextField
          margin="dense"
          name="quote_asset"
          label="Quote Asset"
          type="text"
          fullWidth
          variant="standard"
          onChange={handleChange}
          value={formData.quote_asset}
        />
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
            <MenuItem value="paused">Paused</MenuItem>
            <MenuItem value="suspended">Suspended</MenuItem>
            <MenuItem value="delisted">Delisted</MenuItem>
        </TextField>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit}>{contract ? 'Save' : 'Create'}</Button>
      </DialogActions>
    </Dialog>
  );
};

export default ContractForm;
