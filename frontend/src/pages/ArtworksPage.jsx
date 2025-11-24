import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  HStack,
  Image,
  Badge,
  Button,
  Spinner,
  Center,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import { artworkService } from "../services/api";
import placeholderImg from "../assets/placeholder.jpg";

const ArtworksPage = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [filterCategory, setFilterCategory] = useState("all");

  // Fetch artworks from API
  const {
    data: artworks = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["artworks"],
    queryFn: async () => {
      const response = await artworkService.getAll();
      return response.data;
    },
    staleTime: 30000, // 30 seconds
  });

  // Calculate time left for each artwork
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

  const filteredArtworks = artworks
    .filter((artwork) => {
      const matchesSearch =
        artwork.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (artwork.artist_name &&
          artwork.artist_name.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesCategory = filterCategory === "all" || artwork.category === filterCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "price_low":
          return (a.current_highest_bid || 0) - (b.current_highest_bid || 0);
        case "price_high":
          return (b.current_highest_bid || 0) - (a.current_highest_bid || 0);
        case "ending_soon":
          if (!a.end_date) return 1;
          if (!b.end_date) return -1;
          return new Date(a.end_date) - new Date(b.end_date);
        default: // newest
          return b.id - a.id;
      }
    });

  // Extract unique categories from artworks
  const categories = ["all", ...new Set(artworks.map((a) => a.category).filter(Boolean))];

  // Loading state
  if (isLoading) {
    return (
      <Center h="100vh" bg="#0f172a">
        <Spinner size="xl" color="purple.400" thickness="4px" />
      </Center>
    );
  }

  // Error state
  if (error) {
    return (
      <Center h="100vh" bg="#0f172a">
        <Box textAlign="center" p={8}>
          <Text color="red.400" fontSize="xl" mb={4}>
            Error loading artworks
          </Text>
          <Text color="#94a3b8">{error.message}</Text>
        </Box>
      </Center>
    );
  }

  return (
    <Box bg="#0f172a" color="white" minH="100vh" pt={6}>
      <Container maxW="container.xl" py={8}>
        <VStack spacing={8} align="stretch">
          {/* Header */}
          <Box>
            <Heading size="xl" color="white" mb={2}>
              Artwork Gallery
            </Heading>
            <Text color="#94a3b8">
              Discover and bid on unique artworks from talented artists around the world.
            </Text>
          </Box>

          {/* Search and Filters */}
          <Box
            bg="#1e293b"
            p={6}
            borderRadius="lg"
            border="1px"
            borderColor="rgba(255,255,255,0.1)"
          >
            <Box display="flex" flexDirection={{ base: "column", md: "row" }} gap={4}>
              <Box flex={2}>
                <input
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #334155",
                    borderRadius: "6px",
                    fontSize: "14px",
                    outline: "none",
                    backgroundColor: "#0f172a",
                    color: "white",
                  }}
                  placeholder="🔍 Search artworks or artists..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </Box>

              <Box maxW={{ base: "full", md: "200px" }}>
                <select
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #334155",
                    borderRadius: "6px",
                    fontSize: "14px",
                    outline: "none",
                    backgroundColor: "#0f172a",
                    color: "white",
                  }}
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category} value={category}>
                      {category === "all" ? "All Categories" : category}
                    </option>
                  ))}
                </select>
              </Box>

              <Box maxW={{ base: "full", md: "200px" }}>
                <select
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #334155",
                    borderRadius: "6px",
                    fontSize: "14px",
                    outline: "none",
                    backgroundColor: "#0f172a",
                    color: "white",
                  }}
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                >
                  <option value="newest">Newest First</option>
                  <option value="ending_soon">Ending Soon</option>
                  <option value="price_low">Price: Low to High</option>
                  <option value="price_high">Price: High to Low</option>
                  <option value="most_bids">Most Bids</option>
                </select>
              </Box>
            </Box>
          </Box>

          {/* Results Count */}
          <Text color="#94a3b8">
            Showing {filteredArtworks.length} artwork{filteredArtworks.length !== 1 ? "s" : ""}
          </Text>

          {/* Artwork Grid */}
          <Box
            display="grid"
            gridTemplateColumns={{
              base: "1fr",
              md: "repeat(2, 1fr)",
              lg: "repeat(3, 1fr)",
              xl: "repeat(4, 1fr)",
            }}
            gap={6}
          >
            {filteredArtworks.map((artwork) => (
              <Box
                key={artwork.id}
                bg="#1e293b"
                borderRadius="lg"
                overflow="hidden"
                border="1px"
                borderColor="rgba(255,255,255,0.1)"
                cursor="pointer"
                _hover={{ transform: "translateY(-2px)", boxShadow: "0 8px 25px rgba(0,0,0,0.3)" }}
                transition="all 0.2s"
                onClick={() => navigate(`/artwork/${artwork.id}`)}
              >
                <Image
                  src={artwork.image_url || placeholderImg}
                  alt={artwork.title}
                  h="200px"
                  w="full"
                  objectFit="cover"
                  borderTopRadius="md"
                />
                <Box p={4}>
                  <VStack align="start" spacing={3}>
                    <HStack justify="space-between" w="full">
                      <Badge
                        colorScheme={artwork.status === "sold" ? "red" : "green"}
                        variant="subtle"
                      >
                        {artwork.status === "sold" ? "Sold" : "Active"}
                      </Badge>
                      {artwork.category && (
                        <Badge variant="outline" colorScheme="gray">
                          {artwork.category}
                        </Badge>
                      )}
                    </HStack>

                    <Box w="full">
                      <Heading size="sm" color="white" mb={1}>
                        {artwork.title}
                      </Heading>
                      <Text color="#94a3b8" fontSize="sm">
                        by {artwork.artist_name || "Unknown Artist"}
                      </Text>
                    </Box>

                    <VStack align="start" spacing={1} w="full">
                      <HStack justify="space-between" w="full">
                        <Text fontSize="sm" color="#94a3b8">
                          Current Bid
                        </Text>
                        <Text fontSize="sm" fontWeight="bold" color="green.400">
                          ${artwork.current_highest_bid || 0}
                        </Text>
                      </HStack>
                      {artwork.end_date && (
                        <HStack justify="space-between" w="full">
                          <Text fontSize="xs" color="#94a3b8">
                            Time Left
                          </Text>
                          <Text fontSize="xs" color="#94a3b8">
                            {calculateTimeLeft(artwork.end_date)}
                          </Text>
                        </HStack>
                      )}
                    </VStack>

                    <Button
                      background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                      color="white"
                      size="sm"
                      w="full"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/artwork/${artwork.id}`);
                      }}
                      _hover={{
                        transform: "translateY(-1px)",
                        boxShadow: "0 4px 15px rgba(99, 102, 241, 0.3)",
                      }}
                      isDisabled={artwork.status === "sold"}
                    >
                      {artwork.status === "sold" ? "Sold" : "Place Bid"}
                    </Button>
                  </VStack>
                </Box>
              </Box>
            ))}
          </Box>

          {filteredArtworks.length === 0 && (
            <Box
              bg="#1e293b"
              p={12}
              borderRadius="lg"
              border="1px"
              borderColor="rgba(255,255,255,0.1)"
              textAlign="center"
            >
              <Text color="#94a3b8" fontSize="lg">
                No artworks found matching your criteria.
              </Text>
              <Button
                mt={4}
                variant="outline"
                borderColor="#334155"
                color="#94a3b8"
                onClick={() => {
                  setSearchTerm("");
                  setFilterCategory("all");
                  setSortBy("newest");
                }}
              >
                Clear Filters
              </Button>
            </Box>
          )}
        </VStack>
      </Container>
    </Box>
  );
};

export default ArtworksPage;
