import { useState, useEffect, useCallback } from 'react';
import { Download, Calendar, CreditCard, Receipt, TrendingDown, Pencil, Trash2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { updatePayment, deletePayment } from '@/lib/mock-api';

interface Payment {
    id: string;
    amount: number;
    method: string;
    paymentDate: string;
    referenceNumber?: string;
    status: string;
}

interface PaymentHistoryProps {
    orderId: string;
    orderTotal: number;
    currentBalance: number;
    onDownloadReceipt?: (paymentId: string) => void;
    onPaymentUpdated?: () => void; // Callback to refresh parent component
}

export function PaymentHistory({ orderId, orderTotal, currentBalance, onDownloadReceipt, onPaymentUpdated }: PaymentHistoryProps) {
    const [payments, setPayments] = useState<Payment[]>([]);
    const [loading, setLoading] = useState(true);

    // Edit payment state
    const [editingPayment, setEditingPayment] = useState<Payment | null>(null);
    const [editDialogOpen, setEditDialogOpen] = useState(false);
    const [editFormData, setEditFormData] = useState({
        amount: 0,
        method: 'Cash',
        paymentDate: '',
        referenceNumber: ''
    });
    const [editLoading, setEditLoading] = useState(false);

    // Delete payment state
    const [deletingPayment, setDeletingPayment] = useState<Payment | null>(null);
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [deleteLoading, setDeleteLoading] = useState(false);

    const fetchPaymentHistory = useCallback(async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('access_token');

            console.log(`[PaymentHistory] Fetching payments for order: ${orderId}`);

            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8080/api/v1'}/payments/?orderId=${orderId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) {
                console.error(`[PaymentHistory] API request failed: ${response.status} ${response.statusText}`);
                throw new Error('Failed to fetch payment history');
            }

            // Backend now filters by orderId and sorts by payment_date ascending
            const orderPayments = await response.json();

            console.log(`[PaymentHistory] ✓ Fetched ${orderPayments.length} payments for order ${orderId}`);
            console.log('[PaymentHistory] Raw API Response:', orderPayments);

            if (orderPayments.length > 0) {
                console.log('[PaymentHistory] First payment sample:', orderPayments[0]);
                console.log('[PaymentHistory] Field names:', Object.keys(orderPayments[0]));
            }

            setPayments(orderPayments);
        } catch (error) {
            console.error('[PaymentHistory] Error fetching payment history:', error);
            toast.error('Failed to load payment history');
            // Set empty array on error to show empty state instead of blank screen
            setPayments([]);
        } finally {
            // Always set loading to false to prevent infinite loading state
            setLoading(false);
        }
    }, [orderId]);

    useEffect(() => {
        fetchPaymentHistory();
    }, [fetchPaymentHistory]);

    const handleDownloadReceipt = async (paymentId: string) => {
        if (onDownloadReceipt) {
            onDownloadReceipt(paymentId);
        } else {
            try {
                toast.loading('Generating receipt...', { id: 'download-receipt' });
                const token = localStorage.getItem('access_token');
                const response = await fetch(
                    `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8080/api/v1'}/payments/${paymentId}/receipt`,
                    {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${token}`
                        }
                    }
                );

                if (!response.ok) throw new Error('Failed to generate receipt');

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `receipt-${paymentId}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                toast.success('Receipt downloaded successfully', { id: 'download-receipt' });
            } catch (error) {
                console.error('Error downloading receipt:', error);
                toast.error('Failed to download receipt', { id: 'download-receipt' });
            }
        }
    };

    const handleEditClick = (payment: Payment) => {
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

        // Calculate what the new total paid would be if this edit goes through
        const amountDifference = editFormData.amount - editingPayment.amount;
        const currentTotalPaid = payments.reduce((sum, p) => sum + p.amount, 0);
        const newTotalPaid = currentTotalPaid + amountDifference;

        // Check for overpayment
        if (newTotalPaid > orderTotal) {
            toast.error(`Payment update would cause overpayment. Order total: Rs ${orderTotal.toLocaleString()}, Would result in total paid: Rs ${newTotalPaid.toLocaleString()} (exceeds by Rs ${(newTotalPaid - orderTotal).toLocaleString()})`);
            return;
        }

        try {
            setEditLoading(true);
            await updatePayment(editingPayment.id, editFormData);
            toast.success('Payment updated successfully');
            setEditDialogOpen(false);
            setEditingPayment(null);

            // Refresh payment history
            await fetchPaymentHistory();

            // Notify parent component to refresh
            if (onPaymentUpdated) {
                onPaymentUpdated();
            }
        } catch (error: any) {
            console.error('Error updating payment:', error);
            toast.error(error?.message || 'Failed to update payment');
        } finally {
            setEditLoading(false);
        }
    };

    const handleDeleteClick = (payment: Payment) => {
        setDeletingPayment(payment);
        setDeleteDialogOpen(true);
    };

    const handleDeleteConfirm = async () => {
        if (!deletingPayment) return;

        try {
            setDeleteLoading(true);
            await deletePayment(deletingPayment.id);
            toast.success('Payment deleted successfully');
            setDeleteDialogOpen(false);
            setDeletingPayment(null);

            // Refresh payment history
            await fetchPaymentHistory();

            // Notify parent component to refresh
            if (onPaymentUpdated) {
                onPaymentUpdated();
            }
        } catch (error: any) {
            console.error('Error deleting payment:', error);
            toast.error(error?.message || 'Failed to delete payment');
        } finally {
            setDeleteLoading(false);
        }
    }

    const getMethodIcon = (method: string) => {
        const icons: Record<string, JSX.Element> = {
            'Cash': <span className="text-lg">💵</span>,
            'Bank Transfer': <span className="text-lg">🏦</span>,
            'Cheque': <span className="text-lg">📝</span>,
            'UPI': <span className="text-lg">📱</span>
        };
        return icons[method] || <CreditCard className="w-4 h-4" />;
    };

    const getMethodColor = (method: string) => {
        const colors: Record<string, string> = {
            'Cash': 'bg-green-100 text-green-700 border-green-200',
            'Bank Transfer': 'bg-blue-100 text-blue-700 border-blue-200',
            'Cheque': 'bg-purple-100 text-purple-700 border-purple-200',
            'UPI': 'bg-orange-100 text-orange-700 border-orange-200'
        };
        return colors[method] || 'bg-gray-100 text-gray-700 border-gray-200';
    };

    const calculateRunningBalance = (index: number) => {
        const paidSoFar = payments.slice(0, index + 1).reduce((sum, p) => sum + p.amount, 0);
        return orderTotal - paidSoFar;
    };

    const totalPaid = payments.reduce((sum, p) => sum + p.amount, 0);

    if (loading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Receipt className="w-5 h-5" />
                        Payment History
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-3">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-20 bg-muted rounded-lg animate-pulse"></div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        );
    }

    if (payments.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <Receipt className="w-5 h-5" />
                        Payment History
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-center py-8">
                        <Receipt className="w-12 h-12 mx-auto text-muted-foreground mb-3" />
                        <p className="text-muted-foreground">No payments recorded yet</p>
                    </div>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-2">
                    <Receipt className="w-5 h-5" />
                    Payment History
                    <Badge variant="outline" className="ml-auto">
                        {payments.length} {payments.length === 1 ? 'Payment' : 'Payments'}
                    </Badge>
                </CardTitle>
            </CardHeader>
            <CardContent>
                {/* Payment Summary */}
                <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                    <div>
                        <p className="text-xs text-blue-600 font-medium">Total Amount</p>
                        <p className="text-lg font-bold text-blue-900">Rs {orderTotal.toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-xs text-green-600 font-medium">Total Paid</p>
                        <p className="text-lg font-bold text-green-900">Rs {totalPaid.toLocaleString()}</p>
                    </div>
                    <div>
                        <p className="text-xs text-orange-600 font-medium">Balance</p>
                        <p className="text-lg font-bold text-orange-900">Rs {currentBalance.toLocaleString()}</p>
                    </div>
                </div>

                {/* Payment Timeline */}
                <div className="space-y-4">
                    {payments.map((payment, index) => {
                        const runningBalance = calculateRunningBalance(index);
                        const isLastPayment = index === payments.length - 1;

                        return (
                            <div key={payment.id} className="relative">
                                {/* Timeline connector */}
                                {!isLastPayment && (
                                    <div className="absolute left-6 top-12 bottom-0 w-0.5 bg-gradient-to-b from-blue-300 to-blue-100"></div>
                                )}

                                <div className="flex gap-4">
                                    {/* Timeline dot */}
                                    <div className="flex-shrink-0 w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center text-white font-bold shadow-lg">
                                        {index + 1}
                                    </div>

                                    {/* Payment card */}
                                    <div className="flex-1 bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
                                        <div className="flex items-start justify-between mb-3">
                                            <div className="flex-1">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <Badge className={`${getMethodColor(payment.method)} border`}>
                                                        <span className="mr-1">{getMethodIcon(payment.method)}</span>
                                                        {payment.method}
                                                    </Badge>
                                                    {payment.referenceNumber && (
                                                        <span className="text-xs text-muted-foreground">
                                                            Ref: {payment.referenceNumber}
                                                        </span>
                                                    )}
                                                </div>
                                                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                                    <Calendar className="w-3 h-3" />
                                                    {(() => {
                                                        try {
                                                            const date = new Date(payment.paymentDate);
                                                            if (isNaN(date.getTime())) {
                                                                console.error('[PaymentHistory] Invalid date:', payment.paymentDate);
                                                                return 'Invalid date';
                                                            }
                                                            return format(date, 'MMM dd, yyyy');
                                                        } catch (error) {
                                                            console.error('[PaymentHistory] Date parsing error:', error, payment.paymentDate);
                                                            return 'Date unavailable';
                                                        }
                                                    })()}
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-2xl font-bold text-green-600">
                                                    Rs {payment.amount.toLocaleString()}
                                                </p>
                                                <div className="flex gap-2 mt-2">
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => handleEditClick(payment)}
                                                        className="hover:bg-blue-50 hover:border-blue-300"
                                                    >
                                                        <Pencil className="w-3 h-3 mr-1" />
                                                        Edit
                                                    </Button>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => handleDeleteClick(payment)}
                                                        className="hover:bg-red-50 hover:border-red-300 text-red-600"
                                                    >
                                                        <Trash2 className="w-3 h-3 mr-1" />
                                                        Delete
                                                    </Button>
                                                    <Button
                                                        variant="outline"
                                                        size="sm"
                                                        onClick={() => handleDownloadReceipt(payment.id)}
                                                        className="hover:bg-green-50 hover:border-green-300"
                                                    >
                                                        <Download className="w-3 h-3 mr-1" />
                                                        Receipt
                                                    </Button>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Running balance */}
                                        <div className="flex items-center gap-2 pt-3 border-t border-gray-100">
                                            <TrendingDown className="w-4 h-4 text-blue-500" />
                                            <span className="text-sm text-muted-foreground">
                                                Balance after payment:
                                            </span>
                                            <span className="text-sm font-semibold text-blue-900">
                                                Rs {runningBalance.toLocaleString()}
                                            </span>
                                            {runningBalance === 0 && (
                                                <Badge className="ml-auto bg-green-100 text-green-700 border-green-200">
                                                    ✓ Fully Paid
                                                </Badge>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </CardContent>

            {/* Edit Payment Dialog */}
            <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
                <DialogContent className="max-w-md">
                    <DialogHeader>
                        <DialogTitle>Edit Payment</DialogTitle>
                    </DialogHeader>

                    {editingPayment && (
                        <div className="space-y-4">
                            {/* Order Details */}
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                                <p className="text-sm font-medium text-blue-900 mb-2">Order Details</p>
                                <div className="grid grid-cols-2 gap-2 text-sm">
                                    <div>
                                        <p className="text-blue-600">Total Amount</p>
                                        <p className="font-semibold text-blue-900">Rs {orderTotal.toLocaleString()}</p>
                                    </div>
                                    <div>
                                        <p className="text-blue-600">Current Balance</p>
                                        <p className="font-semibold text-blue-900">Rs {currentBalance.toLocaleString()}</p>
                                    </div>
                                </div>
                            </div>

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

                            {/* Preview of changes */}
                            {editFormData.amount !== editingPayment.amount && (
                                <div className={`rounded-lg p-3 border ${(payments.reduce((sum, p) => sum + p.amount, 0) - editingPayment.amount + editFormData.amount) > orderTotal
                                    ? 'bg-red-50 border-red-200'
                                    : 'bg-green-50 border-green-200'
                                    }`}>
                                    <p className={`text-xs font-medium mb-1 ${(payments.reduce((sum, p) => sum + p.amount, 0) - editingPayment.amount + editFormData.amount) > orderTotal
                                        ? 'text-red-700'
                                        : 'text-green-700'
                                        }`}>
                                        {(payments.reduce((sum, p) => sum + p.amount, 0) - editingPayment.amount + editFormData.amount) > orderTotal
                                            ? '⚠️ Warning: Would cause overpayment'
                                            : '✓ New balance after update'
                                        }
                                    </p>
                                    <p className={`text-sm font-semibold ${(payments.reduce((sum, p) => sum + p.amount, 0) - editingPayment.amount + editFormData.amount) > orderTotal
                                        ? 'text-red-900'
                                        : 'text-green-900'
                                        }`}>
                                        Rs {(orderTotal - (payments.reduce((sum, p) => sum + p.amount, 0) - editingPayment.amount + editFormData.amount)).toLocaleString()}
                                    </p>
                                </div>
                            )}
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
                                                <span className="font-semibold text-gray-900">Rs {deletingPayment.amount.toLocaleString()}</span>
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
                                        </div>
                                    </div>

                                    {/* Impact Preview */}
                                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                                        <p className="text-xs font-medium text-orange-700 mb-1">Impact on Order Balance:</p>
                                        <div className="flex justify-between items-center text-sm">
                                            <span className="text-orange-600">Current Balance:</span>
                                            <span className="font-semibold text-orange-900">Rs {currentBalance.toLocaleString()}</span>
                                        </div>
                                        <div className="flex justify-between items-center text-sm mt-1">
                                            <span className="text-orange-600">New Balance:</span>
                                            <span className="font-bold text-orange-900">Rs {(currentBalance + deletingPayment.amount).toLocaleString()}</span>
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
        </Card>
    );
}
