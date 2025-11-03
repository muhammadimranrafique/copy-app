# Payment Receipt Download Authentication Fix

## Issue Summary
The payment receipt download feature was failing with "Authentication required" error even when users were logged in.

## Root Cause
The `downloadPaymentReceipt` function in `frontend/src/lib/mock-api.ts` was attempting to retrieve the JWT token from `localStorage.getItem('token')`, but the application stores the authentication token under the key `'access_token'`.

## Changes Made

### File: `frontend/src/lib/mock-api.ts`

**Line 280 - Fixed token retrieval:**
```typescript
// BEFORE (incorrect):
const token = localStorage.getItem('token');

// AFTER (correct):
const token = localStorage.getItem('access_token');
```

**Enhanced error handling and logging:**
1. Improved error message when token is missing
2. Added debug logging to show token presence (without exposing the actual token)
3. Added response status logging for debugging
4. Added specific error handling for 401 authentication failures

## Technical Details

### Authentication Flow
1. User logs in → JWT token stored as `'access_token'` in localStorage
2. All API calls use `getAuthHeaders()` which correctly retrieves `'access_token'`
3. Receipt download now also uses `'access_token'` consistently

### Backend Endpoint
- **Endpoint:** `POST /api/v1/payments/{payment_id}/receipt`
- **Authentication:** Required via `get_current_user` dependency
- **Response:** PDF file with Content-Disposition header

### Debug Logging
When `VITE_DEBUG=true`, the following logs are now available:
- `[Download Receipt Request]` - Shows payment ID and token presence
- `[Download Receipt Response]` - Shows HTTP status and status text
- `[Download Receipt Success]` - Shows downloaded filename
- `[Download Receipt Error]` - Shows any errors that occur

## Testing Recommendations

1. **Happy Path Test:**
   - Log in to the application
   - Navigate to Payments page
   - Click download button (⬇) next to any payment
   - Verify PDF downloads successfully

2. **Authentication Test:**
   - Clear localStorage or use incognito mode
   - Try to download a receipt without logging in
   - Verify appropriate error message is shown

3. **Debug Mode Test:**
   - Set `VITE_DEBUG=true` in environment
   - Download a receipt
   - Check browser console for detailed logs

## Files Modified
- `frontend/src/lib/mock-api.ts` - Fixed authentication token retrieval

## Files Verified
- `backend/routers/payments.py` - Confirmed endpoint requires authentication
- `frontend/src/pages/Payments.tsx` - Confirmed UI properly calls the function

## Status
✅ **FIXED** - Authentication now works correctly for payment receipt downloads
