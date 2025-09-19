import { Box, Container, Heading, Text, VStack, SimpleGrid, HStack } from '@chakra-ui/react'
import { useQuery } from '@tanstack/react-query'
import { statsService } from '../../services/api'
import useAuthStore from '../../store/authStore'

const QuickStats = () => {
  const { user } = useAuthStore()

  const { data: platformStats } = useQuery({
    queryKey: ['platform-stats'],
    queryFn: () => statsService.getPlatformStats(),
    staleTime: 5 * 60 * 1000,
  })

  const stats = platformStats || {
    totalArtworks: 1247,
    totalBids: 89000,
    totalArtists: 156,
    liveStatus: '24/7'
  }

  const personalStats = [
    { label: 'Your Bids', value: '12', icon: '💰', color: '#6366f1' },
    { label: 'Artworks Won', value: '3', icon: '🏆', color: '#10b981' },
    { label: 'Following', value: '8', icon: '👥', color: '#f59e0b' },
    { label: 'Wishlist', value: '15', icon: '❤️', color: '#ec4899' },
  ]

  const platformStatsData = [
    { label: 'Active Artworks', value: stats.totalArtworks, icon: '🎨', color: '#6366f1' },
    { label: 'Total Bids', value: `$${stats.totalBids}k`, icon: '💎', color: '#10b981' },
    { label: 'Artists', value: stats.totalArtists, icon: '👨‍🎨', color: '#f59e0b' },
    { label: 'Live Bidding', value: stats.liveStatus, icon: '⚡', color: '#ec4899' },
  ]

  return (
    <Box py={12}>
      <Container maxW="7xl">
        <VStack spacing={12}>
          {/* Personal Stats */}
          <VStack spacing={6} w="full">
            <Heading 
              size="xl" 
              color="white"
              fontWeight="700"
              textAlign="center"
            >
              Your Activity
            </Heading>
            
            <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6} w="full">
              {personalStats.map((stat, index) => (
                <Box
                  key={index}
                  bg="#1e293b"
                  p={6}
                  borderRadius="xl"
                  textAlign="center"
                  border="1px solid"
                  borderColor="rgba(255,255,255,0.1)"
                  _hover={{
                    transform: "translateY(-2px)",
                    boxShadow: "0 8px 25px rgba(0,0,0,0.2)"
                  }}
                  transition="all 0.3s ease"
                >
                  <VStack spacing={3}>
                    <Box
                      w="50px"
                      h="50px"
                      bg={`${stat.color}20`}
                      borderRadius="full"
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      fontSize="xl"
                    >
                      {stat.icon}
                    </Box>
                    <Text fontSize="2xl" fontWeight="700" color={stat.color}>
                      {stat.value}
                    </Text>
                    <Text fontSize="sm" color="#94a3b8" textAlign="center">
                      {stat.label}
                    </Text>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </VStack>

          {/* Platform Stats */}
          <VStack spacing={6} w="full">
            <Heading 
              size="xl" 
              color="white"
              fontWeight="700"
              textAlign="center"
            >
              Platform Overview
            </Heading>
            
            <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6} w="full">
              {platformStatsData.map((stat, index) => (
                <Box
                  key={index}
                  bg="#0f172a"
                  p={6}
                  borderRadius="xl"
                  textAlign="center"
                  border="1px solid"
                  borderColor="rgba(255,255,255,0.1)"
                >
                  <VStack spacing={3}>
                    <Text fontSize="xl">
                      {stat.icon}
                    </Text>
                    <Text fontSize="2xl" fontWeight="700" color={stat.color}>
                      {stat.value}
                    </Text>
                    <Text fontSize="sm" color="#94a3b8" textAlign="center">
                      {stat.label}
                    </Text>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </VStack>
        </VStack>
      </Container>
    </Box>
  )
}

export default QuickStats