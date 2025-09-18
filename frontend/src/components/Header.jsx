import {
  Box,
  Container,
  Heading,
  Button,
  HStack,
  Avatar,
  Badge,
  IconButton,
  Text,
} from '@chakra-ui/react'
const BellIcon = () => <span>🔔</span>
import { useAuth0 } from '@auth0/auth0-react'
import { useNavigate, useLocation } from 'react-router-dom'
import useAuthStore from '../store/authStore'
import { config } from '../config/env'

const Header = () => {
  const { loginWithRedirect, logout } = useAuth0()
  const { user, isAuthenticated, isAdmin, isSeller, isBuyer } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

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

  const navigationItems = [
    { label: 'Home', path: '/', roles: ['admin', 'seller', 'buyer'] },
    { label: 'Artworks', path: '/artworks', roles: ['admin', 'seller', 'buyer'] },
    { label: 'My Dashboard', path: '/dashboard', roles: ['buyer'] },
    { label: 'Seller Dashboard', path: '/seller-dashboard', roles: ['seller'] },
    { label: 'Admin Dashboard', path: '/admin-dashboard', roles: ['admin'] },
    { label: 'Profile', path: '/profile', roles: ['admin', 'seller', 'buyer'] },
  ]

  const publicNavItems = [
    { label: 'How It Works', path: '/#how-it-works' },
    { label: 'Artworks', path: '/artworks' },
    { label: 'About', path: '/#about' },
  ]

  const getVisibleNavItems = () => {
    if (!isAuthenticated || !user?.role) return publicNavItems
    return navigationItems.filter(item => item.roles.includes(user.role))
  }

  return (
    <Box bg="white" shadow="sm" borderBottom="1px" borderColor="gray.200" position="sticky" top={0} zIndex={1000}>
      <Container maxW="container.xl" py={4}>
        <HStack w="full">
          {/* Logo - Left */}
          <Box flex="1">
            <Heading 
              size="lg" 
              color="blue.600" 
              cursor="pointer" 
              onClick={() => navigate('/')}
            >
              {config.APP_NAME}
            </Heading>
          </Box>

          {/* Center Navigation */}
          <Box flex="1" display="flex" justifyContent="center">
            <HStack spacing={32}>
              {publicNavItems.map((item) => (
                <Text
                  key={item.path}
                  color="gray.600"
                  cursor="pointer"
                  fontSize="md"
                  fontWeight="500"
                  mx={4}
                  _hover={{ color: "gray.800" }}
                  onClick={() => {
                    if (item.path.startsWith('/#')) {
                      // Handle anchor links
                      const element = document.querySelector(item.path.substring(1));
                      if (element) {
                        element.scrollIntoView({ behavior: 'smooth' });
                      }
                    } else {
                      navigate(item.path);
                    }
                  }}
                >
                  {item.label}
                </Text>
              ))}
            </HStack>
          </Box>

          {/* Right side - Auth buttons or User menu */}
          <Box flex="1" display="flex" justifyContent="flex-end">
          {isAuthenticated ? (
            <HStack spacing={4}>
              <IconButton
                icon={<BellIcon />}
                variant="ghost"
                size="sm"
                aria-label="Notifications"
                position="relative"
              >
                <Badge
                  colorScheme="red"
                  variant="solid"
                  borderRadius="full"
                  position="absolute"
                  top="-1"
                  right="-1"
                  fontSize="xs"
                  minW="5"
                  h="5"
                >
                  3
                </Badge>
              </IconButton>

              <HStack spacing={3}>
                <Avatar
                  size="sm"
                  name={user?.name}
                  src={user?.picture}
                />
                <Box display={{ base: 'none', md: 'block' }}>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate('/profile')}
                  >
                    {user?.name}
                  </Button>
                </Box>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </HStack>
            </HStack>
          ) : (
            <Button
              colorScheme="blue"
              onClick={handleLogin}
            >
              Login
            </Button>
          )}
          </Box>
        </HStack>
      </Container>
    </Box>
  )
}

export default Header