import { useEffect } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Box, Spinner, Center } from '@chakra-ui/react'
import useAuthStore from './store/authStore'
import socketService from './services/socket'
import Header from './components/Header'
import NotificationSystem from './components/NotificationSystem'
import HomePage from './pages/HomePage'
import Home from './pages/Home'
import ArtworksPage from './pages/ArtworksPage'
import ArtworkPage from './pages/ArtworkPage'
import UserDashboard from './pages/UserDashboard'
import SellerDashboard from './pages/SellerDashboard'
import AdminDashboard from './pages/AdminDashboard'
import ProfilePage from './pages/ProfilePage'
import FavouritesPage from './pages/FavouritesPage'
import HelpPage from './pages/HelpPage'

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

          localStorage.setItem('access_token', token)
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
        <Spinner size="xl" color="primary" />
      </Center>
    )
  }

  return (
    <BrowserRouter>
      <Box minH="100vh">
        <Header />
        <NotificationSystem />
        <Routes>
          <Route path="/" element={isAuthenticated ? <Home /> : <HomePage />} />
          <Route path="/home" element={<Home />} />
          <Route path="/artworks" element={<ArtworksPage />} />
          <Route path="/artwork/:id" element={<ArtworkPage />} />
          <Route path="/dashboard" element={<UserDashboard />} />
          <Route path="/seller-dashboard" element={<SellerDashboard />} />
          <Route path="/admin-dashboard" element={<AdminDashboard />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/favourites" element={<FavouritesPage />} />
          <Route path="/help" element={<HelpPage />} />
        </Routes>
      </Box>
    </BrowserRouter>
  )
}

export default App
