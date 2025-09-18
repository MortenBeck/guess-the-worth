import { Box, Container, Heading, Text, Button, VStack, HStack, SimpleGrid, Badge } from '@chakra-ui/react'
import { useAuth0 } from '@auth0/auth0-react'
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { config } from '../config/env'

const HomePage = () => {
  const { loginWithRedirect, isAuthenticated } = useAuth0()
  const { user } = useAuthStore()
  const navigate = useNavigate()

  const handleLogin = () => {
    loginWithRedirect()
  }

  const handleExplore = () => {
    if (isAuthenticated) {
      navigate('/artworks')
    } else {
      handleLogin()
    }
  }

  return (
    <Box bg="#0f172a" color="white" minH="100vh">
      {/* Hero Section */}
      <Box 
        pt="6rem" 
        pb="8rem"
        position="relative"
        overflow="hidden"
      >
        {/* Background Gradient */}
        <Box
          position="absolute"
          top="0"
          left="0"
          right="0"
          bottom="0"
          background="radial-gradient(circle at 30% 20%, rgba(99, 102, 241, 0.25) 0%, transparent 50%), radial-gradient(circle at 70% 80%, rgba(236, 72, 153, 0.25) 0%, transparent 50%)"
          zIndex="-1"
        />
        <Container maxW="7xl" position="relative" zIndex="1">
          <VStack spacing={16} textAlign="center" py={16}>
            <VStack spacing={10}>
              <Heading 
                size={{ base: "3xl", md: "4xl", lg: "5xl" }}
                fontWeight="800"
                textAlign="center"
                background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                backgroundClip="text"
                color="transparent"
                lineHeight="1.2"
              >
                Bid on Art.<br />Guess the Worth.
              </Heading>
              
              <Text fontSize="xl" color="#94a3b8" maxW="600px">
                Experience the thrill of secret threshold bidding. Artists set hidden minimum prices - 
                bid what you think it's worth and instantly win when you hit the mark.
              </Text>

              <HStack spacing={12} wrap="wrap" justify="center">
                <Button
                  size="lg"
                  background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                  color="white"
                  px={10}
                  py={8}
                  fontSize="lg"
                  fontWeight="600"
                  border="none"
                  onClick={handleExplore}
                  _hover={{
                    transform: "translateY(-2px) scale(1.05)",
                    boxShadow: "0 10px 25px rgba(99, 102, 241, 0.3)",
                  }}
                  transition="all 0.3s ease"
                >
                  {isAuthenticated ? 'Start Bidding' : 'Start Bidding'}
                </Button>
                
                <Button
                  size="lg"
                  variant="outline"
                  borderColor="#334155"
                  color="#94a3b8"
                  bg="transparent"
                  px={10}
                  py={8}
                  fontSize="lg"
                  fontWeight="600"
                  onClick={() => {
                    const element = document.querySelector('#how-it-works');
                    if (element) {
                      element.scrollIntoView({ behavior: 'smooth' });
                    }
                  }}
                  _hover={{
                    bg: "#1e293b",
                    color: "white",
                    borderColor: "#1e293b"
                  }}
                  transition="all 0.3s ease"
                >
                  Learn How
                </Button>
              </HStack>

              {isAuthenticated && (
                <Text fontSize="lg" color="white">
                  Welcome back, {user?.name}!
                </Text>
              )}
            </VStack>

            {/* Statistics */}
            <Box w="full" mt={24}>
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={12}>
                <VStack spacing={3}>
                  <Text fontSize="3xl" fontWeight="700" color="#ec4899">1,247</Text>
                  <Text fontSize="sm" color="#94a3b8" textAlign="center">Active Artworks</Text>
                </VStack>
                <VStack spacing={3}>
                  <Text fontSize="3xl" fontWeight="700" color="#ec4899">$89k</Text>
                  <Text fontSize="sm" color="#94a3b8" textAlign="center">Total Bids Placed</Text>
                </VStack>
                <VStack spacing={3}>
                  <Text fontSize="3xl" fontWeight="700" color="#ec4899">156</Text>
                  <Text fontSize="sm" color="#94a3b8" textAlign="center">Artists</Text>
                </VStack>
                <VStack spacing={3}>
                  <Text fontSize="3xl" fontWeight="700" color="#ec4899">24/7</Text>
                  <Text fontSize="sm" color="#94a3b8" textAlign="center">Live Bidding</Text>
                </VStack>
              </SimpleGrid>
            </Box>
          </VStack>
        </Container>
      </Box>

      {/* How It Works Section */}
      <Box bg="#1e293b" py={32}>
        <Container maxW="7xl">
          <VStack spacing={20}>
            <Heading 
              size="3xl" 
              textAlign="center" 
              fontWeight="700"
              background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
              backgroundClip="text"
              color="transparent"
              mb={4}
            >
              How It Works
            </Heading>
            
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={{ base: 16, md: 32 }}>
              <Box bg="#0f172a" p={12} borderRadius="xl" textAlign="center" border="1px solid" borderColor="rgba(255,255,255,0.1)">
                <VStack spacing={8}>
                  <Box
                    w="80px"
                    h="80px"
                    bg="blue.500"
                    borderRadius="full"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    fontSize="2rem"
                  >
                    🎯
                  </Box>
                  <Heading size="md" color="white">Browse Art</Heading>
                  <Text color="#94a3b8" lineHeight="1.6">
                    Discover unique artworks from talented artists. Each piece has a secret minimum price set by the artist.
                  </Text>
                </VStack>
              </Box>

              <Box bg="#0f172a" p={12} borderRadius="xl" textAlign="center" border="1px solid" borderColor="rgba(255,255,255,0.1)">
                <VStack spacing={8}>
                  <Box
                    w="80px"
                    h="80px"
                    bg="blue.500"
                    borderRadius="full"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    fontSize="2rem"
                  >
                    💰
                  </Box>
                  <Heading size="md" color="white">Place Your Bid</Heading>
                  <Text color="#94a3b8" lineHeight="1.6">
                    Bid what you think the artwork is worth. You won't know the secret threshold until you hit it!
                  </Text>
                </VStack>
              </Box>

              <Box bg="#0f172a" p={12} borderRadius="xl" textAlign="center" border="1px solid" borderColor="rgba(255,255,255,0.1)">
                <VStack spacing={8}>
                  <Box
                    w="80px"
                    h="80px"
                    bg="blue.500"
                    borderRadius="full"
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                    fontSize="2rem"
                  >
                    ⚡
                  </Box>
                  <Heading size="md" color="white">Instant Win</Heading>
                  <Text color="#94a3b8" lineHeight="1.6">
                    When your bid meets or exceeds the secret threshold, you instantly win and purchase the artwork!
                  </Text>
                </VStack>
              </Box>
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* Featured Artworks Section */}
      <Box py={32}>
        <Container maxW="7xl">
          <VStack spacing={16}>
            <VStack spacing={6}>
              <Heading 
                size="3xl" 
                textAlign="center" 
                fontWeight="700"
                background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                backgroundClip="text"
                color="transparent"
                mb={4}
              >
                Featured Artworks
              </Heading>
              
              <HStack spacing={2} justify="center">
                <Box w="8px" h="8px" bg="green.400" borderRadius="full" />
                <Text fontSize="sm" color="#94a3b8">Live bidding in progress</Text>
              </HStack>
            </VStack>

            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={{ base: 16, md: 28, lg: 32 }} w="full">
              {[
                { title: "Midnight Dreams", artist: "Sarah Chen", bid: 245, status: "active" },
                { title: "Abstract Emotions", artist: "Michael Torres", bid: 180, status: "ending" },
                { title: "Ocean Waves", artist: "Emma Rodriguez", bid: 320, status: "active" },
                { title: "Golden Hour", artist: "David Kim", bid: 150, status: "active" },
                { title: "Soft Whispers", artist: "Lisa Park", bid: 275, status: "active" },
                { title: "Desert Sunset", artist: "Alex Johnson", bid: 195, status: "ending" }
              ].map((artwork, index) => (
                <Box
                  key={index}
                  bg="#1e293b"
                  borderRadius="xl"
                  overflow="hidden"
                  cursor="pointer"
                  onClick={() => navigate(`/artwork/${index + 1}`)}
                  border="1px solid"
                  borderColor="rgba(255,255,255,0.1)"
                  _hover={{
                    transform: "translateY(-2px)",
                    boxShadow: "0 8px 25px rgba(0,0,0,0.3)"
                  }}
                  transition="all 0.3s ease"
                >
                  <Box
                    h="200px"
                    bg={`linear-gradient(45deg, ${
                      ['#667eea', '#f093fb', '#4facfe', '#fa709a', '#a8edea', '#ffecd2'][index]
                    } 0%, ${
                      ['#764ba2', '#f5576c', '#00f2fe', '#fee140', '#fed6e3', '#fcb69f'][index]
                    } 100%)`}
                    display="flex"
                    alignItems="center"
                    justifyContent="center"
                  >
                    <Text fontSize="3rem" opacity="0.7">🎨</Text>
                  </Box>
                  
                  <Box p={8}>
                    <VStack align="start" spacing={5}>
                      <HStack justify="space-between" w="full">
                        <Heading size="md" color="white" noOfLines={1}>
                          {artwork.title}
                        </Heading>
                        <Badge colorScheme={artwork.status === 'active' ? 'green' : 'red'} fontSize="xs">
                          {artwork.status === 'active' ? 'Active' : 'Ending Soon'}
                        </Badge>
                      </HStack>
                      
                      <Text color="#94a3b8" fontSize="sm">by {artwork.artist}</Text>
                      
                      <Text fontWeight="bold" color="green.400" fontSize="lg">
                        Current Bid: ${artwork.bid}
                      </Text>
                    </VStack>
                  </Box>
                </Box>
              ))}
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* About Section */}
      <Box id="about" py={32}>
        <Container maxW="7xl">
          <VStack spacing={16}>
            <Heading 
              size="3xl" 
              textAlign="center" 
              fontWeight="700"
              background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
              backgroundClip="text"
              color="transparent"
              mb={8}
            >
              About Guess The Worth
            </Heading>
            
            <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={16} alignItems="center">
              <VStack align="start" spacing={8}>
                <Text fontSize="lg" color="#94a3b8" lineHeight="1.8">
                  Guess The Worth revolutionizes art auctions by introducing the thrill of secret threshold bidding. 
                  Unlike traditional auctions where you compete against others, here you're guessing the artist's 
                  true valuation of their work.
                </Text>
                
                <Text fontSize="lg" color="#94a3b8" lineHeight="1.8">
                  Artists set a hidden minimum price they're willing to accept. When your bid meets or exceeds 
                  this secret threshold, you instantly win the artwork - no waiting, no outbidding, just pure 
                  intuition and art appreciation.
                </Text>

                <VStack align="start" spacing={4}>
                  <HStack spacing={3}>
                    <Box w="6px" h="6px" bg="blue.400" borderRadius="full" />
                    <Text color="white" fontWeight="500">Instant wins when you hit the secret threshold</Text>
                  </HStack>
                  <HStack spacing={3}>
                    <Box w="6px" h="6px" bg="blue.400" borderRadius="full" />
                    <Text color="white" fontWeight="500">No bidding wars or auction stress</Text>
                  </HStack>
                  <HStack spacing={3}>
                    <Box w="6px" h="6px" bg="blue.400" borderRadius="full" />
                    <Text color="white" fontWeight="500">Direct support to artists at fair prices</Text>
                  </HStack>
                  <HStack spacing={3}>
                    <Box w="6px" h="6px" bg="blue.400" borderRadius="full" />
                    <Text color="white" fontWeight="500">Discover emerging and established artists</Text>
                  </HStack>
                </VStack>
              </VStack>

              <Box bg="#1e293b" p={12} borderRadius="2xl" border="1px solid" borderColor="rgba(255,255,255,0.1)">
                <VStack spacing={8}>
                  <Text fontSize="4xl" fontWeight="bold" color="#ec4899">🎨</Text>
                  <VStack spacing={6}>
                    <Heading size="lg" color="white" textAlign="center">
                      Built for DTU DevOps Course
                    </Heading>
                    <Text color="#94a3b8" textAlign="center" lineHeight="1.6">
                      This platform demonstrates modern web development practices, 
                      containerization, and deployment strategies as part of our 
                      DevOps learning journey.
                    </Text>
                  </VStack>
                </VStack>
              </Box>
            </SimpleGrid>
          </VStack>
        </Container>
      </Box>

      {/* CTA Section */}
      <Box 
        bg="#1e293b" 
        py={32}
        position="relative"
        _before={{
          content: '""',
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "radial-gradient(circle at 50% 50%, rgba(99, 102, 241, 0.1) 0%, transparent 70%)",
          zIndex: 0
        }}
      >
        <Container maxW="7xl" position="relative" zIndex="1">
          <VStack spacing={12} textAlign="center">
            <VStack spacing={8}>
              <Heading 
                size="2xl" 
                fontWeight="700"
                background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                backgroundClip="text"
                color="transparent"
                textAlign="center"
              >
                Ready to Start Bidding?
              </Heading>
              <Text color="#94a3b8" maxW="500px" fontSize="lg" lineHeight="1.6">
                Join our community of art enthusiasts and discover your next favorite piece. 
                Sign up now and get access to exclusive artworks.
              </Text>
            </VStack>
            <HStack spacing={8} wrap="wrap" justify="center">
              {!isAuthenticated ? (
                <>
                  <Button 
                    size="lg" 
                    background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                    color="white"
                    border="none"
                    px={10} 
                    py={6} 
                    onClick={handleLogin}
                    _hover={{
                      transform: "translateY(-2px) scale(1.05)",
                      boxShadow: "0 10px 25px rgba(99, 102, 241, 0.3)",
                    }}
                    transition="all 0.3s ease"
                  >
                    Create Account
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    borderColor="#334155"
                    color="#94a3b8"
                    bg="transparent"
                    px={10}
                    py={6}
                    onClick={() => navigate('/artworks')}
                    _hover={{
                      bg: "#334155",
                      color: "white"
                    }}
                    transition="all 0.3s ease"
                  >
                    Browse Gallery
                  </Button>
                </>
              ) : (
                <Button 
                  size="lg" 
                  background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                  color="white"
                  border="none"
                  px={10} 
                  py={6} 
                  onClick={() => navigate('/artworks')}
                  _hover={{
                    transform: "translateY(-2px) scale(1.05)",
                    boxShadow: "0 10px 25px rgba(99, 102, 241, 0.3)",
                  }}
                  transition="all 0.3s ease"
                >
                  Browse Artworks
                </Button>
              )}
            </HStack>
          </VStack>
        </Container>
      </Box>

      {/* Footer */}
      <Box bg="#0f172a" py={16} borderTop="1px solid" borderColor="rgba(255,255,255,0.1)">
        <Container maxW="7xl">
          <Text textAlign="center" color="#94a3b8" fontSize="sm">
            © 2024 {config.APP_NAME || 'Guess The Worth'}. Built for DTU DevOps Course. All rights reserved.
          </Text>
        </Container>
      </Box>
    </Box>
  )
}

export default HomePage