import { io } from 'socket.io-client';

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.isEnabled = false;
  }

  connect() {
    // Skip connection if no backend is available or websockets are disabled
    if (!this.isEnabled || this.socket) {
      return this.socket;
    }

    try {
      // Use environment variable or default to localhost:8000
      const socketUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:8000';
      
      this.socket = io(socketUrl, {
        transports: ['websocket'],
        timeout: 5000,
        forceNew: false,
        auth: {
          token: localStorage.getItem('access_token')
        }
      });

      this.socket.on('connect', () => {
        this.isConnected = true;
        console.log('Socket connected');
      });

      this.socket.on('disconnect', () => {
        this.isConnected = false;
        console.log('Socket disconnected');
      });

      this.socket.on('connect_error', (error) => {
        console.warn('Socket connection failed:', error.message);
        this.isConnected = false;
        this.socket = null;
      });

    } catch (error) {
      console.warn('Socket service initialization failed:', error.message);
      this.socket = null;
    }

    return this.socket;
  }

  enable() {
    this.isEnabled = true;
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
      this.socket.emit('join_artwork', { artwork_id: artworkId });
    }
  }

  leaveArtwork(artworkId) {
    if (this.socket && this.isConnected) {
      this.socket.emit('leave_artwork', { artwork_id: artworkId });
    }
  }

  onNewBid(callback) {
    if (this.socket) {
      this.socket.on('new_bid', callback);
    }
  }

  onArtworkSold(callback) {
    if (this.socket) {
      this.socket.on('artwork_sold', callback);
    }
  }

  offNewBid() {
    if (this.socket) {
      this.socket.off('new_bid');
    }
  }

  offArtworkSold() {
    if (this.socket) {
      this.socket.off('artwork_sold');
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