import React, { createContext, useContext, useState } from 'react';
import { UserRole, PERMISSIONS } from '../lib/roles';

interface RBACContextType {
  userRole: UserRole | null;
  setUserRole: (role: UserRole) => void;
  hasPermission: (permission: string) => boolean;
}

const RBACContext = createContext<RBACContextType | undefined>(undefined);

export const RBACProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [userRole, setUserRole] = useState<UserRole | null>(null);

  const hasPermission = (permission: string) => {
    if (!userRole) return false;
    const userPermissions = PERMISSIONS[userRole];
    if (userPermissions.includes('*')) return true;
    return userPermissions.includes(permission);
  };

  return (
    <RBACContext.Provider value={{ userRole, setUserRole, hasPermission }}>
      {children}
    </RBACContext.Provider>
  );
};

export const useRBAC = () => {
  const context = useContext(RBACContext);
  if (context === undefined) {
    throw new Error('useRBAC must be used within a RBACProvider');
  }
  return context;
};
