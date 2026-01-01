import { useState, useEffect } from 'react';
import { Plus, DollarSign, Download, Banknote, CreditCard, Receipt, Smartphone, Building2, User, School, Pencil, Trash2 } from 'lucide-react';
import { api } from '@/lib/api-client';
import { useAuth } from '@/lib/useAuth';
import { useAuthenticatedQuery } from '@/hooks/useAuthenticatedQuery';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';


export default function Payments() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const { user, isLoading: authLoading } = useAuth();
  const [formData, setFormData] = useState({
    amount: 0,
    method: 'Cash',
    paymentDate: new Date().toISOString().split('T')[0],
    leaderId: '',
    referenceNumber: '',
    orderId: 'none' // Changed from '' to 'none' to fix Select.Item error
  });
  const [leaderOrders, setLeaderOrders] = useState<any[]>([]);
  const [loadingOrders, setLoadingOrders] = useState(false);

  // Edit payment state
  const [editingPayment, setEditingPayment] = useState<any | null>(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({
    amount: 0,
    method: 'Cash',
    paymentDate: '',
    referenceNumber: ''
  });
  const [editLoading, setEditLoading] = useState(false);

  // Delete payment state
  const [deletingPayment, setDeletingPayment] = useState<any | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    if (formData.leaderId) {
      const fetchOrders = async () => {
        try {
          setLoadingOrders(true);
          const orders = await api.getOrdersByLeader(formData.leaderId);

          // Ensure all orders have required fields with default values
          const normalizedOrders = Array.isArray(orders) ? orders.map((order: any) => ({
            ...order,
            balance: order.balance ?? order.totalAmount ?? order.total_amount ?? 0,
            paidAmount: order.paidAmount ?? order.paid_amount ?? 0,
            totalAmount: order.totalAmount ?? order.total_amount ?? 0,
            status: order.status ?? 'Pending',
            // Handle both camelCase (orderNumber) and snake_case (order_number) from API
            orderNumber: order.orderNumber ?? order.order_number ?? 'N/A'
          })) : [];

          setLeaderOrders(normalizedOrders);
        } catch (error) {
          console.error('Failed to fetch orders', error);
          toast.error('Failed to load orders for this leader');
          setLeaderOrders([]);
        } finally {
          setLoadingOrders(false);
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
    () => api.getPayments({}),
    {
      isReady: !authLoading && !!user,
      onError: () => toast.error('Failed to load payments')
    }
  );

  const {
    data: leadersData,
    loading: leadersLoading
  } = useAuthenticatedQuery(
    () => api.getLeaders({}),
    {
      isReady: !authLoading && !!user,
      onError: () => toast.error('Failed to load leaders')
    }
  );

  const payments = paymentsData?.items ?? [];
  const leaders = leadersData?.items ?? [];
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
      const result = await api.createPayment({
        ...formData,
        amount: Number(formData.amount),
        paymentDate: formData.paymentDate ? new Date(formData.paymentDate).toISOString() : undefined,
        orderId: formData.orderId === 'none' ? undefined : formData.orderId // Convert 'none' to undefined
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
        orderId: 'none' // Reset to 'none' instead of empty string
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
      await api.downloadPaymentReceipt(paymentId);
      toast.success('Receipt downloaded successfully', { id: 'download-receipt' });
    } catch (error: any) {
      console.error('Receipt download error:', error);
      toast.error(error?.message || 'Failed to download receipt', { id: 'download-receipt' });
    }
  };

  const handleEditClick = (payment: any) => {
    setEditingPayment(payment);
    setEditFormData({
      amount: payment.amount,
      method: payment.method,
      paymentDate: payment.paymentDate ? new Date(payment.paymentDate).toISOString().split('T')[0] : '',
      referenceNumber: payment.referenceNumber || ''
    });
    setEditDialogOpen(true);
  };

  const handleEditSubmit = async () => {
    if (!editingPayment) return;

    // Validation
    if (editFormData.amount <= 0) {
      toast.error('Payment amount must be greater than 0');
      return;
    }

    try {
      setEditLoading(true);
      await api.updatePayment(editingPayment.id, editFormData);
      toast.success('Payment updated successfully');
      setEditDialogOpen(false);
      setEditingPayment(null);

      // Refresh payments list
      await refetchPayments();
    } catch (error: any) {
      console.error('Error updating payment:', error);
      toast.error(error?.message || 'Failed to update payment');
    } finally {
      setEditLoading(false);
    }
  };

  const handleDeleteClick = (payment: any) => {
    setDeletingPayment(payment);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!deletingPayment) return;

    console.log('[Payment Delete] Starting deletion process for payment:', {
      id: deletingPayment.id,
      amount: deletingPayment.amount,
      client: deletingPayment.client?.name
    });

    try {
      setDeleteLoading(true);

      console.log('[Payment Delete] Calling API to delete payment...');
      await api.deletePayment(deletingPayment.id);

      console.log('[Payment Delete] API call successful, payment deleted from backend');

      // Close dialog and reset state BEFORE showing success message
      setDeleteDialogOpen(false);
      setDeletingPayment(null);

      // Show success message
      toast.success('Payment deleted successfully', {
        description: `Payment of ${formatAmount(deletingPayment.amount)} has been removed`
      });

      console.log('[Payment Delete] Refreshing payments list...');

      // Refresh payments list to update UI
      await refetchPayments();

      console.log('[Payment Delete] ✓ Delete operation completed successfully');
    } catch (error: any) {
      console.error('[Payment Delete] Error during deletion:', {
        error: error.message,
        status: error.status,
        data: error.data,
        paymentId: deletingPayment.id
      });

      // Determine user-friendly error message
      let errorMessage = 'Failed to delete payment';

      if (error.status === 403) {
        errorMessage = 'You do not have permission to delete payments';
      } else if (error.status === 404) {
        errorMessage = 'Payment not found. It may have already been deleted';
      } else if (error.status === 0) {
        errorMessage = 'Network error. Please check your connection and try again';
      } else if (error.message) {
        errorMessage = error.message;
      }

      toast.error(errorMessage, {
        description: 'Please try again or contact support if the problem persists'
      });
    } finally {
      setDeleteLoading(false);
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
                <Select value={formData.leaderId} onValueChange={(value) => setFormData({ ...formData, leaderId: value, orderId: 'none' })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a leader" />
                  </SelectTrigger>
                  <SelectContent>
                    {leaders.map((leader: any) => (
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
                  <Select
                    value={formData.orderId}
                    onValueChange={(value) => setFormData({ ...formData, orderId: value })}
                    disabled={loadingOrders}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={
                        loadingOrders
                          ? "Loading orders..."
                          : "Select an order or leave blank for general payment"
                      } />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">No specific order (General Payment)</SelectItem>
                      {Array.isArray(leaderOrders) && leaderOrders
                        .filter((order: any) => {
                          // Safe filtering with null checks
                          if (!order) return false;
                          const status = order.status ?? 'Pending';
                          const balance = order.balance ?? order.totalAmount ?? 0;
                          return status !== 'Paid' && balance > 0;
                        })
                        .map((order: any) => {
                          // Safe rendering with default values
                          const orderNumber = order.orderNumber ?? 'N/A';
                          const totalAmount = order.totalAmount ?? 0;
                          const balance = order.balance ?? totalAmount;

                          return (
                            <SelectItem key={order.id} value={order.id}>
                              {orderNumber} - Rs {totalAmount.toLocaleString()}
                              (Balance: Rs {balance.toLocaleString()})
                            </SelectItem>
                          );
                        })}
                    </SelectContent>
                  </Select>
                  {!loadingOrders && leaderOrders.length === 0 && (
                    <p className="text-xs text-muted-foreground mt-1">No unpaid orders found for this leader</p>
                  )}
                  {loadingOrders && (
                    <p className="text-xs text-blue-600 mt-1">Loading orders...</p>
                  )}
                </div>
              )}

              {/* Remaining Balance Display */}
              {formData.orderId && formData.orderId !== 'none' && Array.isArray(leaderOrders) && leaderOrders.length > 0 && (() => {
                try {
                  const selectedOrder = leaderOrders.find((o: any) => o?.id === formData.orderId);
                  if (!selectedOrder) return null;

                  // Safe access with default values
                  const totalAmount = selectedOrder.totalAmount ?? 0;
                  const paidAmount = selectedOrder.paidAmount ?? 0;
                  const remainingBalance = selectedOrder.balance ?? (totalAmount - paidAmount);
                  const willExceed = formData.amount > remainingBalance;

                  return (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-blue-900">Order Details</span>
                        <Badge variant="outline" className="bg-white">
                          {selectedOrder.orderNumber ?? 'N/A'}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <p className="text-blue-600">Total Amount</p>
                          <p className="font-semibold text-blue-900">Rs {totalAmount.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-blue-600">Paid So Far</p>
                          <p className="font-semibold text-blue-900">Rs {paidAmount.toLocaleString()}</p>
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
                } catch (error) {
                  console.error('Error rendering balance display:', error);
                  return (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <p className="text-xs text-red-700">Unable to load order details. Please try again.</p>
                    </div>
                  );
                }
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
          {payments.map((payment: any) => {
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
                      <div className="flex flex-col gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditClick(payment)}
                          className="flex items-center gap-2 hover:bg-blue-50 hover:border-blue-300"
                        >
                          <Pencil className="w-3 h-3" />
                          <span className="hidden sm:inline">Edit</span>
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteClick(payment)}
                          className="flex items-center gap-2 hover:bg-red-50 hover:border-red-300 text-red-600"
                        >
                          <Trash2 className="w-3 h-3" />
                          <span className="hidden sm:inline">Delete</span>
                        </Button>
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

      {/* Edit Payment Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Payment</DialogTitle>
          </DialogHeader>

          {editingPayment && (
            <div className="space-y-4">
              {/* Amount Field */}
              <div>
                <Label htmlFor="edit-amount">Payment Amount (Rs) *</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground text-sm">
                    Rs
                  </span>
                  <Input
                    id="edit-amount"
                    type="number"
                    step="0.01"
                    className="pl-8"
                    value={editFormData.amount}
                    onChange={(e) => setEditFormData({ ...editFormData, amount: parseFloat(e.target.value) || 0 })}
                    placeholder="0.00"
                    required
                  />
                </div>
              </div>

              {/* Payment Method */}
              <div>
                <Label htmlFor="edit-method">Payment Method</Label>
                <Select value={editFormData.method} onValueChange={(value) => setEditFormData({ ...editFormData, method: value })}>
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

              {/* Payment Date */}
              <div>
                <Label htmlFor="edit-date">Payment Date *</Label>
                <Input
                  id="edit-date"
                  type="date"
                  value={editFormData.paymentDate}
                  onChange={(e) => setEditFormData({ ...editFormData, paymentDate: e.target.value })}
                  required
                />
              </div>

              {/* Reference Number */}
              <div>
                <Label htmlFor="edit-reference">Reference Number</Label>
                <Input
                  id="edit-reference"
                  value={editFormData.referenceNumber}
                  onChange={(e) => setEditFormData({ ...editFormData, referenceNumber: e.target.value })}
                  placeholder="Optional"
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setEditDialogOpen(false)}
              disabled={editLoading}
            >
              Cancel
            </Button>
            <Button
              onClick={handleEditSubmit}
              disabled={editLoading}
            >
              {editLoading ? 'Updating...' : 'Update Payment'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Payment Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Payment</AlertDialogTitle>
            <AlertDialogDescription>
              {deletingPayment && (
                <div className="space-y-3 mt-2">
                  <p>Are you sure you want to delete this payment?</p>

                  {/* Payment Details */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Amount:</span>
                        <span className="font-semibold text-gray-900">{formatAmount(deletingPayment.amount)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Method:</span>
                        <span className="font-semibold text-gray-900">{deletingPayment.method}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Date:</span>
                        <span className="font-semibold text-gray-900">
                          {format(new Date(deletingPayment.paymentDate), 'MMM dd, yyyy')}
                        </span>
                      </div>
                      {deletingPayment.referenceNumber && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Reference:</span>
                          <span className="font-semibold text-gray-900">{deletingPayment.referenceNumber}</span>
                        </div>
                      )}
                      {deletingPayment.client && (
                        <div className="flex justify-between">
                          <span className="text-gray-600">Client:</span>
                          <span className="font-semibold text-gray-900">{deletingPayment.client.name}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <p className="text-sm text-red-600 font-medium">
                    This action cannot be undone.
                  </p>
                </div>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={deleteLoading}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleteLoading ? 'Deleting...' : 'Delete Payment'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
