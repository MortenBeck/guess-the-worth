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
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { statsService, bidService } from "../services/api";
import useAuthStore from "../store/authStore";
import placeholderImg from "../assets/placeholder.jpg";

const UserDashboard = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  // Fetch user stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["user-stats"],
    queryFn: statsService.getUserStats,
    staleTime: 30000,
  });

  // Fetch user's bids
  const { data: myBidsData, isLoading: bidsLoading } = useQuery({
    queryKey: ["my-bids"],
    queryFn: bidService.getMyBids,
    staleTime: 10000,
  });

  if (statsLoading || bidsLoading) {
    return (
      <Box
        bg="#0f172a"
        color="white"
        minH="100vh"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Spinner size="xl" color="#6366f1" />
      </Box>
    );
  }

  const myBids = myBidsData?.data || [];
  const userStats = stats?.data || {
    active_bids: 0,
    won_auctions: 0,
    total_spent: 0,
  };

  // Separate active bids and won auctions
  // Active bids = bids on active artworks where user is not currently winning
  const activeBids = myBids.filter((bid) => bid.artwork?.status === "ACTIVE" && !bid.is_winning);
  // Won auctions = any winning bid, regardless of payment status
  const wonAuctions = myBids.filter((bid) => bid.is_winning);

  return (
    <Box bg="#0f172a" color="white" minH="100vh" pt={6}>
      <Container maxW="container.xl" py={8}>
        <VStack spacing={8} align="stretch">
          {/* Header */}
          <Box>
            <Heading size="xl" color="white" mb={2}>
              My Dashboard
            </Heading>
            <Text color="#94a3b8">
              Welcome back, {user?.name}! Here's your bidding activity overview.
            </Text>
          </Box>

          {/* Stats Overview */}
          <Box
            display="grid"
            gridTemplateColumns={{ base: "repeat(1, 1fr)", md: "repeat(3, 1fr)" }}
            gap={6}
          >
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
              textAlign="center"
            >
              <VStack spacing={3}>
                <Text fontSize="sm" color="#94a3b8">
                  Active Bids
                </Text>
                <Text fontSize="2xl" fontWeight="bold" color="#6366f1">
                  {userStats.active_bids}
                </Text>
                <Text fontSize="xs" color="#94a3b8">
                  Currently bidding
                </Text>
              </VStack>
            </Box>
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
              textAlign="center"
            >
              <VStack spacing={3}>
                <Text fontSize="sm" color="#94a3b8">
                  Won Auctions
                </Text>
                <Text fontSize="2xl" fontWeight="bold" color="#10b981">
                  {userStats.won_auctions}
                </Text>
                <Text fontSize="xs" color="#94a3b8">
                  Total artworks won
                </Text>
              </VStack>
            </Box>
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
              textAlign="center"
            >
              <VStack spacing={3}>
                <Text fontSize="sm" color="#94a3b8">
                  Total Spent
                </Text>
                <Text fontSize="2xl" fontWeight="bold" color="#ec4899">
                  ${userStats.total_spent}
                </Text>
                <Text fontSize="xs" color="#94a3b8">
                  On artwork purchases
                </Text>
              </VStack>
            </Box>
          </Box>

          {/* Active Bids */}
          <Box
            bg="#1e293b"
            p={6}
            borderRadius="lg"
            border="1px"
            borderColor="rgba(255,255,255,0.1)"
          >
            <Heading size="md" color="white" mb={4}>
              Active Bids
            </Heading>
            {activeBids.length === 0 ? (
              <Text color="#94a3b8">No active bids. Start bidding to see them here!</Text>
            ) : (
              <VStack spacing={4} align="stretch">
                {activeBids.map((bid) => (
                  <Box
                    key={bid.id}
                    bg="#0f172a"
                    p={4}
                    borderRadius="lg"
                    border="1px"
                    borderColor="rgba(255,255,255,0.1)"
                  >
                    <HStack spacing={4}>
                      <Image
                        src={bid.artwork?.image_url || placeholderImg}
                        alt={bid.artwork?.title}
                        boxSize="60px"
                        objectFit="cover"
                        borderRadius="md"
                      />
                      <VStack align="start" spacing={1} flex={1}>
                        <HStack justify="space-between" w="full">
                          <Text fontWeight="semibold" color="white">
                            {bid.artwork?.title}
                          </Text>
                          <Badge colorScheme={bid.is_winning ? "green" : "red"}>
                            {bid.is_winning ? "Winning" : "Outbid"}
                          </Badge>
                        </HStack>
                        <Text fontSize="sm" color="#94a3b8">
                          by {bid.artwork?.seller?.name || "Unknown Artist"}
                        </Text>
                        <HStack spacing={4}>
                          <Text fontSize="sm" color="#94a3b8">
                            Your bid:{" "}
                            <Text as="span" color="white" fontWeight="bold">
                              ${bid.amount}
                            </Text>
                          </Text>
                          <Text fontSize="sm" color="#94a3b8">
                            Current:{" "}
                            <Text
                              as="span"
                              color={bid.is_winning ? "green.400" : "red.400"}
                              fontWeight="bold"
                            >
                              ${bid.artwork?.current_highest_bid || bid.amount}
                            </Text>
                          </Text>
                        </HStack>
                      </VStack>
                      <Button
                        size="sm"
                        background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                        color="white"
                        onClick={() => navigate(`/artwork/${bid.artwork?.id}`)}
                        _hover={{
                          transform: "translateY(-1px)",
                          boxShadow: "0 4px 15px rgba(99, 102, 241, 0.3)",
                        }}
                      >
                        View
                      </Button>
                    </HStack>
                  </Box>
                ))}
              </VStack>
            )}
          </Box>

          {/* Won Auctions */}
          <Box
            bg="#1e293b"
            p={6}
            borderRadius="lg"
            border="1px"
            borderColor="rgba(255,255,255,0.1)"
          >
            <Heading size="md" color="white" mb={4}>
              Won Auctions
            </Heading>
            {wonAuctions.length === 0 ? (
              <Text color="#94a3b8">No won auctions yet. Keep bidding!</Text>
            ) : (
              <Box
                display="grid"
                gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }}
                gap={4}
              >
                {wonAuctions.map((bid) => (
                  <Box
                    key={bid.id}
                    bg="#0f172a"
                    borderRadius="lg"
                    overflow="hidden"
                    border="1px"
                    borderColor="rgba(255,255,255,0.1)"
                    cursor="pointer"
                    onClick={() => navigate(`/artwork/${bid.artwork?.id}`)}
                    _hover={{
                      transform: "translateY(-2px)",
                      boxShadow: "0 8px 25px rgba(0,0,0,0.3)",
                    }}
                    transition="all 0.2s"
                  >
                    <Image
                      src={bid.artwork?.image_url || placeholderImg}
                      alt={bid.artwork?.title}
                      h="150px"
                      w="full"
                      objectFit="cover"
                    />
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
                  </Box>
                ))}
              </Box>
            )}
          </Box>
        </VStack>
      </Container>
    </Box>
  );
};

export default UserDashboard;
