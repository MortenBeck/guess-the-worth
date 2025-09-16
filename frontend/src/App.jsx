import { useEffect } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import { Box, Spinner, Center } from '@chakra-ui/react'
import useAuthStore from './store/authStore'
import socketService from './services/socket'
import HomePage from './pages/HomePage'

function App() {
  const { isLoading: auth0Loading, isAuthenticated, user, getAccessTokenSilently } = useAuth0()
  const { setAuth, clearAuth, setLoading, isLoading } = useAuthStore()

  useEffect(() => {
    const handleAuth = async () => {
      setLoading(true)

      if (isAuthenticated && user) {
        try {
          const token = await getAccessTokenSilently()

          setAuth({
            id: user.sub,
            auth0_sub: user.sub,
            email: user.email,
            name: user.name,
            picture: user.picture,
          }, token)

          // Store token in localStorage for API calls
          localStorage.setItem('access_token', token)

          // Connect socket with authentication
          socketService.connect()

        } catch (error) {
          console.error('Error getting token:', error)
          clearAuth()
        }
      } else if (!isAuthenticated) {
        clearAuth()
        localStorage.removeItem('access_token')
        socketService.disconnect()
      }

      setLoading(false)
    }

    if (!auth0Loading) {
      handleAuth()
    }
  }, [isAuthenticated, user, auth0Loading, getAccessTokenSilently, setAuth, clearAuth, setLoading])

  if (auth0Loading || isLoading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" color="blue.500" />
      </Center>
    )
  }

  return (
    <Box minH="100vh" bg="gray.50">
      <HomePage />
    </Box>
  )
}

export default App
