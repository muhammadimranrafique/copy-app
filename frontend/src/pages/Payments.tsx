import { useState } from 'react';
import { Plus, DollarSign, Download, Banknote, CreditCard, Receipt, Smartphone, Building2, User, School } from 'lucide-react';
import { api } from '@/lib/api-client';
import { useEffect } from 'react';
import { useCurrency } from '@/hooks/useCurrency';
import { useAuth } from '@/lib/useAuth';
import { getPayments, createPayment, getLeaders, downloadPaymentReceipt } from '@/lib/mock-api';
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

interface Payment {
  id: string;
  amount: number;
  method: string;
  paymentDate: string;
  leaderId: string;
  referenceNumber?: string;
}

interface Leader {
  id: string;
  name: string;
  type: string;
}

export default function Payments() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { formatCurrency } = useCurrency();
  const { user, isLoading: authLoading } = useAuth();
  const [formData, setFormData] = useState({
    amount: 0,
    method: 'Cash',
    paymentDate: new Date().toISOString().split('T')[0],
    leaderId: '',
    referenceNumber: '',
    orderId: ''
  });
  const [leaderOrders, setLeaderOrders] = useState<any[]>([]);

  useEffect(() => {
    if (formData.leaderId) {
      const fetchOrders = async () => {
        try {
          // @ts-ignore
          const orders = await api.getOrdersByLeader(formData.leaderId);
          setLeaderOrders(orders);
        } catch (error) {
          console.error('Failed to fetch orders', error);
        }
      };
      fetchOrders();
    } else {
      setLeaderOrders([]);
    }
  }, [formData.leaderId]);

  const {
    data: paymentsData,
    loading: paymentsLoading,
    refetch: refetchPayments
  } = useAuthenticatedQuery(
    () => getPayments({}),
    {
      isReady: !authLoading && !!user,
      onError: () => toast.error('Failed to load payments')
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

  const payments = paymentsData?.payments ?? [];
  const leaders = leadersData?.leaders ?? [];
  const loading = paymentsLoading || leadersLoading;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.leaderId) {
      toast.error('Please select a leader');
      return;
    }

    if (formData.amount <= 0) {
      toast.error('Amount must be greater than 0');
      return;
    }

    // Debug logging
    if (import.meta.env.VITE_DEBUG === 'true') {
      console.debug('[Payment Form Data]', formData);
    }

    try {
      const result = await createPayment({
        ...formData,
        amount: Number(formData.amount),
        paymentDate: formData.paymentDate ? new Date(formData.paymentDate).toISOString() : undefined
      });

      if (import.meta.env.VITE_DEBUG === 'true') {
        console.debug('[Payment Result]', result);
      }

      toast.success('Payment recorded successfully');
      setDialogOpen(false);
      setFormData({
        amount: 0,
        method: 'Cash',
        paymentDate: new Date().toISOString().split('T')[0],
        leaderId: '',
        referenceNumber: '',
        orderId: ''
      });
      refetchPayments();
    } catch (error: any) {
      console.error('Payment creation error:', error);
      toast.error(error?.message || 'Failed to record payment');
    }
  };

  const getMethodIcon = (method?: string) => {
    const icons: Record<string, JSX.Element> = {
      'Cash': <Banknote className="w-4 h-4" />,
      'Bank Transfer': <Building2 className="w-4 h-4" />,
      'Cheque': <Receipt className="w-4 h-4" />,
      'UPI': <Smartphone className="w-4 h-4" />
    };
    return icons[method || 'Cash'] || <CreditCard className="w-4 h-4" />;
  };

  const getMethodBadge = (method?: string) => {
    const colors: Record<string, string> = {
      'Cash': 'bg-green-100 text-green-700 border-green-200',
      'Bank Transfer': 'bg-blue-100 text-blue-700 border-blue-200',
      'Cheque': 'bg-purple-100 text-purple-700 border-purple-200',
      'UPI': 'bg-orange-100 text-orange-700 border-orange-200'
    };
    return colors[method || 'Cash'] || 'bg-gray-100 text-gray-700 border-gray-200';
  };

  const formatAmount = (amount: number): string => {
    return `Rs ${amount.toLocaleString('en-PK', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const handleDownloadReceipt = async (paymentId: string) => {
    try {
      toast.loading('Generating receipt...', { id: 'download-receipt' });
      await downloadPaymentReceipt(paymentId);
      toast.success('Receipt downloaded successfully', { id: 'download-receipt' });
    } catch (error: any) {
      console.error('Receipt download error:', error);
      toast.error(error?.message || 'Failed to download receipt', { id: 'download-receipt' });
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-0">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">Payments</h1>
          <p className="text-sm sm:text-base text-muted-foreground">Manage customer payments</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="w-full sm:w-auto">
              <Plus className="w-4 h-4 mr-2" />
              Record Payment
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-[95vw] sm:max-w-[425px] max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Record New Payment</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="leader">Leader *</Label>
                <Select value={formData.leaderId} onValueChange={(value) => setFormData({ ...formData, leaderId: value, orderId: '' })}>
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

              {/* Order Selection - Only show if leader is selected */}
              {formData.leaderId && (
                <div>
                  <Label htmlFor="order">Order (Optional)</Label>
                  <Select value={formData.orderId} onValueChange={(value) => setFormData({ ...formData, orderId: value })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select an order or leave blank for general payment" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">No specific order (General Payment)</SelectItem>
                      {leaderOrders
                        .filter((order: any) => order.status !== 'Paid' && order.balance > 0)
                        .map((order: any) => (
                          <SelectItem key={order.id} value={order.id}>
                            {order.orderNumber} - Rs {order.totalAmount?.toLocaleString()}
                            (Balance: Rs {order.balance?.toLocaleString()})
                          </SelectItem>
                        ))}
                    </SelectContent>
                  </Select>
                  {leaderOrders.length === 0 && (
                    <p className="text-xs text-muted-foreground mt-1">No unpaid orders found for this leader</p>
                  )}
                </div>
              )}

              {/* Remaining Balance Display */}
              {formData.orderId && leaderOrders.length > 0 && (() => {
                const selectedOrder = leaderOrders.find((o: any) => o.id === formData.orderId);
                if (!selectedOrder) return null;

                const remainingBalance = selectedOrder.balance || 0;
                const willExceed = formData.amount > remainingBalance;

                return (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-blue-900">Order Details</span>
                      <Badge variant="outline" className="bg-white">
                        {selectedOrder.orderNumber}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <p className="text-blue-600">Total Amount</p>
                        <p className="font-semibold text-blue-900">Rs {selectedOrder.totalAmount?.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-blue-600">Paid So Far</p>
                        <p className="font-semibold text-blue-900">Rs {selectedOrder.paidAmount?.toLocaleString()}</p>
                      </div>
                    </div>
                    <div className="pt-2 border-t border-blue-200">
                      <p className="text-sm text-blue-600">Remaining Balance</p>
                      <p className="text-2xl font-bold text-blue-900">Rs {remainingBalance.toLocaleString()}</p>
                    </div>
                    {willExceed && formData.amount > 0 && (
                      <div className="bg-red-50 border border-red-200 rounded p-2 mt-2">
                        <p className="text-xs text-red-700 font-medium">
                          ⚠️ Payment amount exceeds remaining balance by Rs {(formData.amount - remainingBalance).toLocaleString()}
                        </p>
                      </div>
                    )}
                    {formData.amount > 0 && formData.amount <= remainingBalance && (
                      <div className="bg-green-50 border border-green-200 rounded p-2 mt-2">
                        <p className="text-xs text-green-700">
                          ✓ New balance after payment: Rs {(remainingBalance - formData.amount).toLocaleString()}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })()}

              <div>
                <Label htmlFor="amount">Amount (Rs) *</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground text-sm">
                    Rs
                  </span>
                  <Input
                    id="amount"
                    type="number"
                    step="0.01"
                    className="pl-8"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                    placeholder="0.00"
                    required
                  />
                </div>
              </div>
              <div>
                <Label htmlFor="method">Payment Method</Label>
                <Select value={formData.method} onValueChange={(value) => setFormData({ ...formData, method: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Cash">Cash</SelectItem>
                    <SelectItem value="Bank Transfer">Bank Transfer</SelectItem>
                    <SelectItem value="Cheque">Cheque</SelectItem>
                    <SelectItem value="UPI">UPI</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="paymentDate">Payment Date *</Label>
                <Input
                  id="paymentDate"
                  type="date"
                  value={formData.paymentDate}
                  onChange={(e) => setFormData({ ...formData, paymentDate: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="referenceNumber">Reference Number</Label>
                <Input
                  id="referenceNumber"
                  value={formData.referenceNumber}
                  onChange={(e) => setFormData({ ...formData, referenceNumber: e.target.value })}
                  placeholder="Optional"
                />
              </div>
              <Button type="submit" className="w-full">Record Payment</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="space-y-3 sm:space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 sm:h-28 bg-muted rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {payments.map((payment) => {
            return (
              <Card key={payment.id} className="card-hover border-l-4 border-l-green-500 shadow-sm hover:shadow-md transition-all duration-200">
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    {/* Left Section - Client Info & Payment Details */}
                    <div className="flex-1 space-y-3">
                      {/* Client Name & Type */}
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                          {payment.client?.type === 'School' ? (
                            <School className="w-5 h-5 text-blue-600" />
                          ) : (
                            <User className="w-5 h-5 text-gray-600" />
                          )}
                          <h3 className="text-lg font-semibold text-gray-900">
                            {payment.client?.name || 'Unknown Client'}
                          </h3>
                        </div>
                        <Badge variant="outline" className="text-xs">
                          {payment.client?.type || 'N/A'}
                        </Badge>
                      </div>

                      {/* RECEIVED FROM Section */}
                      {payment.client && (
                        <div className="bg-gray-50 p-3 rounded-lg border">
                          <h4 className="text-sm font-medium text-gray-700 mb-2">RECEIVED FROM:</h4>
                          <div className="space-y-1 text-sm text-gray-600">
                            <div className="flex items-center gap-2">
                              <User className="w-3 h-3" />
                              <span>{payment.client.name}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="w-3 h-3 text-center">📞</span>
                              <span>{payment.client.contact}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="w-3 h-3 text-center">📍</span>
                              <span>{payment.client.address}</span>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Payment Method & Reference */}
                      <div className="flex flex-wrap items-center gap-3">
                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border ${getMethodBadge(payment.method)}`}>
                          {getMethodIcon(payment.method)}
                          <span className="text-sm font-medium">{payment.method}</span>
                        </div>
                        {payment.referenceNumber && (
                          <div className="flex items-center gap-1 text-sm text-muted-foreground">
                            <Receipt className="w-3 h-3" />
                            <span>Ref: {payment.referenceNumber}</span>
                          </div>
                        )}
                      </div>

                      {/* Payment Date */}
                      <p className="text-sm text-muted-foreground">
                        Payment Date: {payment.paymentDate ? format(new Date(payment.paymentDate), 'MMMM dd, yyyy') : 'N/A'}
                      </p>
                    </div>

                    {/* Right Section - Amount & Actions */}
                    <div className="flex items-center gap-4 lg:flex-col lg:items-end">
                      <div className="text-right">
                        <p className="text-2xl font-bold text-green-600">
                          {formatAmount(payment.amount || 0)}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Payment Amount
                        </p>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownloadReceipt(payment.id)}
                        className="flex items-center gap-2 hover:bg-green-50 hover:border-green-300"
                      >
                        <Download className="w-4 h-4" />
                        <span className="hidden sm:inline">Receipt</span>
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {!loading && payments.length === 0 && (
        <div className="text-center py-12">
          <DollarSign className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No payments recorded yet</p>
        </div>
      )}
    </div>
  );
}
