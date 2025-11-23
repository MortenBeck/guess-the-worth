import { useQuery } from '@tanstack/react-query';
import {
  Users,
  Gavel,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Activity,
} from 'lucide-react';
import adminApi from '../services/adminApi';
import StatCard from '../components/StatCard';

export default function AdminDashboard() {
  // Fetch platform overview
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin', 'overview'],
    queryFn: adminApi.getPlatformOverview,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch recent transactions
  const { data: transactionsData, isLoading: transactionsLoading } = useQuery({
    queryKey: ['admin', 'transactions'],
    queryFn: () => adminApi.getTransactions({ limit: 10 }),
  });

  // Fetch recent users
  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: () => adminApi.getUsers({ limit: 10 }),
  });

  // Fetch system health
  const { data: systemHealth, isLoading: healthLoading } = useQuery({
    queryKey: ['admin', 'health'],
    queryFn: adminApi.getSystemHealth,
    refetchInterval: 60000, // Refresh every minute
  });

  // Fetch flagged auctions
  const { data: flaggedData } = useQuery({
    queryKey: ['admin', 'flagged'],
    queryFn: adminApi.getFlaggedAuctions,
  });

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading admin dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Platform management and monitoring
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<Users className="w-5 h-5" />}
          label="Total Users"
          value={stats?.users?.total || 0}
          subtext={`${stats?.users?.new_last_30_days || 0} new this month`}
        />
        <StatCard
          icon={<Gavel className="w-5 h-5" />}
          label="Active Auctions"
          value={stats?.auctions?.active || 0}
          subtext={`${stats?.auctions?.total || 0} total artworks`}
        />
        <StatCard
          icon={<DollarSign className="w-5 h-5" />}
          label="Total Revenue"
          value={`$${(stats?.transactions?.total_revenue || 0).toLocaleString()}`}
          subtext={`${stats?.transactions?.total || 0} transactions`}
        />
        <StatCard
          icon={<TrendingUp className="w-5 h-5" />}
          label="Platform Fees"
          value={`$${(stats?.transactions?.platform_fees || 0).toLocaleString()}`}
          subtext="10% commission"
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Users */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Users</h2>
          {usersLoading ? (
            <div className="text-gray-500">Loading...</div>
          ) : (
            <div className="space-y-3">
              {usersData?.users?.slice(0, 5).map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded"
                >
                  <div>
                    <p className="font-medium">{user.name}</p>
                    <p className="text-sm text-gray-500">{user.email}</p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded ${
                      user.role === 'ADMIN'
                        ? 'bg-purple-100 text-purple-800'
                        : user.role === 'SELLER'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-green-100 text-green-800'
                    }`}
                  >
                    {user.role}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
          {transactionsLoading ? (
            <div className="text-gray-500">Loading...</div>
          ) : (
            <div className="space-y-3">
              {transactionsData?.transactions?.slice(0, 5).map((tx) => (
                <div
                  key={tx.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded"
                >
                  <div>
                    <p className="font-medium">{tx.artwork_title}</p>
                    <p className="text-sm text-gray-500">
                      Buyer: {tx.buyer}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-green-600">
                      ${tx.amount.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">{tx.status}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* System Health & Flagged Auctions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">System Health</h2>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          {healthLoading ? (
            <div className="text-gray-500">Loading...</div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Status</span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    systemHealth?.status === 'healthy'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {systemHealth?.status || 'Unknown'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Database</span>
                <span
                  className={`px-3 py-1 rounded-full text-sm ${
                    systemHealth?.database === 'healthy'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {systemHealth?.database || 'Unknown'}
                </span>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">
                  Bids (last hour):{' '}
                  <span className="font-semibold">
                    {systemHealth?.metrics?.bids_last_hour || 0}
                  </span>
                </p>
                <p className="text-sm text-gray-600">
                  Artworks (last 24h):{' '}
                  <span className="font-semibold">
                    {systemHealth?.metrics?.artworks_last_24h || 0}
                  </span>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Flagged Auctions */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Flagged Auctions</h2>
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          </div>
          {flaggedData?.total === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No flagged auctions</p>
              <p className="text-sm mt-1">
                {flaggedData?.message || 'All clear!'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {flaggedData?.flagged_auctions?.map((auction) => (
                <div
                  key={auction.id}
                  className="p-3 bg-yellow-50 border border-yellow-200 rounded"
                >
                  <p className="font-medium">{auction.title}</p>
                  <p className="text-sm text-gray-600">{auction.reason}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
