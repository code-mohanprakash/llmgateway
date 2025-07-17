import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';

export const ProtectedRoute = ({ children }) => {
  const { user, loading, initialized } = useAuth();

  console.log('ProtectedRoute - loading:', loading, 'initialized:', initialized, 'user:', !!user);

  if (loading || !initialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!user) {
    console.log('ProtectedRoute - No user found, redirecting to login');
    return <Navigate to="/login" />;
  }

  console.log('ProtectedRoute - User authenticated, rendering children');
  return children;
};