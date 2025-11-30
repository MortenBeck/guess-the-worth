# Frontend Payment & Dashboard Issues - Implementation Plan

## CONTEXT & SYSTEM ANALYSIS

This document contains a comprehensive plan to fix payment and dashboard issues in the Guess The Worth application. This prompt is optimized for Claude Code LLM execution.

### System Architecture Summary

**Payment Flow:**
```
User places winning bid (bid.amount >= artwork.secret_threshold)
  ↓
Backend: artwork.status = "PENDING_PAYMENT", bid.is_winning = true
  ↓
Socket event "payment_required" emitted to artwork room
  ↓
Frontend: PaymentModal opens, calls POST /api/payments/create-intent
  ↓
Backend: Creates Payment (status: PENDING), returns client_secret
  ↓
Stripe Elements: User completes payment
  ↓
Stripe Webhook: POST /api/payments/webhook (event: payment_intent.succeeded)
  ↓
Backend: Payment.status = "SUCCEEDED", Artwork.status = "SOLD"
  ↓
Socket event "payment_completed" emitted
  ↓
Frontend: SHOULD update UI (CURRENTLY BROKEN)
```

### Database Models (Reference)

**Artwork Statuses:** `ACTIVE`, `PENDING_PAYMENT`, `SOLD`, `ARCHIVED`

**Payment Statuses:** `PENDING`, `PROCESSING`, `SUCCEEDED`, `FAILED`, `CANCELED`

**Bid Model Fields:**
- `id`, `artwork_id`, `bidder_id`, `amount`, `created_at`
- `is_winning` (Boolean) - true when `bid.amount >= artwork.secret_threshold`

**Key Relationships:**
- Bid ↔ Artwork (many-to-one, eager loaded with `joinedload`)
- Bid ↔ Payment (one-to-one, optional)

### API Endpoints (Reference)

**Bids:**
- `GET /api/bids/my-bids` - Returns all user's bids with artwork relationship eager loaded
- `POST /api/bids/` - Creates bid, emits "payment_required" if winning

**Payments:**
- `POST /api/payments/create-intent` - Creates Stripe PaymentIntent, returns client_secret
- `GET /api/payments/my-payments` - Returns all user's payments
- `GET /api/payments/artwork/{artwork_id}` - Returns completed payment for artwork (SUCCEEDED only)
- `POST /api/payments/webhook` - Stripe webhook handler (emits "payment_completed" or "payment_failed")

**Stats:**
- `GET /api/stats/user` - Returns `{active_bids, won_auctions, total_spent}`

**Socket Events:**
- `payment_required` - Emitted when winning bid placed (room: `artwork_{id}`)
- `payment_completed` - Emitted when webhook confirms payment (room: `artwork_{id}`)
- `payment_failed` - Emitted when payment fails (room: `artwork_{id}`)

---

## IDENTIFIED ISSUES & ROOT CAUSES

### Issue 1: Artwork Page Doesn't Update After Payment Completion

**User Report:**
"Once the payment has been completed, the artwork doesn't appear as won in the dashboard. Furthermore, the entire artwork/# page doesn't update to won (stays at 'Active' and status as 'PENDING_PAYMENT')."

**Root Causes:**
1. **File:** `frontend/src/pages/ArtworkPage.jsx` (lines 52-98)
   - Only listens for `payment_required` socket event
   - Does NOT listen for `payment_completed` or `payment_failed` events
   - When webhook fires and updates database, frontend never refetches artwork data

2. **File:** `frontend/src/components/PaymentModal.jsx` (line 118)
   - Uses `alert()` for success notification (poor UX)
   - Doesn't invalidate React Query cache
   - Parent component (ArtworkPage) doesn't know payment succeeded

**Evidence:**
```javascript
// ArtworkPage.jsx line 93 - Only payment_required listener exists
socket.on("payment_required", handlePaymentRequired);
// Missing: socket.on("payment_completed", ...)
// Missing: socket.on("payment_failed", ...)
```

---

### Issue 2: Payment UI Disappears When User Leaves Page

**User Report:**
"If the payment doesn't go through and the user leaves the artwork/# page, there is no way to attempt another transaction anywhere (should be possible in both the dashboard and on the artwork/# page)."

**Root Causes:**
1. **File:** `frontend/src/pages/ArtworkPage.jsx`
   - Payment modal state (`showPaymentModal`, `paymentData`) is local component state (lines 31-32)
   - State resets when component unmounts (user navigates away)
   - No logic on mount to check: "Does this artwork have a pending payment for the current user?"

2. **Missing Functionality:**
   - No API call to retrieve existing payment for an artwork
   - No check for `artwork.status === "PENDING_PAYMENT"` + `user has winning bid` on page load
   - No automatic reopening of payment modal when returning to page

**Required Logic (Not Implemented):**
```javascript
// On ArtworkPage mount, should check:
if (artwork.status === "PENDING_PAYMENT" && userHasWinningBid) {
  // Fetch existing payment or check if payment completed
  // If payment still PENDING/FAILED, reopen PaymentModal
}
```

---

### Issue 3: Dashboard Lists Show Empty (Active Bids & Won Auctions)

**User Report:**
"The dashboard has no function other than listing stats. The active bids and won auctions don't show anything even if the user has won auctions and has bid."

**Visual Evidence:**
- Screenshot shows stats working correctly: "Active Bids: 2", "Won Auctions: 0"
- But lists below show: "No active bids" and "No won auctions yet"

**Root Causes:**

**Critical Bug in Won Auctions Filter:**
- **File:** `frontend/src/pages/UserDashboard.jsx` (line 61)
```javascript
// WRONG - Filters out PENDING_PAYMENT artworks
const wonAuctions = myBids.filter((bid) => bid.is_winning && bid.artwork?.status === "SOLD");
```

**User's Definition (from conversation):**
"Won auction is when a user has a bid at/above threshold (even if payment is pending)"

**Correct Filter Should Be:**
```javascript
// Winning bids regardless of artwork status (includes PENDING_PAYMENT and SOLD)
const wonAuctions = myBids.filter((bid) => bid.is_winning);
```

**Why Stats Work But Lists Don't:**
- Stats come from backend endpoint `/api/stats/user` which correctly counts winning bids
- Lists use frontend filtering logic which has incorrect filter

**Active Bids Filter Analysis:**
- **File:** `frontend/src/pages/UserDashboard.jsx` (line 60)
```javascript
const activeBids = myBids.filter((bid) => bid.artwork?.status === "ACTIVE");
```
- This might be too broad - should exclude winning bids to avoid duplication
- Correct filter: `artwork.status === "ACTIVE" && !bid.is_winning`

---

### Issue 4: No Payment Button in Dashboard for Pending Payments

**User Report:**
"In the dashboard, when a won auction is listed but the payment hasn't been completed, you should also have a button for that here (this button can just go to the artwork/# page for simplicity)."

**Root Causes:**
1. **File:** `frontend/src/pages/UserDashboard.jsx` (lines 227-292)
   - Won Auctions section doesn't check `artwork.status`
   - No conditional UI for PENDING_PAYMENT vs SOLD
   - No "Complete Payment" button for pending payments

**Required Functionality:**
```jsx
// In won auction card, should show:
{bid.artwork?.status === "PENDING_PAYMENT" ? (
  <Button onClick={() => navigate(`/artwork/${bid.artwork.id}`)}>
    Complete Payment
  </Button>
) : (
  <Badge>Paid</Badge>
)}
```

---

## IMPLEMENTATION PLAN

### STAGE 1: Fix Artwork Page Real-time Updates (HIGHEST PRIORITY)

**Objective:** Make artwork page update immediately when payment completes or fails.

**Files to Modify:**
1. `frontend/src/pages/ArtworkPage.jsx`
2. `frontend/src/components/PaymentModal.jsx`

**Tasks:**

**1.1: Add Socket Listeners for Payment Events**

In `ArtworkPage.jsx`, add two new socket event listeners alongside existing `payment_required` listener (around line 93):

```javascript
// Add after existing payment_required listener
useEffect(() => {
  if (!isAuthenticated) return;

  const handlePaymentRequired = (data) => {
    // ... existing code ...
  };

  const handlePaymentCompleted = (data) => {
    console.log("Payment completed event received:", data);

    // Only handle if for this artwork
    if (data.artwork_id === parseInt(id)) {
      // Invalidate queries to refetch fresh data
      queryClient.invalidateQueries(["artwork", id]);
      queryClient.invalidateQueries(["bids", id]);

      // Close payment modal if open
      setShowPaymentModal(false);
      setPaymentData(null);

      // Show success toast
      toaster.create({
        title: "Payment Successful!",
        description: "Congratulations! The artwork is now yours.",
        type: "success",
        duration: 8000,
      });
    }
  };

  const handlePaymentFailed = (data) => {
    console.log("Payment failed event received:", data);

    // Only handle if for this artwork
    if (data.artwork_id === parseInt(id)) {
      // Invalidate queries to refetch artwork (status should be back to ACTIVE)
      queryClient.invalidateQueries(["artwork", id]);
      queryClient.invalidateQueries(["bids", id]);

      // Keep modal open so user can retry
      // Show error toast
      toaster.create({
        title: "Payment Failed",
        description: data.reason || "Your payment could not be processed. Please try again.",
        type: "error",
        duration: 10000,
      });
    }
  };

  socket.on("payment_required", handlePaymentRequired);
  socket.on("payment_completed", handlePaymentCompleted);
  socket.on("payment_failed", handlePaymentFailed);

  return () => {
    socket.off("payment_required", handlePaymentRequired);
    socket.off("payment_completed", handlePaymentCompleted);
    socket.off("payment_failed", handlePaymentFailed);
  };
}, [id, isAuthenticated, artwork, queryClient]);
```

**1.2: Improve PaymentModal Success Handling**

In `PaymentModal.jsx`, replace `alert()` with proper callback (line 116-119):

```javascript
const handleSuccess = (paymentIntent) => {
  console.log("Payment successful!", paymentIntent);

  // Show toast instead of alert
  toaster.create({
    title: "Payment Processing",
    description: "Your payment is being confirmed. The page will update shortly.",
    type: "info",
    duration: 5000,
  });

  // Close modal - socket event will handle the rest
  onClose();
};
```

**Import toaster at top of PaymentModal.jsx:**
```javascript
import { toaster } from "./ui/toaster-instance";
```

**1.3: Verify Backend Webhook Socket Emission**

No changes needed - backend already emits events correctly. Verify by checking:
- File: `backend/routers/payments.py` (lines 80-95 for success, 110-125 for failure)

---

### STAGE 2: Fix Payment UI Persistence (Retry Payment Flow)

**Objective:** When user returns to artwork page with pending payment, automatically show payment modal.

**Files to Modify:**
1. `frontend/src/pages/ArtworkPage.jsx`
2. `frontend/src/services/paymentService.js` (may need new method)

**Tasks:**

**2.1: Add Pending Payment Check on Mount**

In `ArtworkPage.jsx`, add new useEffect after artwork data loads (around line 100):

```javascript
// Check for pending payment on mount/artwork change
useEffect(() => {
  if (!artwork || !isAuthenticated) return;

  const checkPendingPayment = async () => {
    // Only check if artwork is pending payment
    if (artwork.status !== "PENDING_PAYMENT") return;

    // Check if current user has the winning bid
    const userBids = recentBids.filter(bid => bid.bidder?.id === useAuthStore.getState().user?.id);
    const winningBid = userBids.find(bid => bid.is_winning);

    if (!winningBid) return; // User is not the winner

    // Check if payment modal is already open
    if (showPaymentModal) return;

    try {
      // Try to get existing payment for this artwork
      const response = await paymentService.getArtworkPayment(artwork.id);
      const payment = response.data;

      // If payment is still pending/failed, reopen modal
      if (payment && (payment.status === "PENDING" || payment.status === "FAILED")) {
        setPaymentData({
          bidId: winningBid.id,
          amount: winningBid.amount,
          artworkTitle: artwork.title,
        });
        setShowPaymentModal(true);

        toaster.create({
          title: "Complete Your Payment",
          description: "You have a pending payment for this artwork.",
          type: "info",
          duration: 5000,
        });
      }
    } catch (error) {
      // If payment doesn't exist yet (404), show modal to create one
      if (error.response?.status === 404) {
        setPaymentData({
          bidId: winningBid.id,
          amount: winningBid.amount,
          artworkTitle: artwork.title,
        });
        setShowPaymentModal(true);

        toaster.create({
          title: "Payment Required",
          description: "Please complete payment to secure your artwork.",
          type: "warning",
          duration: 5000,
        });
      }
    }
  };

  checkPendingPayment();
}, [artwork, recentBids, isAuthenticated]);
```

**2.2: Add getArtworkPayment Method (if doesn't exist)**

Check if `frontend/src/services/paymentService.js` has `getArtworkPayment` method.

If missing, add:
```javascript
getArtworkPayment: async (artworkId) => {
  const response = await apiClient.get(`/payments/artwork/${artworkId}`);
  return response.data;
},
```

**2.3: Handle 403/404 Errors Gracefully**

The backend endpoint `/api/payments/artwork/{artwork_id}` might return 403 if user is not seller/admin. Update the check to handle this:

```javascript
catch (error) {
  // 404 = no payment exists yet, 403 = user not authorized (buyer trying to access)
  // Both cases mean we should show payment modal
  if (error.response?.status === 404 || error.response?.status === 403) {
    // ... show modal ...
  }
}
```

---

### STAGE 3: Fix Dashboard Data Display

**Objective:** Show actual active bids and won auctions in dashboard lists.

**Files to Modify:**
1. `frontend/src/pages/UserDashboard.jsx`

**Tasks:**

**3.1: Fix Won Auctions Filter**

In `UserDashboard.jsx`, replace line 61:

**BEFORE:**
```javascript
const wonAuctions = myBids.filter((bid) => bid.is_winning && bid.artwork?.status === "SOLD");
```

**AFTER:**
```javascript
// Won auctions = any winning bid, regardless of payment status
const wonAuctions = myBids.filter((bid) => bid.is_winning);
```

**3.2: Fix Active Bids Filter (Optional but Recommended)**

Replace line 60 to exclude winning bids (avoid showing same artwork in both lists):

**BEFORE:**
```javascript
const activeBids = myBids.filter((bid) => bid.artwork?.status === "ACTIVE");
```

**AFTER:**
```javascript
// Active bids = bids on active artworks where user is not currently winning
const activeBids = myBids.filter((bid) => bid.artwork?.status === "ACTIVE" && !bid.is_winning);
```

**3.3: Update Won Auctions Display Logic**

In the Won Auctions map (lines 246-289), add status-aware UI:

**BEFORE:**
```jsx
<Badge colorScheme="green" variant="subtle">
  Won
</Badge>
```

**AFTER:**
```jsx
{bid.artwork?.status === "PENDING_PAYMENT" ? (
  <Badge colorScheme="yellow" variant="subtle">
    Payment Pending
  </Badge>
) : (
  <Badge colorScheme="green" variant="subtle">
    Paid
  </Badge>
)}
```

---

### STAGE 4: Add Payment Button to Dashboard Won Auctions

**Objective:** Allow users to complete pending payments directly from dashboard.

**Files to Modify:**
1. `frontend/src/pages/UserDashboard.jsx`

**Tasks:**

**4.1: Add Complete Payment Button**

In Won Auctions section (around line 270-287), add conditional button:

**Update the card content** (inside the Box that shows artwork details):

```jsx
<Box p={4}>
  <VStack align="start" spacing={2}>
    {bid.artwork?.status === "PENDING_PAYMENT" ? (
      <Badge colorScheme="yellow" variant="subtle">
        Payment Pending
      </Badge>
    ) : (
      <Badge colorScheme="green" variant="subtle">
        Paid
      </Badge>
    )}

    <Text fontWeight="semibold" color="white">
      {bid.artwork?.title}
    </Text>
    <Text fontSize="sm" color="#94a3b8">
      by {bid.artwork?.seller?.name || "Unknown Artist"}
    </Text>
    <Text fontSize="sm" color="green.400" fontWeight="bold">
      Won for ${bid.amount}
    </Text>

    {/* Add payment button for pending payments */}
    {bid.artwork?.status === "PENDING_PAYMENT" ? (
      <Button
        size="sm"
        colorScheme="yellow"
        width="full"
        onClick={(e) => {
          e.stopPropagation(); // Prevent card click navigation
          navigate(`/artwork/${bid.artwork?.id}`);
        }}
      >
        Complete Payment
      </Button>
    ) : (
      <Text fontSize="xs" color="#94a3b8">
        Purchased: {new Date(bid.created_at).toLocaleDateString()}
      </Text>
    )}
  </VStack>
</Box>
```

**4.2: Prevent Double Navigation**

The won auction card already has `onClick={() => navigate(...)}`. Add `e.stopPropagation()` to button click to prevent double navigation (shown in code above).

---

### STAGE 5: Testing & Verification

**Objective:** Ensure all fixes work together correctly.

**Manual Testing Checklist:**

**Test 1: Complete Payment Flow**
1. Place winning bid on artwork
2. Complete payment in modal
3. Verify artwork page updates to "SOLD" status automatically (via socket)
4. Verify dashboard shows artwork in "Won Auctions" with "Paid" badge
5. Verify stats update (Total Spent increases)

**Test 2: Payment Failure & Retry**
1. Place winning bid on artwork
2. Use Stripe test card that fails: `4000000000000002`
3. Verify error toast appears
4. Verify modal stays open for retry
5. Try again with valid card: `4242424242424242`
6. Verify success

**Test 3: Leave Page During Payment**
1. Place winning bid on artwork
2. Payment modal opens
3. Navigate away (close tab or go to different page)
4. Navigate back to artwork page
5. Verify payment modal automatically reopens
6. Complete payment
7. Verify success

**Test 4: Dashboard Lists**
1. Have multiple bids:
   - Some on ACTIVE artworks (not winning)
   - One winning bid with PENDING_PAYMENT status
   - One winning bid with SOLD status (payment completed)
2. Verify "Active Bids" shows only non-winning bids on active artworks
3. Verify "Won Auctions" shows both PENDING_PAYMENT and SOLD winning bids
4. Verify "Complete Payment" button appears only for PENDING_PAYMENT artworks
5. Click button, verify navigation to artwork page with modal open

**Test 5: Real-time Updates**
1. Open artwork page in two browser windows (different users)
2. User A places winning bid
3. User B should see artwork status change to PENDING_PAYMENT in real-time
4. User A completes payment
5. User B should see artwork status change to SOLD in real-time

---

## ADDITIONAL CONSIDERATIONS

### Error Handling

**Payment API Failures:**
- If `createPaymentIntent` fails with 400 "Payment already completed", close modal gracefully
- If Stripe key is invalid, show clear error message
- Handle network errors with retry option

**Socket Disconnection:**
- If socket disconnects during payment, payment will still complete via webhook
- User can refresh page to see updated status
- Consider adding socket reconnection logic

### Edge Cases

**Multiple Browser Tabs:**
- If user completes payment in one tab, other tabs should update via socket events
- React Query cache invalidation handles this

**Payment Already Completed:**
- If user navigates to artwork page after payment completed but before socket event received
- Stage 2 logic will fetch payment status and see SUCCEEDED, won't reopen modal

**User Not Winner:**
- Stage 2 checks if user has winning bid before showing modal
- If another user outbid them, modal won't appear

---

## IMPLEMENTATION ORDER

Execute stages in this exact order:

1. **STAGE 1** - Critical: Fixes real-time updates (solves Issue 1)
2. **STAGE 3** - Quick win: Fixes dashboard filters (solves Issue 3)
3. **STAGE 4** - Enhancement: Adds payment button to dashboard (solves Issue 4)
4. **STAGE 2** - Complex: Fixes payment persistence (solves Issue 2)
5. **STAGE 5** - Validation: Test everything works together

**Rationale for Order:**
- Stage 1 & 3 are independent and solve the most visible bugs
- Stage 4 builds on Stage 3 (won auctions must display first)
- Stage 2 is complex and builds on Stage 1 (needs socket events working)
- Stage 5 validates all changes together

---

## FILES SUMMARY

**Files to Modify:**
1. `frontend/src/pages/ArtworkPage.jsx` - Add socket listeners, pending payment check
2. `frontend/src/components/PaymentModal.jsx` - Replace alert with toast
3. `frontend/src/pages/UserDashboard.jsx` - Fix filters, add payment button
4. `frontend/src/services/paymentService.js` - Verify getArtworkPayment exists

**Files to Reference (No Changes):**
- `backend/routers/payments.py` - Webhook implementation (already correct)
- `backend/routers/bids.py` - Bid creation and socket events
- `backend/models/payment.py` - Payment model structure
- `backend/models/artwork.py` - Artwork status enum

---

## SUCCESS CRITERIA

**All issues resolved when:**

✅ After payment completion, artwork page updates to "SOLD" automatically (no refresh needed)

✅ After payment completion, dashboard shows artwork in "Won Auctions" list

✅ If user leaves during payment, modal reopens when they return to artwork page

✅ Dashboard "Active Bids" shows all non-winning bids on active artworks

✅ Dashboard "Won Auctions" shows all winning bids (including PENDING_PAYMENT)

✅ Dashboard "Won Auctions" shows "Complete Payment" button for pending payments

✅ Clicking "Complete Payment" navigates to artwork page and opens modal

✅ All real-time updates work via socket events (no manual refresh required)

---

## EXECUTION INSTRUCTIONS FOR CLAUDE CODE

1. Read this entire document carefully
2. Execute stages sequentially (1 → 3 → 4 → 2 → 5)
3. Use TodoWrite tool to track progress through each stage
4. For each stage:
   - Mark stage as "in_progress" before starting
   - Complete all tasks in the stage
   - Test changes work correctly
   - Mark stage as "completed" before moving to next
5. After all stages complete, run full test suite (Stage 5)
6. Report any issues or blockers encountered
7. Provide summary of all changes made

**Do not skip stages. Do not modify files not listed. Follow implementation exactly as specified.**

---

END OF IMPLEMENTATION PLAN
