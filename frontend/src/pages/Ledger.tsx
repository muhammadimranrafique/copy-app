import { useState } from 'react';
import { useAuth } from '@/lib/useAuth';
import { api } from '@/lib/api-client';
import { useAuthenticatedQuery } from '@/hooks/useAuthenticatedQuery';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { useCurrency } from '@/hooks/useCurrency';
import { toast } from 'sonner';
import { Loader2, DollarSign, ShoppingCart, CreditCard, TrendingUp, TrendingDown } from 'lucide-react';

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

interface Leader {
    id: string;
    name: string;
    type: string;
    contact?: string;
    address?: string;
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
}

export default function Ledger() {
    const { user, isLoading: authLoading } = useAuth();
    const { formatCurrency } = useCurrency();
    const [selectedLeaderId, setSelectedLeaderId] = useState<string>('');

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

    const {
        data: ledgerData,
        loading: ledgerLoading
    } = useAuthenticatedQuery<LedgerData>(
        () => api.getLeaderLedger(selectedLeaderId),
        {
            isReady: !!selectedLeaderId,
            onError: () => toast.error('Failed to load ledger data'),
            queryKey: ['leaderLedger', selectedLeaderId]
        }
    );

    const leaders = leadersData?.items ?? [];

    const getStatusBadge = (status: string) => {
        const variants: Record<string, { className: string }> = {
            'Paid': { className: 'bg-green-100 text-green-700 border-green-300' },
            'PAID': { className: 'bg-green-100 text-green-700 border-green-300' },
            'Partially Paid': { className: 'bg-orange-100 text-orange-700 border-orange-300' },
            'PARTIALLY_PAID': { className: 'bg-orange-100 text-orange-700 border-orange-300' },
            'Pending': { className: 'bg-red-100 text-red-700 border-red-300' },
            'PENDING': { className: 'bg-red-100 text-red-700 border-red-300' }
        };
        return variants[status] || variants['Pending'];
    };

    const getBalanceColor = (balance: number) => {
        if (balance === 0) return 'text-green-600';
        if (balance > 0) return 'text-orange-600';
        return 'text-gray-600';
    };

    return (
        <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
            <div>
                <h1 className="text-2xl sm:text-3xl font-bold">Ledger</h1>
                <p className="text-sm sm:text-base text-muted-foreground">View detailed transaction history and balances</p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Select Client</CardTitle>
                </CardHeader>
                <CardContent>
                    <Select value={selectedLeaderId} onValueChange={setSelectedLeaderId}>
                        <SelectTrigger className="w-full sm:w-[300px]">
                            <SelectValue placeholder="Select a client" />
                        </SelectTrigger>
                        <SelectContent>
                            {leadersLoading ? (
                                <div className="p-2 text-center text-muted-foreground">Loading...</div>
                            ) : (
                                leaders.map((leader: Leader) => (
                                    <SelectItem key={leader.id} value={leader.id}>
                                        {leader.name} ({leader.type})
                                    </SelectItem>
                                ))
                            )}
                        </SelectContent>
                    </Select>
                </CardContent>
            </Card>

            {selectedLeaderId && (
                ledgerLoading ? (
                    <div className="flex justify-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                    </div>
                ) : ledgerData ? (
                    <div className="space-y-6">
                        {/* Client Info */}
                        <Card>
                            <CardHeader>
                                <CardTitle>{ledgerData.client.name}</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-2">
                                <div className="flex justify-between">
                                    <span className="text-muted-foreground">Type:</span>
                                    <Badge>{ledgerData.client.type}</Badge>
                                </div>
                                {ledgerData.client.contact && (
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Contact:</span>
                                        <span>{ledgerData.client.contact}</span>
                                    </div>
                                )}
                                {ledgerData.client.address && (
                                    <div className="flex justify-between">
                                        <span className="text-muted-foreground">Address:</span>
                                        <span className="text-right">{ledgerData.client.address}</span>
                                    </div>
                                )}
                            </CardContent>
                        </Card>

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

                        {/* Orders & Payments */}
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
                    </div>
                ) : (
                    <div className="text-center py-8 text-muted-foreground">
                        No data available
                    </div>
                )
            )}
        </div>
    );
}
