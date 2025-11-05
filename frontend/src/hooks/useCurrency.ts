import { useState, useEffect } from 'react';

export function useCurrency() {
  const [currencySymbol, setCurrencySymbol] = useState('Rs');
  const [currencyCode, setCurrencyCode] = useState('PKR');

  useEffect(() => {
    // Get currency from localStorage or use default
    const savedSymbol = localStorage.getItem('currencySymbol') || 'Rs';
    const savedCode = localStorage.getItem('currencyCode') || 'PKR';
    setCurrencySymbol(savedSymbol);
    setCurrencyCode(savedCode);

    // Listen for storage changes to update currency in real-time
    const handleStorageChange = () => {
      const newSymbol = localStorage.getItem('currencySymbol') || 'Rs';
      const newCode = localStorage.getItem('currencyCode') || 'PKR';
      setCurrencySymbol(newSymbol);
      setCurrencyCode(newCode);
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const formatCurrency = (amount: number): string => {
    // Format based on currency code for better localization
    const localeMap: Record<string, string> = {
      'PKR': 'en-PK',
      'INR': 'en-IN',
      'USD': 'en-US',
      'EUR': 'en-EU',
      'GBP': 'en-GB'
    };
    
    const locale = localeMap[currencyCode] || 'en-US';
    const formattedAmount = amount.toLocaleString(locale, { 
      minimumFractionDigits: 0, 
      maximumFractionDigits: 2 
    });
    
    return `${currencySymbol} ${formattedAmount}`;
  };

  const updateCurrency = (symbol: string, code: string) => {
    setCurrencySymbol(symbol);
    setCurrencyCode(code);
    localStorage.setItem('currencySymbol', symbol);
    localStorage.setItem('currencyCode', code);
    
    // Trigger storage event for other components
    window.dispatchEvent(new Event('storage'));
  };

  return {
    currencySymbol,
    currencyCode,
    formatCurrency,
    updateCurrency
  };
}
