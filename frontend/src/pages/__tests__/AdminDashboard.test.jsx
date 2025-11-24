import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { renderWithProviders } from "../../test/utils";
import AdminDashboard from "../AdminDashboard";
import * as adminApi from "../../services/adminApi";

vi.mock("../../services/adminApi");

describe("AdminDashboard", () => {
  const mockStats = {
    users: { total: 100, new_last_30_days: 10 },
    auctions: { total: 50, active: 20 },
    transactions: { total: 75, total_revenue: 50000, platform_fees: 5000 },
  };

  const mockTransactions = {
    transactions: [
      {
        id: 1,
        artwork_title: "Test Art",
        buyer: "testuser",
        amount: 1000,
        status: "completed",
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    adminApi.default.getPlatformOverview.mockResolvedValue(mockStats);
    adminApi.default.getTransactions.mockResolvedValue(mockTransactions);
    adminApi.default.getUsers.mockResolvedValue({ users: [] });
    adminApi.default.getSystemHealth.mockResolvedValue({
      status: "healthy",
      database: "healthy",
      metrics: { bids_last_hour: 5, artworks_last_24h: 10 },
    });
    adminApi.default.getFlaggedAuctions.mockResolvedValue({
      total: 0,
      flagged_auctions: [],
    });
  });

  it("displays platform statistics", async () => {
    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText("100")).toBeInTheDocument(); // Total users
      expect(screen.getByText("20")).toBeInTheDocument(); // Active auctions
    });
  });

  it("displays recent transactions", async () => {
    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText("Test Art")).toBeInTheDocument();
      expect(screen.getByText(/testuser/i)).toBeInTheDocument();
    });
  });

  it("shows system health status", async () => {
    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      const healthyElements = screen.getAllByText("healthy");
      expect(healthyElements.length).toBeGreaterThan(0);
    });
  });

  it("shows no flagged auctions message", async () => {
    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/no flagged auctions/i)).toBeInTheDocument();
    });
  });

  it("displays recent users with different roles", async () => {
    const mockUsers = {
      users: [
        { id: 1, name: "Admin User", email: "admin@test.com", role: "ADMIN" },
        { id: 2, name: "Seller User", email: "seller@test.com", role: "SELLER" },
        { id: 3, name: "Buyer User", email: "buyer@test.com", role: "BUYER" },
      ],
    };

    adminApi.default.getUsers.mockResolvedValue(mockUsers);
    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText("Admin User")).toBeInTheDocument();
      expect(screen.getByText("Seller User")).toBeInTheDocument();
      expect(screen.getByText("Buyer User")).toBeInTheDocument();
    });
  });

  it("displays flagged auctions when they exist", async () => {
    adminApi.default.getFlaggedAuctions.mockResolvedValue({
      total: 2,
      flagged_auctions: [
        { id: 1, title: "Suspicious Art", reason: "Possible copyright violation" },
        { id: 2, title: "Another Flagged", reason: "Inappropriate content" },
      ],
    });

    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText("Suspicious Art")).toBeInTheDocument();
      expect(screen.getByText("Possible copyright violation")).toBeInTheDocument();
      expect(screen.getByText("Another Flagged")).toBeInTheDocument();
    });
  });

  it("shows system health as degraded", async () => {
    adminApi.default.getSystemHealth.mockResolvedValue({
      status: "degraded",
      database: "healthy",
      metrics: { bids_last_hour: 0, artworks_last_24h: 0 },
    });

    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText("degraded")).toBeInTheDocument();
    });
  });

  it("displays loading state initially", () => {
    renderWithProviders(<AdminDashboard />);
    expect(screen.getByText("Loading admin dashboard...")).toBeInTheDocument();
  });

  it("displays fallback values when stats are undefined", async () => {
    adminApi.default.getPlatformOverview.mockResolvedValue({
      users: {},
      auctions: {},
      transactions: {},
    });

    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      // Check that fallback values are displayed (multiple zeros exist)
      const zeroElements = screen.getAllByText("0");
      expect(zeroElements.length).toBeGreaterThan(0);
    });
  });
});
