import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ChakraProvider } from '@chakra-ui/react'
import Header from '../Header'

// Mock Auth0
const mockLoginWithRedirect = vi.fn()
const mockLogout = vi.fn()

vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    loginWithRedirect: mockLoginWithRedirect,
    logout: mockLogout,
    isAuthenticated: false,
    user: null
  })
}))

const renderHeader = (authProps = {}) => {
  // Override mock if needed
  if (Object.keys(authProps).length > 0) {
    vi.mocked(require('@auth0/auth0-react').useAuth0).mockReturnValue({
      loginWithRedirect: mockLoginWithRedirect,
      logout: mockLogout,
      isAuthenticated: authProps.isAuthenticated || false,
      user: authProps.user || null
    })
  }

  return render(
    <ChakraProvider>
      <BrowserRouter>
        <Header />
      </BrowserRouter>
    </ChakraProvider>
  )
}

describe('Header Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('when user is not authenticated', () => {
    it('renders the logo', () => {
      renderHeader()
      expect(screen.getByText('Guess The Worth')).toBeInTheDocument()
    })

    it('displays public navigation items', () => {
      renderHeader()
      expect(screen.getByText('How It Works')).toBeInTheDocument()
      expect(screen.getByText('Artworks')).toBeInTheDocument()
      expect(screen.getByText('About')).toBeInTheDocument()
    })

    it('displays login button', () => {
      renderHeader()
      expect(screen.getByText('Login')).toBeInTheDocument()
    })

    it('calls loginWithRedirect when login button is clicked', () => {
      renderHeader()
      const loginButton = screen.getByText('Login')
      fireEvent.click(loginButton)
      expect(mockLoginWithRedirect).toHaveBeenCalledTimes(1)
    })

    it('does not display dashboard navigation items', () => {
      renderHeader()
      expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
      expect(screen.queryByText('Sell Artwork')).not.toBeInTheDocument()
    })
  })

  describe('when user is authenticated', () => {
    const mockUser = {
      name: 'John Doe',
      email: 'john@example.com'
    }

    beforeEach(() => {
      vi.mocked(require('@auth0/auth0-react').useAuth0).mockReturnValue({
        loginWithRedirect: mockLoginWithRedirect,
        logout: mockLogout,
        isAuthenticated: true,
        user: mockUser
      })
    })

    it('displays user greeting', () => {
      renderHeader({ isAuthenticated: true, user: mockUser })
      expect(screen.getByText(/Hello John Doe/i)).toBeInTheDocument()
    })

    it('displays authenticated navigation items', () => {
      renderHeader({ isAuthenticated: true, user: mockUser })
      expect(screen.getByText('Home')).toBeInTheDocument()
      expect(screen.getByText('Dashboard')).toBeInTheDocument()
      expect(screen.getByText('Sell Artwork')).toBeInTheDocument()
    })

    it('does not display login button', () => {
      renderHeader({ isAuthenticated: true, user: mockUser })
      expect(screen.queryByText('Login')).not.toBeInTheDocument()
    })

    it('opens dropdown menu when user name is clicked', () => {
      renderHeader({ isAuthenticated: true, user: mockUser })
      const userButton = screen.getByText(/Hello John Doe/i)
      fireEvent.click(userButton)

      expect(screen.getByText('👤 Profile Settings')).toBeInTheDocument()
      expect(screen.getByText('⭐ Favourites')).toBeInTheDocument()
      expect(screen.getByText('Logout')).toBeInTheDocument()
    })

    it('calls logout when logout is clicked', () => {
      renderHeader({ isAuthenticated: true, user: mockUser })

      // Open dropdown
      const userButton = screen.getByText(/Hello John Doe/i)
      fireEvent.click(userButton)

      // Click logout
      const logoutButton = screen.getByText('Logout')
      fireEvent.click(logoutButton)

      expect(mockLogout).toHaveBeenCalledWith({
        logoutParams: { returnTo: window.location.origin }
      })
    })
  })
})
