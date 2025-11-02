import { useState } from 'react';
import { useAuthenticatedQuery } from '@/hooks/useAuthenticatedQuery';
import { Plus, Package } from 'lucide-react';
import { useCurrency } from '@/hooks/useCurrency';
import { useAuth } from '@/lib/useAuth';
import { getProducts, createProduct } from '@/lib/mock-api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Badge } from '@/components/ui/badge';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import { ErrorBoundary } from '@/components/ErrorBoundary';

interface Product {
  id: string;
  productName: string;
  category: string;
  costPrice: number;
  salePrice: number;
  stockQuantity: number;
  unit: string;
}

export default function Products() {
  const { formatCurrency } = useCurrency();
  const { user, isLoading: authLoading } = useAuth();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    productName: '',
    category: '',
    costPrice: 0,
    salePrice: 0,
    stockQuantity: 0,
    unit: 'pcs'
  });

  const {
    data: productsData,
    loading,
    error,
    refetch: loadProducts
  } = useAuthenticatedQuery(
    () => getProducts({}),
    {
      isReady: !authLoading && !!user,
      onError: (err) => toast.error(`Failed to load products: ${err.message}`),
      retryCount: 3,
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
    }
  );

  const products = productsData?.products ?? [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.productName.trim()) {
      toast.error('Please enter a product name');
      return;
    }
    
    if (formData.salePrice <= 0) {
      toast.error('Sale price must be greater than 0');
      return;
    }
    
    try {
      await createProduct(formData);
      toast.success('Product created successfully');
      setDialogOpen(false);
      setFormData({ productName: '', category: '', costPrice: 0, salePrice: 0, stockQuantity: 0, unit: 'pcs' });
      loadProducts();
    } catch (error: any) {
      console.error('Product creation error:', error);
      toast.error(error?.message || 'Failed to create product');
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Products</h1>
          <p className="text-muted-foreground">Manage your product inventory</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Add Product
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Product</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="productName">Product Name *</Label>
                <Input
                  id="productName"
                  value={formData.productName}
                  onChange={(e) => setFormData({ ...formData, productName: e.target.value })}
                  required
                />
              </div>
              <div>
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="e.g., Paper, Binding, Cover"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="costPrice">Cost Price</Label>
                  <Input
                    id="costPrice"
                    type="number"
                    step="0.01"
                    value={formData.costPrice}
                    onChange={(e) => setFormData({ ...formData, costPrice: parseFloat(e.target.value) || 0 })}
                  />
                </div>
                <div>
                  <Label htmlFor="salePrice">Sale Price</Label>
                  <Input
                    id="salePrice"
                    type="number"
                    step="0.01"
                    value={formData.salePrice}
                    onChange={(e) => setFormData({ ...formData, salePrice: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="stockQuantity">Stock Quantity</Label>
                  <Input
                    id="stockQuantity"
                    type="number"
                    value={formData.stockQuantity}
                    onChange={(e) => setFormData({ ...formData, stockQuantity: parseInt(e.target.value) || 0 })}
                  />
                </div>
                <div>
                  <Label htmlFor="unit">Unit</Label>
                  <Input
                    id="unit"
                    value={formData.unit}
                    onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
                    placeholder="pcs, ream, etc."
                  />
                </div>
              </div>
              <Button type="submit" className="w-full">Create Product</Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-56 bg-muted rounded-lg animate-pulse"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {products.map((product) => {
            const profit = (product.salePrice || 0) - (product.costPrice || 0);
            const profitMargin = product.costPrice ? ((profit / product.costPrice) * 100).toFixed(1) : 0;
            
            return (
              <Card key={product.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <Package className="w-5 h-5 text-primary" />
                      <CardTitle className="text-lg">{product.productName}</CardTitle>
                    </div>
                  </div>
                  {product.category && (
                    <Badge variant="outline" className="w-fit">{product.category}</Badge>
                  )}
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-xs text-muted-foreground">Cost Price</p>
                      <p className="font-medium">{formatCurrency(product.costPrice || 0)}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Sale Price</p>
                      <p className="font-medium text-green-600">{formatCurrency(product.salePrice || 0)}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <p className="text-xs text-muted-foreground">Stock</p>
                      <p className="font-semibold">{product.stockQuantity || 0} {product.unit}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Margin</p>
                      <p className="font-semibold text-blue-600">{profitMargin}%</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      {!loading && products.length === 0 && (
        <div className="text-center py-12">
          <Package className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No products found</p>
        </div>
      )}
    </div>
  );
}
