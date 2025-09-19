import { Box, VStack } from '@chakra-ui/react'
import WelcomeHero from '../components/home/WelcomeHero'
import LiveAuctions from '../components/home/LiveAuctions'
import ActivityFeed from '../components/home/ActivityFeed'

const DashboardHome = () => {
  return (
    <Box bg="#0f172a" color="white" minH="100vh">
      <VStack spacing={0} align="stretch">
        <WelcomeHero />
        <LiveAuctions />
        <ActivityFeed />
      </VStack>
    </Box>
  )
}

export default DashboardHome