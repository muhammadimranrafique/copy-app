# 307 Redirect Fix - Verification Checklist

## Quick Verification Steps

### ✅ Step 1: Restart Frontend (Required)

The frontend dev server needs to be restarted to pick up the changes.

**If frontend is running:**
```bash
# In the terminal running the frontend, press Ctrl+C
# Then restart:
cd frontend
npm run dev
```

**If frontend is NOT running:**
```bash
cd frontend
npm run dev
```

Wait for the message:
```
  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

### ✅ Step 2: Open Browser & Developer Tools

1. Open browser: http://localhost:5173
2. Press **F12** to open Developer Tools
3. Go to **Console** tab

---

### ✅ Step 3: Test Leaders Page

1. Navigate to **Leaders** page (click "Leaders" in sidebar)
2. Check **Console** tab for debug logs

**✅ Expected (GOOD):**
```
[API Request] GET http://127.0.0.1:8000/api/v1/leaders/
[API Response] 200 OK http://127.0.0.1:8000/api/v1/leaders/
[API Response Text] http://127.0.0.1:8000/api/v1/leaders/ => [{"id":"...
[API Response JSON] http://127.0.0.1:8000/api/v1/leaders/ => Array(X)
```

**❌ Old Behavior (BAD - should NOT see):**
```
[API Request] GET http://127.0.0.1:8000/api/v1/leaders
[API Response] 307 Temporary Redirect ...
```

3. Go to **Network** tab
4. Filter by **Fetch/XHR**
5. Look for the `leaders` request

**✅ Expected:**
- URL: `http://127.0.0.1:8000/api/v1/leaders/` (with trailing slash)
- Status: `200`
- No redirect

**❌ Old Behavior (should NOT see):**
- URL: `http://127.0.0.1:8000/api/v1/leaders` (no trailing slash)
- Status: `307`

---

### ✅ Step 4: Test Orders Page

1. Navigate to **Orders** page
2. Check **Console** tab

**✅ Expected:**
```
[API Request] GET http://127.0.0.1:8000/api/v1/orders/
[API Response] 200 OK http://127.0.0.1:8000/api/v1/orders/
```

3. Check **Network** tab
4. Verify URL ends with `/orders/` (with trailing slash)
5. Verify status is `200` (not `307`)

---

### ✅ Step 5: Test Products Page

1. Navigate to **Products** page
2. Check **Console** tab

**✅ Expected:**
```
[API Request] GET http://127.0.0.1:8000/api/v1/products/
[API Response] 200 OK http://127.0.0.1:8000/api/v1/products/
```

3. Check **Network** tab
4. Verify URL ends with `/products/` (with trailing slash)
5. Verify status is `200` (not `307`)

---

### ✅ Step 6: Test Payments Page

1. Navigate to **Payments** page
2. Check **Console** tab

**✅ Expected:**
```
[API Request] GET http://127.0.0.1:8000/api/v1/payments/
[API Response] 200 OK http://127.0.0.1:8000/api/v1/payments/
```

3. Check **Network** tab
4. Verify URL ends with `/payments/` (with trailing slash)
5. Verify status is `200` (not `307`)

---

### ✅ Step 7: Test Dashboard Page

1. Navigate to **Dashboard** page
2. Check **Console** tab

**✅ Expected:**
```
[API Request] GET http://127.0.0.1:8000/api/v1/dashboard/stats
[API Response] 200 OK http://127.0.0.1:8000/api/v1/dashboard/stats
```

3. Check **Network** tab
4. Verify URL is `/dashboard/stats` (not `/dashboard`)
5. Verify status is `200` (not `307`)

---

### ✅ Step 8: Check Backend Terminal

Look at the backend terminal (where uvicorn is running).

**✅ Expected (GOOD):**
```
INFO: 127.0.0.1:XXXXX - "GET /api/v1/leaders/ HTTP/1.1" 200 OK
INFO: sqlalchemy.engine.Engine SELECT ... FROM clients
INFO: sqlalchemy.engine.Engine ROLLBACK
```

**❌ Old Behavior (BAD - should NOT see):**
```
INFO: 127.0.0.1:XXXXX - "GET /api/v1/leaders HTTP/1.1" 307 Temporary Redirect
INFO: 127.0.0.1:XXXXX - "GET /api/v1/leaders/ HTTP/1.1" 200 OK
```

**Note:** The `ROLLBACK` messages are NORMAL and expected. They indicate proper transaction cleanup.

---

### ✅ Step 9: Verify Real Data (Not Mock)

1. Check that the data shown is from your PostgreSQL database
2. Look for the debug log showing actual records:
   ```
   [API Response JSON] http://127.0.0.1:8000/api/v1/leaders/ => Array(X)
   ```
3. Expand the array in the console to see the actual records

**How to confirm:**
- Mock data always returns the same static records
- Real data comes from your database
- If you see different data than the mock data, it's working!

---

## 🎯 Final Checklist

Mark each item as you verify it:

- [ ] Frontend dev server restarted successfully
- [ ] Browser opened at http://localhost:5173
- [ ] Developer Tools (F12) opened
- [ ] **Leaders page:** No 307 redirects, URL has trailing slash
- [ ] **Orders page:** No 307 redirects, URL has trailing slash
- [ ] **Products page:** No 307 redirects, URL has trailing slash
- [ ] **Payments page:** No 307 redirects, URL has trailing slash
- [ ] **Dashboard page:** No 307 redirects, URL is `/dashboard/stats`
- [ ] Backend terminal shows no 307 redirects
- [ ] All requests return `200 OK`
- [ ] Data loads from PostgreSQL (not mock data)
- [ ] No errors in browser console
- [ ] No errors in backend terminal

---

## 🐛 Troubleshooting

### Issue: Still seeing 307 redirects

**Solution:**
1. Make sure you restarted the frontend dev server
2. Clear browser cache (Ctrl+Shift+Delete)
3. Hard reload the page (Ctrl+Shift+R)
4. Check that `frontend/src/lib/mock-api.ts` has the trailing slashes

### Issue: "Failed to load leaders/orders/etc."

**Solution:**
1. Check that backend is running (http://localhost:8000/docs)
2. Check that you're logged in (JWT token is valid)
3. Check backend terminal for errors
4. Verify `.env` has `VITE_USE_MOCK=false`

### Issue: Seeing mock data instead of real data

**Solution:**
1. Check `frontend/.env` has `VITE_USE_MOCK=false`
2. Restart frontend dev server
3. Clear localStorage: Open console and run `localStorage.clear()`
4. Refresh the page

### Issue: "Session expired" error

**Solution:**
1. Your JWT token has expired
2. Log out and log back in
3. Check `backend/config.py` for token expiration time
4. Consider increasing `access_token_expire_minutes`

### Issue: SQLAlchemy ROLLBACK messages

**This is NORMAL!** These messages indicate proper transaction cleanup. They are NOT errors.

To reduce log noise, set `echo=False` in `backend/database.py`:
```python
engine = create_engine(settings.database_url, echo=False)
```

---

## 📊 Performance Comparison

### Before Fix:
- **Requests per API call:** 2 (original + redirect)
- **Extra latency:** ~10-50ms per request
- **Network traffic:** 2x normal

### After Fix:
- **Requests per API call:** 1 (no redirect)
- **Extra latency:** 0ms
- **Network traffic:** Normal

---

## ✅ Success!

If all checklist items are marked, congratulations! The 307 redirect issue is fixed.

**What changed:**
- All GET request URLs now include trailing slashes
- Dashboard endpoint uses `/dashboard/stats` instead of `/dashboard`
- No more 307 redirects
- Faster API calls (~10-50ms improvement per request)

**Next steps:**
- Consider implementing optional enhancements (see `307_REDIRECT_FIX_SUMMARY.md`)
- Disable debug logging in production (`VITE_DEBUG=false`)
- Disable SQL logging in production (`echo=False` in `database.py`)

---

## 📞 Need Help?

If you encounter issues not covered here:

1. Check `307_REDIRECT_FIX_SUMMARY.md` for detailed information
2. Check `DEBUGGING_GUIDE.md` for debugging tips
3. Review the changes in `frontend/src/lib/mock-api.ts`
4. Verify backend routes in `backend/routers/*.py`

