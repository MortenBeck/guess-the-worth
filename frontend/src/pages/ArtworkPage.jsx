import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Image,
  Badge,
  Spinner,
  Center,
} from "@chakra-ui/react";
import { useParams } from "react-router-dom";
import { artworkService, bidService } from "../services/api";
import useAuthStore from "../store/authStore";
import useFavoritesStore from "../store/favoritesStore";
import { useRealtimeBids } from "../hooks/useRealtimeBids";
import placeholderImg from "../assets/placeholder.jpg";
import { toaster } from "../components/ui/toaster";
import PaymentModal from "../components/PaymentModal";
import socket from "../services/socket";

const ArtworkPage = () => {
  const { id } = useParams();
  const { isAuthenticated } = useAuthStore();
  const { toggleFavorite, isFavorite } = useFavoritesStore();
  const [bidAmount, setBidAmount] = useState("");
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentData, setPaymentData] = useState(null);
  const queryClient = useQueryClient();

  // Enable real-time bid updates for this artwork
  useRealtimeBids(id);

  // Fetch artwork details
  const {
    data: artwork,
    isLoading: artworkLoading,
    error: artworkError,
  } = useQuery({
    queryKey: ["artwork", id],
    queryFn: async () => {
      const response = await artworkService.getById(id);
      return response.data;
    },
    staleTime: 10000,
  });

  // Listen for payment_required event
  useEffect(() => {
    if (!isAuthenticated) return;

    const handlePaymentRequired = (data) => {
      console.log("Payment required event received:", data);

      // Only show payment modal if it's for this artwork
      if (data.artwork_id === parseInt(id)) {
        setPaymentData({
          bidId: data.bid_id,
          amount: data.winning_bid,
          artworkTitle: artwork?.title || "Unknown",
        });
        setShowPaymentModal(true);

        toaster.create({
          title: "Payment Required",
          description: `Congratulations! Please complete payment of $${data.winning_bid} to secure your artwork.`,
          type: "info",
          duration: 10000,
        });
      }
    };

    socket.on("payment_required", handlePaymentRequired);

    return () => {
      socket.off("payment_required", handlePaymentRequired);
    };
  }, [id, isAuthenticated, artwork]);

  // Fetch recent bids
  const { data: recentBids = [], isLoading: bidsLoading } = useQuery({
    queryKey: ["bids", id],
    queryFn: async () => {
      const response = await bidService.getByArtwork(id);
      return response.data;
    },
    staleTime: 5000,
  });

  // Place bid mutation
  const placeBidMutation = useMutation({
    mutationFn: (amount) =>
      bidService.create({
        artwork_id: parseInt(id),
        amount: parseFloat(amount),
      }),
    onSuccess: (response) => {
      const { data: bid } = response;
      toaster.create({
        title: bid.is_winning ? "Congratulations! You won!" : "Bid placed successfully",
        description: bid.is_winning
          ? `Your bid of $${bid.amount} met the threshold!`
          : `Your bid of $${bid.amount} has been recorded.`,
        type: bid.is_winning ? "success" : "info",
        duration: 5000,
      });

      // Refresh artwork and bids
      queryClient.invalidateQueries(["artwork", id]);
      queryClient.invalidateQueries(["bids", id]);

      setBidAmount("");
    },
    onError: (error) => {
      toaster.create({
        title: "Bid failed",
        description: error.data?.detail || error.message || "Failed to place bid",
        type: "error",
        duration: 5000,
      });
    },
  });

  const handleBidSubmit = async () => {
    if (!bidAmount || parseFloat(bidAmount) <= 0) {
      toaster.create({
        title: "Invalid bid amount",
        description: "Please enter a valid bid amount",
        type: "warning",
        duration: 3000,
      });
      return;
    }

    placeBidMutation.mutate(bidAmount);
  };

  // Calculate time left
  const calculateTimeLeft = (endDate) => {
    if (!endDate) return "No end date";
    const now = new Date();
    const end = new Date(endDate);
    const diffMs = end - now;

    if (diffMs <= 0) return "Ended";

    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));

    if (days > 0)
      return `${days} day${days !== 1 ? "s" : ""} ${hours} hour${hours !== 1 ? "s" : ""}`;
    return `${hours} hour${hours !== 1 ? "s" : ""}`;
  };

  // Loading state
  if (artworkLoading || bidsLoading) {
    return (
      <Center h="100vh" bg="#0f172a">
        <Spinner size="xl" color="purple.400" thickness="4px" />
      </Center>
    );
  }

  // Error state
  if (artworkError) {
    return (
      <Center h="100vh" bg="#0f172a">
        <Box textAlign="center" p={8}>
          <Text color="red.400" fontSize="xl" mb={4}>
            Error loading artwork
          </Text>
          <Text color="#94a3b8">{artworkError.message}</Text>
        </Box>
      </Center>
    );
  }

  // Not found state
  if (!artwork) {
    return (
      <Center h="100vh" bg="#0f172a">
        <Box textAlign="center" p={8}>
          <Text color="#94a3b8" fontSize="xl">
            Artwork not found
          </Text>
        </Box>
      </Center>
    );
  }

  return (
    <Box bg="#0f172a" minH="100vh" color="white">
      <Container maxW="container.xl" py={8}>
        <Box display="grid" gridTemplateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={8}>
          {/* Left Column - Artwork Details */}
          <VStack spacing={6} align="stretch">
            <Image
              src={artwork.image_url || placeholderImg}
              alt={artwork.title}
              w="full"
              h="400px"
              objectFit="cover"
              borderRadius="lg"
            />

            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
            >
              <VStack spacing={4} align="stretch">
                <Box>
                  <HStack justify="space-between" align="start" mb={2}>
                    <VStack align="start" spacing={1}>
                      <Heading size="lg" color="text">
                        {artwork.title}
                      </Heading>
                      <Text color="#94a3b8" fontSize="lg">
                        by {artwork.artist_name || "Unknown Artist"}
                      </Text>
                    </VStack>
                    {isAuthenticated && (
                      <Button
                        variant="ghost"
                        color={isFavorite(artwork.id) ? "#ec4899" : "#94a3b8"}
                        _hover={{ color: "#ec4899" }}
                        onClick={() => toggleFavorite(artwork)}
                        size="sm"
                      >
                        {isFavorite(artwork.id) ? "❤️" : "🤍"}
                      </Button>
                    )}
                  </HStack>
                </Box>

                <Text color="#94a3b8">{artwork.description || "No description available."}</Text>

                <Box h="1px" bg="rgba(255,255,255,0.1)" />

                <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={4}>
                  {artwork.category && (
                    <Box>
                      <Text fontWeight="bold" color="text">
                        Category
                      </Text>
                      <Text color="#94a3b8">{artwork.category}</Text>
                    </Box>
                  )}
                  <Box>
                    <Text fontWeight="bold" color="text">
                      Status
                    </Text>
                    <Text color="#94a3b8" textTransform="capitalize">
                      {artwork.status}
                    </Text>
                  </Box>
                </Box>
              </VStack>
            </Box>
          </VStack>

          {/* Right Column - Bidding */}
          <VStack spacing={6} align="stretch">
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
            >
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Heading size="md" color="text">
                    Current Auction
                  </Heading>
                  <Badge colorScheme={artwork.status === "sold" ? "red" : "green"}>
                    {artwork.status === "sold" ? "Sold" : "Active"}
                  </Badge>
                </HStack>

                <Box>
                  <Text color="#94a3b8" fontSize="sm">
                    Current Highest Bid
                  </Text>
                  <Text fontSize="2xl" fontWeight="bold" color="primary">
                    ${artwork.current_highest_bid || 0}
                  </Text>
                </Box>

                <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={4}>
                  <Box>
                    <Text fontWeight="bold" color="text">
                      Total Bids
                    </Text>
                    <Text color="#94a3b8">{recentBids.length}</Text>
                  </Box>
                  {artwork.end_date && (
                    <Box>
                      <Text fontWeight="bold" color="text">
                        Time Left
                      </Text>
                      <Text color="#94a3b8">{calculateTimeLeft(artwork.end_date)}</Text>
                    </Box>
                  )}
                </Box>

                <Box h="1px" bg="rgba(255,255,255,0.1)" />

                {artwork.status === "sold" ? (
                  <Box
                    bg="rgba(239, 68, 68, 0.1)"
                    border="1px"
                    borderColor="rgba(239, 68, 68, 0.3)"
                    borderRadius="md"
                    p={4}
                  >
                    <HStack>
                      <Text mr={2}>🔒</Text>
                      <Text color="rgb(252, 165, 165)">This artwork has been sold</Text>
                    </HStack>
                  </Box>
                ) : isAuthenticated ? (
                  <VStack spacing={4}>
                    <Box w="full">
                      <Text color="text" mb={2} fontWeight="medium">
                        Your Bid Amount
                      </Text>
                      <input
                        style={{
                          width: "100%",
                          padding: "12px",
                          border: "1px solid rgba(255,255,255,0.1)",
                          borderRadius: "6px",
                          fontSize: "16px",
                          outline: "none",
                          backgroundColor: "#0f172a",
                          color: "white",
                        }}
                        type="number"
                        step="0.01"
                        placeholder="Enter your bid amount"
                        value={bidAmount}
                        onChange={(e) => setBidAmount(e.target.value)}
                      />
                    </Box>

                    <Button
                      bg="white"
                      color="#1e293b"
                      size="lg"
                      w="full"
                      onClick={handleBidSubmit}
                      isLoading={placeBidMutation.isLoading}
                      isDisabled={!bidAmount || parseFloat(bidAmount) <= 0}
                      _hover={{
                        bg: "#f1f5f9",
                        transform: "translateY(-1px)",
                      }}
                      _disabled={{
                        opacity: 0.6,
                        cursor: "not-allowed",
                        transform: "none",
                        boxShadow: "none",
                      }}
                      transition="all 0.2s"
                    >
                      Place Bid
                    </Button>

                    <Text fontSize="sm" color="#94a3b8" textAlign="center">
                      Enter any amount to place your bid
                    </Text>
                  </VStack>
                ) : (
                  <Box
                    bg="rgba(59, 130, 246, 0.1)"
                    border="1px"
                    borderColor="rgba(59, 130, 246, 0.3)"
                    borderRadius="md"
                    p={4}
                  >
                    <HStack>
                      <Text mr={2}>ℹ️</Text>
                      <Text color="rgb(147, 197, 253)">Please log in to place a bid</Text>
                    </HStack>
                  </Box>
                )}
              </VStack>
            </Box>

            {/* Recent Bids */}
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
            >
              <VStack spacing={4} align="stretch">
                <Heading size="md" color="text">
                  Recent Bids ({recentBids.length})
                </Heading>
                {recentBids.length > 0 ? (
                  <VStack spacing={2} align="stretch">
                    {recentBids.slice(0, 10).map((bid) => (
                      <HStack
                        key={bid.id}
                        justify="space-between"
                        p={2}
                        bg="rgba(255,255,255,0.05)"
                        borderRadius="md"
                      >
                        <VStack align="start" spacing={0}>
                          <Text fontWeight="bold" fontSize="sm">
                            Bid #{bid.id}
                          </Text>
                          <Text fontSize="xs" color="#94a3b8">
                            {new Date(bid.bid_time).toLocaleString()}
                          </Text>
                        </VStack>
                        <VStack align="end" spacing={0}>
                          <Text fontWeight="bold" color="primary">
                            ${bid.amount}
                          </Text>
                          {bid.is_winning && (
                            <Badge colorScheme="green" fontSize="xs">
                              Winning
                            </Badge>
                          )}
                        </VStack>
                      </HStack>
                    ))}
                  </VStack>
                ) : (
                  <Text color="#94a3b8" textAlign="center" py={4}>
                    No bids yet. Be the first to bid!
                  </Text>
                )}
              </VStack>
            </Box>
          </VStack>
        </Box>
      </Container>

      {/* Payment Modal */}
      {paymentData && (
        <PaymentModal
          isOpen={showPaymentModal}
          onClose={() => {
            setShowPaymentModal(false);
            setPaymentData(null);
          }}
          bidId={paymentData.bidId}
          amount={paymentData.amount}
          artworkTitle={paymentData.artworkTitle}
        />
      )}
    </Box>
  );
};

export default ArtworkPage;
