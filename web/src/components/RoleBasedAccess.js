import { useAuth } from '../contexts/AuthContext';

const RoleBasedAccess = ({ 
  children, 
  allowedRoles = [], 
  fallback = null,
  requireAdmin = false,
  requireOwner = false 
}) => {
  const { user } = useAuth();

  if (!user) {
    return fallback;
  }

  // Role hierarchy: viewer < member < admin < owner
  const roleHierarchy = {
    'viewer': 1,
    'member': 2,
    'admin': 3,
    'owner': 4
  };

  const userRoleLevel = roleHierarchy[user.role?.toLowerCase()] || 0;

  // Check specific requirements
  if (requireOwner && user.role?.toLowerCase() !== 'owner') {
    return fallback;
  }

  if (requireAdmin && userRoleLevel < roleHierarchy['admin']) {
    return fallback;
  }

  // Check allowed roles
  if (allowedRoles.length > 0) {
    const hasPermission = allowedRoles.some(role => {
      if (role === 'admin+') {
        return userRoleLevel >= roleHierarchy['admin'];
      }
      if (role === 'member+') {
        return userRoleLevel >= roleHierarchy['member'];
      }
      return user.role?.toLowerCase() === role?.toLowerCase();
    });

    if (!hasPermission) {
      return fallback;
    }
  }

  return children;
};

export default RoleBasedAccess; 