import { useState } from "react";
import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  SimpleGrid,
  Badge,
  HStack,
  Image,
  Skeleton,
} from "@chakra-ui/react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { artworkService } from "../../services/api";

// Optimized artwork image component with lazy loading
const ArtworkImage = ({ imageUrl, title, index }) => {
  const [imageLoaded, setImageLoaded] = useState(false);

  const gradientColors = [
    ["#667eea", "#764ba2"],
    ["#f093fb", "#f5576c"],
    ["#4facfe", "#00f2fe"],
    ["#fa709a", "#fee140"],
  ];

  const [color1, color2] = gradientColors[index % 4];
  const gradientBg = `linear-gradient(45deg, ${color1} 0%, ${color2} 100%)`;

  return (
    <Box h="120px" position="relative" overflow="hidden">
      {/* Gradient background (always shown as fallback) */}
      <Box
        position="absolute"
        top="0"
        left="0"
        right="0"
        bottom="0"
        bg={gradientBg}
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text fontSize="2rem" opacity="0.7">
          🎨
        </Text>
      </Box>

      {/* Actual image (lazy loaded if available) */}
      {imageUrl && (
        <>
          {!imageLoaded && (
            <Skeleton
              position="absolute"
              top="0"
              left="0"
              right="0"
              bottom="0"
              startColor="gray.700"
              endColor="gray.600"
            />
          )}
          <Image
            src={imageUrl}
            alt={title}
            loading="lazy" // Native lazy loading
            position="absolute"
            top="0"
            left="0"
            w="100%"
            h="100%"
            objectFit="cover"
            onLoad={() => setImageLoaded(true)}
            display={imageLoaded ? "block" : "none"}
          />
        </>
      )}
    </Box>
  );
};

const LiveAuctions = () => {
  const navigate = useNavigate();

  const { data: artworks, isLoading } = useQuery({
    queryKey: ["featured-artworks"],
    queryFn: () => artworkService.getFeatured(),
    staleTime: 30000,
  });

  const artworkData = artworks?.data || [];

  const displayArtworks = artworkData.slice(0, 4);

  return (
    <Box py={12}>
      <Container maxW="7xl">
        <VStack spacing={8}>
          <VStack spacing={4}>
            <HStack spacing={3}>
              <Box w="8px" h="8px" bg="green.400" borderRadius="full" />
              <Heading size="xl" color="white" fontWeight="700">
                Live Auctions
              </Heading>
            </HStack>
            <Text color="#94a3b8" textAlign="center">
              Active bidding happening now
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacingX={12} w="full">
            {displayArtworks.map((artwork, index) => (
              <Box
                mx={3}
                key={artwork.id || index}
                bg="#1e293b"
                borderRadius="xl"
                overflow="hidden"
                cursor="pointer"
                onClick={() => navigate(`/artwork/${artwork.id || index + 1}`)}
                border="1px solid"
                borderColor="rgba(255,255,255,0.1)"
                _hover={{
                  transform: "translateY(-2px)",
                  boxShadow: "0 8px 25px rgba(0,0,0,0.3)",
                }}
                transition="all 0.3s ease"
              >
                {/* Optimized image component with lazy loading */}
                <ArtworkImage imageUrl={artwork.image_url} title={artwork.title} index={index} />

                <Box p={4}>
                  <VStack align="start" spacing={3}>
                    <HStack justify="space-between" w="full">
                      <Heading size="sm" color="white" noOfLines={1}>
                        {artwork.title}
                      </Heading>
                      <Badge
                        colorScheme={artwork.status === "active" ? "green" : "red"}
                        fontSize="xs"
                      >
                        {artwork.status === "active" ? "Live" : "Ending"}
                      </Badge>
                    </HStack>

                    <Text color="#94a3b8" fontSize="xs">
                      by {artwork.artist || artwork.artist_name || "Unknown Artist"}
                    </Text>

                    <HStack justify="space-between" w="full">
                      <Text fontWeight="bold" color="green.400" fontSize="sm">
                        ${artwork.current_bid || artwork.current_highest_bid || 0}
                      </Text>
                      <Text color="#94a3b8" fontSize="xs">
                        {artwork.time_left || "1h 30m"}
                      </Text>
                    </HStack>
                  </VStack>
                </Box>
              </Box>
            ))}
          </SimpleGrid>

          {displayArtworks.length === 0 && !isLoading && (
            <Text color="#94a3b8" textAlign="center" py={8}>
              No live auctions at the moment. Check back soon!
            </Text>
          )}
        </VStack>
      </Container>
    </Box>
  );
};

export default LiveAuctions;
