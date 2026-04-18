import React from 'react';
import { useRBAC } from '../../contexts/RBACProvider';
import { UserRole } from '../../lib/roles';

// Import all the dashboards
import SuperAdminDashboard from './SuperAdminDashboard';
import AdminDashboard from './AdminDashboard';
import ModeratorDashboard from './ModeratorDashboard';
import TechnicalTeamDashboard from './TechnicalTeamDashboard';
import ListingsManagerDashboard from './ListingsManagerDashboard';
import BusinessHeadDashboard from './BusinessHeadDashboard';
import WhiteLabelClientDashboard from './WhiteLabelClientDashboard';
import PrimeBrokerageDashboard from './PrimeBrokerageDashboard';
import LiquidityProviderDashboard from './LiquidityProviderDashboard';
import MarketMakerDashboard from './MarketMakerDashboard';
import TradingDashboard from '../../pages/advanced-trading'; // Default for traders
import UserDashboard from '@/app/page'; // Default for users

const DashboardRouter: React.FC = () => {
  const { userRole } = useRBAC();

  switch (userRole) {
    case 'superadmin':
      return <SuperAdminDashboard />;
    case 'admin':
      return <AdminDashboard />;
    case 'moderator':
      return <ModeratorDashboard />;
    case 'technical_team':
      return <TechnicalTeamDashboard />;
    case 'listings_manager':
      return <ListingsManagerDashboard />;
    case 'business_head':
      return <BusinessHeadDashboard />;
    case 'white_label_client':
      return <WhiteLabelClientDashboard />;
    case 'prime_brokerage':
      return <PrimeBrokerageDashboard />;
    case 'liquidity_provider':
      return <LiquidityProviderDashboard />;
    case 'market_maker':
      return <MarketMakerDashboard />;
    case 'trader':
        return <TradingDashboard />;
    case 'user':
    default:
      return <UserDashboard />;
  }
};

export default DashboardRouter;
