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
import { useParams } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import placeholderImg from '../assets/placeholder.jpg'

const ArtworkPage = () => {
  const { id } = useParams()
  const { user, isAuthenticated } = useAuthStore()
  const [bidAmount, setBidAmount] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Mock artwork data - replace with actual API call
  const artwork = {
    id,
    title: "Sunset Dreams",
    artist: "John Doe",
    description: "A beautiful painting capturing the essence of a perfect sunset over the mountains. This piece represents the artist's journey through different emotional landscapes.",
    image: placeholderImg,
    currentBid: 150,
    minimumBid: 160,
    totalBids: 23,
    timeLeft: "2 days 14 hours",
    status: "active",
    category: "Painting",
    dimensions: "24' x 36'",
    medium: "Oil on Canvas",
    yearCreated: 2023,
    seller: {
      name: "John Doe",
      avatar: placeholderImg,
      rating: 4.8,
      totalSales: 12
    }
  }

  const recentBids = [
    { id: 1, bidder: "Anonymous", amount: 150, timestamp: "2 minutes ago" },
    { id: 2, bidder: "Art Lover", amount: 140, timestamp: "5 minutes ago" },
    { id: 3, bidder: "Anonymous", amount: 130, timestamp: "12 minutes ago" },
  ]

  const handleBidSubmit = async () => {
    if (!bidAmount || bidAmount < artwork.minimumBid) return
    
    setIsSubmitting(true)
    
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false)
      setBidAmount('')
      // Show success notification
    }, 1000)
  }

  return (
    <Container maxW="container.xl" py={8}>
      <Box display="grid" gridTemplateColumns={{ base: "1fr", lg: "1fr 1fr" }} gap={8}>
        {/* Left Column - Artwork Details */}
        <VStack spacing={6} align="stretch">
          <Image
            src={artwork.image}
            alt={artwork.title}
            w="full"
            h="400px"
            objectFit="cover"
            borderRadius="lg"
          />
          
          <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
            <VStack spacing={4} align="stretch">
              <Box>
                <Heading size="lg" color="text" mb={2}>
                  {artwork.title}
                </Heading>
                <Text color="gray.600" fontSize="lg">
                  by {artwork.artist}
                </Text>
              </Box>
              
              <Text color="gray.700">
                {artwork.description}
              </Text>
              
              <Box h="1px" bg="gray.200" />
              
              <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={4}>
                <Box>
                  <Text fontWeight="bold" color="text">Category</Text>
                  <Text color="gray.600">{artwork.category}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="text">Medium</Text>
                  <Text color="gray.600">{artwork.medium}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="text">Dimensions</Text>
                  <Text color="gray.600">{artwork.dimensions}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="text">Year</Text>
                  <Text color="gray.600">{artwork.yearCreated}</Text>
                </Box>
              </Box>
            </VStack>
          </Box>
        </VStack>

        {/* Right Column - Bidding */}
        <VStack spacing={6} align="stretch">
          <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <Heading size="md" color="text">
                  Current Auction
                </Heading>
                <Badge colorScheme={artwork.status === 'ending_soon' ? 'red' : 'green'}>
                  {artwork.status === 'ending_soon' ? 'Ending Soon' : 'Active'}
                </Badge>
              </HStack>
              
              <Box>
                <Text color="gray.600" fontSize="sm">Current Highest Bid</Text>
                <Text fontSize="2xl" fontWeight="bold" color="primary">
                  ${artwork.currentBid}
                </Text>
              </Box>
              
              <Box display="grid" gridTemplateColumns="repeat(2, 1fr)" gap={4}>
                <Box>
                  <Text fontWeight="bold" color="text">Total Bids</Text>
                  <Text color="gray.600">{artwork.totalBids}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="text">Time Left</Text>
                  <Text color="gray.600">{artwork.timeLeft}</Text>
                </Box>
              </Box>
              
              <Box h="1px" bg="gray.200" />
              
              {isAuthenticated ? (
                <VStack spacing={4}>
                  <Box w="full">
                    <Text color="text" mb={2} fontWeight="medium">Your Bid Amount</Text>
                    <input
                      style={{
                        width: '100%',
                        padding: '12px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '6px',
                        fontSize: '16px',
                        outline: 'none'
                      }}
                      type="number"
                      placeholder={`Minimum $${artwork.minimumBid}`}
                      value={bidAmount}
                      onChange={(e) => setBidAmount(e.target.value)}
                      min={artwork.minimumBid}
                    />
                  </Box>
                  
                  <Button
                    colorScheme="primary"
                    size="lg"
                    w="full"
                    onClick={handleBidSubmit}
                    isLoading={isSubmitting}
                    isDisabled={!bidAmount || bidAmount < artwork.minimumBid}
                  >
                    Place Bid
                  </Button>
                  
                  <Text fontSize="sm" color="gray.500" textAlign="center">
                    Minimum bid: ${artwork.minimumBid}
                  </Text>
                </VStack>
              ) : (
                <Box bg="blue.50" border="1px" borderColor="blue.200" borderRadius="md" p={4}>
                  <HStack>
                    <Text mr={2}>ℹ️</Text>
                    <Text color="blue.800">Please log in to place a bid</Text>
                  </HStack>
                </Box>
              )}
            </VStack>
          </Box>
          
          {/* Seller Info */}
          <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
            <VStack spacing={4} align="stretch">
              <Heading size="md" color="text">Seller Information</Heading>
              <HStack spacing={3}>
                <Image
                  src={artwork.seller.avatar}
                  alt={artwork.seller.name}
                  w="40px"
                  h="40px"
                  borderRadius="full"
                />
                <VStack align="start" spacing={1}>
                  <Text fontWeight="bold" color="text">{artwork.seller.name}</Text>
                  <HStack>
                    <Text fontSize="sm" color="gray.600">
                      Rating: {artwork.seller.rating}/5
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      •
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {artwork.seller.totalSales} sales
                    </Text>
                  </HStack>
                </VStack>
              </HStack>
            </VStack>
          </Box>
          
          {/* Recent Bids */}
          <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
            <VStack spacing={4} align="stretch">
              <Heading size="md" color="text">Recent Bids</Heading>
              <VStack spacing={2} align="stretch">
                {recentBids.map((bid) => (
                  <HStack key={bid.id} justify="space-between" p={2} bg="gray.50" borderRadius="md">
                    <VStack align="start" spacing={0}>
                      <Text fontWeight="bold" fontSize="sm">{bid.bidder}</Text>
                      <Text fontSize="xs" color="gray.600">{bid.timestamp}</Text>
                    </VStack>
                    <Text fontWeight="bold" color="primary">${bid.amount}</Text>
                  </HStack>
                ))}
              </VStack>
            </VStack>
          </Box>
        </VStack>
      </Box>
    </Container>
  )
}

export default ArtworkPage