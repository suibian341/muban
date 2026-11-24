# Testing Checklist

## Pre-Testing Setup

- [ ] Database migrations completed (`python backend/migrations/run.py`)
- [ ] Backend server running (`python backend/app.py`)
- [ ] Frontend server running (`npm run dev` in frontend directory)
- [ ] Python requests library installed (`pip install requests`)

## Feature Testing Checklist

### 1. Clearance Products Feature
- [ ] Clearance products display on home page
- [ ] Clearance products page loads correctly
- [ ] Clearance products can be filtered by category
- [ ] Clearance products show stock quantity
- [ ] Clearance badge displays on product cards
- [ ] API endpoint `/api/clearance-products` returns data

### 2. Wishlist Feature
- [ ] "Add to Wishlist" button appears on product cards
- [ ] Items can be added to wishlist
- [ ] Wishlist panel displays correctly
- [ ] Items can be removed from wishlist
- [ ] Wishlist can be cleared
- [ ] Wishlist items can be submitted as inquiry
- [ ] Wishlist persists across page navigation
- [ ] API endpoints work correctly:
  - [ ] POST `/api/wishlist` (add item)
  - [ ] GET `/api/wishlist` (get items)
  - [ ] DELETE `/api/wishlist/:id` (remove item)
  - [ ] POST `/api/wishlist/submit` (submit as inquiry)

### 3. Product Filtering
- [ ] Filter by MOQ works
- [ ] Filter by lead time works
- [ ] Filter by certification works
- [ ] Filter by clearance status works
- [ ] Multiple filters can be combined
- [ ] Filters persist when navigating
- [ ] API supports all filter parameters

### 4. Admin Dashboard
- [ ] Dashboard loads without errors
- [ ] Stats cards display correct numbers
- [ ] Factory approval tab works
- [ ] Product approval tab works
- [ ] Batch selection works
- [ ] Batch operations (feature, clearance, delete) work
- [ ] Analytics tab displays
- [ ] Customers tab displays
- [ ] Factory detail view works
- [ ] Product detail view works

### 5. Inquiry Management
- [ ] Inquiries display in admin panel
- [ ] Inquiries can be filtered by status
- [ ] Inquiry details can be viewed
- [ ] Inquiry status can be updated
- [ ] Admin notes can be added
- [ ] New inquiries from wishlist appear

### 6. Data Integrity
- [ ] Products have `is_clearance` field
- [ ] Products have `stock_quantity` field
- [ ] Products have `certification` field
- [ ] Inquiries have `source` field
- [ ] Inquiries have `customer_level` field
- [ ] Wishlist table exists and works

### 7. Internationalization
- [ ] Chinese text displays correctly
- [ ] English text displays correctly
- [ ] Language switching works
- [ ] New fields have translations:
  - [ ] Clearance (清仓)
  - [ ] Wishlist (意向单)
  - [ ] Analytics (数据分析)
  - [ ] Customers (客户管理)

### 8. Floating Widgets
- [ ] WhatsApp button displays
- [ ] WeChat QR code panel works
- [ ] Live chat panel works
- [ ] Quick inquiry form works
- [ ] Widgets are responsive on mobile

### 9. Performance
- [ ] Page load time is acceptable (< 3s)
- [ ] API responses are fast (< 1s)
- [ ] No console errors
- [ ] No memory leaks
- [ ] Images load correctly

### 10. Browser Compatibility
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari
- [ ] Edge
- [ ] Mobile browsers

## Bug Reporting

If you find issues, document:
- [ ] Browser and version
- [ ] Steps to reproduce
- [ ] Expected behavior
- [ ] Actual behavior
- [ ] Screenshots/videos if applicable
- [ ] Console errors (if any)

## Sign-Off

- [ ] All tests passed
- [ ] No critical bugs found
- [ ] Performance acceptable
- [ ] Ready for deployment

**Tested by:** ________________
**Date:** ________________
**Notes:** ________________
