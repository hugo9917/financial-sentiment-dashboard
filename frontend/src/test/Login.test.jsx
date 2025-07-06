import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import Login from '../components/Login'

// Mock fetch
global.fetch = vi.fn()

describe('Login Component', () => {
  const mockOnLogin = vi.fn()
  const mockOnClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders login modal', () => {
    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)
    
    expect(screen.getByText('Iniciar Sesión')).toBeInTheDocument()
    expect(screen.getByLabelText('Usuario:')).toBeInTheDocument()
    expect(screen.getByLabelText('Contraseña:')).toBeInTheDocument()
  })

  it('shows user credentials info', () => {
    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)
    
    expect(screen.getByText('Usuarios de prueba:')).toBeInTheDocument()
    expect(screen.getByText(/Admin: admin/)).toBeInTheDocument()
    expect(screen.getByText(/Usuario: user/)).toBeInTheDocument()
  })

  it('handles form submission successfully', async () => {
    const mockResponse = {
      access_token: 'mock-token',
      token_type: 'bearer',
      user: {
        username: 'admin',
        email: 'admin@example.com',
        full_name: 'Administrator',
        role: 'admin'
      }
    }

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    })

    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)

    const usernameInput = screen.getByLabelText('Usuario:')
    const passwordInput = screen.getByLabelText('Contraseña:')
    const submitButton = screen.getByText('Iniciar Sesión')

    fireEvent.change(usernameInput, { target: { value: 'admin' } })
    fireEvent.change(passwordInput, { target: { value: 'admin123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'),
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData)
        })
      )
    })

    await waitFor(() => {
      expect(mockOnLogin).toHaveBeenCalledWith(mockResponse)
    })
  })

  it('handles login error', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Incorrect username or password' })
    })

    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)

    const usernameInput = screen.getByLabelText('Usuario:')
    const passwordInput = screen.getByLabelText('Contraseña:')
    const submitButton = screen.getByText('Iniciar Sesión')

    fireEvent.change(usernameInput, { target: { value: 'wrong' } })
    fireEvent.change(passwordInput, { target: { value: 'wrong' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Incorrect username or password')).toBeInTheDocument()
    })

    expect(mockOnLogin).not.toHaveBeenCalled()
  })

  it('handles network error', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'))

    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)

    const usernameInput = screen.getByLabelText('Usuario:')
    const passwordInput = screen.getByLabelText('Contraseña:')
    const submitButton = screen.getByText('Iniciar Sesión')

    fireEvent.change(usernameInput, { target: { value: 'admin' } })
    fireEvent.change(passwordInput, { target: { value: 'admin123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument()
    })

    expect(mockOnLogin).not.toHaveBeenCalled()
  })

  it('validates required fields', async () => {
    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)

    const submitButton = screen.getByText('Iniciar Sesión')
    fireEvent.click(submitButton)

    // HTML5 validation should prevent submission
    expect(fetch).not.toHaveBeenCalled()
  })

  it('shows loading state during submission', async () => {
    // Mock a slow response
    fetch.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)))

    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)

    const usernameInput = screen.getByLabelText('Usuario:')
    const passwordInput = screen.getByLabelText('Contraseña:')
    const submitButton = screen.getByText('Iniciar Sesión')

    fireEvent.change(usernameInput, { target: { value: 'admin' } })
    fireEvent.change(passwordInput, { target: { value: 'admin123' } })
    fireEvent.click(submitButton)

    expect(screen.getByText('Iniciando sesión...')).toBeInTheDocument()
    expect(submitButton).toBeDisabled()
  })

  it('calls onClose when close button is clicked', () => {
    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)

    const closeButton = screen.getByText('×')
    fireEvent.click(closeButton)

    expect(mockOnClose).toHaveBeenCalled()
  })

  it('stores token and user data in localStorage on successful login', async () => {
    const mockResponse = {
      access_token: 'mock-token-123',
      token_type: 'bearer',
      user: {
        username: 'admin',
        email: 'admin@example.com',
        full_name: 'Administrator',
        role: 'admin'
      }
    }

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    })

    // Mock localStorage
    const localStorageMock = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
    }
    Object.defineProperty(window, 'localStorage', {
      value: localStorageMock,
      writable: true
    })

    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)

    const usernameInput = screen.getByLabelText('Usuario:')
    const passwordInput = screen.getByLabelText('Contraseña:')
    const submitButton = screen.getByText('Iniciar Sesión')

    fireEvent.change(usernameInput, { target: { value: 'admin' } })
    fireEvent.change(passwordInput, { target: { value: 'admin123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'mock-token-123')
      expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockResponse.user))
    })
  })

  it('clears error message when form is resubmitted', async () => {
    // First, trigger an error
    fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ detail: 'Incorrect username or password' })
    })

    render(<Login onLogin={mockOnLogin} onClose={mockOnClose} />)

    const usernameInput = screen.getByLabelText('Usuario:')
    const passwordInput = screen.getByLabelText('Contraseña:')
    const submitButton = screen.getByText('Iniciar Sesión')

    fireEvent.change(usernameInput, { target: { value: 'wrong' } })
    fireEvent.change(passwordInput, { target: { value: 'wrong' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.getByText('Incorrect username or password')).toBeInTheDocument()
    })

    // Then, trigger a success
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'mock-token',
        token_type: 'bearer',
        user: { username: 'admin', email: 'admin@example.com', full_name: 'Admin', role: 'admin' }
      })
    })

    fireEvent.change(usernameInput, { target: { value: 'admin' } })
    fireEvent.change(passwordInput, { target: { value: 'admin123' } })
    fireEvent.click(submitButton)

    await waitFor(() => {
      expect(screen.queryByText('Incorrect username or password')).not.toBeInTheDocument()
    })
  })
}) 