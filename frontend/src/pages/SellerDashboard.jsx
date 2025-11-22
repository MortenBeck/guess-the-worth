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
import { statsService, artworkService } from "../services/api";
const AddIcon = () => <span>➕</span>;
import placeholderImg from "../assets/placeholder.jpg";

const SellerDashboard = () => {
  const navigate = useNavigate();

  // Fetch seller stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["seller-stats"],
    queryFn: statsService.getSellerStats,
    staleTime: 30000,
  });

  // Fetch seller's artworks
  const { data: myArtworksData, isLoading: artworksLoading } = useQuery({
    queryKey: ["my-artworks"],
    queryFn: artworkService.getMyArtworks,
    staleTime: 10000,
  });

  if (statsLoading || artworksLoading) {
    return (
      <Box bg="#0f172a" minH="100vh" color="white" display="flex" alignItems="center" justifyContent="center">
        <Spinner size="xl" color="#6366f1" />
      </Box>
    );
  }

  const myArtworks = myArtworksData?.data || [];
  const sellerStats = stats?.data || {
    total_artworks: 0,
    active_auctions: 0,
    sold_artworks: 0,
    total_earnings: 0,
  };

  // Separate by status
  const activeArtworks = myArtworks.filter(a => a.status === "ACTIVE");
  const soldArtworks = myArtworks.filter(a => a.status === "SOLD");

  const getStatusColor = (status) => {
    switch (status) {
      case "ACTIVE":
        return "green";
      case "SOLD":
        return "blue";
      case "ENDED":
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
                {sellerStats.total_artworks}
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
                {sellerStats.active_auctions}
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
                {sellerStats.sold_artworks}
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
                ${sellerStats.total_earnings}
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
            {myArtworks.length === 0 ? (
              <Text color="#94a3b8">
                No artworks yet. Click "Add New Artwork" to get started!
              </Text>
            ) : (
              <VStack spacing={4} align="stretch">
                {myArtworks.map((artwork) => (
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
                        src={artwork.image_url || placeholderImg}
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
                            ${artwork.secret_threshold}
                          </Text>
                        </HStack>
                        {artwork.status === "ACTIVE" && (
                          <>
                            <HStack>
                              <Text fontSize="sm" color="#94a3b8">
                                Current bid:{" "}
                              </Text>
                              <Text
                                fontSize="sm"
                                fontWeight="bold"
                                color={
                                  isThresholdMet(artwork.current_highest_bid || 0, artwork.secret_threshold)
                                    ? "#22c55e"
                                    : "#94a3b8"
                                }
                              >
                                ${artwork.current_highest_bid || 0}
                              </Text>
                              {isThresholdMet(artwork.current_highest_bid || 0, artwork.secret_threshold) && (
                                <Badge colorScheme="green" size="sm">
                                  Threshold Met!
                                </Badge>
                              )}
                            </HStack>
                          </>
                        )}
                        {artwork.status === "SOLD" && (
                          <Text fontSize="sm" color="#94a3b8">
                            Sold for ${artwork.current_highest_bid}
                          </Text>
                        )}
                      </VStack>
                      <VStack align="center" spacing={2}>
                        <Badge colorScheme={getStatusColor(artwork.status)}>
                          {artwork.status}
                        </Badge>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate(`/artwork/${artwork.id}`)}
                        >
                          View Details
                        </Button>
                      </VStack>
                    </HStack>
                  </Box>
                ))}
              </VStack>
            )}
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
            {activeArtworks.length === 0 ? (
              <Text color="#94a3b8">No active auctions</Text>
            ) : (
              <VStack spacing={4} align="stretch">
                {activeArtworks.map((artwork) => (
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
                        src={artwork.image_url || placeholderImg}
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
                            Current: ${artwork.current_highest_bid || 0}
                          </Text>
                          <Text fontSize="sm" color="#94a3b8">
                            •
                          </Text>
                          <Text fontSize="sm" color="#94a3b8">
                            Target: ${artwork.secret_threshold}
                          </Text>
                        </HStack>
                      </VStack>
                      <VStack align="center" spacing={2}>
                        <Text
                          fontSize="lg"
                          fontWeight="bold"
                          color={
                            isThresholdMet(artwork.current_highest_bid || 0, artwork.secret_threshold)
                              ? "#22c55e"
                              : "#f97316"
                          }
                        >
                          {Math.round(((artwork.current_highest_bid || 0) / artwork.secret_threshold) * 100)}%
                        </Text>
                        <Text fontSize="xs" color="#64748b">
                          to threshold
                        </Text>
                      </VStack>
                    </HStack>
                  </Box>
                ))}
              </VStack>
            )}
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
            {soldArtworks.length === 0 ? (
              <Text color="#94a3b8">No sales yet</Text>
            ) : (
              <VStack spacing={3}>
                {soldArtworks.map((artwork) => (
                  <HStack key={artwork.id} justify="space-between" w="full" p={3} bg="#0f172a" borderRadius="md">
                    <VStack align="start" spacing={0}>
                      <Text fontWeight="bold" color="white">
                        {artwork.title}
                      </Text>
                      <Text fontSize="sm" color="#94a3b8">
                        {new Date(artwork.updated_at).toLocaleDateString()}
                      </Text>
                    </VStack>
                    <VStack align="end" spacing={0}>
                      <Text fontSize="sm" color="#94a3b8">
                        Threshold: ${artwork.secret_threshold}
                      </Text>
                      <Text fontWeight="bold" color="white">
                        Sold: ${artwork.current_highest_bid}
                      </Text>
                    </VStack>
                  </HStack>
                ))}
              </VStack>
            )}
          </Box>
        </VStack>
      </Container>
    </Box>
  );
};

export default SellerDashboard;
