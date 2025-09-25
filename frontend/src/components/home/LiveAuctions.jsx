import { Box, Container, Heading, Text, VStack, SimpleGrid, Badge, HStack } from '@chakra-ui/react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { artworkService } from '../../services/api'

const LiveAuctions = () => {
  const navigate = useNavigate()

  const { data: artworks, isLoading } = useQuery({
    queryKey: ['featured-artworks'],
    queryFn: () => artworkService.getFeatured(),
    staleTime: 30000,
  })

  const artworkData = artworks?.data || []

  const mockArtworks = [
    { id: 1, title: "Midnight Dreams", artist: "Sarah Chen", current_bid: 245, status: "active", time_left: "2h 15m" },
    { id: 2, title: "Abstract Emotions", artist: "Michael Torres", current_bid: 180, status: "ending", time_left: "15m" },
    { id: 3, title: "Ocean Waves", artist: "Emma Rodriguez", current_bid: 320, status: "active", time_left: "4h 32m" },
    { id: 4, title: "Golden Hour", artist: "David Kim", current_bid: 150, status: "active", time_left: "1h 45m" },
  ]

  const displayArtworks = artworkData.length > 0 ? artworkData.slice(0, 4) : mockArtworks

  return (
    <Box py={12}>
      <Container maxW="7xl">
        <VStack spacing={8}>
          <VStack spacing={4}>
            <HStack spacing={3}>
              <Box w="8px" h="8px" bg="green.400" borderRadius="full" />
              <Heading 
                size="xl" 
                color="white"
                fontWeight="700"
              >
                Live Auctions
              </Heading>
            </HStack>
            <Text color="#94a3b8" textAlign="center">
              Active bidding happening now
            </Text>
          </VStack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacingX={12} w="full">
            {displayArtworks.map((artwork, index) => (
              <Box mx={3}
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
                  boxShadow: "0 8px 25px rgba(0,0,0,0.3)"
                }}
                transition="all 0.3s ease"
              >
                <Box
                  h="120px"
                  bg={`linear-gradient(45deg, ${
                    ['#667eea', '#f093fb', '#4facfe', '#fa709a'][index % 4]
                  } 0%, ${
                    ['#764ba2', '#f5576c', '#00f2fe', '#fee140'][index % 4]
                  } 100%)`}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Text fontSize="2rem" opacity="0.7">🎨</Text>
                </Box>
                
                <Box p={4}>
                  <VStack align="start" spacing={3}>
                    <HStack justify="space-between" w="full">
                      <Heading size="sm" color="white" noOfLines={1}>
                        {artwork.title}
                      </Heading>
                      <Badge colorScheme={artwork.status === 'active' ? 'green' : 'red'} fontSize="xs">
                        {artwork.status === 'active' ? 'Live' : 'Ending'}
                      </Badge>
                    </HStack>
                    
                    <Text color="#94a3b8" fontSize="xs">
                      by {artwork.artist || 'Unknown Artist'}
                    </Text>
                    
                    <HStack justify="space-between" w="full">
                      <Text fontWeight="bold" color="green.400" fontSize="sm">
                        ${artwork.current_bid || artwork.current_highest_bid || 0}
                      </Text>
                      <Text color="#94a3b8" fontSize="xs">
                        {artwork.time_left || '1h 30m'}
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
  )
}

export default LiveAuctions