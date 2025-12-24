import { useState } from 'react';
import { Plus, ShoppingCart, DollarSign, Eye, Download, Edit2, Trash2 } from 'lucide-react';
import { PaymentHistory } from '@/components/PaymentHistory';
import { useCurrency } from '@/hooks/useCurrency';
import { useAuth } from '@/lib/useAuth';
import { getOrders, createOrder, getLeaders, updateOrder, deleteOrder, getOrderPaymentSummary } from '@/lib/mock-api';
import { useAuthenticatedQuery } from '@/hooks/useAuthenticatedQuery';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';

interface OrderItem {
  id?: string;
  itemDescription: string;
  quantity: number;
  pages?: number;
  paper?: string;
  unitPrice: number;
  totalPrice: number;
}

interface Order {
  id: string;
  orderNumber: string;
  leaderId: string;
  leaderName: string;
  totalAmount: number;
  status: string;
  orderDate: string;
  createdAt: string;
  paidAmount?: number;
  balance?: number;
  details?: string;
  orderCategory?: string;
  pages?: number;
  paper?: string;
  items?: OrderItem[];
}


export default function Orders() {
  const { formatCurrency } = useCurrency();
  const { user, isLoading: authLoading } = useAuth();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [paymentHistoryOpen, setPaymentHistoryOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editingOrder, setEditingOrder] = useState<Order | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deletingOrder, setDeletingOrder] = useState<Order | null>(null);
  const [deletePaymentInfo, setDeletePaymentInfo] = useState<{ count: number, total: number } | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [formData, setFormData] = useState({
    orderNumber: '',
    leaderId: '',
    orderDate: new Date().toISOString().split('T')[0],
    status: 'Pending',
    items: [
      {
        itemDescription: '',
        quantity: 1,
        pages: 0,
        paper: '',
        unitPrice: 0,
        totalPrice: 0
      }
    ],
    initialPayment: 0,
    paymentMode: 'Cash',
    paymentDate: new Date().toISOString().split('T')[0],
    details: ''
  });
  const [editFormData, setEditFormData] = useState({
    orderNumber: '',
    leaderId: '',
    orderDate: '',
    status: 'Pending',
    items: [
      {
        itemDescription: '',
        quantity: 1,
        pages: 0,
        paper: '',
        unitPrice: 0,
        totalPrice: 0
      }
    ],
    details: '',
    amountReceived: 0
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

  // Item management functions
  const addItem = () => {
    setFormData({
      ...formData,
      items: [
        ...formData.items,
        {
          itemDescription: '',
          quantity: 1,
          pages: 0,
          paper: '',
          unitPrice: 0,
          totalPrice: 0
        }
      ]
    });
  };

  const removeItem = (index: number) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const updateItem = (index: number, field: string, value: any) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };

    // Auto-calculate total price when quantity or unitPrice changes
    if (field === 'quantity' || field === 'unitPrice') {
      const qty = field === 'quantity' ? value : newItems[index].quantity;
      const price = field === 'unitPrice' ? value : newItems[index].unitPrice;
      newItems[index].totalPrice = qty * price;
    }

    setFormData({ ...formData, items: newItems });
  };

  // Calculate total amount from all items
  const calculateTotal = () => {
    return formData.items.reduce((sum, item) => sum + item.totalPrice, 0);
  };

  // Edit Item management functions
  const addEditItem = () => {
    setEditFormData({
      ...editFormData,
      items: [
        ...editFormData.items,
        {
          itemDescription: '',
          quantity: 1,
          pages: 0,
          paper: '',
          unitPrice: 0,
          totalPrice: 0
        }
      ]
    });
  };

  const removeEditItem = (index: number) => {
    const newItems = editFormData.items.filter((_, i) => i !== index);
    setEditFormData({ ...editFormData, items: newItems });
  };

  const updateEditItem = (index: number, field: string, value: any) => {
    const newItems = [...editFormData.items];
    newItems[index] = { ...newItems[index], [field]: value };

    // Auto-calculate total price when quantity or unitPrice changes
    if (field === 'quantity' || field === 'unitPrice') {
      const qty = field === 'quantity' ? value : newItems[index].quantity;
      const price = field === 'unitPrice' ? value : newItems[index].unitPrice;
      newItems[index].totalPrice = qty * price;
    }

    setEditFormData({ ...editFormData, items: newItems });
  };

  // Calculate total amount for edit form
  const calculateEditTotal = () => {
    return editFormData.items.reduce((sum, item) => sum + item.totalPrice, 0);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.orderNumber.trim()) {
      toast.error('Please enter an order number');
      return;
    }

    if (!formData.leaderId) {
      toast.error('Please select a leader');
      return;
    }

    // Validate items
    if (!formData.items || formData.items.length === 0) {
      toast.error('Please add at least one item');
      return;
    }

    // Validate each item
    for (let i = 0; i < formData.items.length; i++) {
      const item = formData.items[i];
      if (!item.itemDescription.trim()) {
        toast.error(`Item ${i + 1}: Please enter item description`);
        return;
      }
      if (item.quantity <= 0) {
        toast.error(`Item ${i + 1}: Quantity must be greater than 0`);
        return;
      }
      if (item.unitPrice <= 0) {
        toast.error(`Item ${i + 1}: Unit price must be greater than 0`);
        return;
      }
    }

    const totalAmount = calculateTotal();
    if (totalAmount <= 0) {
      toast.error('Total amount must be greater than 0');
      return;
    }

    // Validate initial payment
    if (formData.initialPayment < 0) {
      toast.error('Initial payment cannot be negative');
      return;
    }

    if (formData.initialPayment > totalAmount) {
      toast.error(`Initial payment (${formatCurrency(formData.initialPayment)}) cannot exceed total amount (${formatCurrency(totalAmount)})`);
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
        status: 'Pending',
        items: [
          {
            itemDescription: '',
            quantity: 1,
            pages: 0,
            paper: '',
            unitPrice: 0,
            totalPrice: 0
          }
        ],
        initialPayment: 0,
        paymentMode: 'Cash',
        paymentDate: new Date().toISOString().split('T')[0],
        details: ''
      });
      loadOrders();
    } catch (error: any) {
      console.error('Order creation error:', error);
      toast.error(error?.message || 'Failed to create order');
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'Paid': return 'default';
      case 'Partially Paid': return 'secondary';
      case 'Delivered': return 'default';
      case 'In Production': return 'secondary';
      default: return 'outline';
    }
  };

  const handleDownloadInvoice = async (orderId: string) => {
    try {
      toast.loading('Generating invoice...', { id: 'download-invoice' });
      const token = localStorage.getItem('access_token');
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'}/orders/${orderId}/invoice`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      if (!response.ok) throw new Error('Failed to generate invoice');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `invoice-${orderId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      toast.success('Invoice downloaded successfully', { id: 'download-invoice' });
    } catch (error) {
      console.error('Error downloading invoice:', error);
      toast.error('Failed to download invoice', { id: 'download-invoice' });
    }
  };

  const handleViewPaymentHistory = (orderId: string) => {
    setSelectedOrderId(orderId);
    setPaymentHistoryOpen(true);
  };

  const handleEditOrder = (order: Order) => {
    setEditingOrder(order);

    // Prepare items - use existing items or create one from legacy fields
    let items = order.items && order.items.length > 0 ? order.items.map(item => ({
      itemDescription: item.itemDescription,
      quantity: item.quantity,
      pages: item.pages || 0,
      paper: item.paper || '',
      unitPrice: item.unitPrice,
      totalPrice: item.totalPrice
    })) : [
      {
        itemDescription: order.details || 'Product / Service Order',
        quantity: 1,
        pages: order.pages || 0,
        paper: order.paper || '',
        unitPrice: order.totalAmount,
        totalPrice: order.totalAmount
      }
    ];

    setEditFormData({
      orderNumber: order.orderNumber,
      leaderId: order.leaderId,
      orderDate: order.orderDate ? new Date(order.orderDate).toISOString().split('T')[0] : '',
      status: order.status,
      items: items,
      details: order.details || '',
      amountReceived: (order as any).amountReceived || 0
    });
    setEditDialogOpen(true);
  };

  const handleUpdateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingOrder) return;

    // Validation
    if (!editFormData.orderNumber.trim()) {
      toast.error('Please enter an order number');
      return;
    }

    if (!editFormData.leaderId) {
      toast.error('Please select a leader');
      return;
    }

    // Validate items
    if (!editFormData.items || editFormData.items.length === 0) {
      toast.error('Please add at least one item');
      return;
    }

    // Validate each item
    for (let i = 0; i < editFormData.items.length; i++) {
      const item = editFormData.items[i];
      if (!item.itemDescription.trim()) {
        toast.error(`Item ${i + 1}: Please enter item description`);
        return;
      }
      if (item.quantity <= 0) {
        toast.error(`Item ${i + 1}: Quantity must be greater than 0`);
        return;
      }
      if (item.unitPrice <= 0) {
        toast.error(`Item ${i + 1}: Unit price must be greater than 0`);
        return;
      }
    }

    const totalAmount = calculateEditTotal();
    if (totalAmount <= 0) {
      toast.error('Total amount must be greater than 0');
      return;
    }

    // Check if total amount is less than paid amount
    if (totalAmount < (editingOrder.paidAmount || 0)) {
      toast.error(`Total amount (${formatCurrency(totalAmount)}) cannot be less than already paid amount (${formatCurrency(editingOrder.paidAmount || 0)})`);
      return;
    }

    setIsProcessing(true);
    try {
      await updateOrder(editingOrder.id, editFormData);
      toast.success('Order updated successfully');
      setEditDialogOpen(false);
      setEditingOrder(null);
      loadOrders();
    } catch (error: any) {
      console.error('Order update error:', error);
      toast.error(error?.message || 'Failed to update order');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDeleteClick = async (order: Order) => {
    setDeletingOrder(order);

    // Fetch payment summary
    try {
      const summary = await getOrderPaymentSummary(order.id);
      setDeletePaymentInfo(summary);
    } catch (error) {
      console.error('Failed to fetch payment summary:', error);
      setDeletePaymentInfo(null);
    }

    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (!deletingOrder) return;

    setIsProcessing(true);
    try {
      await deleteOrder(deletingOrder.id);
      toast.success('Order deleted successfully');
      setDeleteDialogOpen(false);
      setDeletingOrder(null);
      setDeletePaymentInfo(null);
      loadOrders();
    } catch (error: any) {
      console.error('Order deletion error:', error);
      toast.error(error?.message || 'Failed to delete order');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-0">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">Orders</h1>
          <p className="text-sm sm:text-base text-muted-foreground">Manage customer orders</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="w-full sm:w-auto">
              <Plus className="w-4 h-4 mr-2" />
              Create Order
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-[95vw] sm:max-w-[425px] max-h-[90vh] overflow-y-auto">
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
                    {leaders.map((leader: any) => (
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
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <Label className="text-base font-semibold">Order Items *</Label>
                  <Button type="button" variant="outline" size="sm" onClick={addItem}>
                    <Plus className="w-4 h-4 mr-1" /> Add Item
                  </Button>
                </div>

                {formData.items.map((item, index) => (
                  <Card key={index} className="p-4 bg-slate-50">
                    <div className="space-y-3">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm font-medium text-slate-700">Item {index + 1}</span>
                        {formData.items.length > 1 && (
                          <Button
                            type="button"
                            variant="destructive"
                            size="sm"
                            onClick={() => removeItem(index)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>

                      <div>
                        <Label htmlFor={`item-desc-${index}`}>Item Description *</Label>
                        <Input
                          id={`item-desc-${index}`}
                          value={item.itemDescription}
                          onChange={(e) => updateItem(index, 'itemDescription', e.target.value)}
                          placeholder="e.g., Copy, Register, Diary"
                          required
                        />
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label htmlFor={`item-qty-${index}`}>Quantity *</Label>
                          <Input
                            id={`item-qty-${index}`}
                            type="number"
                            min="1"
                            value={item.quantity}
                            onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 1)}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor={`item-price-${index}`}>Unit Price *</Label>
                          <Input
                            id={`item-price-${index}`}
                            type="number"
                            step="0.01"
                            min="0"
                            value={item.unitPrice}
                            onChange={(e) => updateItem(index, 'unitPrice', parseFloat(e.target.value) || 0)}
                            required
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <Label htmlFor={`item-pages-${index}`}>Pages</Label>
                          <Input
                            id={`item-pages-${index}`}
                            type="number"
                            min="0"
                            value={item.pages}
                            onChange={(e) => updateItem(index, 'pages', parseInt(e.target.value) || 0)}
                            placeholder="Optional"
                          />
                        </div>
                        <div>
                          <Label htmlFor={`item-paper-${index}`}>Paper</Label>
                          <Input
                            id={`item-paper-${index}`}
                            type="text"
                            maxLength={200}
                            value={item.paper}
                            onChange={(e) => updateItem(index, 'paper', e.target.value)}
                            placeholder="e.g., A4 80gsm"
                          />
                        </div>
                      </div>

                      <div className="pt-2 border-t">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-slate-600">Item Total:</span>
                          <span className="text-base font-semibold text-blue-600">
                            {formatCurrency(item.totalPrice)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}

                <div className="p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-bold text-blue-900">Order Total:</span>
                    <span className="text-xl font-bold text-blue-600">
                      {formatCurrency(calculateTotal())}
                    </span>
                  </div>
                </div>
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
              <div>
                <Label htmlFor="details">Order Details</Label>
                <Textarea
                  id="details"
                  value={formData.details}
                  onChange={(e) => setFormData({ ...formData, details: e.target.value })}
                  placeholder="Add any additional notes or details about this order..."
                  rows={3}
                  maxLength={2000}
                  className="resize-none"
                />
                {formData.details && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {formData.details.length}/2000 characters
                  </p>
                )}
              </div>

              <div className="border-t pt-4 mt-4">
                <h4 className="font-medium mb-3">Initial Payment (Optional)</h4>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="initialPayment">Amount Received</Label>
                    <Input
                      id="initialPayment"
                      type="number"
                      step="0.01"
                      value={formData.initialPayment}
                      onChange={(e) => setFormData({ ...formData, initialPayment: parseFloat(e.target.value) || 0 })}
                      placeholder="0.00"
                    />
                  </div>

                  {/* Remaining Balance Display */}
                  {calculateTotal() > 0 && (
                    <div className={`p-4 rounded-lg border-2 ${formData.initialPayment >= calculateTotal()
                      ? 'bg-green-50 border-green-300'
                      : formData.initialPayment > 0
                        ? 'bg-orange-50 border-orange-300'
                        : 'bg-blue-50 border-blue-300'
                      }`}>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Total Amount:</span>
                          <span className="font-semibold">{formatCurrency(calculateTotal())}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Initial Payment:</span>
                          <span className="font-semibold text-green-600">
                            {formatCurrency(formData.initialPayment)}
                          </span>
                        </div>
                        <div className="border-t pt-2">
                          <div className="flex justify-between">
                            <span className="font-medium">Remaining Balance:</span>
                            <span className={`text-xl font-bold ${formData.initialPayment >= calculateTotal()
                              ? 'text-green-600'
                              : formData.initialPayment > 0
                                ? 'text-orange-600'
                                : 'text-blue-600'
                              }`}>
                              {formatCurrency(calculateTotal() - formData.initialPayment)}
                            </span>
                          </div>
                          {/* Progress Bar */}
                          <div className="mt-2 w-full bg-gray-200 rounded-full h-2">
                            <div
                              className={`h-2 rounded-full transition-all ${formData.initialPayment >= calculateTotal()
                                ? 'bg-green-600'
                                : 'bg-orange-500'
                                }`}
                              style={{
                                width: `${Math.min((formData.initialPayment / calculateTotal()) * 100, 100)}%`
                              }}
                            />
                          </div>
                          <p className="text-xs text-muted-foreground mt-1 text-center">
                            {formData.initialPayment >= calculateTotal()
                              ? '✓ Fully Paid'
                              : formData.initialPayment > 0
                                ? `${((formData.initialPayment / calculateTotal()) * 100).toFixed(1)}% Paid`
                                : 'No payment yet'}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {formData.initialPayment > 0 && (
                    <>
                      <div>
                        <Label htmlFor="paymentMode">Payment Mode</Label>
                        <Select value={formData.paymentMode} onValueChange={(value) => setFormData({ ...formData, paymentMode: value })}>
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
                        <Label htmlFor="paymentDate">Payment Date</Label>
                        <Input
                          id="paymentDate"
                          type="date"
                          value={formData.paymentDate}
                          onChange={(e) => setFormData({ ...formData, paymentDate: e.target.value })}
                        />
                      </div>
                    </>
                  )}
                </div>
              </div>
              <Button type="submit" className="w-full">Create Order</Button>
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
        <div className="space-y-3 sm:space-y-4">
          {orders.map((order: any) => (
            <Card key={order.id} className="card-hover">
              <CardContent className="p-4 sm:p-6">
                <div className="flex flex-col gap-4">
                  {/* Header Section */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div className="flex items-start gap-3 sm:gap-4 flex-1">
                      <div className="p-2 sm:p-3 rounded-full bg-primary/10 flex-shrink-0">
                        <ShoppingCart className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-base sm:text-lg truncate">{order.orderNumber !== 'N/A' ? `Order #${order.orderNumber}` : order.orderNumber}</h3>
                        <p className="text-xs sm:text-sm text-muted-foreground">
                          {order.orderDate ? format(new Date(order.orderDate), 'MMM dd, yyyy') : 'N/A'}
                        </p>
                        <p className="text-xs sm:text-sm text-muted-foreground mt-1 truncate">
                          Leader: {order.leaderName || 'N/A'}
                        </p>
                      </div>
                    </div>
                    <Badge variant={getStatusColor(order.status)} className="text-xs flex-shrink-0 self-start sm:self-center">
                      {order.status || 'Pending'}
                    </Badge>
                  </div>

                  {/* Payment Details Section */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 bg-gray-50 rounded-lg border">
                    <div>
                      <p className="text-xs text-muted-foreground">Total Amount</p>
                      <p className="text-sm font-semibold">{formatCurrency(order.totalAmount)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Paid</p>
                      <p className="text-sm font-semibold text-green-600">
                        {formatCurrency(order.paidAmount || 0)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Balance</p>
                      <p className="text-sm font-semibold text-orange-600">
                        {formatCurrency(order.balance || order.totalAmount)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Progress</p>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full transition-all"
                            style={{
                              width: `${Math.min(((order.paidAmount || 0) / order.totalAmount) * 100, 100)}%`
                            }}
                          />
                        </div>
                        <span className="text-xs font-medium">
                          {Math.round(((order.paidAmount || 0) / order.totalAmount) * 100)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Order Details Section */}
                  {order.details && (
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-xs font-medium text-blue-900 mb-1">Order Details:</p>
                      <p className="text-sm text-blue-800 whitespace-pre-wrap">{order.details}</p>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex flex-wrap gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditOrder(order)}
                      className="flex items-center gap-1"
                      disabled={isProcessing}
                    >
                      <Edit2 className="w-3 h-3" />
                      <span className="hidden sm:inline">Edit</span>
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewPaymentHistory(order.id)}
                      className="flex items-center gap-1"
                    >
                      <Eye className="w-3 h-3" />
                      <span className="hidden sm:inline">View</span> Payments
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDownloadInvoice(order.id)}
                      className="flex items-center gap-1"
                    >
                      <Download className="w-3 h-3" />
                      <span className="hidden sm:inline">Download</span> Invoice
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteClick(order)}
                      className="flex items-center gap-1"
                      disabled={isProcessing}
                    >
                      <Trash2 className="w-3 h-3" />
                      <span className="hidden sm:inline">Delete</span>
                    </Button>
                    {(order.status === 'Pending' || order.status === 'Partially Paid') && order.balance > 0 && (
                      <Button
                        variant="default"
                        size="sm"
                        onClick={() => {
                          // Navigate to payments page with this order pre-selected
                          window.location.href = `/payments?orderId=${order.id}&leaderId=${order.leaderId}`;
                        }}
                        className="flex items-center gap-1 ml-auto"
                      >
                        <DollarSign className="w-3 h-3" />
                        Record Payment
                      </Button>
                    )}
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

      {/* Payment History Dialog */}
      <Dialog open={paymentHistoryOpen} onOpenChange={setPaymentHistoryOpen}>
        <DialogContent className="max-w-[95vw] sm:max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Payment History</DialogTitle>
          </DialogHeader>
          {selectedOrderId ? (() => {
            const selectedOrder = orders.find((o: any) => o.id === selectedOrderId);

            if (!selectedOrder) {
              console.error('[Orders] Selected order not found:', selectedOrderId);
              return (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">Order not found. Please try again.</p>
                </div>
              );
            }

            console.log('[Orders] Rendering PaymentHistory for order:', {
              orderId: selectedOrderId,
              orderNumber: selectedOrder.orderNumber,
              totalAmount: selectedOrder.totalAmount,
              balance: selectedOrder.balance
            });

            return (
              <PaymentHistory
                orderId={selectedOrderId}
                orderTotal={selectedOrder.totalAmount}
                currentBalance={selectedOrder.balance || selectedOrder.totalAmount}
                onPaymentUpdated={() => {
                  console.log('[Orders] Payment updated, refreshing orders list');
                  loadOrders();
                }}
              />
            );
          })() : (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No order selected</p>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Order Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-[95vw] sm:max-w-[425px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Order</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleUpdateOrder} className="space-y-4">
            <div>
              <Label htmlFor="edit-orderNumber">Order Number *</Label>
              <Input
                id="edit-orderNumber"
                value={editFormData.orderNumber}
                disabled
                className="bg-muted"
              />
              <p className="text-xs text-muted-foreground mt-1">Order number cannot be changed</p>
            </div>
            <div>
              <Label htmlFor="edit-leader">Leader *</Label>
              <Select value={editFormData.leaderId} onValueChange={(value) => setEditFormData({ ...editFormData, leaderId: value })}>
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
            <div>
              <Label htmlFor="edit-orderDate">Order Date *</Label>
              <Input
                id="edit-orderDate"
                type="date"
                value={editFormData.orderDate}
                onChange={(e) => setEditFormData({ ...editFormData, orderDate: e.target.value })}
                required
              />
            </div>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <Label className="text-base font-semibold">Order Items *</Label>
                <Button type="button" variant="outline" size="sm" onClick={addEditItem}>
                  <Plus className="w-4 h-4 mr-1" /> Add Item
                </Button>
              </div>

              {editFormData.items.map((item, index) => (
                <Card key={index} className="p-4 bg-slate-50">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium text-slate-700">Item {index + 1}</span>
                      {editFormData.items.length > 1 && (
                        <Button
                          type="button"
                          variant="destructive"
                          size="sm"
                          onClick={() => removeEditItem(index)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
                    </div>

                    <div>
                      <Label htmlFor={`edit-item-desc-${index}`}>Item Description *</Label>
                      <Input
                        id={`edit-item-desc-${index}`}
                        value={item.itemDescription}
                        onChange={(e) => updateEditItem(index, 'itemDescription', e.target.value)}
                        placeholder="e.g., Copy, Register, Diary"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor={`edit-item-qty-${index}`}>Quantity *</Label>
                        <Input
                          id={`edit-item-qty-${index}`}
                          type="number"
                          min="1"
                          value={item.quantity}
                          onChange={(e) => updateEditItem(index, 'quantity', parseInt(e.target.value) || 1)}
                          required
                        />
                      </div>
                      <div>
                        <Label htmlFor={`edit-item-price-${index}`}>Unit Price *</Label>
                        <Input
                          id={`edit-item-price-${index}`}
                          type="number"
                          step="0.01"
                          min="0"
                          value={item.unitPrice}
                          onChange={(e) => updateEditItem(index, 'unitPrice', parseFloat(e.target.value) || 0)}
                          required
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <Label htmlFor={`edit-item-pages-${index}`}>Pages</Label>
                        <Input
                          id={`edit-item-pages-${index}`}
                          type="number"
                          min="0"
                          value={item.pages}
                          onChange={(e) => updateEditItem(index, 'pages', parseInt(e.target.value) || 0)}
                          placeholder="Optional"
                        />
                      </div>
                      <div>
                        <Label htmlFor={`edit-item-paper-${index}`}>Paper</Label>
                        <Input
                          id={`edit-item-paper-${index}`}
                          type="text"
                          maxLength={200}
                          value={item.paper}
                          onChange={(e) => updateEditItem(index, 'paper', e.target.value)}
                          placeholder="e.g., A4 80gsm"
                        />
                      </div>
                    </div>

                    <div className="pt-2 border-t">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-600">Item Total:</span>
                        <span className="text-base font-semibold text-blue-600">
                          {formatCurrency(item.totalPrice)}
                        </span>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}

              <div className="p-4 bg-blue-50 rounded-lg border-2 border-blue-200">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-bold text-blue-900">Order Total:</span>
                  <span className="text-xl font-bold text-blue-600">
                    {formatCurrency(calculateEditTotal())}
                  </span>
                </div>
                {editingOrder && (editingOrder.paidAmount || 0) > 0 && (
                  <p className="text-right text-xs text-muted-foreground mt-1">
                    Already paid: {formatCurrency(editingOrder.paidAmount || 0)}
                  </p>
                )}
              </div>
            </div>
            <div>
              <Label htmlFor="edit-status">Status</Label>
              <Select value={editFormData.status} onValueChange={(value) => setEditFormData({ ...editFormData, status: value })}>
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
            <div>
              <Label htmlFor="edit-amountReceived">Amount Received</Label>
              <Input
                id="edit-amountReceived"
                type="number"
                min="0"
                step="0.01"
                value={editFormData.amountReceived}
                onChange={(e) => setEditFormData({ ...editFormData, amountReceived: parseFloat(e.target.value) || 0 })}
                placeholder="Enter amount received"
              />
              <p className="text-xs text-muted-foreground mt-1">Initial payment or amount received for this order</p>
            </div>
            <div>
              <Label htmlFor="edit-details">Order Details</Label>
              <Textarea
                id="edit-details"
                value={editFormData.details}
                onChange={(e) => setEditFormData({ ...editFormData, details: e.target.value })}
                placeholder="Add any additional notes or details about this order..."
                rows={3}
                maxLength={2000}
                className="resize-none"
              />
              {editFormData.details && (
                <p className="text-xs text-muted-foreground mt-1">
                  {editFormData.details.length}/2000 characters
                </p>
              )}
            </div>
            <div className="flex gap-2">
              <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)} className="flex-1" disabled={isProcessing}>
                Cancel
              </Button>
              <Button type="submit" className="flex-1" disabled={isProcessing}>
                {isProcessing ? 'Updating...' : 'Update Order'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Order Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Order</AlertDialogTitle>
            <AlertDialogDescription className="space-y-3">
              <p>Are you sure you want to delete this order? This action cannot be undone.</p>

              {deletingOrder && (
                <div className="p-3 bg-muted rounded-lg space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Order Number:</span>
                    <span>{deletingOrder.orderNumber}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Total Amount:</span>
                    <span>{formatCurrency(deletingOrder.totalAmount)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Leader:</span>
                    <span>{deletingOrder.leaderName}</span>
                  </div>
                </div>
              )}

              {deletePaymentInfo && deletePaymentInfo.count > 0 && (
                <div className="p-3 bg-destructive/10 border border-destructive/30 rounded-lg">
                  <p className="text-sm font-semibold text-destructive mb-2">⚠️ Warning: Payment Records</p>
                  <p className="text-sm text-destructive">
                    This order has <strong>{deletePaymentInfo.count}</strong> payment(s) totaling <strong>{formatCurrency(deletePaymentInfo.total)}</strong>.
                  </p>
                  <p className="text-sm text-destructive mt-1">
                    Deleting this order will also delete all associated payment records.
                  </p>
                </div>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isProcessing}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={isProcessing}
            >
              {isProcessing ? 'Deleting...' : 'Delete Order'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div >
  );
}
