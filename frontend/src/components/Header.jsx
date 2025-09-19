import { Box, Button, HStack, Text, Container } from '@chakra-ui/react'
import { useAuth0 } from '@auth0/auth0-react'
import { useNavigate } from 'react-router-dom'

const Header = () => {
  const { loginWithRedirect, logout, isAuthenticated, user } = useAuth0()
  const navigate = useNavigate()

  const publicNavItems = [
    { label: 'How It Works', path: '#how-it-works' },
    { label: 'Artworks', path: '/artworks' },
    { label: 'About', path: '#about' },
  ]

  const authenticatedNavItems = [
    { label: 'Home', path: '/' },
    { label: 'Artworks', path: '/artworks' },
    { label: 'Dashboard', path: '/dashboard' },
  ]

  const navItems = isAuthenticated ? authenticatedNavItems : publicNavItems

  const handleNavClick = (path) => {
    if (path.startsWith('#')) {
      // Handle anchor links - scroll to section
      const element = document.querySelector(path);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    } else {
      navigate(path);
    }
  }

  return (
    <Box bg="#1e293b" color="white" borderBottom="1px solid" borderColor="rgba(255,255,255,0.1)" position="sticky" top={0} zIndex={1000}>
      <Container maxW="container.xl" py={4}>
        <HStack w="full">
          {/* Logo - Left */}
          <Box flex="1">
            <Text 
              fontSize="xl" 
              fontWeight="bold"
              cursor="pointer" 
              onClick={() => navigate('/')}
              _hover={{ opacity: 0.8 }}
              transition="opacity 0.2s"
            >
              Guess The Worth
            </Text>
          </Box>
          
          {/* Navigation - Center */}
          <Box flex="1" display="flex" justifyContent="center">
            <HStack spacing={8}>
              {navItems.map((item) => (
                <Text 
                  key={item.path}
                  cursor="pointer" 
                  color="#94a3b8"
                  fontSize="md"
                  fontWeight="500"
                  mx={4}
                  _hover={{ 
                    color: "white",
                    transform: "translateY(-1px)"
                  }}
                  transition="all 0.2s"
                  onClick={() => handleNavClick(item.path)}
                >
                  {item.label}
                </Text>
              ))}
            </HStack>
          </Box>

          {/* Auth Section - Right */}
          <Box flex="1" display="flex" justifyContent="flex-end">
            {isAuthenticated ? (
              <HStack spacing={3}>
                <Text fontSize="sm" color="#94a3b8">Hello {user?.name}</Text>
                <Button 
                  size="sm"
                  variant="outline"
                  borderColor="#334155"
                  color="#94a3b8"
                  bg="transparent"
                  onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
                  _hover={{
                    bg: "#334155",
                    color: "white",
                    borderColor: "#334155"
                  }}
                >
                  Logout
                </Button>
              </HStack>
            ) : (
              <Button 
                background="linear-gradient(135deg, #6366f1 0%, #ec4899 100%)"
                color="white"
                onClick={() => loginWithRedirect()}
                _hover={{
                  transform: "translateY(-1px)",
                  boxShadow: "0 4px 15px rgba(99, 102, 241, 0.3)",
                }}
                transition="all 0.2s"
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