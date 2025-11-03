export const mockOrders = [
  { id: '1', orderNumber: 'ORD-001', leaderId: '1', orderDate: new Date().toISOString(), totalAmount: 15000, status: 'Paid' },
  { id: '2', orderNumber: 'ORD-002', leaderId: '2', orderDate: new Date().toISOString(), totalAmount: 25000, status: 'Pending' },
];

export const mockLeaders = [
  { id: '1', name: 'ABC School', type: 'School', contact: '+92 300 1234567', address: 'Karachi, Pakistan', openingBalance: 5000 },
  { id: '2', name: 'XYZ Dealer', type: 'Dealer', contact: '+92 300 7654321', address: 'Lahore, Pakistan', openingBalance: -2000 },
];

export const mockProducts = [
  { id: '1', productName: 'Copier Paper A4', category: 'Paper', costPrice: 150, salePrice: 200, stockQuantity: 1000, unit: 'pcs' },
  { id: '2', productName: 'Spiral Binding', category: 'Binding', costPrice: 50, salePrice: 75, stockQuantity: 500, unit: 'pcs' },
];

export const mockPayments = [
  { id: '1', amount: 10000, method: 'Cash', paymentDate: new Date().toISOString(), leaderId: '1' },
  { id: '2', amount: 15000, method: 'Bank Transfer', paymentDate: new Date().toISOString(), leaderId: '2' },
];

export const mockExpenses = [
  { id: '1', category: 'MATERIAL', amount: 5000, description: 'Paper purchase for printing', expenseDate: new Date().toISOString(), paymentMethod: 'Cash', referenceNumber: 'EXP-001' },
  { id: '2', category: 'STAFF', amount: 8000, description: 'Staff salaries', expenseDate: new Date().toISOString(), paymentMethod: 'Bank Transfer', referenceNumber: 'EXP-002' },
  { id: '3', category: 'UTILITIES', amount: 3000, description: 'Electricity bill', expenseDate: new Date().toISOString(), paymentMethod: 'Bank Transfer', referenceNumber: 'EXP-003' },
];
