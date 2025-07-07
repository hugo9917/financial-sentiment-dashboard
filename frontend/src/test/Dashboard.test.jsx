import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Dashboard from '../pages/Dashboard'

// Mock fetch globally
global.fetch = vi.fn()

// Mock Chart.js components
vi.mock('react-chartjs-2', () => ({
  Line: ({ data }) => <div data-testid="line-chart">{JSON.stringify(data)}</div>,
  Bar: ({ data }) => <div data-testid="bar-chart">{JSON.stringify(data)}</div>,
  Doughnut: ({ data }) => <div data-testid="doughnut-chart">{JSON.stringify(data)}</div>
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
    expect(screen.getByText(/Cargando dashboard/i)).toBeInTheDocument()
  })

  it('displays dashboard stats when data is loaded', async () => {
    const mockStats = {
      general_stats: {
        total_records: 1422,
        overall_sentiment: -0.07,
        avg_stock_price: 298.75,
        latest_data_time: "2025-06-30T00:00:00"
      },
      sentiment_distribution: [
        { sentiment_category: 'Positive', count: 45 },
        { sentiment_category: 'Neutral', count: 30 },
        { sentiment_category: 'Negative', count: 25 }
      ]
    }

    const mockTimeline = {
      timeline: [
        { time_period: "2025-06-30T10:00:00", sentiment_score: 0.65, avg_price: 150.25, news_count: 15, total_volume: 1000000 },
        { time_period: "2025-06-30T09:00:00", sentiment_score: 0.45, avg_price: 149.80, news_count: 12, total_volume: 950000 }
      ]
    }

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockTimeline
      })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('1,422')).toBeInTheDocument() // Total records
      expect(screen.getByText('-0.070')).toBeInTheDocument() // Overall sentiment
      expect(screen.getByText('$298.75')).toBeInTheDocument() // Avg stock price
    })
  })

  it('handles API errors gracefully', async () => {
    global.fetch.mockRejectedValue(new Error('API Error'))

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText(/Error al cargar datos del dashboard/i)).toBeInTheDocument()
    })
  })

  it('displays time filters', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ general_stats: {}, sentiment_distribution: [] })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ timeline: [] })
      })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('24h')).toBeInTheDocument()
      expect(screen.getByText('7d')).toBeInTheDocument()
      expect(screen.getByText('30d')).toBeInTheDocument()
    })
  })

  it('changes time range when filter is clicked', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ general_stats: {}, sentiment_distribution: [] })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ timeline: [] })
      })

    render(<Dashboard />)

    await waitFor(() => {
      const sevenDayButton = screen.getByText('7d')
      fireEvent.click(sevenDayButton)
      
      // Should make new API calls with updated time range
      expect(global.fetch).toHaveBeenCalledTimes(4) // Initial + 3 filter clicks
    })
  })

  it('displays sentiment distribution chart', async () => {
    const mockStats = {
      general_stats: {
        total_records: 1422,
        overall_sentiment: -0.07,
        avg_stock_price: 298.75,
        latest_data_time: "2025-06-30T00:00:00"
      },
      sentiment_distribution: [
        { sentiment_category: 'Positive', count: 45 },
        { sentiment_category: 'Neutral', count: 30 },
        { sentiment_category: 'Negative', count: 25 }
      ]
    }

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ timeline: [] })
      })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByTestId('doughnut-chart')).toBeInTheDocument()
    })
  })

  it('displays timeline chart', async () => {
    const mockTimeline = {
      timeline: [
        { time_period: "2025-06-30T10:00:00", sentiment_score: 0.65, avg_price: 150.25, news_count: 15, total_volume: 1000000 },
        { time_period: "2025-06-30T09:00:00", sentiment_score: 0.45, avg_price: 149.80, news_count: 12, total_volume: 950000 }
      ]
    }

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ general_stats: {}, sentiment_distribution: [] })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockTimeline
      })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByTestId('line-chart')).toBeInTheDocument()
    })
  })

  it('displays system information', async () => {
    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ general_stats: {}, sentiment_distribution: [] })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ timeline: [] })
      })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText(/Información del Sistema/i)).toBeInTheDocument()
      expect(screen.getByText(/Estado de la API/i)).toBeInTheDocument()
      expect(screen.getByText(/Base de Datos/i)).toBeInTheDocument()
    })
  })

  it('shows positive sentiment in green color', async () => {
    const mockStats = {
      general_stats: {
        total_records: 1422,
        overall_sentiment: 0.15, // Positive sentiment
        avg_stock_price: 298.75,
        latest_data_time: "2025-06-30T00:00:00"
      },
      sentiment_distribution: []
    }

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ timeline: [] })
      })

    render(<Dashboard />)

    await waitFor(() => {
      const sentimentElement = screen.getByText('0.150')
      expect(sentimentElement).toHaveClass('positive')
    })
  })

  it('shows negative sentiment in red color', async () => {
    const mockStats = {
      general_stats: {
        total_records: 1422,
        overall_sentiment: -0.15, // Negative sentiment
        avg_stock_price: 298.75,
        latest_data_time: "2025-06-30T00:00:00"
      },
      sentiment_distribution: []
    }

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ timeline: [] })
      })

    render(<Dashboard />)

    await waitFor(() => {
      const sentimentElement = screen.getByText('-0.150')
      expect(sentimentElement).toHaveClass('negative')
    })
  })

  it('handles empty data gracefully', async () => {
    const mockStats = {
      general_stats: {
        total_records: 0,
        overall_sentiment: 0,
        avg_stock_price: 0,
        latest_data_time: null
      },
      sentiment_distribution: []
    }

    global.fetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ timeline: [] })
      })

    render(<Dashboard />)

    await waitFor(() => {
      expect(screen.getByText('0')).toBeInTheDocument() // Total records
      expect(screen.getByText('0.000')).toBeInTheDocument() // Overall sentiment
      expect(screen.getByText('$0.00')).toBeInTheDocument() // Avg stock price
    })
  })
}) 