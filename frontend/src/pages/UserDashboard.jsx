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
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import placeholderImg from "../assets/placeholder.jpg";
import { useEffect } from "react";

const UserDashboard = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    window.scrollTo(0, 0)
  }, [])

  // Mock data
  const stats = {
    activeBids: 5,
    wonAuctions: 3,
    totalSpent: 1250,
    watchlist: 12,
  };

  const activeBids = [
    {
      id: 1,
      title: "Sunset Dreams",
      artist: "John Doe",
      image: placeholderImg,
      yourBid: 175,
      currentHighest: 180,
      status: "outbid",
      timeLeft: "2 days",
      artworkId: 1,
    },
    {
      id: 2,
      title: "Ocean Waves",
      artist: "Jane Smith",
      image: placeholderImg,
      yourBid: 300,
      currentHighest: 300,
      status: "winning",
      timeLeft: "5 hours",
      artworkId: 2,
    },
    {
      id: 3,
      title: "Mountain Peak",
      artist: "Bob Wilson",
      image: placeholderImg,
      yourBid: 420,
      currentHighest: 450,
      status: "outbid",
      timeLeft: "1 day",
      artworkId: 3,
    },
  ];

  const wonAuctions = [
    {
      id: 1,
      title: "City Lights",
      artist: "Alice Brown",
      image: placeholderImg,
      winningBid: 320,
      datePurchased: "2024-01-15",
      artworkId: 4,
    },
    {
      id: 2,
      title: "Forest Path",
      artist: "Mike Johnson",
      image: placeholderImg,
      winningBid: 200,
      datePurchased: "2024-01-10",
      artworkId: 5,
    },
  ];

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
            gridTemplateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }}
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
                  {stats.activeBids}
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
                  {stats.wonAuctions}
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
                  ${stats.totalSpent}
                </Text>
                <Text fontSize="xs" color="#94a3b8">
                  On artwork purchases
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
                  Watchlist
                </Text>
                <Text fontSize="2xl" fontWeight="bold" color="#f59e0b">
                  {stats.watchlist}
                </Text>
                <Text fontSize="xs" color="#94a3b8">
                  Items watching
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
                      src={bid.image}
                      alt={bid.title}
                      boxSize="60px"
                      objectFit="cover"
                      borderRadius="md"
                    />
                    <VStack align="start" spacing={1} flex={1}>
                      <HStack justify="space-between" w="full">
                        <Text fontWeight="semibold" color="white">
                          {bid.title}
                        </Text>
                        <Badge colorScheme={bid.status === "winning" ? "green" : "red"}>
                          {bid.status === "winning" ? "Winning" : "Outbid"}
                        </Badge>
                      </HStack>
                      <Text fontSize="sm" color="#94a3b8">
                        by {bid.artist}
                      </Text>
                      <HStack spacing={4}>
                        <Text fontSize="sm" color="#94a3b8">
                          Your bid:{" "}
                          <Text as="span" color="white" fontWeight="bold">
                            ${bid.yourBid}
                          </Text>
                        </Text>
                        <Text fontSize="sm" color="#94a3b8">
                          Current:{" "}
                          <Text
                            as="span"
                            color={bid.status === "winning" ? "green.400" : "red.400"}
                            fontWeight="bold"
                          >
                            ${bid.currentHighest}
                          </Text>
                        </Text>
                        <Text fontSize="sm" color="#94a3b8">
                          {bid.timeLeft} left
                        </Text>
                      </HStack>
                    </VStack>
                    <Button
                      size="sm"
                      background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                      color="white"
                      onClick={() => navigate(`/artwork/${bid.artworkId}`)}
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
            <Box
              display="grid"
              gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }}
              gap={4}
            >
              {wonAuctions.map((auction) => (
                <Box
                  key={auction.id}
                  bg="#0f172a"
                  borderRadius="lg"
                  overflow="hidden"
                  border="1px"
                  borderColor="rgba(255,255,255,0.1)"
                  cursor="pointer"
                  onClick={() => navigate(`/artwork/${auction.artworkId}`)}
                  _hover={{
                    transform: "translateY(-2px)",
                    boxShadow: "0 8px 25px rgba(0,0,0,0.3)",
                  }}
                  transition="all 0.2s"
                >
                  <Image
                    src={auction.image}
                    alt={auction.title}
                    h="150px"
                    w="full"
                    objectFit="cover"
                  />
                  <Box p={4}>
                    <VStack align="start" spacing={2}>
                      <Badge colorScheme="green" variant="subtle">
                        Won
                      </Badge>
                      <Text fontWeight="semibold" color="white">
                        {auction.title}
                      </Text>
                      <Text fontSize="sm" color="#94a3b8">
                        by {auction.artist}
                      </Text>
                      <Text fontSize="sm" color="green.400" fontWeight="bold">
                        Won for ${auction.winningBid}
                      </Text>
                      <Text fontSize="xs" color="#94a3b8">
                        Purchased: {auction.datePurchased}
                      </Text>
                    </VStack>
                  </Box>
                </Box>
              ))}
            </Box>
          </Box>
        </VStack>
      </Container>
    </Box>
  );
};

export default UserDashboard;
