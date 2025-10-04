'use client';

import React from 'react';
import AdminDashboard from '../../components/admin/AdminDashboard';

export default function AdminPage() {
  const handleNavigation = (section: string) => {
    console.log('Navigate to:', section);
    // Handle admin navigation
  };

  return <AdminDashboard onNavigate={handleNavigation} />;
}