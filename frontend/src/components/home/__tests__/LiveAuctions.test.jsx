import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ChakraProvider } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import LiveAuctions from '../LiveAuctions'

// Mock the artwork service
vi.mock('../../../services/api', () => ({
  artworkService: {
    getFeatured: vi.fn()
  }
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })

  return ({ children }) => (
    <ChakraProvider>
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </BrowserRouter>
    </ChakraProvider>
  )
}

describe('LiveAuctions Component', () => {
  it('renders the component title', () => {
    render(<LiveAuctions />, { wrapper: createWrapper() })
    expect(screen.getByText('Live Auctions')).toBeInTheDocument()
  })

  it('renders the subtitle', () => {
    render(<LiveAuctions />, { wrapper: createWrapper() })
    expect(screen.getByText('Active bidding happening now')).toBeInTheDocument()
  })

  it('displays mock artworks when no data is returned', async () => {
    const { artworkService } = await import('../../../services/api')
    artworkService.getFeatured.mockResolvedValue({ data: [] })

    render(<LiveAuctions />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Midnight Dreams')).toBeInTheDocument()
      expect(screen.getByText('Abstract Emotions')).toBeInTheDocument()
      expect(screen.getByText('Ocean Waves')).toBeInTheDocument()
      expect(screen.getByText('Golden Hour')).toBeInTheDocument()
    })
  })

  it('displays status badges correctly', async () => {
    const { artworkService } = await import('../../../services/api')
    artworkService.getFeatured.mockResolvedValue({ data: [] })

    render(<LiveAuctions />, { wrapper: createWrapper() })

    await waitFor(() => {
      const liveBadges = screen.getAllByText('Live')
      expect(liveBadges.length).toBeGreaterThan(0)
    })
  })

  it('displays artist names', async () => {
    const { artworkService } = await import('../../../services/api')
    artworkService.getFeatured.mockResolvedValue({ data: [] })

    render(<LiveAuctions />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText(/Sarah Chen/i)).toBeInTheDocument()
      expect(screen.getByText(/Michael Torres/i)).toBeInTheDocument()
    })
  })

  it('displays current bid amounts', async () => {
    const { artworkService } = await import('../../../services/api')
    artworkService.getFeatured.mockResolvedValue({ data: [] })

    render(<LiveAuctions />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('$245')).toBeInTheDocument()
      expect(screen.getByText('$180')).toBeInTheDocument()
      expect(screen.getByText('$320')).toBeInTheDocument()
    })
  })

  it('displays real artwork data when available', async () => {
    const mockArtworks = [
      {
        id: 100,
        title: 'Real Artwork',
        artist: 'Real Artist',
        current_highest_bid: 500,
        status: 'active'
      }
    ]

    const { artworkService } = await import('../../../services/api')
    artworkService.getFeatured.mockResolvedValue({ data: mockArtworks })

    render(<LiveAuctions />, { wrapper: createWrapper() })

    await waitFor(() => {
      expect(screen.getByText('Real Artwork')).toBeInTheDocument()
      expect(screen.getByText(/Real Artist/i)).toBeInTheDocument()
      expect(screen.getByText('$500')).toBeInTheDocument()
    })
  })

  it('limits display to 4 artworks', async () => {
    const mockArtworks = Array.from({ length: 10 }, (_, i) => ({
      id: i + 1,
      title: `Artwork ${i + 1}`,
      artist: `Artist ${i + 1}`,
      current_highest_bid: 100 + i * 50,
      status: 'active'
    }))

    const { artworkService } = await import('../../../services/api')
    artworkService.getFeatured.mockResolvedValue({ data: mockArtworks })

    const { container } = render(<LiveAuctions />, { wrapper: createWrapper() })

    await waitFor(() => {
      // Count the number of artwork cards
      const artworkCards = container.querySelectorAll('[data-testid], .chakra-box')
      // Should display only first 4 artworks
      expect(screen.getByText('Artwork 1')).toBeInTheDocument()
      expect(screen.getByText('Artwork 4')).toBeInTheDocument()
      expect(screen.queryByText('Artwork 5')).not.toBeInTheDocument()
    })
  })
})
