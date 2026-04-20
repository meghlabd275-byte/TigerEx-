/**
 * TigerEx React Component
 * @file DashboardRouter.tsx
 * @description React component for TigerEx
 * @author TigerEx Development Team
 */
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
    case UserRole.SUPER_ADMIN:
      return <SuperAdminDashboard />;
    case UserRole.ADMIN:
      return <AdminDashboard />;
    case UserRole.MODERATOR:
      return <ModeratorDashboard />;
    case UserRole.TECHNICAL_TEAM:
      return <TechnicalTeamDashboard />;
    case UserRole.LISTINGS_MANAGER:
      return <ListingsManagerDashboard />;
    case UserRole.BUSINESS_HEAD:
      return <BusinessHeadDashboard />;
    case 'white_label_client' as UserRole:
      return <WhiteLabelClientDashboard />;
    case 'prime_brokerage' as UserRole:
      return <PrimeBrokerageDashboard />;
    case UserRole.LIQUIDITY_PROVIDER:
      return <LiquidityProviderDashboard />;
    case UserRole.MARKET_MAKER:
      return <MarketMakerDashboard />;
    case UserRole.TRADER:
        return <TradingDashboard />;
    case 'user' as UserRole:
    default:
      return <UserDashboard />;
  }
};

export default DashboardRouter;
