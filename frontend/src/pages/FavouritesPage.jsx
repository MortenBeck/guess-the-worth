import {
  Box,
  Container,
  Heading,
  Text,
  VStack,
  SimpleGrid,
  Badge,
  HStack,
  Button,
  Image,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";
import useFavoritesStore from "../store/favoritesStore";
import placeholderImg from "../assets/placeholder.jpg";

const FavouritesPage = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const { favorites, removeFromFavorites } = useFavoritesStore();

  const formatDateAdded = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return "Today";
    if (diffInDays === 1) return "1 day ago";
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30)
      return `${Math.floor(diffInDays / 7)} week${Math.floor(diffInDays / 7) > 1 ? "s" : ""} ago`;
    return date.toLocaleDateString();
  };

  return (
    <Box bg="#0f172a" minH="100vh" color="white">
      <Container maxW="7xl" py={8}>
        <VStack spacing={8} align="stretch">
          {/* Header */}
          <Box>
            <Heading
              size="2xl"
              mb={2}
              background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
              backgroundClip="text"
              color="transparent"
            >
              Your Favourites
            </Heading>
            <Text color="#94a3b8" fontSize="lg">
              Artworks you've saved for later • {favorites.length} items
            </Text>
          </Box>

          {/* Favourites Grid */}
          {favorites.length > 0 ? (
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8}>
              {favorites.map((artwork) => (
                <Box
                  key={artwork.id}
                  bg="#1e293b"
                  borderRadius="xl"
                  overflow="hidden"
                  cursor="pointer"
                  onClick={() => navigate(`/artwork/${artwork.id}`)}
                  border="1px solid"
                  borderColor="rgba(255,255,255,0.1)"
                  _hover={{
                    transform: "translateY(-2px)",
                    boxShadow: "0 8px 25px rgba(0,0,0,0.3)",
                  }}
                  transition="all 0.3s ease"
                >
                  <Image
                    src={artwork.image}
                    alt={artwork.title}
                    w="full"
                    h="200px"
                    objectFit="cover"
                  />

                  <Box p={6}>
                    <VStack align="start" spacing={4}>
                      <HStack justify="space-between" w="full">
                        <VStack align="start" spacing={1}>
                          <Heading size="md" color="white" noOfLines={1}>
                            {artwork.title}
                          </Heading>
                          <Text color="#94a3b8" fontSize="sm">
                            by {artwork.artist}
                          </Text>
                        </VStack>
                        <Badge
                          colorScheme={artwork.status === "active" ? "green" : "red"}
                          fontSize="xs"
                        >
                          {artwork.status === "active" ? "Active" : "Ending Soon"}
                        </Badge>
                      </HStack>

                      <HStack justify="space-between" w="full">
                        <Text fontWeight="bold" color="green.400" fontSize="lg">
                          Current Bid: ${artwork.currentBid}
                        </Text>
                        <Text fontSize="xs" color="#94a3b8">
                          Added {formatDateAdded(artwork.dateAdded)}
                        </Text>
                      </HStack>

                      <HStack spacing={2} w="full">
                        <Button
                          size="sm"
                          bg="white"
                          color="#1e293b"
                          _hover={{ bg: "#f1f5f9" }}
                          flex="1"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/artwork/${artwork.id}`);
                          }}
                        >
                          View Artwork
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          borderColor="#f87171"
                          color="#f87171"
                          _hover={{ bg: "#7f1d1d", color: "white" }}
                          onClick={(e) => {
                            e.stopPropagation();
                            removeFromFavorites(artwork.id);
                          }}
                        >
                          Remove
                        </Button>
                      </HStack>
                    </VStack>
                  </Box>
                </Box>
              ))}
            </SimpleGrid>
          ) : (
            <Box
              bg="#1e293b"
              border="1px solid"
              borderColor="rgba(255,255,255,0.1)"
              borderRadius="xl"
              p={12}
              textAlign="center"
            >
              <VStack spacing={6}>
                <Text fontSize="4xl">⭐</Text>
                <VStack spacing={3}>
                  <Heading size="lg" color="white">
                    No Favourites Yet
                  </Heading>
                  <Text color="#94a3b8" maxW="500px" lineHeight="1.6">
                    Start exploring artworks and save the ones you love. Your favourite pieces will
                    appear here.
                  </Text>
                </VStack>
                <Button
                  background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                  color="white"
                  size="lg"
                  onClick={() => navigate("/artworks")}
                  _hover={{
                    transform: "translateY(-1px)",
                    boxShadow: "0 4px 15px rgba(99, 102, 241, 0.3)",
                  }}
                  transition="all 0.2s"
                >
                  Browse Artworks
                </Button>
              </VStack>
            </Box>
          )}
        </VStack>
      </Container>
    </Box>
  );
};

export default FavouritesPage;
