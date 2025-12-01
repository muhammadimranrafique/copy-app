import { useState } from 'react';
import { Plus, Search } from 'lucide-react';
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

interface Leader {
  id: string;
  name: string;
  type: string;
  contact: string;
  address: string;
  opening_balance: number;
}

export default function Leaders() {
  const { formatCurrency } = useCurrency();
  const { user, isLoading: authLoading } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
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
            <div key={i} className="h-48 bg-muted rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
          {filteredLeaders.map((leader) => (
            <Card key={leader.id} className="card-hover">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <CardTitle className="text-base sm:text-lg flex-1 min-w-0 break-words">{leader.name}</CardTitle>
                  <Badge variant={leader.type === 'School' ? 'default' : 'secondary'} className="text-xs flex-shrink-0">
                    {leader.type}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-2 pt-3">
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground">Contact</p>
                  <p className="font-medium text-sm sm:text-base break-words">{leader.contact || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground">Address</p>
                  <p className="font-medium text-sm sm:text-base break-words">{leader.address || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-xs sm:text-sm text-muted-foreground">Balance</p>
                  <p className={`font-semibold text-sm sm:text-base ${(leader.opening_balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(leader.opening_balance || 0)}
                  </p>
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
    </div>
  );
}
