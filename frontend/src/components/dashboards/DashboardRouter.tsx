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
import TradingDashboard from '../../pages/TradingInterface'; // Default for traders
import UserDashboard from '../../pages/Dashboard'; // Default for users

const DashboardRouter: React.FC = () => {
  const { userRole } = useRBAC();

  switch (userRole) {
    case UserRole.SUPER_ADMIN:
      return <SuperAdminDashboard />;
    case UserRole.ADMIN:
      return <AdminDashboard />;
    case UserRole.MODERATOR:
      return <ModeratorDashboard />;
    case UserRole.TECHNICAL_TEAM:
      return <TechnicalTeamDashboard />;
    case UserRole.LISTING_MANAGER:
      return <ListingsManagerDashboard />;
    case UserRole.BUSINESS_HEAD:
      return <BusinessHeadDashboard />;
    case UserRole.WHITE_LEVEL_CLIENT:
      return <WhiteLabelClientDashboard />;
    case UserRole.PRIME_BROKERAGE:
      return <PrimeBrokerageDashboard />;
    case UserRole.LIQUIDITY_PROVIDER:
      return <LiquidityProviderDashboard />;
    case UserRole.MARKET_MAKER:
      return <MarketMakerDashboard />;
    case UserRole.TRADER:
        return <TradingDashboard />;
    case UserRole.USER:
    default:
      return <UserDashboard />;
  }
};

export default DashboardRouter;
