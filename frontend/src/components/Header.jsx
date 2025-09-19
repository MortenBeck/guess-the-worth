import { Box, Button, HStack, Text } from '@chakra-ui/react'
import { useAuth0 } from '@auth0/auth0-react'
import { useNavigate } from 'react-router-dom'

const Header = () => {
  const { loginWithRedirect, logout, isAuthenticated, user } = useAuth0()
  const navigate = useNavigate()

  return (
    <Box bg="#1e293b" color="white" p={4}>
      <HStack justify="space-between">
        <Text 
          fontSize="xl" 
          fontWeight="bold"
          cursor="pointer" 
          onClick={() => navigate('/')}
        >
          Guess The Worth
        </Text>
        
        <HStack spacing={4}>
          <Text cursor="pointer" onClick={() => navigate('/artworks')}>Artworks</Text>
          {isAuthenticated && (
            <Text cursor="pointer" onClick={() => navigate('/dashboard')}>Dashboard</Text>
          )}
        </HStack>

        {isAuthenticated ? (
          <HStack>
            <Text fontSize="sm">Hello {user?.name}</Text>
            <Button 
              size="sm" 
              onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
            >
              Logout
            </Button>
          </HStack>
        ) : (
          <Button onClick={() => loginWithRedirect()}>Login</Button>
        )}
      </HStack>
    </Box>
  )
}

export default Header