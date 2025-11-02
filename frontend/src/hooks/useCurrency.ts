import { useState, useEffect } from 'react';

// Currency settings hook
export function useCurrency() {
  const [currencySymbol, setCurrencySymbol] = useState('Rs');
  const [currencyCode, setCurrencyCode] = useState('PKR');

  useEffect(() => {
    // Get currency from localStorage or use default
    const savedSymbol = localStorage.getItem('currencySymbol') || 'Rs';
    const savedCode = localStorage.getItem('currencyCode') || 'PKR';
    setCurrencySymbol(savedSymbol);
    setCurrencyCode(savedCode);
  }, []);

  const formatCurrency = (amount: number): string => {
    return `${currencySymbol}${amount.toLocaleString()}`;
  };

  const updateCurrency = (symbol: string, code: string) => {
    setCurrencySymbol(symbol);
    setCurrencyCode(code);
    localStorage.setItem('currencySymbol', symbol);
    localStorage.setItem('currencyCode', code);
  };

  return {
    currencySymbol,
    currencyCode,
    formatCurrency,
    updateCurrency
  };
}
