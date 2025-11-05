# Dynamic Company Branding Implementation

## Overview
This document describes the implementation of dynamic company branding throughout the application. Company information is now fetched from the database and displayed dynamically in multiple locations.

## Features Implemented

### 1. Dashboard Sidebar - Dynamic Company Name
**Location**: `frontend/src/components/Layout.tsx`

**Implementation**:
- Fetches company settings from the API on component mount
- Displays company name dynamically in both desktop and mobile sidebar headers
- Falls back to "SchoolCopy" if settings are not available

**Code Changes**:
```typescript
// Added state for company name
const [companyName, setCompanyName] = useState('SchoolCopy');

// Fetch settings on mount
useEffect(() => {
  const fetchSettings = async () => {
    try {
      const settings = await api.getSettings();
      if (settings?.company_name) {
        setCompanyName(settings.company_name);
      }
    } catch (error) {
      console.error('Failed to load company settings:', error);
    }
  };
  fetchSettings();
}, []);
```

### 2. PDF Invoice - Dynamic Company Information
**Location**: `backend/services/invoice_generator.py`

**Implementation**:
- Accepts `company_settings` parameter (already implemented)
- Uses database values for company name, address, phone, email, and currency
- Falls back to config values if database settings are not available
- Displays company information in both header and footer sections

**Updated Sections**:
- **Header**: Company name and contact information
- **Footer**: Complete company details with address, phone, and email
- **Currency**: Uses dynamic currency symbol throughout the invoice

**Code Changes**:
```python
# Fetch and use company settings with fallback
company_name = (company_settings or {}).get('company_name', settings.company_name)
company_address = (company_settings or {}).get('company_address', settings.company_address)
company_phone = (company_settings or {}).get('company_phone', settings.company_phone)
company_email = (company_settings or {}).get('company_email', settings.company_email)
currency_symbol = (company_settings or {}).get('currency_symbol', 'Rs')
```

### 3. Payment Receipt - Dynamic Company Information
**Location**: `backend/services/payment_receipt_generator.py`

**Implementation**:
- Added `company_settings` parameter to all relevant methods
- Uses database values for company branding throughout the receipt
- Displays company information in header, footer, and contact sections
- Uses dynamic currency symbol for amount display

**Updated Methods**:
- `_create_premium_header()`: Uses dynamic company name
- `_create_amount_spotlight()`: Uses dynamic currency symbol
- `_create_inline_footer()`: Uses all company details (name, phone, email, address)
- `generate_receipt()`: Accepts and passes company settings to all methods

### 4. Payment Receipt API Integration
**Location**: `backend/routers/payments.py`

**Implementation**:
- Fetches company settings from database when generating receipts
- Passes settings to the receipt generator
- Includes proper error handling and logging

**Code Changes**:
```python
# Fetch company settings from database
settings_statement = select(Settings)
company_settings_obj = session.exec(settings_statement).first()
company_settings = None
if company_settings_obj:
    company_settings = {
        "company_name": company_settings_obj.company_name,
        "company_email": company_settings_obj.company_email,
        "company_phone": company_settings_obj.company_phone,
        "company_address": company_settings_obj.company_address,
        "currency_symbol": company_settings_obj.currency_symbol
    }

# Generate receipt with company settings
receipt_path = payment_receipt_generator.generate_receipt(
    payment_data, 
    client_data, 
    company_settings
)
```

## Data Flow

### Frontend (Sidebar)
```
Layout Component → api.getSettings() → Backend /settings endpoint → Database → Display in Sidebar
```

### Backend (PDF Generation)
```
Generate Invoice/Receipt Request → Fetch Settings from DB → Pass to Generator → Create PDF with Dynamic Data
```

## Database Schema
The `settings` table contains:
- `company_name`: Business name
- `company_email`: Contact email
- `company_phone`: Contact phone number
- `company_address`: Business address
- `currency_code`: Currency code (e.g., PKR, USD)
- `currency_symbol`: Currency symbol (e.g., Rs, $)
- `timezone`: Business timezone
- `date_format`: Preferred date format

## API Endpoints Used

### GET /settings
**Purpose**: Fetch current company settings
**Used By**: 
- Frontend Layout component (sidebar)
- Frontend Settings page

**Response**:
```json
{
  "company_name": "Saleem Copy Manufacturing",
  "company_email": "Saleem@schoolcopy.com",
  "company_phone": "+92 300 1234567",
  "company_address": "123 Business Street, Karachi",
  "currency_code": "PKR",
  "currency_symbol": "Rs",
  "timezone": "Asia/Karachi",
  "date_format": "DD/MM/YYYY",
  "id": "uuid",
  "updated_at": "timestamp",
  "created_at": "timestamp"
}
```

### PUT /settings
**Purpose**: Update company settings
**Used By**: Frontend Settings page
**Note**: Already implemented, no changes needed

## Error Handling

### Frontend
- Graceful fallback to default company name if API fails
- Console error logging for debugging
- No user-facing errors (silent failure with fallback)

### Backend
- Fallback to config values if database settings are not available
- Proper error logging for debugging
- PDF generation continues even if settings are missing

## Testing

### Manual Testing Steps

1. **Test Sidebar Company Name**:
   - Open the application
   - Navigate to Settings page
   - Update company name
   - Save settings
   - Verify sidebar shows new company name (may need to refresh)

2. **Test PDF Invoice**:
   - Go to Orders page
   - Select an order
   - Generate invoice
   - Verify PDF shows:
     - Company name in header
     - Company details in footer
     - Correct currency symbol

3. **Test Payment Receipt**:
   - Go to Payments page
   - Select a payment
   - Generate receipt
   - Verify PDF shows:
     - Company name in header
     - Company contact details in footer
     - Correct currency symbol in amount

### Automated Testing
Run the test script:
```bash
python test_dynamic_branding.py
```

## Fallback Behavior

If database settings are not available:
- **Sidebar**: Shows "SchoolCopy"
- **PDFs**: Use values from `backend/config.py`
- **Currency**: Defaults to "Rs"

This ensures the application continues to work even if settings are not configured.

## Configuration Files

### Backend Config
**File**: `backend/config.py`
Contains default values used as fallbacks:
- `company_name`
- `company_email`
- `company_phone`
- `company_address`

### Frontend API Client
**File**: `frontend/src/lib/api-client.ts`
Contains `getSettings()` and `updateSettings()` methods

## Benefits

1. **Centralized Management**: Update company info once in Settings page
2. **Consistency**: Same information across all locations
3. **Professional**: PDFs and UI reflect actual business branding
4. **Flexibility**: Easy to update without code changes
5. **Multi-tenant Ready**: Foundation for supporting multiple companies

## Future Enhancements

Potential improvements:
1. Add company logo upload and display
2. Support multiple color themes
3. Add custom email templates
4. Support multiple languages
5. Add company-specific terms and conditions

## Troubleshooting

### Issue: Sidebar still shows old company name
**Solution**: Refresh the page or clear browser cache

### Issue: PDFs show default values
**Solution**: 
1. Check if settings are saved in database
2. Run `python test_dynamic_branding.py`
3. Verify backend logs for errors

### Issue: Settings API returns 404
**Solution**: 
1. Ensure database migration is complete
2. Check if `settings` table exists
3. Verify backend server is running

## Code Quality

### Best Practices Followed
- ✓ Proper error handling with fallbacks
- ✓ Type hints for better code clarity
- ✓ Minimal code changes (no breaking changes)
- ✓ Backward compatible (works with or without settings)
- ✓ No hardcoded values in new code
- ✓ Consistent naming conventions
- ✓ Proper documentation

### No Breaking Changes
- Existing settings routes unchanged
- Existing save functionality unchanged
- All existing features continue to work
- Backward compatible with missing settings

## Summary

This implementation successfully adds dynamic company branding throughout the application by:
1. Fetching company settings from the database
2. Displaying them in the dashboard sidebar
3. Using them in PDF invoice generation
4. Using them in payment receipt generation
5. Providing proper fallbacks for reliability
6. Maintaining code quality and best practices

The implementation is production-ready and requires no additional configuration beyond using the existing Settings page to update company information.
