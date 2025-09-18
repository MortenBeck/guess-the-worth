import {
  Box,
  Container,
  Heading,
  Button,
  HStack,
  Avatar,
  Badge,
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

  const getVisibleNavItems = () => {
    if (!isAuthenticated || !user?.role) return []
    return navigationItems.filter(item => item.roles.includes(user.role))
  }

  return (
    <Box bg="bg" shadow="sm" borderBottom="1px" borderColor="gray.200" position="sticky" top={0} zIndex={1000}>
      <Container maxW="container.xl" py={4}>
        <HStack justify="space-between">
          <Heading 
            size="lg" 
            color="primary" 
            cursor="pointer" 
            onClick={() => navigate('/')}
          >
            {config.APP_NAME}
          </Heading>

          {isAuthenticated ? (
            <HStack spacing={4}>
              <HStack spacing={2} display={{ base: 'none', md: 'flex' }}>
                {getVisibleNavItems().map((item) => (
                  <Button
                    key={item.path}
                    variant={location.pathname === item.path ? 'solid' : 'ghost'}
                    colorScheme={location.pathname === item.path ? 'primary' : 'gray'}
                    size="sm"
                    onClick={() => navigate(item.path)}
                  >
                    {item.label}
                  </Button>
                ))}
              </HStack>

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
              colorScheme="primary"
              onClick={handleLogin}
            >
              Login
            </Button>
          )}
        </HStack>
      </Container>
    </Box>
  )
}

export default Header