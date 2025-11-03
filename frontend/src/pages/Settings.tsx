import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Building2, Mail, Phone, MapPin, Save, Globe } from 'lucide-react';
import { toast } from 'sonner';

export default function Settings() {
  const [businessInfo, setBusinessInfo] = useState({
    businessName: 'School Copy Manufacturing',
    email: 'info@schoolcopy.com',
    phone: '+92 300 1234567',
    address: '123 Business Street, Karachi'
  });

  const [regionalSettings, setRegionalSettings] = useState({
    currency: localStorage.getItem('currencyCode') || 'PKR',
    currencySymbol: localStorage.getItem('currencySymbol') || 'Rs',
    timezone: 'Asia/Karachi',
    dateFormat: 'DD/MM/YYYY'
  });

  const [isSaving, setIsSaving] = useState(false);

  const handleBusinessInfoChange = (field: string, value: string) => {
    setBusinessInfo(prev => ({ ...prev, [field]: value }));
  };

  const handleRegionalChange = (field: string, value: string) => {
    setRegionalSettings(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveBusinessInfo = async () => {
    setIsSaving(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Business information saved successfully');
    } catch (error) {
      toast.error('Failed to save business information');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveRegionalSettings = async () => {
    setIsSaving(true);
    try {
      // Save to localStorage
      localStorage.setItem('currencyCode', regionalSettings.currency);
      localStorage.setItem('currencySymbol', regionalSettings.currencySymbol);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success('Regional settings saved successfully. Refresh to see changes.');
      
      // Trigger a storage event for other components
      window.dispatchEvent(new Event('storage'));
    } catch (error) {
      toast.error('Failed to save regional settings');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold">Settings</h1>
        <p className="text-sm sm:text-base text-muted-foreground">Manage your business settings and preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
        {/* Business Information */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
              <Building2 className="w-4 h-4 sm:w-5 sm:h-5" />
              Business Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 sm:space-y-4">
            <div>
              <Label htmlFor="businessName">Business Name</Label>
              <Input
                id="businessName"
                value={businessInfo.businessName}
                onChange={(e) => handleBusinessInfoChange('businessName', e.target.value)}
                className="mt-2"
                placeholder="Enter business name"
              />
            </div>
            <div>
              <Label htmlFor="email">
                <div className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  Email Address
                </div>
              </Label>
              <Input
                id="email"
                type="email"
                value={businessInfo.email}
                onChange={(e) => handleBusinessInfoChange('email', e.target.value)}
                className="mt-2"
                placeholder="business@example.com"
              />
            </div>
            <div>
              <Label htmlFor="phone">
                <div className="flex items-center gap-2">
                  <Phone className="w-4 h-4" />
                  Phone Number
                </div>
              </Label>
              <Input
                id="phone"
                value={businessInfo.phone}
                onChange={(e) => handleBusinessInfoChange('phone', e.target.value)}
                className="mt-2"
                placeholder="+92 300 1234567"
              />
            </div>
            <div>
              <Label htmlFor="address">
                <div className="flex items-center gap-2">
                  <MapPin className="w-4 h-4" />
                  Business Address
                </div>
              </Label>
              <Input
                id="address"
                value={businessInfo.address}
                onChange={(e) => handleBusinessInfoChange('address', e.target.value)}
                className="mt-2"
                placeholder="Enter complete address"
              />
            </div>
            <Button 
              onClick={handleSaveBusinessInfo} 
              className="w-full"
              disabled={isSaving}
            >
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save Business Info'}
            </Button>
          </CardContent>
        </Card>

        {/* Currency & Regional Settings */}
        <Card className="card-hover">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-lg sm:text-xl">
              <Globe className="w-4 h-4 sm:w-5 sm:h-5" />
              Currency & Regional Settings
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 sm:space-y-4">
            <div>
              <Label htmlFor="currency">Currency</Label>
              <Select 
                value={regionalSettings.currency} 
                onValueChange={(value) => {
                  handleRegionalChange('currency', value);
                  const symbols: Record<string, string> = {
                    'PKR': 'Rs',
                    'INR': '₹',
                    'USD': '$',
                    'EUR': '€',
                    'GBP': '£'
                  };
                  handleRegionalChange('currencySymbol', symbols[value] || value);
                }}
              >
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PKR">PKR - Pakistani Rupee (Rs)</SelectItem>
                  <SelectItem value="INR">INR - Indian Rupee (₹)</SelectItem>
                  <SelectItem value="USD">USD - US Dollar ($)</SelectItem>
                  <SelectItem value="EUR">EUR - Euro (€)</SelectItem>
                  <SelectItem value="GBP">GBP - British Pound (£)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="currencySymbol">Currency Symbol</Label>
              <Input
                id="currencySymbol"
                value={regionalSettings.currencySymbol}
                onChange={(e) => handleRegionalChange('currencySymbol', e.target.value)}
                className="mt-2"
                placeholder="Rs"
              />
            </div>
            <div>
              <Label htmlFor="timezone">Timezone</Label>
              <Select 
                value={regionalSettings.timezone} 
                onValueChange={(value) => handleRegionalChange('timezone', value)}
              >
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Asia/Karachi">Asia/Karachi (PKT)</SelectItem>
                  <SelectItem value="Asia/Kolkata">Asia/Kolkata (IST)</SelectItem>
                  <SelectItem value="Asia/Dubai">Asia/Dubai (GST)</SelectItem>
                  <SelectItem value="Europe/London">Europe/London (GMT)</SelectItem>
                  <SelectItem value="America/New_York">America/New York (EST)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="dateFormat">Date Format</Label>
              <Select 
                value={regionalSettings.dateFormat} 
                onValueChange={(value) => handleRegionalChange('dateFormat', value)}
              >
                <SelectTrigger className="mt-2">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                  <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                  <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button 
              onClick={handleSaveRegionalSettings} 
              className="w-full"
              disabled={isSaving}
            >
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save Regional Settings'}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* App Information */}
      <Card className="card-hover">
        <CardHeader>
          <CardTitle className="text-lg sm:text-xl">Application Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Version</p>
              <p className="text-lg font-semibold">1.0.0</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Environment</p>
              <p className="text-lg font-semibold">Production</p>
            </div>
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Last Updated</p>
              <p className="text-lg font-semibold">{new Date().toLocaleDateString()}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
