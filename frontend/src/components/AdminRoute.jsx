import { Navigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

export default function AdminRoute({ children }) {
  const { isAuthenticated, isLoading: authLoading } = useAuth0();

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await api.get('/api/auth/me');
      return response.data;
    },
    enabled: isAuthenticated,
  });

  if (authLoading || userLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (user?.role !== 'admin') {
    return <Navigate to="/" />;
  }

  return children;
}
