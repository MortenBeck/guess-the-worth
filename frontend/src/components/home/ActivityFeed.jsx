import { Box, Container, Heading, Text, VStack, HStack, Avatar } from '@chakra-ui/react'
import useAuthStore from '../../store/authStore'

const ActivityFeed = () => {
  const { user } = useAuthStore()

  const mockActivities = [
    {
      id: 1,
      type: 'bid_placed',
      message: 'Alex_B placed a bid of $245 on "Midnight Dreams"',
      timestamp: '2 minutes ago',
      icon: '💰'
    },
    {
      id: 2,
      type: 'auction_won',
      message: 'Sarah_K won "Abstract Emotions" for $180',
      timestamp: '1 hour ago',
      icon: '🎉'
    },
    {
      id: 3,
      type: 'new_artwork',
      message: 'New artwork "Ocean Waves" by Emma Rodriguez is now live',
      timestamp: '3 hours ago',
      icon: '🎨'
    },
    {
      id: 4,
      type: 'bid_placed',
      message: 'Mike_T placed a bid of $320 on "Golden Hour"',
      timestamp: '5 hours ago',
      icon: '💰'
    },
    {
      id: 5,
      type: 'new_artwork',
      message: 'David Kim uploaded "Desert Sunset"',
      timestamp: '1 day ago',
      icon: '🎨'
    }
  ]

  const getActivityColor = (type) => {
    switch (type) {
      case 'auction_won': return 'green.400'
      case 'bid_placed': return 'blue.400'
      case 'bid_outbid': return 'red.400'
      case 'new_artwork': return 'purple.400'
      default: return '#94a3b8'
    }
  }

  return (
    <Box py={12}>
      <Container maxW="7xl">
        <VStack spacing={8}>
          <VStack spacing={4}>
            <Heading 
              size="xl" 
              color="white"
              fontWeight="700"
            >
              Platform Activity
            </Heading>
            <Text color="#94a3b8" textAlign="center">
              See what's happening across all auctions
            </Text>
          </VStack>

          <Box 
            bg="#1e293b" 
            borderRadius="xl" 
            p={6} 
            w="full" 
            maxW="4xl"
            border="1px solid"
            borderColor="rgba(255,255,255,0.1)"
          >
            <VStack spacing={4} align="stretch">
              {mockActivities.map((activity, index) => (
                <Box key={activity.id}>
                  <HStack spacing={4} align="start">
                    <Box
                      w="40px"
                      h="40px"
                      bg="rgba(99, 102, 241, 0.1)"
                      borderRadius="full"
                      display="flex"
                      alignItems="center"
                      justifyContent="center"
                      fontSize="lg"
                      flexShrink={0}
                    >
                      {activity.icon}
                    </Box>
                    
                    <VStack align="start" spacing={1} flex="1">
                      <Text 
                        color="white" 
                        fontSize="sm" 
                        fontWeight="500"
                        lineHeight="1.5"
                      >
                        {activity.message}
                      </Text>
                      <Text 
                        color="#94a3b8" 
                        fontSize="xs"
                      >
                        {activity.timestamp}
                      </Text>
                    </VStack>
                  </HStack>
                  
                  {index < mockActivities.length - 1 && (
                    <Box 
                      w="full" 
                      h="1px" 
                      bg="rgba(255,255,255,0.1)" 
                      mt={4}
                    />
                  )}
                </Box>
              ))}
            </VStack>
          </Box>

          <Text color="#94a3b8" fontSize="sm" textAlign="center">
            View all activity in your dashboard
          </Text>
        </VStack>
      </Container>
    </Box>
  )
}

export default ActivityFeed