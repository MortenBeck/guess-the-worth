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
import { useNavigate } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import placeholderImg from '../assets/placeholder.jpg'

const UserDashboard = () => {
  const { user } = useAuthStore()
  const navigate = useNavigate()

  // Mock data
  const stats = {
    activeBids: 5,
    wonAuctions: 3,
    totalSpent: 1250,
    watchlist: 12
  }

  const activeBids = [
    {
      id: 1,
      title: "Sunset Dreams",
      artist: "John Doe",
      image: placeholderImg,
      yourBid: 175,
      currentHighest: 180,
      status: "outbid",
      timeLeft: "2 days",
      artworkId: 1
    },
    {
      id: 2,
      title: "Ocean Waves",
      artist: "Jane Smith",
      image: placeholderImg,
      yourBid: 300,
      currentHighest: 300,
      status: "winning",
      timeLeft: "5 hours",
      artworkId: 2
    }
  ]

  const wonAuctions = [
    {
      id: 1,
      title: "Mountain Peak",
      artist: "Bob Wilson",
      image: placeholderImg,
      winningBid: 450,
      datePurchased: "2024-01-15",
      status: "delivered",
      artworkId: 3
    }
  ]

  const getBidStatusColor = (status) => {
    return status === 'winning' ? 'green' : 'red'
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="xl" color="text" mb={2}>
            Welcome back, {user?.name}!
          </Heading>
          <Text color="gray.600">
            Track your bids, manage your collection, and discover new artworks.
          </Text>
        </Box>

        {/* Stats Overview */}
        <Box display="grid" gridTemplateColumns={{ base: "repeat(2, 1fr)", md: "repeat(4, 1fr)" }} gap={6}>
          <Box bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" textAlign="center">
            <VStack spacing={1}>
              <Text fontSize="sm" color="gray.600">Active Bids</Text>
              <Text fontSize="2xl" fontWeight="bold" color="primary">{stats.activeBids}</Text>
              <Text fontSize="xs" color="gray.500">Currently bidding</Text>
            </VStack>
          </Box>
          <Box bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" textAlign="center">
            <VStack spacing={1}>
              <Text fontSize="sm" color="gray.600">Won Auctions</Text>
              <Text fontSize="2xl" fontWeight="bold" color="accent">{stats.wonAuctions}</Text>
              <Text fontSize="xs" color="gray.500">Total artworks won</Text>
            </VStack>
          </Box>
          <Box bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" textAlign="center">
            <VStack spacing={1}>
              <Text fontSize="sm" color="gray.600">Total Spent</Text>
              <Text fontSize="2xl" fontWeight="bold" color="primary">${stats.totalSpent}</Text>
              <Text fontSize="xs" color="gray.500">On artwork purchases</Text>
            </VStack>
          </Box>
          <Box bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200" textAlign="center">
            <VStack spacing={1}>
              <Text fontSize="sm" color="gray.600">Watchlist</Text>
              <Text fontSize="2xl" fontWeight="bold" color="accent">{stats.watchlist}</Text>
              <Text fontSize="xs" color="gray.500">Items watching</Text>
            </VStack>
          </Box>
        </Box>

        {/* Active Bids */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" color="text" mb={4}>Active Bids</Heading>
          <VStack spacing={4} align="stretch">
            {activeBids.map((bid) => (
              <Box key={bid.id} bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
                <HStack spacing={4}>
                  <Image
                    src={bid.image}
                    alt={bid.title}
                    w="80px"
                    h="80px"
                    objectFit="cover"
                    borderRadius="md"
                  />
                  <VStack align="start" flex={1} spacing={1}>
                    <Heading size="md" color="text">{bid.title}</Heading>
                    <Text color="gray.600">by {bid.artist}</Text>
                    <HStack>
                      <Text fontSize="sm">Your bid: </Text>
                      <Text fontSize="sm" fontWeight="bold" color="primary">${bid.yourBid}</Text>
                    </HStack>
                    <HStack>
                      <Text fontSize="sm">Current highest: </Text>
                      <Text fontSize="sm" fontWeight="bold">${bid.currentHighest}</Text>
                    </HStack>
                  </VStack>
                  <VStack align="center" spacing={2}>
                    <Badge colorScheme={getBidStatusColor(bid.status)}>
                      {bid.status === 'winning' ? 'Winning' : 'Outbid'}
                    </Badge>
                    <Text fontSize="sm" color="gray.600">{bid.timeLeft} left</Text>
                    <Button
                      size="sm"
                      colorScheme="primary"
                      onClick={() => navigate(`/artwork/${bid.artworkId}`)}
                    >
                      View Artwork
                    </Button>
                  </VStack>
                </HStack>
              </Box>
            ))}
          </VStack>
        </Box>

        {/* Won Auctions */}
        <Box bg="white" p={6} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
          <Heading size="md" color="text" mb={4}>Won Auctions</Heading>
          <VStack spacing={4} align="stretch">
            {wonAuctions.map((auction) => (
              <Box key={auction.id} bg="white" p={4} borderRadius="lg" boxShadow="sm" border="1px" borderColor="gray.200">
                <HStack spacing={4}>
                  <Image
                    src={auction.image}
                    alt={auction.title}
                    w="80px"
                    h="80px"
                    objectFit="cover"
                    borderRadius="md"
                  />
                  <VStack align="start" flex={1} spacing={1}>
                    <Heading size="md" color="text">{auction.title}</Heading>
                    <Text color="gray.600">by {auction.artist}</Text>
                    <HStack>
                      <Text fontSize="sm">Winning bid: </Text>
                      <Text fontSize="sm" fontWeight="bold" color="primary">${auction.winningBid}</Text>
                    </HStack>
                    <Text fontSize="sm" color="gray.600">
                      Purchased on {new Date(auction.datePurchased).toLocaleDateString()}
                    </Text>
                  </VStack>
                  <VStack align="center" spacing={2}>
                    <Badge colorScheme={auction.status === 'delivered' ? 'green' : 'yellow'}>
                      {auction.status}
                    </Badge>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => navigate(`/artwork/${auction.artworkId}`)}
                    >
                      View Details
                    </Button>
                  </VStack>
                </HStack>
              </Box>
            ))}
          </VStack>
        </Box>
      </VStack>
    </Container>
  )
}

export default UserDashboard