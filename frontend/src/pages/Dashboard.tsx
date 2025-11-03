import { useEffect, useState } from 'react';
import { ShoppingCart, DollarSign, TrendingUp, TrendingDown } from 'lucide-react';
import { getDashboardData } from '@/lib/mock-api';
import StatCard from '@/components/StatCard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { useCurrency } from '@/hooks/useCurrency';
import WelcomeAlert from '@/components/WelcomeAlert';
import { useAuth } from '@/lib/useAuth';

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showWelcome, setShowWelcome] = useState(false);
  const { formatCurrency } = useCurrency();
  const { user, isLoading: authLoading } = useAuth();

  useEffect(() => {
    const hasSeenWelcome = localStorage.getItem('hasSeenWelcome');
    if (!hasSeenWelcome) {
      setShowWelcome(true);
      localStorage.setItem('hasSeenWelcome', 'true');
    }
  }, []);

  useEffect(() => {
    if (!authLoading && user) {
      loadDashboardData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, user]);

  const loadDashboardData = async () => {
    if (!user) return;
    try {
      setLoading(true);
      const result = await getDashboardData({});
      setData(result);
    } catch (error) {
      console.error('Error loading dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-muted rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-muted rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">Dashboard</h1>
        <p className="text-sm sm:text-base text-muted-foreground">Welcome back! Here's your business overview.</p>
      </div>

      {showWelcome && <WelcomeAlert />}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
        <StatCard
          title="Total Orders"
          value={data?.totalOrders || 0}
          icon={ShoppingCart}
          colorClass="text-blue-600"
        />
        <StatCard
          title="Total Revenue"
          value={formatCurrency(data?.totalRevenue || 0)}
          icon={DollarSign}
          colorClass="text-green-600"
        />
        <StatCard
          title="Total Payments"
          value={formatCurrency(data?.totalPayments || 0)}
          icon={TrendingDown}
          colorClass="text-orange-600"
        />
        <StatCard
          title="Net Profit"
          value={formatCurrency(data?.netProfit || 0)}
          icon={TrendingUp}
          colorClass="text-purple-600"
        />
      </div>

      {/* Recent Orders and Payments */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Orders</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 sm:space-y-3">
              {data?.recentOrders && data.recentOrders.length > 0 ? (
                data.recentOrders.map((order: any) => (
                  <div key={order.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 sm:p-4 rounded-lg border gap-2 sm:gap-0 hover-lift">
                    <div className="flex-1">
                      <p className="font-medium text-sm sm:text-base">{order.orderNumber}</p>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        {order.orderDate ? format(new Date(order.orderDate), 'MMM dd, yyyy') : 'N/A'}
                      </p>
                    </div>
                    <div className="flex items-center justify-between sm:flex-col sm:items-end gap-2">
                      <p className="font-semibold text-base sm:text-lg">{formatCurrency(order.totalAmount || 0)}</p>
                      <Badge variant={order.status === 'Paid' ? 'default' : 'secondary'} className="text-xs">
                        {order.status}
                      </Badge>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">No orders yet</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Payments</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 sm:space-y-3">
              {data?.recentPayments && data.recentPayments.length > 0 ? (
                data.recentPayments.map((payment: any) => (
                  <div key={payment.id} className="flex flex-col sm:flex-row sm:items-center justify-between p-3 sm:p-4 rounded-lg border gap-2 sm:gap-0 hover-lift">
                    <div className="flex-1">
                      <p className="font-medium text-sm sm:text-base">{payment.method}</p>
                      <p className="text-xs sm:text-sm text-muted-foreground">
                        {payment.paymentDate ? format(new Date(payment.paymentDate), 'MMM dd, yyyy') : 'N/A'}
                      </p>
                    </div>
                    <p className="font-semibold text-base sm:text-lg text-green-600">{formatCurrency(payment.amount || 0)}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">No payments yet</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
