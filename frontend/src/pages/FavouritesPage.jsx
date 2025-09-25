import { Box, Container, Heading, Text, VStack, SimpleGrid, Badge, HStack, Button, Image } from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import placeholderImg from '../assets/placeholder.jpg'

const FavouritesPage = () => {
  const { user } = useAuthStore()
  const navigate = useNavigate()

  // Mock favourite artworks data
  const favouriteArtworks = [
    {
      id: 1,
      title: "Sunset Dreams",
      artist: "Sarah Chen",
      currentBid: 245,
      status: "active",
      image: placeholderImg,
      dateAdded: "2 days ago"
    },
    {
      id: 3,
      title: "Ocean Waves",
      artist: "Emma Rodriguez",
      currentBid: 320,
      status: "active",
      image: placeholderImg,
      dateAdded: "5 days ago"
    },
    {
      id: 6,
      title: "Desert Sunset",
      artist: "Alex Johnson",
      currentBid: 195,
      status: "ending",
      image: placeholderImg,
      dateAdded: "1 week ago"
    },
  ]

  return (
    <Box bg="#0f172a" minH="100vh" color="white">
      <Container maxW="7xl" py={8}>
        <VStack spacing={8} align="stretch">
          {/* Header */}
          <Box>
            <Heading size="2xl" mb={2} background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)" backgroundClip="text" color="transparent">
              Your Favourites
            </Heading>
            <Text color="#94a3b8" fontSize="lg">
              Artworks you've saved for later • {favouriteArtworks.length} items
            </Text>
          </Box>

          {/* Favourites Grid */}
          {favouriteArtworks.length > 0 ? (
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={8}>
              {favouriteArtworks.map((artwork) => (
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
                    boxShadow: "0 8px 25px rgba(0,0,0,0.3)"
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
                          <Text color="#94a3b8" fontSize="sm">by {artwork.artist}</Text>
                        </VStack>
                        <Badge colorScheme={artwork.status === 'active' ? 'green' : 'red'} fontSize="xs">
                          {artwork.status === 'active' ? 'Active' : 'Ending Soon'}
                        </Badge>
                      </HStack>

                      <HStack justify="space-between" w="full">
                        <Text fontWeight="bold" color="green.400" fontSize="lg">
                          Current Bid: ${artwork.currentBid}
                        </Text>
                        <Text fontSize="xs" color="#94a3b8">
                          Added {artwork.dateAdded}
                        </Text>
                      </HStack>

                      <Button
                        size="sm"
                        bg="white"
                        color="#1e293b"
                        _hover={{ bg: "#f1f5f9" }}
                        w="full"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/artwork/${artwork.id}`)
                        }}
                      >
                        View Artwork
                      </Button>
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
                  <Heading size="lg" color="white">No Favourites Yet</Heading>
                  <Text color="#94a3b8" maxW="500px" lineHeight="1.6">
                    Start exploring artworks and save the ones you love. Your favourite pieces will appear here.
                  </Text>
                </VStack>
                <Button
                  background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                  color="white"
                  size="lg"
                  onClick={() => navigate('/artworks')}
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
  )
}

export default FavouritesPage