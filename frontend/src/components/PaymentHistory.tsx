import { useState, useEffect } from 'react';
import { Download, Calendar, CreditCard, Receipt, TrendingDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { toast } from 'sonner';

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
}

export function PaymentHistory({ orderId, orderTotal, currentBalance, onDownloadReceipt }: PaymentHistoryProps) {
    const [payments, setPayments] = useState<Payment[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchPaymentHistory();
    }, [orderId]);

    const fetchPaymentHistory = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('access_token');
            const response = await fetch(
                `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'}/payments/?orderId=${orderId}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            if (!response.ok) throw new Error('Failed to fetch payment history');

            const allPayments = await response.json();
            // Filter payments for this specific order
            const orderPayments = allPayments.filter((p: any) => p.orderId === orderId);

            // Sort by payment date
            orderPayments.sort((a: any, b: any) =>
                new Date(a.paymentDate).getTime() - new Date(b.paymentDate).getTime()
            );

            setPayments(orderPayments);
        } catch (error) {
            console.error('Error fetching payment history:', error);
            toast.error('Failed to load payment history');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadReceipt = async (paymentId: string) => {
        if (onDownloadReceipt) {
            onDownloadReceipt(paymentId);
        } else {
            try {
                toast.loading('Generating receipt...', { id: 'download-receipt' });
                const token = localStorage.getItem('access_token');
                const response = await fetch(
                    `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'}/payments/${paymentId}/receipt`,
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
                                                    {format(new Date(payment.paymentDate), 'MMM dd, yyyy')}
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-2xl font-bold text-green-600">
                                                    Rs {payment.amount.toLocaleString()}
                                                </p>
                                                <Button
                                                    variant="outline"
                                                    size="sm"
                                                    onClick={() => handleDownloadReceipt(payment.id)}
                                                    className="mt-2"
                                                >
                                                    <Download className="w-3 h-3 mr-1" />
                                                    Receipt
                                                </Button>
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
        </Card>
    );
}
