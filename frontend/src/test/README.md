# Frontend Testing Guide

This directory contains all frontend tests for the Guess The Worth application.

## 📋 Test Overview

- **Framework**: Vitest + React Testing Library
- **Total Tests**: 92 tests (all passing)
- **Coverage**: 100% on Zustand stores, 95%+ on API services
- **Test Types**: Unit tests for stores and services

## 🗂️ Test Structure

```
frontend/src/test/
├── setup.js                    # Test environment setup
├── unit/
│   ├── authStore.test.js      # Auth state management (27 tests)
│   ├── biddingStore.test.js   # Bidding state management (24 tests)
│   ├── favoritesStore.test.js # Favorites state management (22 tests)
│   └── apiServices.test.js    # API service functions (19 tests)
└── component/                  # Component tests (future)
```

## 🚀 Running Tests

### Basic Commands

```bash
# Run all tests once
npm test

# Run tests in watch mode (re-runs on file changes)
npm test -- --watch

# Run with coverage report
npm test -- --coverage

# Run specific test file
npm test -- authStore.test.js

# Run tests matching pattern
npm test -- --grep "bid"

# Run with UI (interactive test viewer)
npm test:ui
```

### Coverage Reports

```bash
# Generate coverage report
npm test -- --coverage

# Coverage files generated:
# - frontend/coverage/index.html (open in browser)
# - frontend/coverage/lcov-report/index.html
# - frontend/coverage/coverage-final.json
```

## 📊 Test Coverage

### Current Coverage (Unit Tests)

| File                  | % Stmts | % Branch | % Funcs | % Lines | Status                     |
| --------------------- | ------- | -------- | ------- | ------- | -------------------------- |
| **authStore.js**      | 100%    | 100%     | 100%    | 100%    | ✅                         |
| **biddingStore.js**   | 100%    | 100%     | 100%    | 100%    | ✅                         |
| **favoritesStore.js** | 100%    | 100%     | 100%    | 100%    | ✅                         |
| **api.js**            | 95.2%   | 97.36%   | 88.88%  | 95.2%   | ✅                         |
| **Overall**           | ~7%     | ~77%     | ~60%    | ~7%     | ⚠️ (Components not tested) |

**Note**: Overall coverage is low because components and pages are not yet tested. Store and service coverage is excellent.

## 📝 Test Categories

### 1. Auth Store Tests (`authStore.test.js`)

Tests authentication state management with 27 test cases:

**Covered Functionality**:

- ✅ `setAuth()` - Sets user and token, marks authenticated
- ✅ `clearAuth()` - Clears all auth data
- ✅ `setLoading()` - Manages loading state
- ✅ `updateUser()` - Partially updates user data
- ✅ `hasRole()` - Checks if user has specific role
- ✅ `isAdmin()` - Checks if user is admin
- ✅ `isSeller()` - Checks if user can sell (seller or admin)
- ✅ `isBuyer()` - Checks if user can buy (buyer, seller, or admin)

**Edge Cases Tested**:

- User with missing role
- Empty token
- Null user state
- Role hierarchy (admin > seller > buyer)

**Example Test**:

```javascript
it("should set user and token correctly", () => {
  const mockUser = {
    id: 1,
    email: "test@example.com",
    role: "buyer",
  };
  const mockToken = "test-token-123";

  useAuthStore.getState().setAuth(mockUser, mockToken);

  const state = useAuthStore.getState();
  expect(state.user).toEqual(mockUser);
  expect(state.token).toBe(mockToken);
  expect(state.isAuthenticated).toBe(true);
});
```

---

### 2. Bidding Store Tests (`biddingStore.test.js`)

Tests real-time bidding state with 24 test cases:

**Covered Functionality**:

- ✅ `joinArtwork()` - Adds artwork to active tracking
- ✅ `leaveArtwork()` - Removes artwork and associated bids
- ✅ `updateBid()` - Updates bid and artwork's current_highest_bid
- ✅ `markArtworkSold()` - Marks artwork as sold
- ✅ `clearAll()` - Clears all artworks and bids
- ✅ `setSocketConnected()` - Manages WebSocket connection state

**Complex Scenarios Tested**:

- Full bidding lifecycle (join → bid → update → sold → leave)
- Multiple concurrent auctions
- Bid updates on non-tracked artworks
- Socket connection state changes

**Example Test**:

```javascript
it("should update artwork's current_highest_bid", () => {
  const artworkId = 1;
  const artworkData = { id: 1, title: "Test", current_highest_bid: 100 };
  const bidData = { amount: 150, bidder_id: 5 };

  useBiddingStore.getState().joinArtwork(artworkId, artworkData);
  useBiddingStore.getState().updateBid(artworkId, bidData);

  const state = useBiddingStore.getState();
  expect(state.activeArtworks.get(artworkId).current_highest_bid).toBe(150);
});
```

---

### 3. Favorites Store Tests (`favoritesStore.test.js`)

Tests favorites management with 22 test cases:

**Covered Functionality**:

- ✅ `addToFavorites()` - Adds artwork with timestamp
- ✅ `removeFromFavorites()` - Removes specific artwork
- ✅ `isFavorite()` - Checks favorite status
- ✅ `toggleFavorite()` - Toggles favorite state

**Features Tested**:

- Prevents duplicate favorites
- Maintains FIFO order
- Adds `dateAdded` timestamp automatically
- Preserves all artwork properties

**Edge Cases Tested**:

- Artwork with id 0
- Rapid add/remove operations
- Complex artwork data structures
- Removing non-existent artworks

**Example Test**:

```javascript
it("should toggle favorite multiple times correctly", () => {
  const artwork = { id: 1, title: "Artwork 1" };

  // Add
  useFavoritesStore.getState().toggleFavorite(artwork);
  expect(useFavoritesStore.getState().isFavorite(1)).toBe(true);

  // Remove
  useFavoritesStore.getState().toggleFavorite(artwork);
  expect(useFavoritesStore.getState().isFavorite(1)).toBe(false);
});
```

---

### 4. API Services Tests (`apiServices.test.js`)

Tests API client and service functions with 19 test cases:

**Services Tested**:

- ✅ **artworkService**: getAll, getById, getFeatured, create, uploadImage
- ✅ **bidService**: getByArtwork, create
- ✅ **userService**: getAll, getById, getCurrentUser, register
- ✅ **statsService**: getPlatformStats

**Error Handling Tested**:

- 401 Unauthorized (clears token, redirects to login)
- Network failures (graceful error messages)
- HTTP errors (5xx, 4xx status codes)
- API unavailability (fallback mock data for stats)

**Example Test**:

```javascript
it("should fetch all artworks with pagination", async () => {
  const mockArtworks = [
    { id: 1, title: "Artwork 1" },
    { id: 2, title: "Artwork 2" },
  ];

  fetch.mockResolvedValueOnce({
    ok: true,
    status: 200,
    json: async () => mockArtworks,
  });

  const result = await artworkService.getAll({ skip: 10, limit: 5 });

  expect(fetch).toHaveBeenCalledWith(expect.stringContaining("skip=10"), expect.any(Object));
  expect(result.data).toEqual(mockArtworks);
});
```

---

## 🛠️ Testing Utilities

### Test Setup (`setup.js`)

```javascript
import "@testing-library/jest-dom";
```

Imports jest-dom matchers for better assertions:

- `toBeInTheDocument()`
- `toHaveTextContent()`
- `toBeVisible()`
- etc.

### Mocking Best Practices

**Mocking Fetch API**:

```javascript
import { vi } from "vitest";

global.fetch = vi.fn();

// Mock successful response
fetch.mockResolvedValueOnce({
  ok: true,
  status: 200,
  json: async () => ({ id: 1, title: "Test" }),
});
```

**Mocking localStorage**:

```javascript
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

global.localStorage = localStorageMock;
```

**Mocking Zustand Stores**:

```javascript
import useAuthStore from "../../store/authStore";

beforeEach(() => {
  // Reset to initial state
  useAuthStore.setState({
    user: null,
    token: null,
    isAuthenticated: false,
  });
});
```

---

## 📚 Writing New Tests

### Test File Template

```javascript
import { describe, it, expect, beforeEach, vi } from "vitest";
import useMyStore from "../../store/myStore";

describe("MyStore", () => {
  beforeEach(() => {
    // Reset state before each test
    useMyStore.setState({
      /* initial state */
    });
  });

  describe("Feature Name", () => {
    it("should do something specific", () => {
      // Arrange: Set up test data
      const testData = { id: 1, name: "Test" };

      // Act: Call the function
      useMyStore.getState().myFunction(testData);

      // Assert: Verify the result
      const state = useMyStore.getState();
      expect(state.someValue).toBe(expectedValue);
    });
  });
});
```

### Testing Store Actions

```javascript
it("should update state correctly", () => {
  const store = useMyStore.getState();

  // Call store action
  store.updateData({ key: "value" });

  // Verify state changed
  expect(store.data.key).toBe("value");
});
```

### Testing Async API Calls

```javascript
it("should fetch data from API", async () => {
  // Mock the API response
  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ data: "test" }),
  });

  // Call the service
  const result = await myService.getData();

  // Verify the call and result
  expect(fetch).toHaveBeenCalledWith(expect.stringContaining("/api/data"), expect.any(Object));
  expect(result.data).toEqual({ data: "test" });
});
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Tests fail with "Cannot find module"**

```bash
# Install dependencies
npm install
```

**2. Coverage reports not generated**

```bash
# Install coverage package
npm install -D @vitest/coverage-v8
```

**3. Tests timeout**

```bash
# Increase timeout in vite.config.js
test: {
  testTimeout: 10000
}
```

**4. Mock not working**

```bash
# Make sure to clear mocks in beforeEach
beforeEach(() => {
  vi.clearAllMocks();
});
```

---

## 📈 Future Test Improvements

### Component Testing (Recommended)

Create tests for React components:

```javascript
import { render, screen, fireEvent } from "@testing-library/react";
import ArtworkCard from "../../components/ArtworkCard";

it("renders artwork card and handles favorite click", () => {
  const artwork = { id: 1, title: "Test Art" };
  const onFavorite = vi.fn();

  render(<ArtworkCard artwork={artwork} onFavorite={onFavorite} />);

  expect(screen.getByText("Test Art")).toBeInTheDocument();

  const favoriteBtn = screen.getByRole("button", { name: /favorite/i });
  fireEvent.click(favoriteBtn);

  expect(onFavorite).toHaveBeenCalledWith(artwork);
});
```

### Integration Testing

Test complete user flows:

```javascript
it("completes full bidding flow", async () => {
  // 1. User logs in
  // 2. Browses artworks
  // 3. Places bid
  // 4. Receives confirmation
  // 5. WebSocket updates bid status
});
```

---

## 📖 Additional Resources

- [Vitest Documentation](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [Jest DOM Matchers](https://github.com/testing-library/jest-dom)
- [Zustand Testing Guide](https://docs.pmnd.rs/zustand/guides/testing)

---

**Last Updated**: 2025-01-16
