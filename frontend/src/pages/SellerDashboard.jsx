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
// Simple custom icon
const AddIcon = () => <span>➕</span>;
import placeholderImg from "../assets/placeholder.jpg";

const SellerDashboard = () => {
  const navigate = useNavigate();

  // Mock data - replace with actual API calls
  const stats = {
    totalArtworks: 15,
    activeAuctions: 8,
    soldArtworks: 7,
    totalEarnings: 3250,
  };

  const artworks = [
    {
      id: 1,
      title: "Sunset Dreams",
      image: placeholderImg,
      secretThreshold: 200,
      currentBid: 175,
      totalBids: 12,
      timeLeft: "2 days",
      status: "active",
    },
    {
      id: 2,
      title: "Ocean Waves",
      image: placeholderImg,
      secretThreshold: 350,
      currentBid: 300,
      totalBids: 8,
      timeLeft: "5 hours",
      status: "active",
    },
    {
      id: 3,
      title: "Mountain Peak",
      image: placeholderImg,
      secretThreshold: 400,
      currentBid: 450,
      totalBids: 23,
      dateSold: "2024-01-15",
      status: "sold",
    },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case "active":
        return "green";
      case "sold":
        return "blue";
      case "ended":
        return "gray";
      default:
        return "gray";
    }
  };

  const isThresholdMet = (currentBid, threshold) => currentBid >= threshold;

  return (
    <Box bg="#0f172a" minH="100vh" color="white">
      <Container maxW="container.xl" py={8}>
        <VStack spacing={8} align="stretch">
          <HStack justify="space-between">
            <Box>
              <Heading size="xl" color="text" mb={2}>
                Seller Dashboard
              </Heading>
              <Text color="#94a3b8">
                Manage your artworks, track sales, and grow your business.
              </Text>
            </Box>
            <Button
              leftIcon={<AddIcon />}
              bg="white"
              color="#1e293b"
              onClick={() => navigate("/add-artwork")}
              _hover={{
                bg: "#f1f5f9",
                transform: "translateY(-1px)",
              }}
              transition="all 0.2s"
            >
              Add New Artwork
            </Button>
          </HStack>

          {/* Stats Overview */}
          <Box
            display="grid"
            gridTemplateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }}
            gap={6}
          >
            <Box
              bg="#1e293b"
              p={4}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
              textAlign="center"
            >
              <Text fontSize="sm" color="#94a3b8">
                Total Artworks
              </Text>
              <Text fontSize="2xl" fontWeight="bold" color="white">
                {stats.totalArtworks}
              </Text>
              <Text fontSize="xs" color="#64748b">
                All time uploads
              </Text>
            </Box>
            <Box
              bg="#1e293b"
              p={4}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
              textAlign="center"
            >
              <Text fontSize="sm" color="#94a3b8">
                Active Auctions
              </Text>
              <Text fontSize="2xl" fontWeight="bold" color="#3b82f6">
                {stats.activeAuctions}
              </Text>
              <Text fontSize="xs" color="#64748b">
                Currently live
              </Text>
            </Box>
            <Box
              bg="#1e293b"
              p={4}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
              textAlign="center"
            >
              <Text fontSize="sm" color="#94a3b8">
                Sold Artworks
              </Text>
              <Text fontSize="2xl" fontWeight="bold" color="white">
                {stats.soldArtworks}
              </Text>
              <Text fontSize="xs" color="#64748b">
                Successfully sold
              </Text>
            </Box>
            <Box
              bg="#1e293b"
              p={4}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
              textAlign="center"
            >
              <Text fontSize="sm" color="#94a3b8">
                Total Earnings
              </Text>
              <Text fontSize="2xl" fontWeight="bold" color="#3b82f6">
                ${stats.totalEarnings}
              </Text>
              <Text fontSize="xs" color="#64748b">
                From sales
              </Text>
            </Box>
          </Box>

          {/* My Artworks */}
          <Box
            bg="#1e293b"
            p={6}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="rgba(255,255,255,0.1)"
          >
            <Heading size="md" color="white" mb={4}>
              My Artworks
            </Heading>
            <VStack spacing={4} align="stretch">
              {artworks.map((artwork) => (
                <Box
                  key={artwork.id}
                  bg="#0f172a"
                  p={4}
                  borderRadius="lg"
                  boxShadow="sm"
                  border="1px"
                  borderColor="rgba(255,255,255,0.1)"
                >
                  <HStack spacing={4}>
                    <Image
                      src={artwork.image}
                      alt={artwork.title}
                      w="80px"
                      h="80px"
                      objectFit="cover"
                      borderRadius="md"
                    />
                    <VStack align="start" flex={1} spacing={1}>
                      <Heading size="md" color="white">
                        {artwork.title}
                      </Heading>
                      <HStack>
                        <Text fontSize="sm" color="#94a3b8">
                          Secret threshold:{" "}
                        </Text>
                        <Text fontSize="sm" fontWeight="bold" color="white">
                          ${artwork.secretThreshold}
                        </Text>
                      </HStack>
                      {artwork.status === "active" && (
                        <>
                          <HStack>
                            <Text fontSize="sm" color="#94a3b8">
                              Current bid:{" "}
                            </Text>
                            <Text
                              fontSize="sm"
                              fontWeight="bold"
                              color={
                                isThresholdMet(artwork.currentBid, artwork.secretThreshold)
                                  ? "#22c55e"
                                  : "#94a3b8"
                              }
                            >
                              ${artwork.currentBid}
                            </Text>
                            {isThresholdMet(artwork.currentBid, artwork.secretThreshold) && (
                              <Badge colorScheme="green" size="sm">
                                Threshold Met!
                              </Badge>
                            )}
                          </HStack>
                          <Text fontSize="sm" color="#94a3b8">
                            {artwork.totalBids} bids • {artwork.timeLeft} left
                          </Text>
                        </>
                      )}
                      {artwork.status === "sold" && (
                        <Text fontSize="sm" color="#94a3b8">
                          Sold on {new Date(artwork.dateSold).toLocaleDateString()} for $
                          {artwork.currentBid}
                        </Text>
                      )}
                    </VStack>
                    <VStack align="center" spacing={2}>
                      <Badge colorScheme={getStatusColor(artwork.status)}>{artwork.status}</Badge>
                      <Button size="sm" variant="outline">
                        View Details
                      </Button>
                    </VStack>
                  </HStack>
                </Box>
              ))}
            </VStack>
          </Box>

          {/* Active Auctions */}
          <Box
            bg="#1e293b"
            p={6}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="rgba(255,255,255,0.1)"
          >
            <Heading size="md" color="white" mb={4}>
              Active Auctions
            </Heading>
            <VStack spacing={4} align="stretch">
              {artworks
                .filter((a) => a.status === "active")
                .map((artwork) => (
                  <Box
                    key={artwork.id}
                    bg="#0f172a"
                    p={4}
                    borderRadius="lg"
                    boxShadow="sm"
                    border="1px"
                    borderColor="rgba(255,255,255,0.1)"
                  >
                    <HStack spacing={4}>
                      <Image
                        src={artwork.image}
                        alt={artwork.title}
                        w="80px"
                        h="80px"
                        objectFit="cover"
                        borderRadius="md"
                      />
                      <VStack align="start" flex={1} spacing={1}>
                        <Heading size="md" color="white">
                          {artwork.title}
                        </Heading>
                        <HStack>
                          <Text fontSize="sm" color="#94a3b8">
                            Current: ${artwork.currentBid}
                          </Text>
                          <Text fontSize="sm" color="#94a3b8">
                            •
                          </Text>
                          <Text fontSize="sm" color="#94a3b8">
                            Target: ${artwork.secretThreshold}
                          </Text>
                        </HStack>
                        <Text fontSize="sm" color="#94a3b8">
                          {artwork.totalBids} bids • {artwork.timeLeft} left
                        </Text>
                      </VStack>
                      <VStack align="center" spacing={2}>
                        <Text
                          fontSize="lg"
                          fontWeight="bold"
                          color={
                            isThresholdMet(artwork.currentBid, artwork.secretThreshold)
                              ? "#22c55e"
                              : "#f97316"
                          }
                        >
                          {Math.round((artwork.currentBid / artwork.secretThreshold) * 100)}%
                        </Text>
                        <Text fontSize="xs" color="#64748b">
                          to threshold
                        </Text>
                      </VStack>
                    </HStack>
                  </Box>
                ))}
            </VStack>
          </Box>

          {/* Sales History */}
          <Box
            bg="#1e293b"
            p={6}
            borderRadius="lg"
            boxShadow="sm"
            border="1px"
            borderColor="rgba(255,255,255,0.1)"
          >
            <Heading size="md" color="white" mb={4}>
              Sales History
            </Heading>
            <VStack spacing={3}>
              <HStack justify="space-between" w="full" p={3} bg="#0f172a" borderRadius="md">
                <VStack align="start" spacing={0}>
                  <Text fontWeight="bold" color="white">
                    Mountain Peak
                  </Text>
                  <Text fontSize="sm" color="#94a3b8">
                    Jan 15, 2024
                  </Text>
                </VStack>
                <VStack align="end" spacing={0}>
                  <Text fontSize="sm" color="#94a3b8">
                    Threshold: $400
                  </Text>
                  <Text fontWeight="bold" color="white">
                    Sold: $450
                  </Text>
                </VStack>
              </HStack>
              <HStack justify="space-between" w="full" p={3} bg="#0f172a" borderRadius="md">
                <VStack align="start" spacing={0}>
                  <Text fontWeight="bold" color="white">
                    City Lights
                  </Text>
                  <Text fontSize="sm" color="#94a3b8">
                    Jan 10, 2024
                  </Text>
                </VStack>
                <VStack align="end" spacing={0}>
                  <Text fontSize="sm" color="#94a3b8">
                    Threshold: $300
                  </Text>
                  <Text fontWeight="bold" color="white">
                    Sold: $320
                  </Text>
                </VStack>
              </HStack>
            </VStack>
          </Box>

          {/* Analytics */}
          <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
            >
              <Heading size="md" color="white" mb={4}>
                Performance Metrics
              </Heading>
              <VStack spacing={4}>
                <HStack justify="space-between" w="full">
                  <Text color="#94a3b8">Average sale price</Text>
                  <Text fontWeight="bold" color="white">
                    $385
                  </Text>
                </HStack>
                <HStack justify="space-between" w="full">
                  <Text color="#94a3b8">Success rate</Text>
                  <Text fontWeight="bold" color="white">
                    78%
                  </Text>
                </HStack>
                <HStack justify="space-between" w="full">
                  <Text color="#94a3b8">Avg. threshold hit rate</Text>
                  <Text fontWeight="bold" color="white">
                    65%
                  </Text>
                </HStack>
              </VStack>
            </Box>
            <Box
              bg="#1e293b"
              p={6}
              borderRadius="lg"
              boxShadow="sm"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
            >
              <Heading size="md" color="white" mb={4}>
                Recent Activity
              </Heading>
              <VStack spacing={3} align="start">
                <Text fontSize="sm" color="#94a3b8">
                  New bid on "Sunset Dreams" - $175
                </Text>
                <Text fontSize="sm" color="#94a3b8">
                  Threshold reached for "Ocean Waves"
                </Text>
                <Text fontSize="sm" color="#94a3b8">
                  "Mountain Peak" sold for $450
                </Text>
              </VStack>
            </Box>
          </Box>
        </VStack>
      </Container>
    </Box>
  );
};

export default SellerDashboard;
