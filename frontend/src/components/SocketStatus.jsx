import { useEffect, useState } from "react";
import { Box, Badge } from "@chakra-ui/react";
import socketService from "../services/socket";

/**
 * Connection status indicator that shows whether the WebSocket
 * connection is active. Displays a badge in the bottom-right corner.
 */
export default function SocketStatus() {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const checkConnection = () => {
      setConnected(socketService.socket?.connected || false);
    };

    // Check immediately
    checkConnection();

    // Check every 5 seconds
    const interval = setInterval(checkConnection, 5000);

    return () => clearInterval(interval);
  }, []);

  // Only show when connected (hide when disconnected to avoid clutter)
  if (!connected) return null;

  return (
    <Box position="fixed" bottom={4} right={4} zIndex={1000}>
      <Badge
        colorScheme={connected ? "green" : "red"}
        fontSize="sm"
        px={3}
        py={1}
        borderRadius="full"
        boxShadow="lg"
      >
        {connected ? "🟢 Live" : "🔴 Disconnected"}
      </Badge>
    </Box>
  );
}
