import { useState } from 'react';
import { Plus, Search, Download, Eye } from 'lucide-react';
import { useCurrency } from '@/hooks/useCurrency';
import { useAuth } from '@/lib/useAuth';
import { api } from '@/lib/api-client';
import { useAuthenticatedQuery } from '@/hooks/useAuthenticatedQuery';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { exportLeaderPayments } from '@/lib/export-utils';
import { ClientLedgerModal } from '@/components/ClientLedgerModal';

interface Leader {
  id: string;
  name: string;
  type: string;
  contact: string;
  address: string;
  opening_balance: number;
  total_orders?: number;
  total_order_amount?: number;
  total_paid?: number;
  outstanding_balance?: number;
}

export default function Leaders() {
  const { formatCurrency } = useCurrency();
  const { user, isLoading: authLoading } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [exportingId, setExportingId] = useState<string | null>(null);
  const [selectedLeader, setSelectedLeader] = useState<Leader | null>(null);
  const [ledgerModalOpen, setLedgerModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: 'School',
    contact: '',
    address: '',
    opening_balance: 0
  });

  const {
    data: leadersData,
    loading,
    refetch: loadLeaders
  } = useAuthenticatedQuery(
    () => api.getLeaders({}),
    {
      isReady: !authLoading && !!user,
      onError: () => toast.error('Failed to load leaders')
    }
  );

  const leaders = leadersData?.items ?? [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createLeader(formData);
      toast.success('Leader created successfully');
      setDialogOpen(false);
      setFormData({ name: '', type: 'School', contact: '', address: '', opening_balance: 0 });
      loadLeaders();
    } catch (error) {
      toast.error('Failed to create leader');
    }
  };

  const handleExport = async (leader: Leader, e: React.MouseEvent) => {
    e.stopPropagation();
    setExportingId(leader.id);
    try {
      await exportLeaderPayments(leader.id, leader.name);
    } catch (error) {
      // Error already handled in exportLeaderPayments
    } finally {
      setExportingId(null);
    }
  };

  const handleViewLedger = (leader: Leader, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedLeader(leader);
    setLedgerModalOpen(true);
  };

  const filteredLeaders = leaders.filter(leader =>
    leader.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    leader.contact?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 sm:gap-0">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">Leaders</h1>
          <p className="text-sm sm:text-base text-muted-foreground">Manage schools and dealers</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="w-full sm:w-auto">
              <Plus className="w-4 h-4 mr-2" />
              Add Leader
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-[95vw] sm:max-w-[425px] max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Add New Leader</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="type">Type *</Label>
                <Select value={formData.type} onValueChange={(value) => setFormData({ ...formData, type: value })}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="School">School</SelectItem>
                    <SelectItem value="Dealer">Dealer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="contact">Contact</Label>
                <Input
                  id="contact"
                  value={formData.contact}
                  onChange={(e) => setFormData({ ...formData, contact: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="address">Address</Label>
                <Input
                  id="address"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="balance">Opening Balance</Label>
                <Input
                  id="balance"
                  type="number"
                  value={formData.opening_balance}
                  onChange={(e) => setFormData({ ...formData, opening_balance: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <Button type="submit" className="w-full">Create Leader</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <Input
          placeholder="Search leaders..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-64 bg-muted rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {filteredLeaders.map((leader) => (
            <Card key={leader.id} className="card-hover cursor-pointer" onClick={(e) => handleViewLedger(leader, e)}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base sm:text-lg flex-1 min-w-0 break-words">{leader.name}</CardTitle>
                  <Badge variant={leader.type === 'School' ? 'default' : 'secondary'} className="text-xs flex-shrink-0">
                    {leader.type}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3 pt-3">
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground">Contact</p>
                  <p className="font-medium text-sm sm:text-base break-words">{leader.contact || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground">Address</p>
                  <p className="font-medium text-sm sm:text-base break-words">{leader.address || 'N/A'}</p>
                </div>

                {/* Financial Summary */}
                <div className="border-t pt-3 space-y-2">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-xs text-muted-foreground">Total Orders</p>
                      <p className="font-semibold text-sm">{leader.total_orders || 0}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Total Paid</p>
                      <p className="font-semibold text-sm text-green-600">
                        {formatCurrency(leader.total_paid || 0)}
                      </p>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Outstanding Balance</p>
                    <p className={`text-lg font-bold ${(leader.outstanding_balance || 0) > 0 ? 'text-red-600' : 'text-green-600'
                      }`}>
                      {formatCurrency(leader.outstanding_balance || 0)}
                    </p>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={(e) => handleViewLedger(leader, e)}
                  >
                    <Eye className="w-4 h-4 mr-1" />
                    View Ledger
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={(e) => handleExport(leader, e)}
                    disabled={exportingId === leader.id}
                  >
                    {exportingId === leader.id ? (
                      <>
                        <div className="w-4 h-4 mr-1 border-2 border-current border-t-transparent rounded-full animate-spin" />
                        Exporting...
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4 mr-1" />
                        Export
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {!loading && filteredLeaders.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No leaders found</p>
        </div>
      )}

      {/* Client Ledger Modal */}
      {selectedLeader && (
        <ClientLedgerModal
          clientId={selectedLeader.id}
          clientName={selectedLeader.name}
          open={ledgerModalOpen}
          onOpenChange={setLedgerModalOpen}
        />
      )}
    </div>
  );
}
