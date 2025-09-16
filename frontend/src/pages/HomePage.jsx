import {
  Box,
  Container,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Avatar,
} from '@chakra-ui/react'
import { useAuth0 } from '@auth0/auth0-react'
import useAuthStore from '../store/authStore'
import { config } from '../config/env'

const HomePage = () => {
  const { loginWithRedirect, logout } = useAuth0()
  const { user, isAuthenticated, isAdmin, isSeller, isBuyer } = useAuthStore()

  const handleLogin = () => {
    loginWithRedirect()
  }

  const handleLogout = () => {
    logout({
      logoutParams: {
        returnTo: window.location.origin
      }
    })
  }

  return (
    <Box>
      {/* Header */}
      <Box bg="white" shadow="sm" borderBottom="1px" borderColor="gray.200">
        <Container maxW="container.xl" py={4}>
          <HStack justify="space-between">
            <Heading size="lg" color="blue.600">
              {config.APP_NAME}
            </Heading>

            {isAuthenticated ? (
              <HStack spacing={4}>
                <Avatar
                  size="sm"
                  name={user?.name}
                  src={user?.picture}
                />
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </HStack>
            ) : (
              <Button
                colorScheme="blue"
                onClick={handleLogin}
              >
                Login
              </Button>
            )}
          </HStack>
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxW="container.xl" py={8}>
        {isAuthenticated ? (
          <VStack spacing={6} align="stretch">
            <Box>
              <Heading size="xl" mb={4}>
                Welcome back, {user?.name}!
              </Heading>
              <HStack spacing={2} mb={4}>
                <Text fontSize="lg" color="gray.600">
                  Role:
                </Text>
                <Text
                  fontSize="lg"
                  fontWeight="bold"
                  color={isAdmin() ? "red.500" : isSeller() ? "blue.500" : "green.500"}
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

            {/* Role-specific content */}
            {isAdmin() && (
              <Box p={6} bg="red.50" border="1px" borderColor="red.200" rounded="lg">
                <Heading size="md" color="red.700" mb={2}>
                  Admin Dashboard
                </Heading>
                <Text color="red.600">
                  Manage users, monitor transactions, and oversee platform operations
                </Text>
              </Box>
            )}

            {isSeller() && (
              <Box p={6} bg="blue.50" border="1px" borderColor="blue.200" rounded="lg">
                <Heading size="md" color="blue.700" mb={2}>
                  Seller Dashboard
                </Heading>
                <Text color="blue.600">
                  Upload new artworks, manage your gallery, and track sales
                </Text>
              </Box>
            )}

            {/* Artwork gallery */}
            <Box
              p={8}
              bg="white"
              rounded="lg"
              shadow="sm"
              textAlign="center"
            >
              <Text fontSize="lg" color="gray.500">
                Artwork gallery coming soon...
              </Text>
            </Box>
          </VStack>
        ) : (
          <VStack spacing={8} align="center" py={12}>
            <VStack spacing={4} textAlign="center">
              <Heading size="2xl">
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
                colorScheme="blue"
                onClick={handleLogin}
              >
                Get Started
              </Button>
              <Text fontSize="sm" color="gray.500">
                Sign in with Google, Facebook, or your preferred provider
              </Text>
            </VStack>
          </VStack>
        )}
      </Container>
    </Box>
  )
}

export default HomePage