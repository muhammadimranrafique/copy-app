import { useState } from 'react';
import { Plus, ShoppingCart } from 'lucide-react';
import { useCurrency } from '@/hooks/useCurrency';
import { useAuth } from '@/lib/useAuth';
import { getOrders, createOrder, getLeaders } from '@/lib/mock-api';
import { useAuthenticatedQuery } from '@/hooks/useAuthenticatedQuery';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';

interface Order {
  id: string;
  orderNumber: string;
  leaderId: string;
  orderDate: string;
  totalAmount: number;
  status: string;
}

interface Leader {
  id: string;
  name: string;
  type: string;
}

export default function Orders() {
  const { formatCurrency } = useCurrency();
  const { user, isLoading: authLoading } = useAuth();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    orderNumber: '',
    leaderId: '',
    orderDate: new Date().toISOString().split('T')[0],
    totalAmount: 0,
    status: 'Pending'
  });

  const {
    data: ordersData,
    loading: ordersLoading,
    refetch: loadOrders
  } = useAuthenticatedQuery(
    () => getOrders({}),
    {
      isReady: !authLoading && !!user,
      onError: () => toast.error('Failed to load orders')
    }
  );

  const {
    data: leadersData,
    loading: leadersLoading
  } = useAuthenticatedQuery(
    () => getLeaders({}),
    {
      isReady: !authLoading && !!user,
      onError: () => toast.error('Failed to load leaders')
    }
  );

  const orders = ordersData?.orders ?? [];
  const leaders = leadersData?.leaders ?? [];
  const loading = ordersLoading || leadersLoading;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.leaderId) {
      toast.error('Please select a leader');
      return;
    }
    try {
      await createOrder(formData);
      toast.success('Order created successfully');
      setDialogOpen(false);
      setFormData({
        orderNumber: '',
        leaderId: '',
        orderDate: new Date().toISOString().split('T')[0],
        totalAmount: 0,
        status: 'Pending'
      });
      loadData();
    } catch (error) {
      toast.error('Failed to create order');
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'Paid': return 'default';
      case 'Delivered': return 'default';
      case 'In Production': return 'secondary';
      default: return 'outline';
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Orders</h1>
          <p className="text-muted-foreground">Manage customer orders</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Create Order
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Order</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="orderNumber">Order Number *</Label>
                <Input
                  id="orderNumber"
                  value={formData.orderNumber}
                  onChange={(e) => setFormData({ ...formData, orderNumber: e.target.value })}
                  required
                  placeholder="ORD-001"
                />
              </div>
              <div>
                <Label htmlFor="leader">Leader *</Label>
                <Select value={formData.leaderId} onValueChange={(value) => setFormData({ ...formData, leaderId: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a leader" />
                  </SelectTrigger>
                  <SelectContent>
                    {leaders.map((leader) => (
                      <SelectItem key={leader.id} value={leader.id}>
                        {leader.name} ({leader.type})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="orderDate">Order Date *</Label>
                <Input
                  id="orderDate"
                  type="date"
                  value={formData.orderDate}
                  onChange={(e) => setFormData({ ...formData, orderDate: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="totalAmount">Total Amount *</Label>
                <Input
                  id="totalAmount"
                  type="number"
                  step="0.01"
                  value={formData.totalAmount}
                  onChange={(e) => setFormData({ ...formData, totalAmount: parseFloat(e.target.value) || 0 })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="status">Status</Label>
                <Select value={formData.status} onValueChange={(value) => setFormData({ ...formData, status: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Pending">Pending</SelectItem>
                    <SelectItem value="In Production">In Production</SelectItem>
                    <SelectItem value="Delivered">Delivered</SelectItem>
                    <SelectItem value="Paid">Paid</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Button type="submit" className="w-full">Create Order</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-muted rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Card key={order.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-full bg-primary/10">
                      <ShoppingCart className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg">{order.orderNumber}</h3>
                      <p className="text-sm text-muted-foreground">
                        {order.orderDate ? format(new Date(order.orderDate), 'MMM dd, yyyy') : 'N/A'}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm text-muted-foreground">Amount</p>
                      <p className="text-xl font-bold">{formatCurrency(order.totalAmount || 0)}</p>
                    </div>
                    <Badge variant={getStatusColor(order.status)}>
                      {order.status}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!loading && orders.length === 0 && (
        <div className="text-center py-12">
          <ShoppingCart className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No orders found</p>
        </div>
      )}
    </div>
  );
}
