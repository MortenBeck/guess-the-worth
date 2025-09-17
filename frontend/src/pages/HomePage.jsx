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
} from '@chakra-ui/react'
import { useAuth0 } from '@auth0/auth0-react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { config } from '../config/env'
import placeholderImg from '../assets/placeholder.jpg'

const HomePage = () => {
  const { loginWithRedirect } = useAuth0()
  const { user, isAuthenticated, isAdmin, isSeller, isBuyer } = useAuthStore()
  const navigate = useNavigate()

  const handleLogin = () => {
    loginWithRedirect()
  }

  const featuredArtworks = [
    {
      id: 1,
      title: "Sunset Dreams",
      artist: "John Doe",
      image: placeholderImg,
      currentBid: 150,
      status: "active"
    },
    {
      id: 2,
      title: "Ocean Waves",
      artist: "Jane Smith",
      image: placeholderImg,
      currentBid: 300,
      status: "active"
    },
    {
      id: 3,
      title: "Mountain Peak",
      artist: "Bob Wilson",
      image: placeholderImg,
      currentBid: 450,
      status: "ending_soon"
    }
  ]

  return (
    <Container maxW="container.xl" py={8}>
      {isAuthenticated ? (
        <VStack spacing={8} align="stretch">
          <Box>
            <Heading size="xl" mb={4} color="text">
              Welcome back, {user?.name}!
            </Heading>
            <HStack spacing={2} mb={4}>
              <Text fontSize="lg" color="gray.600">
                Role:
              </Text>
              <Text
                fontSize="lg"
                fontWeight="bold"
                color={isAdmin() ? "red.500" : isSeller() ? "primary" : "accent"}
                textTransform="capitalize"
              >
                {user?.role}
              </Text>
            </HStack>
            <Text fontSize="lg" color="gray.600">
              {isAdmin() ? "Manage the platform and oversee all activities" :
               isSeller() ? "Upload your artworks and set secret thresholds" :
               "Discover amazing artworks and place your bids"}
            </Text>
          </Box>

          {/* Quick Actions */}
          <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(3, 1fr)" }} gap={6}>
            {isAdmin() && (
              <Box bg="white" p={4} borderRadius="md" shadow="sm">
                <Box>
                  <Heading size="md" color="primary" mb={2}>
                    Admin Dashboard
                  </Heading>
                  <Text color="gray.600">
                    Manage users and platform operations
                  </Text>
                </Box>
                <Box pt={3}>
                  <Button colorScheme="primary" size="sm" onClick={() => navigate('/admin-dashboard')}>
                    Go to Dashboard
                  </Button>
                </Box>
              </Box>
            )}

            {isSeller() && (
              <Box bg="white" p={4} borderRadius="md" shadow="sm">
                <Box>
                  <Heading size="md" color="primary" mb={2}>
                    Seller Dashboard
                  </Heading>
                  <Text color="gray.600">
                    Upload artworks and track sales
                  </Text>
                </Box>
                <Box pt={3}>
                  <Button colorScheme="primary" size="sm" onClick={() => navigate('/seller-dashboard')}>
                    Go to Dashboard
                  </Button>
                </Box>
              </Box>
            )}

            {isBuyer() && (
              <Box bg="white" p={4} borderRadius="md" shadow="sm">
                <Box>
                  <Heading size="md" color="primary" mb={2}>
                    My Dashboard
                  </Heading>
                  <Text color="gray.600">
                    View your bids and won artworks
                  </Text>
                </Box>
                <Box pt={3}>
                  <Button colorScheme="primary" size="sm" onClick={() => navigate('/dashboard')}>
                    Go to Dashboard
                  </Button>
                </Box>
              </Box>
            )}
          </Box>

          {/* Featured Artworks */}
          <Box>
            <Heading size="lg" mb={6} color="text">
              Featured Artworks
            </Heading>
            <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} gap={6}>
              {featuredArtworks.map((artwork) => (
                <Box key={artwork.id} bg="white" p={4} borderRadius="md" shadow="sm" cursor="pointer" onClick={() => navigate(`/artwork/${artwork.id}`)}>
                  <Image
                    src={artwork.image}
                    alt={artwork.title}
                    h="200px"
                    w="full"
                    objectFit="cover"
                  />
                  <Box>
                    <VStack align="start" spacing={2}>
                      <HStack justify="space-between" w="full">
                        <Heading size="md">{artwork.title}</Heading>
                        <Badge colorScheme={artwork.status === 'ending_soon' ? 'red' : 'green'}>
                          {artwork.status === 'ending_soon' ? 'Ending Soon' : 'Active'}
                        </Badge>
                      </HStack>
                      <Text color="gray.600">by {artwork.artist}</Text>
                      <Text fontWeight="bold" color="primary">
                        Current Bid: ${artwork.currentBid}
                      </Text>
                    </VStack>
                  </Box>
                </Box>
              ))}
            </Box>
          </Box>
        </VStack>
      ) : (
        <VStack spacing={8} align="center" py={12}>
          <VStack spacing={4} textAlign="center">
            <Heading size="2xl" color="text">
              Welcome to {config.APP_NAME}
            </Heading>
            <Text fontSize="xl" color="gray.600" maxW="2xl">
              Discover unique artworks from talented artists.
              Place your bid and see if you hit the secret threshold!
            </Text>
          </VStack>

          <VStack spacing={4}>
            <Button
              size="lg"
              colorScheme="primary"
              onClick={handleLogin}
            >
              Get Started
            </Button>
            <Text fontSize="sm" color="gray.500">
              Sign in with Google, Facebook, or your preferred provider
            </Text>
          </VStack>

          {/* Preview Gallery */}
          <Box w="full">
            <Heading size="lg" mb={6} textAlign="center" color="text">
              Featured Artworks
            </Heading>
            <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)" }} gap={6}>
              {featuredArtworks.map((artwork) => (
                <Box key={artwork.id} bg="white" p={4} borderRadius="md" shadow="sm">
                  <Image
                    src={artwork.image}
                    alt={artwork.title}
                    h="200px"
                    w="full"
                    objectFit="cover"
                  />
                  <Box>
                    <VStack align="start" spacing={2}>
                      <Heading size="md">{artwork.title}</Heading>
                      <Text color="gray.600">by {artwork.artist}</Text>
                      <Text fontWeight="bold" color="primary">
                        Current Bid: ${artwork.currentBid}
                      </Text>
                    </VStack>
                  </Box>
                </Box>
              ))}
            </Box>
          </Box>
        </VStack>
      )}
    </Container>
  )
}

export default HomePage