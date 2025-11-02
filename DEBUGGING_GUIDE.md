# Network/API Debugging Guide

## Overview

This guide explains the network/API debugging features added to the application and how to diagnose common issues.

## Debug Logging

### Enabling Debug Mode

Debug logging is controlled by the `VITE_DEBUG` environment variable in the frontend `.env` file:

```env
VITE_DEBUG=true
```

When enabled, the `fetchJSON` function will log detailed information about every API request and response to the browser console.

### What Gets Logged

When `VITE_DEBUG=true`, you'll see the following in the browser console:

1. **Request Details**
   - HTTP method (GET, POST, PUT, DELETE)
   - Full URL
   - Request body (for POST/PUT requests)
   ```
   [API Request] GET http://127.0.0.1:8000/api/v1/leaders/
   ```

2. **Response Status**
   - HTTP status code
   - Status text
   - URL
   ```
   [API Response] 200 OK http://127.0.0.1:8000/api/v1/leaders/
   ```

3. **Response Body**
   - Raw text (first 500 characters)
   - Parsed JSON object
   ```
   [API Response Text] http://127.0.0.1:8000/api/v1/leaders/ => [{"id":"...","name":"..."}...]
   [API Response JSON] http://127.0.0.1:8000/api/v1/leaders/ => Array(10)
   ```

4. **Error Details**
   - Error response body
   - JSON parsing errors
   - Network errors
   ```
   [API Error Body] http://127.0.0.1:8000/api/v1/leaders/ {"detail":"Not found"}
   [API JSON Parse Error] http://127.0.0.1:8000/api/v1/leaders/ SyntaxError: Unexpected token...
   ```

### Disabling Debug Mode

To disable debug logging, set `VITE_DEBUG=false` or remove the line from `.env`:

```env
VITE_DEBUG=false
```

## Common Issues Explained

### 1. 307 Temporary Redirect

**What you see in logs:**
```
INFO: 127.0.0.1:51756 - "GET /api/v1/leaders HTTP/1.1" 307 Temporary Redirect
INFO: 127.0.0.1:51756 - "GET /api/v1/leaders HTTP/1.1" 307 Temporary Redirect
```

**What it means:**
- FastAPI automatically redirects URLs without trailing slashes to URLs with trailing slashes
- The browser follows the redirect automatically
- This causes two requests for every API call

**Is it a problem?**
- **Performance Impact**: Minor - adds ~10-50ms per request
- **Functionality**: No - the redirect works correctly
- **Best Practice**: Should be fixed to avoid unnecessary redirects

**How to fix:**
The frontend is calling `/api/v1/leaders` but FastAPI expects `/api/v1/leaders/`. 

**Option 1: Add trailing slashes to frontend calls** (Recommended)
```typescript
// In mock-api.ts, update the getLeaders function:
const res = await fetchJSON(`/leaders/`);  // Add trailing slash
```

**Option 2: Configure FastAPI to not require trailing slashes**
```python
# In backend/main.py
app = FastAPI(
    title="School Copy API",
    redirect_slashes=False  # Add this
)
```

### 2. SQLAlchemy ROLLBACK Messages

**What you see in logs:**
```
2025-11-02 19:06:12,875 INFO sqlalchemy.engine.Engine ROLLBACK
```

**What it means:**
- SQLAlchemy automatically rolls back read-only transactions when the session closes
- This is **NORMAL** and **EXPECTED** behavior
- It's part of SQLAlchemy's transaction management

**Is it a problem?**
- **No** - This is standard SQLAlchemy behavior
- The ROLLBACK happens after successful SELECT queries
- It's just cleaning up the transaction

**Why it happens:**
```python
# In backend/database.py
def get_session():
    with Session(engine) as session:
        yield session
    # When the context manager exits, SQLAlchemy calls ROLLBACK
    # to clean up any uncommitted transactions
```

**How to reduce log noise:**
Set `echo=False` in `backend/database.py` to disable SQL logging:
```python
engine = create_engine(settings.database_url, echo=False)  # Change to False
```

### 3. 401 Unauthorized Errors

**What you see:**
- Automatic redirect to `/login` page
- "Session expired. Please log in again." message

**What it means:**
- Your JWT token has expired or is invalid
- The `fetchJSON` function automatically handles this by:
  1. Clearing the token from localStorage
  2. Redirecting to the login page

**How to fix:**
- Log in again
- Check token expiration time in `backend/config.py`:
  ```python
  access_token_expire_minutes: int = 30  # Increase if needed
  ```

### 4. JSON Parsing Errors

**What you see in debug logs:**
```
[API JSON Parse Error] http://127.0.0.1:8000/api/v1/leaders/ SyntaxError: Unexpected token < in JSON at position 0
Raw text: <!DOCTYPE html>...
```

**What it means:**
- The server returned HTML instead of JSON
- Usually indicates a server error (500) or wrong endpoint

**How to fix:**
1. Check the backend logs for errors
2. Verify the endpoint exists in the backend
3. Check if the backend is running

## Improved Error Handling

The updated `fetchJSON` function includes:

1. **Single Response Read**: Reads the response body only once to avoid errors
2. **Proper JSON Detection**: Checks if response starts with `{` or `[` before parsing
3. **Graceful Error Handling**: Catches and logs JSON parsing errors with the raw text
4. **Conditional Logging**: Only logs when `VITE_DEBUG=true` to avoid console spam

## Testing the Debug Mode

1. **Enable debug mode:**
   ```bash
   # In frontend/.env
   echo "VITE_DEBUG=true" >> .env
   ```

2. **Restart the frontend dev server:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open browser console:**
   - Press F12 or right-click → Inspect
   - Go to the Console tab

4. **Navigate to any page:**
   - You should see detailed API logs for every request

5. **Look for issues:**
   - Check for 307 redirects
   - Look for failed requests
   - Verify response data structure

## Performance Considerations

### Debug Mode Impact

- **Console Logging**: Minimal performance impact (~1-2ms per log)
- **String Operations**: Truncating long responses to 500 chars
- **Production**: Always set `VITE_DEBUG=false` in production

### 307 Redirect Impact

- **Extra Network Round Trip**: ~10-50ms per request
- **Doubled Request Count**: 2x requests for every API call
- **Recommendation**: Fix by adding trailing slashes to API calls

## Backend Logging Configuration

### Current Setup

```python
# backend/database.py
engine = create_engine(settings.database_url, echo=True)
```

This logs **all SQL queries** to the console, which is useful for debugging but verbose.

### Recommended for Production

```python
# backend/database.py
engine = create_engine(settings.database_url, echo=False)
```

### Selective Logging

To log only slow queries:
```python
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
```

## Summary

| Issue | Severity | Action Required |
|-------|----------|----------------|
| 307 Redirects | Low | Optional: Add trailing slashes to API calls |
| SQLAlchemy ROLLBACK | None | Normal behavior, no action needed |
| Debug Logging | None | Disable in production (`VITE_DEBUG=false`) |
| SQL Query Logging | Low | Optional: Set `echo=False` in production |

## Next Steps

1. ✅ Debug logging is now enabled and working
2. ⚠️ Consider fixing 307 redirects by adding trailing slashes
3. ⚠️ Disable SQL logging in production (`echo=False`)
4. ✅ Use debug mode to diagnose any future API issues

