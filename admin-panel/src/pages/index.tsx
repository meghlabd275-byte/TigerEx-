import React from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent } from '@mui/material';
import {
  TrendingUp,
  People,
  AccountBalance,
  ShowChart,
  Security,
  Warning,
} from '@mui/icons-material';
import DashboardLayout from '../components/Layout/DashboardLayout';
import StatCard from '../components/Dashboard/StatCard';
import RevenueChart from '../components/Dashboard/RevenueChart';
import UserGrowthChart from '../components/Dashboard/UserGrowthChart';
import RecentTransactions from '../components/Dashboard/RecentTransactions';
import SystemHealth from '../components/Dashboard/SystemHealth';

export default function Dashboard() {
  const stats = [
    {
      title: 'Total Revenue',
      value: '$12,458,392',
      change: '+12.5%',
      icon: <AccountBalance />,
      color: '#4CAF50',
    },
    {
      title: 'Active Users',
      value: '45,892',
      change: '+8.2%',
      icon: <People />,
      color: '#2196F3',
    },
    {
      title: 'Trading Volume (24h)',
      value: '$89,234,567',
      change: '+15.3%',
      icon: <TrendingUp />,
      color: '#FF9800',
    },
    {
      title: 'Total Trades',
      value: '1,234,567',
      change: '+5.7%',
      icon: <ShowChart />,
      color: '#9C27B0',
    },
    {
      title: 'Pending KYC',
      value: '234',
      change: '-3.2%',
      icon: <Security />,
      color: '#F44336',
    },
    {
      title: 'Active Alerts',
      value: '12',
      change: '+2',
      icon: <Warning />,
      color: '#FF5722',
    },
  ];

  return (
    <DashboardLayout>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard Overview
        </Typography>

        {/* Stats Grid */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {stats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={4} lg={2} key={index}>
              <StatCard {...stat} />
            </Grid>
          ))}
        </Grid>

        {/* Charts Row */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Revenue Analytics
              </Typography>
              <RevenueChart />
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                User Growth
              </Typography>
              <UserGrowthChart />
            </Paper>
          </Grid>
        </Grid>

        {/* Bottom Row */}
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Recent Transactions
              </Typography>
              <RecentTransactions />
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                System Health
              </Typography>
              <SystemHealth />
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </DashboardLayout>
  );
}