import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/useAuth';
import { api } from '@/lib/api-client';
import { useAuthenticatedQuery } from '@/hooks/useAuthenticatedQuery';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { format } from 'date-fns';
import { useCurrency } from '@/hooks/useCurrency';
import { toast } from 'sonner';
import { Loader2, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface LedgerEntry {
    id: string;
    date: string;
    type: 'ORDER' | 'PAYMENT' | 'OPENING';
    description: string;
    debit: number;
    credit: number;
    balance: number;
    reference?: string;
}

export default function Ledger() {
    const { user, isLoading: authLoading } = useAuth();
    const { formatCurrency } = useCurrency();
    const [selectedLeaderId, setSelectedLeaderId] = useState<string>('');
    const [ledgerData, setLedgerData] = useState<LedgerEntry[]>([]);
    const [loadingLedger, setLoadingLedger] = useState(false);

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

    const leaders = leadersData?.items ?? [];

    useEffect(() => {
        if (selectedLeaderId) {
            fetchLedger(selectedLeaderId);
        } else {
            setLedgerData([]);
        }
    }, [selectedLeaderId]);

    const fetchLedger = async (leaderId: string) => {
        setLoadingLedger(true);
        try {
            const data = await api.getLeaderLedger(leaderId);
            setLedgerData(data);
        } catch (error) {
            console.error('Error fetching ledger:', error);
            toast.error('Failed to fetch ledger data');
        } finally {
            setLoadingLedger(false);
        }
    };

    const calculateTotals = () => {
        const openingBalance = ledgerData.find(entry => entry.type === 'OPENING')?.debit || 0;
        const totalDebit = ledgerData.reduce((sum, entry) => sum + (entry.type !== 'OPENING' ? entry.debit : 0), 0);
        const totalCredit = ledgerData.reduce((sum, entry) => sum + entry.credit, 0);
        const balance = openingBalance + totalDebit - totalCredit;
        return { totalDebit, totalCredit, balance, openingBalance };
    };

    const totals = calculateTotals();

    return (
        <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
            <div>
                <h1 className="text-2xl sm:text-3xl font-bold">Ledger</h1>
                <p className="text-sm sm:text-base text-muted-foreground">View transaction history and balances</p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Select Leader</CardTitle>
                </CardHeader>
                <CardContent>
                    <Select value={selectedLeaderId} onValueChange={setSelectedLeaderId}>
                        <SelectTrigger className="w-full sm:w-[300px]">
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
                </CardContent>
            </Card>

            {selectedLeaderId && (
                <div className="space-y-6">
                    {/* Summary Cards */}
                    <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-sm font-medium text-muted-foreground">Opening Balance</div>
                                <div className="text-2xl font-bold">{formatCurrency(totals.openingBalance)}</div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-sm font-medium text-muted-foreground">Total Orders</div>
                                <div className="text-2xl font-bold text-blue-600">{formatCurrency(totals.totalDebit)}</div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-sm font-medium text-muted-foreground">Total Paid</div>
                                <div className="text-2xl font-bold text-green-600">{formatCurrency(totals.totalCredit)}</div>
                            </CardContent>
                        </Card>
                        <Card>
                            <CardContent className="pt-6">
                                <div className="text-sm font-medium text-muted-foreground">Outstanding Balance</div>
                                <div className={`text-2xl font-bold ${totals.balance > 0 ? 'text-red-600' : 'text-green-600'}`}>
                                    {formatCurrency(totals.balance)}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Ledger Table */}
                    <Card>
                        <CardHeader className="flex flex-row items-center justify-between">
                            <CardTitle>Transactions</CardTitle>
                            <Button variant="outline" size="sm" disabled>
                                <Download className="w-4 h-4 mr-2" />
                                Export
                            </Button>
                        </CardHeader>
                        <CardContent>
                            {loadingLedger ? (
                                <div className="flex justify-center py-8">
                                    <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
                                </div>
                            ) : ledgerData.length === 0 ? (
                                <div className="text-center py-8 text-muted-foreground">
                                    No transactions found for this leader.
                                </div>
                            ) : (
                                <div className="relative w-full overflow-auto">
                                    <Table>
                                        <TableHeader>
                                            <TableRow>
                                                <TableHead>Date</TableHead>
                                                <TableHead>Description</TableHead>
                                                <TableHead>Reference</TableHead>
                                                <TableHead className="text-right">Debit (Order)</TableHead>
                                                <TableHead className="text-right">Credit (Payment)</TableHead>
                                                <TableHead className="text-right">Balance</TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {ledgerData.map((entry) => (
                                                <TableRow key={entry.id}>
                                                    <TableCell>{format(new Date(entry.date), 'dd/MM/yyyy')}</TableCell>
                                                    <TableCell>
                                                        <span className={`font-medium ${entry.type === 'ORDER' ? 'text-blue-600' : 'text-green-600'}`}>
                                                            {entry.type}
                                                        </span>
                                                        <span className="ml-2 text-muted-foreground">
                                                            {entry.description.replace(entry.type === 'ORDER' ? 'Order #' : 'Payment ', '')}
                                                        </span>
                                                    </TableCell>
                                                    <TableCell>{entry.reference || '-'}</TableCell>
                                                    <TableCell className="text-right">
                                                        {entry.debit > 0 ? formatCurrency(entry.debit) : '-'}
                                                    </TableCell>
                                                    <TableCell className="text-right">
                                                        {entry.credit > 0 ? formatCurrency(entry.credit) : '-'}
                                                    </TableCell>
                                                    <TableCell className="text-right font-bold">
                                                        {formatCurrency(entry.balance)}
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
