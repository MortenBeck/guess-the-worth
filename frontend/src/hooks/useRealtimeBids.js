import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useToast } from "@chakra-ui/react";
import socketService from "../services/socket";
import useBiddingStore from "../store/biddingStore";

/**
 * Custom hook to enable real-time bid updates for a specific artwork.
 *
 * Automatically joins the artwork's WebSocket room, listens for bid events,
 * and updates the UI in real-time when new bids are placed.
 *
 * @param {number|string} artworkId - The ID of the artwork to track
 */
export function useRealtimeBids(artworkId) {
  const queryClient = useQueryClient();
  const { updateBid, markArtworkSold } = useBiddingStore();
  const toast = useToast();

  useEffect(() => {
    if (!artworkId) return;

    // Join artwork room to receive real-time updates
    socketService.joinArtwork(artworkId);

    // Handler for new bid events
    const handleNewBid = (data) => {
      console.log("New bid received:", data);

      // Update bidding store with new bid data
      updateBid(artworkId, data.bid);

      // Invalidate queries to refresh UI
      queryClient.invalidateQueries({ queryKey: ["bids", artworkId] });
      queryClient.invalidateQueries({ queryKey: ["artwork", artworkId] });

      // Show toast notification
      toast({
        title: "New bid placed!",
        description: `$${data.bid.amount.toLocaleString()}`,
        status: "info",
        duration: 3000,
        isClosable: true,
      });
    };

    // Handler for artwork sold events
    const handleArtworkSold = (data) => {
      console.log("Artwork sold:", data);

      // Update store to mark artwork as sold
      markArtworkSold(artworkId);

      // Invalidate queries to refresh UI
      queryClient.invalidateQueries({ queryKey: ["artwork", artworkId] });
      queryClient.invalidateQueries({ queryKey: ["artworks"] });

      // Show success message
      toast({
        title: "Auction Ended!",
        description: `Sold for $${data.winning_bid.toLocaleString()}`,
        status: "success",
        duration: 5000,
        isClosable: true,
      });
    };

    // Register event handlers
    socketService.onNewBid(handleNewBid);
    socketService.onArtworkSold(handleArtworkSold);

    // Cleanup on unmount
    return () => {
      socketService.leaveArtwork(artworkId);
      // Note: We don't remove listeners here as they're managed globally
      // The socket service handles listener cleanup
    };
  }, [artworkId, queryClient, updateBid, markArtworkSold]);
}
