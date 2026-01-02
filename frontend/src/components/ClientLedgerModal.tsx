import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useCurrency } from '@/hooks/useCurrency';
import { useAuthenticatedQuery } from '@/hooks/useAuthenticatedQuery';
import { api } from '@/lib/api-client';
import { toast } from 'sonner';
import { format } from 'date-fns';
import { DollarSign, ShoppingCart, CreditCard, TrendingUp, TrendingDown } from 'lucide-react';

interface ClientLedgerModalProps {
    clientId: string;
    clientName: string;
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

interface Order {
    id: string;
    order_number: string;
    order_date: string;
    total_amount: number;
    paid_amount: number;
    balance: number;
    status: string;
    payments: Payment[];
}

interface Payment {
    id: string;
    payment_date: string;
    amount: number;
    mode: string;
    reference_number: string;
}

interface LedgerData {
    client: {
        id: string;
        name: string;
        type: string;
        contact: string;
        address: string;
        opening_balance: number;
    };
    summary: {
        total_orders: number;
        total_order_amount: number;
        total_paid: number;
        total_outstanding: number;
    };
    orders: Order[];
    unallocated_payments: Payment[];
}

export function ClientLedgerModal({ clientId, clientName, open, onOpenChange }: ClientLedgerModalProps) {
    const { formatCurrency } = useCurrency();

    const { data: ledgerData, loading } = useAuthenticatedQuery<LedgerData>(
        () => api.getLeaderLedger(clientId),
        {
            isReady: open && !!clientId,
            onError: () => toast.error('Failed to load ledger data'),
            queryKey: ['clientLedger', clientId]
        }
    );

    const getStatusBadge = (status: string) => {
        const variants: Record<string, { variant: any; className: string }> = {
            'Paid': { variant: 'default', className: 'bg-green-100 text-green-700 border-green-300' },
            'Partially Paid': { variant: 'secondary', className: 'bg-orange-100 text-orange-700 border-orange-300' },
            'Pending': { variant: 'outline', className: 'bg-red-100 text-red-700 border-red-300' }
        };
        return variants[status] || variants['Pending'];
    };

    const getBalanceColor = (balance: number) => {
        if (balance === 0) return 'text-green-600';
        if (balance > 0) return 'text-orange-600';
        return 'text-gray-600';
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                    <DialogTitle className="text-2xl">Client Ledger - {clientName}</DialogTitle>
                </DialogHeader>

                {loading ? (
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                            <div key={i} className="h-24 bg-muted rounded-lg animate-pulse"></div>
                        ))}
                    </div>
                ) : ledgerData ? (
                    <div className="space-y-6">
                        {/* Summary Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <Card>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                                        <ShoppingCart className="w-4 h-4" />
                                        Total Orders
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-2xl font-bold">{ledgerData.summary.total_orders}</p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {formatCurrency(ledgerData.summary.total_order_amount)}
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                                        <CreditCard className="w-4 h-4" />
                                        Total Paid
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className="text-2xl font-bold text-green-600">
                                        {formatCurrency(ledgerData.summary.total_paid)}
                                    </p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {ledgerData.summary.total_order_amount > 0
                                            ? `${((ledgerData.summary.total_paid / ledgerData.summary.total_order_amount) * 100).toFixed(1)}% paid`
                                            : '0% paid'}
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                                        <DollarSign className="w-4 h-4" />
                                        Outstanding
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className={`text-2xl font-bold ${ledgerData.summary.total_outstanding > 0 ? 'text-red-600' : 'text-green-600'
                                        }`}>
                                        {formatCurrency(ledgerData.summary.total_outstanding)}
                                    </p>
                                    <p className="text-xs text-muted-foreground mt-1">
                                        {ledgerData.summary.total_outstanding > 0 ? 'Amount due' : 'All settled'}
                                    </p>
                                </CardContent>
                            </Card>

                            <Card>
                                <CardHeader className="pb-2">
                                    <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                                        {ledgerData.client.opening_balance >= 0 ? (
                                            <TrendingUp className="w-4 h-4" />
                                        ) : (
                                            <TrendingDown className="w-4 h-4" />
                                        )}
                                        Opening Balance
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <p className={`text-2xl font-bold ${ledgerData.client.opening_balance >= 0 ? 'text-green-600' : 'text-red-600'
                                        }`}>
                                        {formatCurrency(ledgerData.client.opening_balance)}
                                    </p>
                                    <p className="text-xs text-muted-foreground mt-1">Initial balance</p>
                                </CardContent>
                            </Card>
                        </div>

                        {/* Orders Table */}
                        <div>
                            <h3 className="text-lg font-semibold mb-3">Orders & Payments</h3>
                            {ledgerData.orders.length === 0 ? (
                                <Card>
                                    <CardContent className="py-8 text-center text-muted-foreground">
                                        No orders found for this client
                                    </CardContent>
                                </Card>
                            ) : (
                                <div className="space-y-4">
                                    {ledgerData.orders.map((order) => (
                                        <Card key={order.id} className="border-l-4" style={{
                                            borderLeftColor: order.balance === 0 ? '#22c55e' : order.paid_amount > 0 ? '#f97316' : '#ef4444'
                                        }}>
                                            <CardHeader className="pb-3">
                                                <div className="flex items-center justify-between">
                                                    <div>
                                                        <CardTitle className="text-base">Order #{order.order_number}</CardTitle>
                                                        <p className="text-sm text-muted-foreground">
                                                            {order.order_date ? format(new Date(order.order_date), 'MMM dd, yyyy') : 'N/A'}
                                                        </p>
                                                    </div>
                                                    <Badge {...getStatusBadge(order.status)} className="border">
                                                        {order.status}
                                                    </Badge>
                                                </div>
                                            </CardHeader>
                                            <CardContent className="space-y-3">
                                                {/* Order Financial Summary */}
                                                <div className="grid grid-cols-3 gap-4 p-3 bg-gray-50 rounded-lg">
                                                    <div>
                                                        <p className="text-xs text-muted-foreground">Total Amount</p>
                                                        <p className="font-semibold">{formatCurrency(order.total_amount)}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs text-muted-foreground">Paid Amount</p>
                                                        <p className="font-semibold text-green-600">{formatCurrency(order.paid_amount)}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs text-muted-foreground">Balance</p>
                                                        <p className={`font-bold ${getBalanceColor(order.balance)}`}>
                                                            {formatCurrency(order.balance)}
                                                        </p>
                                                    </div>
                                                </div>

                                                {/* Payment Progress Bar */}
                                                <div className="w-full bg-gray-200 rounded-full h-2">
                                                    <div
                                                        className={`h-2 rounded-full ${order.balance === 0 ? 'bg-green-600' : 'bg-orange-500'
                                                            }`}
                                                        style={{
                                                            width: `${(order.paid_amount / order.total_amount) * 100}%`
                                                        }}
                                                    />
                                                </div>

                                                {/* Payment History */}
                                                {order.payments.length > 0 && (
                                                    <div className="mt-3">
                                                        <p className="text-sm font-medium mb-2">Payment History ({order.payments.length})</p>
                                                        <div className="space-y-2">
                                                            {order.payments.map((payment) => (
                                                                <div key={payment.id} className="flex items-center justify-between p-2 bg-white border rounded text-sm">
                                                                    <div className="flex items-center gap-2">
                                                                        <CreditCard className="w-3 h-3 text-muted-foreground" />
                                                                        <span className="text-muted-foreground">
                                                                            {payment.payment_date ? format(new Date(payment.payment_date), 'MMM dd, yyyy') : 'N/A'}
                                                                        </span>
                                                                        <Badge variant="outline" className="text-xs">{payment.mode}</Badge>
                                                                    </div>
                                                                    <div className="flex items-center gap-2">
                                                                        {payment.reference_number && (
                                                                            <span className="text-xs text-muted-foreground">Ref: {payment.reference_number}</span>
                                                                        )}
                                                                        <span className="font-semibold text-green-600">
                                                                            {formatCurrency(payment.amount)}
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Unallocated Payments Section */}
                        {ledgerData.unallocated_payments && ledgerData.unallocated_payments.length > 0 && (
                            <div>
                                <h3 className="text-lg font-semibold mb-3">General Payments</h3>
                                <Card>
                                    <CardContent className="p-0">
                                        <div className="divide-y">
                                            {ledgerData.unallocated_payments.map((payment) => (
                                                <div key={payment.id} className="flex items-center justify-between p-4 hover:bg-gray-50">
                                                    <div className="flex items-center gap-4">
                                                        <div className="p-2 bg-green-100 rounded-full">
                                                            <CreditCard className="w-4 h-4 text-green-700" />
                                                        </div>
                                                        <div>
                                                            <p className="font-medium text-sm">
                                                                {payment.payment_date ? format(new Date(payment.payment_date), 'MMMM dd, yyyy') : 'N/A'}
                                                            </p>
                                                            <div className="flex items-center gap-2 mt-1">
                                                                <Badge variant="outline" className="text-xs">{payment.mode}</Badge>
                                                                {payment.reference_number && (
                                                                    <span className="text-xs text-muted-foreground">Ref: {payment.reference_number}</span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="font-bold text-green-600">
                                                            {formatCurrency(payment.amount)}
                                                        </p>
                                                        <p className="text-xs text-muted-foreground mt-1">Payment Received</p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </CardContent>
                                </Card>
                            </div>
                        )}
                    </div>
                ) : (
                    <div className="text-center py-8 text-muted-foreground">
                        No data available
                    </div>
                )}
            </DialogContent>
        </Dialog>
    );
}
