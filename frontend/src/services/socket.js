import { io } from "socket.io-client";

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.isEnabled = false;
  }

  connect() {
    // Skip connection if no backend is available or websockets are disabled
    if (!this.isEnabled) {
      return this.socket;
    }

    // If socket exists and is connected, return it
    if (this.socket && this.isConnected) {
      return this.socket;
    }

    // If socket exists but disconnected, try to reconnect
    if (this.socket && !this.isConnected) {
      console.log("Reconnecting existing socket...");
      this.socket.connect();
      return this.socket;
    }

    try {
      // Use environment variable or default to localhost:8000
      const socketUrl = import.meta.env.VITE_SOCKET_URL || "http://localhost:8000";

      // Get JWT token from localStorage
      const token = localStorage.getItem("access_token");

      this.socket = io(socketUrl, {
        transports: ["websocket"],
        timeout: 10000,
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5,
        // Pass token in query params (backend expects it there)
        query: {
          token: token,
        },
      });

      this.socket.on("connect", () => {
        this.isConnected = true;
        console.log("Socket connected");
      });

      this.socket.on("disconnect", (reason) => {
        this.isConnected = false;
        console.log("Socket disconnected:", reason);

        // If disconnect was due to server-side issue, socket.io will auto-reconnect
        // If it was intentional (io server disconnect or client disconnect), it won't
        if (reason === "io server disconnect") {
          // Server forcibly disconnected, likely due to auth - try to reconnect with fresh token
          console.log("Server disconnected socket, attempting to reconnect...");
          this.socket.connect();
        }
      });

      this.socket.on("connect_error", (error) => {
        console.warn("Socket connection error:", error.message);
        this.isConnected = false;
        // Don't set socket to null - let socket.io handle reconnection
      });

      this.socket.on("reconnect_attempt", (attempt) => {
        console.log(`Socket reconnection attempt ${attempt}`);
      });

      this.socket.on("reconnect_failed", () => {
        console.error("Socket reconnection failed after all attempts");
      });

    } catch (error) {
      console.warn("Socket service initialization failed:", error.message);
      this.socket = null;
    }

    return this.socket;
  }

  enable() {
    this.isEnabled = true;
    this.connect();
  }

  disable() {
    this.isEnabled = false;
    this.disconnect();
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  joinArtwork(artworkId) {
    if (this.socket && this.isConnected) {
      this.socket.emit("join_artwork", { artwork_id: artworkId });
    }
  }

  leaveArtwork(artworkId) {
    if (this.socket && this.isConnected) {
      this.socket.emit("leave_artwork", { artwork_id: artworkId });
    }
  }

  onNewBid(callback) {
    if (this.socket) {
      this.socket.on("new_bid", callback);
    }
  }

  onArtworkSold(callback) {
    if (this.socket) {
      this.socket.on("artwork_sold", callback);
    }
  }

  offNewBid() {
    if (this.socket) {
      this.socket.off("new_bid");
    }
  }

  offArtworkSold() {
    if (this.socket) {
      this.socket.off("artwork_sold");
    }
  }

  // Generic method to listen to socket events
  on(event, callback) {
    if (!this.isEnabled) {
      return; // Skip if websockets are disabled
    }
    if (!this.socket) {
      this.connect();
    }
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  // Generic method to remove socket event listeners
  off(event, callback) {
    if (this.socket) {
      this.socket.off(event, callback);
    }
  }
}

export default new SocketService();
