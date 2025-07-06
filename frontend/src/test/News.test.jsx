import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import News from '../pages/News'

// Mock fetch
global.fetch = vi.fn()

// Mock Chart.js
vi.mock('react-chartjs-2', () => ({
  Line: ({ data }) => <div data-testid="chart">Chart: {data?.datasets?.[0]?.data?.length || 0} points</div>
}))

describe('News Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders news page title', () => {
    render(<News />)
    expect(screen.getByText(/Noticias Financieras/i)).toBeInTheDocument()
  })

  it('shows loading state initially', () => {
    render(<News />)
    expect(screen.getByText(/Cargando noticias/i)).toBeInTheDocument()
  })

  it('displays news when data is loaded', async () => {
    const mockNews = [
      {
        title: 'Apple Reports Strong Q4 Earnings',
        description: 'Apple Inc. reported better-than-expected quarterly earnings...',
        url: 'https://example.com/apple-earnings',
        published_at: '2024-01-15T10:30:00',
        source_name: 'Financial Times',
        sentiment_score: 0.75,
        sentiment_subjectivity: 0.45
      }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ news: mockNews, total_count: 1 })
    })

    render(<News />)

    await waitFor(() => {
      expect(screen.getByText('Apple Reports Strong Q4 Earnings')).toBeInTheDocument()
    })
  })

  it('handles API errors gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('API Error'))

    render(<News />)

    await waitFor(() => {
      expect(screen.getByText(/Error al cargar las noticias/i)).toBeInTheDocument()
    })
  })

  it('filters news by search term', async () => {
    const mockNews = [
      {
        title: 'Apple Reports Strong Q4 Earnings',
        description: 'Apple Inc. reported better-than-expected quarterly earnings...',
        url: 'https://example.com/apple-earnings',
        published_at: '2024-01-15T10:30:00',
        source_name: 'Financial Times',
        sentiment_score: 0.75,
        sentiment_subjectivity: 0.45
      },
      {
        title: 'Tech Stocks Face Market Volatility',
        description: 'Technology stocks experienced significant volatility...',
        url: 'https://example.com/tech-volatility',
        published_at: '2024-01-15T09:15:00',
        source_name: 'Reuters',
        sentiment_score: -0.25,
        sentiment_subjectivity: 0.35
      }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ news: mockNews, total_count: 2 })
    })

    render(<News />)

    await waitFor(() => {
      expect(screen.getByText('Apple Reports Strong Q4 Earnings')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/Buscar en títulos y descripciones/i)
    fireEvent.change(searchInput, { target: { value: 'Apple' } })

    await waitFor(() => {
      expect(screen.getByText('Apple Reports Strong Q4 Earnings')).toBeInTheDocument()
      expect(screen.queryByText('Tech Stocks Face Market Volatility')).not.toBeInTheDocument()
    })
  })

  it('filters news by sentiment', async () => {
    const mockNews = [
      {
        title: 'Positive News',
        description: 'Good news',
        url: 'https://example.com/positive',
        published_at: '2024-01-15T10:30:00',
        source_name: 'Financial Times',
        sentiment_score: 0.75,
        sentiment_subjectivity: 0.45
      },
      {
        title: 'Negative News',
        description: 'Bad news',
        url: 'https://example.com/negative',
        published_at: '2024-01-15T09:15:00',
        source_name: 'Reuters',
        sentiment_score: -0.75,
        sentiment_subjectivity: 0.35
      }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ news: mockNews, total_count: 2 })
    })

    render(<News />)

    await waitFor(() => {
      expect(screen.getByText('Positive News')).toBeInTheDocument()
    })

    const sentimentSelect = screen.getByLabelText(/Sentimiento/i)
    fireEvent.change(sentimentSelect, { target: { value: 'positive' } })

    await waitFor(() => {
      expect(screen.getByText('Positive News')).toBeInTheDocument()
      expect(screen.queryByText('Negative News')).not.toBeInTheDocument()
    })
  })

  it('displays sentiment statistics', async () => {
    const mockNews = [
      {
        title: 'Test News',
        description: 'Test description',
        url: 'https://example.com/test',
        published_at: '2024-01-15T10:30:00',
        source_name: 'Financial Times',
        sentiment_score: 0.5,
        sentiment_subjectivity: 0.45
      }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ news: mockNews, total_count: 1 })
    })

    render(<News />)

    await waitFor(() => {
      expect(screen.getByText('1')).toBeInTheDocument() // Total de noticias
      expect(screen.getByText('0.500')).toBeInTheDocument() // Sentimiento promedio
      expect(screen.getByText('1')).toBeInTheDocument() // Fuentes únicas
    })
  })

  it('displays sentiment labels correctly', async () => {
    const mockNews = [
      {
        title: 'Positive News',
        description: 'Good news',
        url: 'https://example.com/positive',
        published_at: '2024-01-15T10:30:00',
        source_name: 'Financial Times',
        sentiment_score: 0.75,
        sentiment_subjectivity: 0.45
      }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ news: mockNews, total_count: 1 })
    })

    render(<News />)

    await waitFor(() => {
      expect(screen.getByText('📈 Positivo')).toBeInTheDocument()
      expect(screen.getByText(/Score: 0.750/i)).toBeInTheDocument()
      expect(screen.getByText(/Subjetividad: 0.450/i)).toBeInTheDocument()
    })
  })

  it('changes limit and refetches data', async () => {
    const mockNews = [
      {
        title: 'Test News',
        description: 'Test description',
        url: 'https://example.com/test',
        published_at: '2024-01-15T10:30:00',
        source_name: 'Financial Times',
        sentiment_score: 0.5,
        sentiment_subjectivity: 0.45
      }
    ]

    fetch.mockResolvedValue({
      ok: true,
      json: async () => ({ news: mockNews, total_count: 1 })
    })

    render(<News />)

    await waitFor(() => {
      expect(screen.getByText('Test News')).toBeInTheDocument()
    })

    const limitSelect = screen.getByLabelText(/Mostrar/i)
    fireEvent.change(limitSelect, { target: { value: '50' } })

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(expect.stringContaining('limit=50'))
    })
  })

  it('shows no results message when filters return empty', async () => {
    const mockNews = [
      {
        title: 'Test News',
        description: 'Test description',
        url: 'https://example.com/test',
        published_at: '2024-01-15T10:30:00',
        source_name: 'Financial Times',
        sentiment_score: 0.5,
        sentiment_subjectivity: 0.45
      }
    ]

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ news: mockNews, total_count: 1 })
    })

    render(<News />)

    await waitFor(() => {
      expect(screen.getByText('Test News')).toBeInTheDocument()
    })

    const searchInput = screen.getByPlaceholderText(/Buscar en títulos y descripciones/i)
    fireEvent.change(searchInput, { target: { value: 'NonExistentTerm' } })

    await waitFor(() => {
      expect(screen.getByText(/No se encontraron noticias con los filtros seleccionados/i)).toBeInTheDocument()
    })
  })
}) 