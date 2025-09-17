import { useState } from 'react'
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
// Simple custom icon
const AddIcon = () => <span>➕</span>
import useAuthStore from '../store/authStore'
import placeholderImg from '../assets/placeholder.jpg'

const SellerDashboard = () => {
  const { user } = useAuthStore()
  const [showAddForm, setShowAddForm] = useState(false)
  const [newArtwork, setNewArtwork] = useState({
    title: '',
    description: '',
    secretThreshold: '',
    category: '',
    medium: '',
    dimensions: '',
    yearCreated: ''
  })

  // Mock data - replace with actual API calls
  const stats = {
    totalArtworks: 15,
    activeAuctions: 8,
    soldArtworks: 7,
    totalEarnings: 3250
  }

  const artworks = [
    {
      id: 1,
      title: "Sunset Dreams",
      image: placeholderImg,
      secretThreshold: 200,
      currentBid: 175,
      totalBids: 12,
      timeLeft: "2 days",
      status: "active"
    },
    {
      id: 2,
      title: "Ocean Waves",
      image: placeholderImg,
      secretThreshold: 350,
      currentBid: 300,
      totalBids: 8,
      timeLeft: "5 hours",
      status: "active"
    },
    {
      id: 3,
      title: "Mountain Peak",
      image: placeholderImg,
      secretThreshold: 400,
      currentBid: 450,
      totalBids: 23,
      dateSold: "2024-01-15",
      status: "sold"
    }
  ]

  const handleSubmitArtwork = () => {
    // Handle artwork submission
    console.log('Submitting artwork:', newArtwork)
    setShowAddForm(false)
    setNewArtwork({
      title: '',
      description: '',
      secretThreshold: '',
      category: '',
      medium: '',
      dimensions: '',
      yearCreated: ''
    })
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'green'
      case 'sold': return 'blue'
      case 'ended': return 'gray'
      default: return 'gray'
    }
  }

  const isThresholdMet = (currentBid, threshold) => currentBid >= threshold

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <HStack justify="space-between">
          <Box>
            <Heading size="xl" color="text" mb={2}>
              Seller Dashboard
            </Heading>
            <Text color="gray.600">
              Manage your artworks, track sales, and grow your business.
            </Text>
          </Box>
          <Button leftIcon={<AddIcon />} colorScheme="primary" onClick={() => setShowAddForm(true)}>
            Add New Artwork
          </Button>
        </HStack>

        {/* Stats Overview */}
        <Box display="grid" gridTemplateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }} gap={6}>
          <Box bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" textAlign="center">
            <Text fontSize="sm" color="gray.600">Total Artworks</Text>
            <Text fontSize="2xl" fontWeight="bold" color="primary">{stats.totalArtworks}</Text>
            <Text fontSize="xs" color="gray.500">All time uploads</Text>
          </Box>
          <Box bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" textAlign="center">
            <Text fontSize="sm" color="gray.600">Active Auctions</Text>
            <Text fontSize="2xl" fontWeight="bold" color="accent">{stats.activeAuctions}</Text>
            <Text fontSize="xs" color="gray.500">Currently live</Text>
          </Box>
          <Box bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" textAlign="center">
            <Text fontSize="sm" color="gray.600">Sold Artworks</Text>
            <Text fontSize="2xl" fontWeight="bold" color="primary">{stats.soldArtworks}</Text>
            <Text fontSize="xs" color="gray.500">Successfully sold</Text>
          </Box>
          <Box bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" textAlign="center">
            <Text fontSize="sm" color="gray.600">Total Earnings</Text>
            <Text fontSize="2xl" fontWeight="bold" color="accent">${stats.totalEarnings}</Text>
            <Text fontSize="xs" color="gray.500">From sales</Text>
          </Box>
        </Box>

        {/* My Artworks */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" color="text" mb={4}>My Artworks</Heading>
          <VStack spacing={4} align="stretch">
            {artworks.map((artwork) => (
              <Box key={artwork.id} bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
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
                    <Heading size="md" color="text">{artwork.title}</Heading>
                    <HStack>
                      <Text fontSize="sm">Secret threshold: </Text>
                      <Text fontSize="sm" fontWeight="bold" color="primary">
                        ${artwork.secretThreshold}
                      </Text>
                    </HStack>
                    {artwork.status === 'active' && (
                      <>
                        <HStack>
                          <Text fontSize="sm">Current bid: </Text>
                          <Text 
                            fontSize="sm" 
                            fontWeight="bold" 
                            color={isThresholdMet(artwork.currentBid, artwork.secretThreshold) ? "green.500" : "gray.600"}
                          >
                            ${artwork.currentBid}
                          </Text>
                          {isThresholdMet(artwork.currentBid, artwork.secretThreshold) && (
                            <Badge colorScheme="green" size="sm">Threshold Met!</Badge>
                          )}
                        </HStack>
                        <Text fontSize="sm" color="gray.600">
                          {artwork.totalBids} bids • {artwork.timeLeft} left
                        </Text>
                      </>
                    )}
                    {artwork.status === 'sold' && (
                      <Text fontSize="sm" color="gray.600">
                        Sold on {new Date(artwork.dateSold).toLocaleDateString()} for ${artwork.currentBid}
                      </Text>
                    )}
                  </VStack>
                  <VStack align="center" spacing={2}>
                    <Badge colorScheme={getStatusColor(artwork.status)}>
                      {artwork.status}
                    </Badge>
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
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" color="text" mb={4}>Active Auctions</Heading>
          <VStack spacing={4} align="stretch">
            {artworks.filter(a => a.status === 'active').map((artwork) => (
              <Box key={artwork.id} bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
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
                    <Heading size="md" color="text">{artwork.title}</Heading>
                    <HStack>
                      <Text fontSize="sm">Current: ${artwork.currentBid}</Text>
                      <Text fontSize="sm">•</Text>
                      <Text fontSize="sm">Target: ${artwork.secretThreshold}</Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      {artwork.totalBids} bids • {artwork.timeLeft} left
                    </Text>
                  </VStack>
                  <VStack align="center" spacing={2}>
                    <Text fontSize="lg" fontWeight="bold" color={isThresholdMet(artwork.currentBid, artwork.secretThreshold) ? "green.500" : "orange.500"}>
                      {Math.round((artwork.currentBid / artwork.secretThreshold) * 100)}%
                    </Text>
                    <Text fontSize="xs" color="gray.500">to threshold</Text>
                  </VStack>
                </HStack>
              </Box>
            ))}
          </VStack>
        </Box>

        {/* Sales History */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" color="text" mb={4}>Sales History</Heading>
          <VStack spacing={3}>
            <HStack justify="space-between" w="full" p={3} bg="gray.50" borderRadius="md">
              <VStack align="start" spacing={0}>
                <Text fontWeight="bold">Mountain Peak</Text>
                <Text fontSize="sm" color="gray.600">Jan 15, 2024</Text>
              </VStack>
              <VStack align="end" spacing={0}>
                <Text fontSize="sm">Threshold: $400</Text>
                <Text fontWeight="bold" color="primary">Sold: $450</Text>
              </VStack>
            </HStack>
            <HStack justify="space-between" w="full" p={3} bg="gray.50" borderRadius="md">
              <VStack align="start" spacing={0}>
                <Text fontWeight="bold">City Lights</Text>
                <Text fontSize="sm" color="gray.600">Jan 10, 2024</Text>
              </VStack>
              <VStack align="end" spacing={0}>
                <Text fontSize="sm">Threshold: $300</Text>
                <Text fontWeight="bold" color="primary">Sold: $320</Text>
              </VStack>
            </HStack>
          </VStack>
        </Box>

        {/* Analytics */}
        <Box display="grid" gridTemplateColumns={{ base: "1fr", md: "repeat(2, 1fr)" }} gap={6}>
          <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
            <Heading size="md" color="text" mb={4}>Performance Metrics</Heading>
            <VStack spacing={4}>
              <HStack justify="space-between" w="full">
                <Text>Average sale price</Text>
                <Text fontWeight="bold">$385</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text>Success rate</Text>
                <Text fontWeight="bold">78%</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text>Avg. threshold hit rate</Text>
                <Text fontWeight="bold">65%</Text>
              </HStack>
            </VStack>
          </Box>
          <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
            <Heading size="md" color="text" mb={4}>Recent Activity</Heading>
            <VStack spacing={3} align="start">
              <Text fontSize="sm">New bid on "Sunset Dreams" - $175</Text>
              <Text fontSize="sm">Threshold reached for "Ocean Waves"</Text>
              <Text fontSize="sm">"Mountain Peak" sold for $450</Text>
            </VStack>
          </Box>
        </Box>
      </VStack>

      {/* Add Artwork Form */}
      {showAddForm && (
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" mt={8}>
          <HStack justify="space-between" mb={4}>
            <Heading size="md">Add New Artwork</Heading>
            <Button size="sm" onClick={() => setShowAddForm(false)}>✕</Button>
          </HStack>
          <VStack spacing={4}>
            <Box w="full">
              <Text fontWeight="bold" mb={2}>Title</Text>
              <input
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                value={newArtwork.title}
                onChange={(e) => setNewArtwork({...newArtwork, title: e.target.value})}
                placeholder="Enter artwork title"
              />
            </Box>
            <Box w="full">
              <Text fontWeight="bold" mb={2}>Description</Text>
              <textarea
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none',
                  minHeight: '100px',
                  fontFamily: 'inherit'
                }}
                value={newArtwork.description}
                onChange={(e) => setNewArtwork({...newArtwork, description: e.target.value})}
                placeholder="Describe your artwork"
              />
            </Box>
            <Box w="full">
              <Text fontWeight="bold" mb={2}>Secret Threshold ($)</Text>
              <input
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  fontSize: '14px',
                  outline: 'none'
                }}
                type="number"
                value={newArtwork.secretThreshold}
                onChange={(e) => setNewArtwork({...newArtwork, secretThreshold: e.target.value})}
                placeholder="Set your secret threshold"
              />
            </Box>
            <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={4} w="full">
              <Box>
                <Text fontWeight="bold" mb={2}>Category</Text>
                <input
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                  value={newArtwork.category}
                  onChange={(e) => setNewArtwork({...newArtwork, category: e.target.value})}
                  placeholder="e.g., Painting"
                />
              </Box>
              <Box>
                <Text fontWeight="bold" mb={2}>Medium</Text>
                <input
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                  value={newArtwork.medium}
                  onChange={(e) => setNewArtwork({...newArtwork, medium: e.target.value})}
                  placeholder="e.g., Oil on Canvas"
                />
              </Box>
            </Box>
            <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={4} w="full">
              <Box>
                <Text fontWeight="bold" mb={2}>Dimensions</Text>
                <input
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                  value={newArtwork.dimensions}
                  onChange={(e) => setNewArtwork({...newArtwork, dimensions: e.target.value})}
                  placeholder="e.g., 24 x 36 inches"
                />
              </Box>
              <Box>
                <Text fontWeight="bold" mb={2}>Year Created</Text>
                <input
                  style={{
                    width: '100%',
                    padding: '8px 12px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    fontSize: '14px',
                    outline: 'none'
                  }}
                  type="number"
                  value={newArtwork.yearCreated}
                  onChange={(e) => setNewArtwork({...newArtwork, yearCreated: e.target.value})}
                  placeholder="2024"
                />
              </Box>
            </Box>
            <HStack spacing={3} w="full" justify="end">
              <Button variant="outline" onClick={() => setShowAddForm(false)}>
                Cancel
              </Button>
              <Button colorScheme="primary" onClick={handleSubmitArtwork}>
                Add Artwork
              </Button>
            </HStack>
          </VStack>
        </Box>
      )}
    </Container>
  )
}

export default SellerDashboard