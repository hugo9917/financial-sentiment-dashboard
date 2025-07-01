import { render, screen, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Dashboard from '../pages/Dashboard'

// Mock the API calls
vi.mock('../utils/api', () => ({
  fetchDashboardStats: vi.fn(),
  fetchSentimentSummary: vi.fn(),
  fetchStockPrices: vi.fn(),
  fetchLatestNews: vi.fn()
}))

describe('Dashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard title', () => {
    render(<Dashboard />)
    expect(screen.getByText(/Financial Sentiment Dashboard/i)).toBeInTheDocument()
  })

  it('shows loading state initially', () => {
    render(<Dashboard />)
    expect(screen.getByText(/Loading/i)).toBeInTheDocument()
  })

  it('displays dashboard stats when data is loaded', async () => {
    const mockStats = {
      total_news: 100,
      total_stocks: 5,
      avg_sentiment: 0.25
    }

    const { fetchDashboardStats } = await import('../utils/api')
    fetchDashboardStats.mockResolvedValue(mockStats)

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('100')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    const { fetchDashboardStats } = await import('../utils/api')
    fetchDashboardStats.mockRejectedValue(new Error('API Error'))

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText(/Error loading data/i)).toBeInTheDocument()
    })
  })

  it('displays sentiment summary when available', async () => {
    const mockSentiment = [
      { sentiment_category: 'Positive', count: 50, avg_score: 0.6 },
      { sentiment_category: 'Negative', count: 30, avg_score: -0.4 }
    ]

    const { fetchSentimentSummary } = await import('../utils/api')
    fetchSentimentSummary.mockResolvedValue({ summary: mockSentiment })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('Positive')).toBeInTheDocument()
      expect(screen.getByText('Negative')).toBeInTheDocument()
    })
  })

  it('displays stock prices chart when data is available', async () => {
    const mockPrices = [
      { symbol: 'AAPL', close_price: 150.25, timestamp: '2024-01-15T10:00:00Z' },
      { symbol: 'GOOGL', close_price: 2800.50, timestamp: '2024-01-15T10:00:00Z' }
    ]

    const { fetchStockPrices } = await import('../utils/api')
    fetchStockPrices.mockResolvedValue({ prices: mockPrices })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('AAPL')).toBeInTheDocument()
      expect(screen.getByText('GOOGL')).toBeInTheDocument()
    })
  })

  it('displays latest news when available', async () => {
    const mockNews = [
      { title: 'Apple Reports Strong Q4 Earnings', sentiment_score: 0.8 },
      { title: 'Tech Stocks Rally on Fed Decision', sentiment_score: 0.6 }
    ]

    const { fetchLatestNews } = await import('../utils/api')
    fetchLatestNews.mockResolvedValue({ news: mockNews })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText(/Apple Reports Strong Q4 Earnings/i)).toBeInTheDocument()
      expect(screen.getByText(/Tech Stocks Rally/i)).toBeInTheDocument()
    })
  })
}) 