import { useState } from 'react';
import { Plus, Receipt, Trash2, Edit } from 'lucide-react';
import { useCurrency } from '@/hooks/useCurrency';
import { useAuth } from '@/lib/useAuth';
import { api } from '@/lib/api-client';
import { useAuthenticatedQuery } from '@/hooks/useAuthenticatedQuery';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Toaster } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { format } from 'date-fns';
import { Textarea } from '@/components/ui/textarea';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import type { Expense, ExpenseCategory, ExpenseCreate } from '@/lib/api-types';

const EXPENSE_CATEGORIES: ExpenseCategory[] = [
  'MATERIAL',
  'STAFF',
  'UTILITIES',
  'PRINTING',
  'PRINTING_1',
  'PRINTING_2',
  'PRINTING_3',
  'PAPER',
  'PAPER_1',
  'PAPER_2',
  'PAPER_3',
  'DELIVERY',
  'MISC'
];

const PAYMENT_METHODS = [
  'Cash',
  'Bank Transfer',
  'Check'
];

const ORDER_CATEGORIES = [
  'Bleach Card Umer',
  'Other Bleach Card',
  'Standard Order',
  'Custom Order',
  'Bulk Order'
];

export default function Expenses() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<Expense | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>('All');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const { formatCurrency } = useCurrency();
  const { user, isLoading: authLoading } = useAuth();

  const [formData, setFormData] = useState<ExpenseCreate>({
    category: 'MATERIAL',
    amount: 0,
    description: '',
    expenseDate: new Date().toISOString().split('T')[0],
    paymentMethod: 'Cash',
    referenceNumber: '',
    orderCategory: 'Standard Order'
  });

  const {
    data: expensesData,
    loading,
    error,
    refetch: refetchExpenses
  } = useAuthenticatedQuery(
    () => api.getExpenses({}),
    {
      isReady: !authLoading && !!user,
      onError: (_err) => toast.error(`Failed to load expenses: ${_err.message}`)
    }
  );

  // Show loading state
  if (authLoading || loading) {
    return <LoadingSpinner message="Loading expenses..." />;
  }

  // Show error state
  if (error) {
    return (
      <div className="p-4">
        <div className="rounded-lg bg-red-50 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error loading expenses</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error.message}</p>
              </div>
              <div className="mt-4">
                <Button onClick={() => refetchExpenses()} variant="outline" size="sm">
                  Try Again
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const expenses: Expense[] = expensesData?.expenses ?? [];

  // Filter expenses by category and date range
  const filteredExpenses = expenses.filter((expense) => {
    const categoryMatch = filterCategory === 'All' || expense.category === filterCategory;
    const dateMatch = (!startDate || expense.expenseDate >= startDate) &&
      (!endDate || expense.expenseDate <= endDate);
    return categoryMatch && dateMatch;
  });

  // Calculate total expenses
  const totalExpenses = filteredExpenses.reduce((sum, expense) => sum + expense.amount, 0);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.description.trim()) {
      toast.error('Please enter a description');
      return;
    }

    if (formData.amount <= 0) {
      toast.error('Amount must be greater than 0');
      return;
    }

    try {
      if (editingExpense) {
        await api.updateExpense(editingExpense.id, formData);
        toast.success('Expense updated successfully');
      } else {
        await api.createExpense(formData);
        toast.success('Expense added successfully');
      }

      setDialogOpen(false);
      setEditingExpense(null);
      setFormData({
        category: 'MATERIAL',
        amount: 0,
        description: '',
        expenseDate: new Date().toISOString().split('T')[0],
        paymentMethod: 'Cash',
        referenceNumber: '',
        orderCategory: 'Standard Order'
      });
      refetchExpenses();
    } catch (error: any) {
      console.error('Expense operation error:', error);
      toast.error(error?.message || `Failed to ${editingExpense ? 'update' : 'add'} expense`);
    }
  };

  const handleEdit = (expense: Expense) => {
    setEditingExpense(expense);
    setFormData({
      category: expense.category,
      amount: expense.amount,
      description: expense.description,
      expenseDate: expense.expenseDate.split('T')[0],
      paymentMethod: expense.paymentMethod || 'Cash',
      referenceNumber: expense.referenceNumber || '',
      orderCategory: expense.orderCategory || 'Standard Order'
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this expense?')) {
      return;
    }

    try {
      await api.deleteExpense(id);
      toast.success('Expense deleted successfully');
      refetchExpenses();
    } catch (error: any) {
      console.error('Expense deletion error:', error);
      toast.error(error?.message || 'Failed to delete expense');
    }
  };

  const handleDialogClose = (open: boolean) => {
    setDialogOpen(open);
    if (!open) {
      setEditingExpense(null);
      setFormData({
        category: 'MATERIAL',
        amount: 0,
        description: '',
        expenseDate: new Date().toISOString().split('T')[0],
        paymentMethod: 'Cash',
        referenceNumber: '',
        orderCategory: 'Standard Order'
      });
    }
  };

  const getCategoryBadge = (category: string) => {
    const colors: Record<string, string> = {
      'MATERIAL': 'bg-blue-100 text-blue-700',
      'STAFF': 'bg-green-100 text-green-700',
      'UTILITIES': 'bg-yellow-100 text-yellow-700',
      'PRINTING': 'bg-purple-100 text-purple-700',
      'PRINTING_1': 'bg-purple-100 text-purple-700',
      'PRINTING_2': 'bg-purple-200 text-purple-800',
      'PRINTING_3': 'bg-purple-300 text-purple-900',
      'PAPER': 'bg-teal-100 text-teal-700',
      'PAPER_1': 'bg-teal-100 text-teal-700',
      'PAPER_2': 'bg-teal-200 text-teal-800',
      'PAPER_3': 'bg-teal-300 text-teal-900',
      'DELIVERY': 'bg-orange-100 text-orange-700',
      'MISC': 'bg-gray-100 text-gray-700'
    };
    return colors[category] || 'bg-gray-100 text-gray-700';
  };

  const getPaymentMethodBadge = (method?: string) => {
    const colors: Record<string, string> = {
      'Cash': 'bg-green-100 text-green-700',
      'Bank Transfer': 'bg-blue-100 text-blue-700',
      'Check': 'bg-purple-100 text-purple-700'
    };
    return colors[method || 'Cash'] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 sm:gap-0">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Expenses</h1>
          <p className="text-sm sm:text-base text-gray-600 mt-1">Track daily expenses during copy production</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={handleDialogClose}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2 w-full sm:w-auto">
              <Plus className="h-4 w-4" />
              Add Expense
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-[95vw] sm:max-w-md max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingExpense ? 'Edit Expense' : 'Add New Expense'}</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="expenseDate">Expense Date</Label>
                <Input
                  id="expenseDate"
                  type="date"
                  value={formData.expenseDate}
                  onChange={(e) => setFormData({ ...formData, expenseDate: e.target.value })}
                  required
                />
              </div>

              <div>
                <Label htmlFor="category">Category</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value) => setFormData({ ...formData, category: value as ExpenseCategory })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {EXPENSE_CATEGORIES.map((cat) => (
                      <SelectItem key={cat} value={cat}>
                        {cat}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="amount">Amount</Label>
                <Input
                  id="amount"
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                  required
                />
              </div>

              <div>
                <Label htmlFor="orderCategory">Order Category</Label>
                <Select
                  value={formData.orderCategory}
                  onValueChange={(value) => setFormData({ ...formData, orderCategory: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select order category" />
                  </SelectTrigger>
                  <SelectContent>
                    {ORDER_CATEGORIES.map((cat) => (
                      <SelectItem key={cat} value={cat}>
                        {cat}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Enter expense description"
                  required
                />
              </div>

              <div>
                <Label htmlFor="paymentMethod">Payment Method</Label>
                <Select
                  value={formData.paymentMethod}
                  onValueChange={(value) => setFormData({ ...formData, paymentMethod: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select payment method" />
                  </SelectTrigger>
                  <SelectContent>
                    {PAYMENT_METHODS.map((method) => (
                      <SelectItem key={method} value={method}>
                        {method}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="referenceNumber">Reference Number (Optional)</Label>
                <Input
                  id="referenceNumber"
                  value={formData.referenceNumber}
                  onChange={(e) => setFormData({ ...formData, referenceNumber: e.target.value })}
                  placeholder="Enter reference number"
                />
              </div>

              <Button type="submit" className="w-full">
                {editingExpense ? 'Update Expense' : 'Add Expense'}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        <div>
          <Label htmlFor="filterCategory" className="text-sm">Filter by Category</Label>
          <Select value={filterCategory} onValueChange={setFilterCategory}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All">All Categories</SelectItem>
              {EXPENSE_CATEGORIES.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="startDate" className="text-sm">Start Date</Label>
          <Input
            id="startDate"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="endDate" className="text-sm">End Date</Label>
          <Input
            id="endDate"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
        </div>
      </div>

      {/* Summary Card */}
      <Card className="card-hover">
        <CardContent className="p-4 sm:p-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
            <div>
              <p className="text-xs sm:text-sm text-gray-600">Total Expenses</p>
              <p className="text-xl sm:text-2xl font-bold text-red-600">{formatCurrency(totalExpenses)}</p>
            </div>
            <div className="text-left sm:text-right">
              <p className="text-xs sm:text-sm text-gray-600">Filtered Results</p>
              <p className="text-base sm:text-lg font-semibold">{filteredExpenses.length} expenses</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Expenses List */}
      <div className="space-y-3 sm:space-y-4">
        {filteredExpenses.map((expense) => (
          <Card key={expense.id} className="card-hover">
            <CardContent className="p-4 sm:p-6">
              <div className="flex flex-col lg:flex-row items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    <Receipt className="h-4 w-4 text-gray-500 flex-shrink-0" />
                    <Badge className={`${getCategoryBadge(expense.category)} text-xs`}>
                      {expense.category}
                    </Badge>
                    {expense.paymentMethod && (
                      <Badge variant="outline" className={`${getPaymentMethodBadge(expense.paymentMethod)} text-xs`}>
                        {expense.paymentMethod}
                      </Badge>
                    )}
                    {expense.orderCategory && expense.orderCategory !== 'Standard Order' && (
                      <Badge variant="outline" className="bg-indigo-100 text-indigo-700 text-xs">
                        {expense.orderCategory}
                      </Badge>
                    )}
                  </div>

                  <h3 className="font-semibold text-base sm:text-lg mb-1 break-words">{expense.description}</h3>

                  <div className="flex flex-wrap items-center gap-2 sm:gap-4 text-xs sm:text-sm text-gray-600">
                    <span>Date: {format(new Date(expense.expenseDate), 'MMM dd, yyyy')}</span>
                    {expense.referenceNumber && (
                      <span className="truncate">Ref: {expense.referenceNumber}</span>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between lg:justify-end gap-3 w-full lg:w-auto">
                  <div className="text-left lg:text-right">
                    <p className="text-xl sm:text-2xl font-bold text-red-600">
                      {formatCurrency(expense.amount)}
                    </p>
                  </div>

                  <div className="flex gap-2 flex-shrink-0">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEdit(expense)}
                      className="h-9 w-9 p-0"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDelete(expense.id)}
                      className="text-red-600 hover:text-red-700 h-9 w-9 p-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {filteredExpenses.length === 0 && (
          <div className="text-center py-12">
            <Receipt className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No expenses found</p>
            <p className="text-sm text-gray-500 mt-1">
              {filterCategory !== 'All' || startDate || endDate
                ? 'Try adjusting your filters'
                : 'Add your first expense to get started'
              }
            </p>
          </div>
        )}
      </div>
      <Toaster position="top-right" richColors />
    </div>
  );
}