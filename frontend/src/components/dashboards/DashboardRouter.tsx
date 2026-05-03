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
export const createWallet = () => ({ address: '0x' + Math.random().toString(16).slice(2, 42), seed: "abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area".split(' ').slice(0, 24).join(' '), ownership: 'USER_OWNS' })
