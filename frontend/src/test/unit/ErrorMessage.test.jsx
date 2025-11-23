import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ErrorMessage from "../../components/ErrorMessage";

describe("ErrorMessage Component", () => {
  it("renders error message when error is provided", () => {
    const error = { message: "An error occurred" };
    render(<ErrorMessage error={error} />);

    expect(screen.getByText("An error occurred")).toBeInTheDocument();
    expect(screen.getByText("Error")).toBeInTheDocument();
  });

  it("does not render when error is null", () => {
    const { container } = render(<ErrorMessage error={null} />);
    expect(container.firstChild).toBeNull();
  });

  it("renders network error message", () => {
    const error = { isNetworkError: true };
    render(<ErrorMessage error={error} />);

    expect(screen.getByText(/Unable to connect to server/i)).toBeInTheDocument();
    expect(screen.getByText("⚠️")).toBeInTheDocument();
  });

  it("renders 401 unauthorized error", () => {
    const error = { status: 401 };
    render(<ErrorMessage error={error} />);

    expect(screen.getByText(/Your session has expired/i)).toBeInTheDocument();
    expect(screen.getByText("🔒")).toBeInTheDocument();
  });

  it("renders 403 forbidden error", () => {
    const error = { status: 403 };
    render(<ErrorMessage error={error} />);

    expect(screen.getByText(/You do not have permission/i)).toBeInTheDocument();
  });

  it("renders 404 not found error", () => {
    const error = { status: 404 };
    render(<ErrorMessage error={error} />);

    expect(screen.getByText(/resource was not found/i)).toBeInTheDocument();
    expect(screen.getByText("🔍")).toBeInTheDocument();
  });

  it("renders 500 server error", () => {
    const error = { status: 500 };
    render(<ErrorMessage error={error} />);

    expect(screen.getByText(/server error occurred/i)).toBeInTheDocument();
    expect(screen.getByText("⚙️")).toBeInTheDocument();
  });

  it("renders retry button when onRetry is provided", () => {
    const error = { message: "Error" };
    const onRetry = vi.fn();
    render(<ErrorMessage error={error} onRetry={onRetry} />);

    const retryButton = screen.getByRole("button", { name: /try again/i });
    expect(retryButton).toBeInTheDocument();
  });

  it("calls onRetry when retry button is clicked", async () => {
    const user = userEvent.setup();
    const error = { message: "Error" };
    const onRetry = vi.fn();
    render(<ErrorMessage error={error} onRetry={onRetry} />);

    const retryButton = screen.getByRole("button", { name: /try again/i });
    await user.click(retryButton);

    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("does not render retry button when onRetry is not provided", () => {
    const error = { message: "Error" };
    render(<ErrorMessage error={error} />);

    expect(screen.queryByRole("button", { name: /try again/i })).not.toBeInTheDocument();
  });
});
