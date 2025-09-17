import { useState } from 'react'
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
} from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'
import placeholderImg from '../assets/placeholder.jpg'

const ArtworksPage = () => {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('newest')
  const [filterCategory, setFilterCategory] = useState('all')

  // Mock artworks data - replace with actual API call
  const artworks = [
    {
      id: 1,
      title: "Sunset Dreams",
      artist: "John Doe",
      image: placeholderImg,
      currentBid: 150,
      minimumBid: 160,
      totalBids: 12,
      timeLeft: "2 days 14 hours",
      status: "active",
      category: "Painting"
    },
    {
      id: 2,
      title: "Ocean Waves",
      artist: "Jane Smith",
      image: placeholderImg,
      currentBid: 300,
      minimumBid: 310,
      totalBids: 8,
      timeLeft: "5 hours",
      status: "ending_soon",
      category: "Painting"
    },
    {
      id: 3,
      title: "Mountain Peak",
      artist: "Bob Wilson",
      image: placeholderImg,
      currentBid: 450,
      minimumBid: 460,
      totalBids: 23,
      timeLeft: "1 day 3 hours",
      status: "active",
      category: "Photography"
    },
    {
      id: 4,
      title: "City Lights",
      artist: "Alice Brown",
      image: placeholderImg,
      currentBid: 320,
      minimumBid: 330,
      totalBids: 15,
      timeLeft: "3 days 8 hours",
      status: "active",
      category: "Digital Art"
    },
    {
      id: 5,
      title: "Forest Path",
      artist: "Mike Johnson",
      image: placeholderImg,
      currentBid: 200,
      minimumBid: 210,
      totalBids: 5,
      timeLeft: "6 days 12 hours",
      status: "active",
      category: "Painting"
    },
    {
      id: 6,
      title: "Abstract Thoughts",
      artist: "Sarah Lee",
      image: placeholderImg,
      currentBid: 180,
      minimumBid: 190,
      totalBids: 9,
      timeLeft: "12 hours",
      status: "ending_soon",
      category: "Abstract"
    }
  ]

  const filteredArtworks = artworks
    .filter(artwork => {
      const matchesSearch = artwork.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           artwork.artist.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesCategory = filterCategory === 'all' || artwork.category === filterCategory
      return matchesSearch && matchesCategory
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'price_low':
          return a.currentBid - b.currentBid
        case 'price_high':
          return b.currentBid - a.currentBid
        case 'ending_soon':
          // This would need proper time parsing in a real app
          return a.status === 'ending_soon' ? -1 : 1
        case 'most_bids':
          return b.totalBids - a.totalBids
        default: // newest
          return b.id - a.id
      }
    })

  const categories = ['all', 'Painting', 'Photography', 'Digital Art', 'Abstract', 'Sculpture']

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="xl" color="text" mb={2}>
            Artwork Gallery
          </Heading>
          <Text color="gray.600">
            Discover and bid on unique artworks from talented artists around the world.
          </Text>
        </Box>

        {/* Search and Filters */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <Box display="flex" flexDirection={{ base: 'column', md: 'row' }} gap={4}>
            <Box flex={2}>
              <input
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                placeholder="🔍 Search artworks or artists..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </Box>
            
            <Box maxW={{ base: "full", md: "200px" }}>
              <select
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none',
                  backgroundColor: 'white'
                }}
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category === 'all' ? 'All Categories' : category}
                  </option>
                ))}
              </select>
            </Box>
            
            <Box maxW={{ base: "full", md: "200px" }}>
              <select
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none',
                  backgroundColor: 'white'
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
        <Text color="gray.600">
          Showing {filteredArtworks.length} artwork{filteredArtworks.length !== 1 ? 's' : ''}
        </Text>

        {/* Artwork Grid */}
        <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)", lg: "repeat(3, 1fr)", xl: "repeat(4, 1fr)" }} gap={6}>
          {filteredArtworks.map((artwork) => (
            <Box 
              key={artwork.id} 
              bg="white"
              borderRadius="lg"
              overflow="hidden"
              boxShadow="sm"
              border="1px"
              borderColor="gray.200"
              cursor="pointer" 
              _hover={{ transform: 'translateY(-2px)', shadow: 'lg' }}
              transition="all 0.2s"
              onClick={() => navigate(`/artwork/${artwork.id}`)}
            >
              <Image
                src={artwork.image}
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
                      colorScheme={artwork.status === 'ending_soon' ? 'red' : 'green'}
                      variant="subtle"
                    >
                      {artwork.status === 'ending_soon' ? 'Ending Soon' : 'Active'}
                    </Badge>
                    <Badge variant="outline" colorScheme="gray">
                      {artwork.category}
                    </Badge>
                  </HStack>
                  
                  <Box w="full">
                    <Heading size="sm" color="text" mb={1}>
                      {artwork.title}
                    </Heading>
                    <Text color="gray.600" fontSize="sm">
                      by {artwork.artist}
                    </Text>
                  </Box>
                  
                  <VStack align="start" spacing={1} w="full">
                    <HStack justify="space-between" w="full">
                      <Text fontSize="sm" color="gray.600">Current Bid</Text>
                      <Text fontSize="sm" fontWeight="bold" color="primary">
                        ${artwork.currentBid}
                      </Text>
                    </HStack>
                    <HStack justify="space-between" w="full">
                      <Text fontSize="xs" color="gray.500">
                        {artwork.totalBids} bid{artwork.totalBids !== 1 ? 's' : ''}
                      </Text>
                      <Text fontSize="xs" color="gray.500">
                        {artwork.timeLeft} left
                      </Text>
                    </HStack>
                  </VStack>
                  
                  <Button 
                    colorScheme="primary" 
                    size="sm" 
                    w="full"
                    onClick={(e) => {
                      e.stopPropagation()
                      navigate(`/artwork/${artwork.id}`)
                    }}
                  >
                    Place Bid (Min: ${artwork.minimumBid})
                  </Button>
                </VStack>
              </Box>
            </Box>
          ))}
        </Box>

        {filteredArtworks.length === 0 && (
          <Box bg="white" p={12} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" textAlign="center">
            <Text color="gray.500" fontSize="lg">
              No artworks found matching your criteria.
            </Text>
            <Button 
              mt={4} 
              variant="outline" 
              onClick={() => {
                setSearchTerm('')
                setFilterCategory('all')
                setSortBy('newest')
              }}
            >
              Clear Filters
            </Button>
          </Box>
        )}
      </VStack>
    </Container>
  )
}

export default ArtworksPage