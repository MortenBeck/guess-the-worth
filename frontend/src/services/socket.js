import { io } from 'socket.io-client';
import { config } from '../config/env';

class SocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
  }

  connect() {
    if (this.socket) {
      return this.socket;
    }

    this.socket = io(config.SOCKET_URL, {
      transports: ['websocket'],
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

    return this.socket;
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
}

export default new SocketService();