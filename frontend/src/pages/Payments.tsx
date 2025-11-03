import { useState } from 'react';
import { Plus, DollarSign } from 'lucide-react';
import { useCurrency } from '@/hooks/useCurrency';
import { useAuth } from '@/lib/useAuth';
import { getPayments, createPayment, getLeaders } from '@/lib/mock-api';
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
    referenceNumber: ''
  });

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
        referenceNumber: ''
      });
      refetchPayments();
    } catch (error: any) {
      console.error('Payment creation error:', error);
      toast.error(error?.message || 'Failed to record payment');
    }
  };

  const getMethodBadge = (method?: string) => {
    const colors: Record<string, string> = {
      'Cash': 'bg-green-100 text-green-700',
      'Bank Transfer': 'bg-blue-100 text-blue-700',
      'Cheque': 'bg-purple-100 text-purple-700',
      'UPI': 'bg-orange-100 text-orange-700'
    };
    return colors[method || 'Cash'] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Payments</h1>
          <p className="text-muted-foreground">Manage customer payments</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Record Payment
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Record New Payment</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
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
                <Label htmlFor="amount">Amount *</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                  required
                />
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
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-muted rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {payments.map((payment) => (
            <Card key={payment.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="p-3 rounded-full bg-green-100">
                      <DollarSign className="w-6 h-6 text-green-600" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getMethodBadge(payment.method)}`}>
                          {payment.method}
                        </span>
                        {payment.referenceNumber && (
                          <span className="text-sm text-muted-foreground">Ref: {payment.referenceNumber}</span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {payment.paymentDate ? format(new Date(payment.paymentDate), 'MMM dd, yyyy') : 'N/A'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-green-600">{formatCurrency(payment.amount || 0)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
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
