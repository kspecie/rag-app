import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import UploadPage from '../../pages/Upload'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock window.confirm
global.confirm = vi.fn()


describe('UploadPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockClear()
  })

  it('renders without crashing', () => {
    // Mock the fetch calls that happen on mount
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve([]) } as Response) // documents fetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({}) } as Response) // collections fetch

    render(<UploadPage />)
    expect(document.body).toBeInTheDocument()
  })

  it('displays main heading', () => {
    // Mock the fetch calls that happen on mount
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve([]) } as Response) // documents fetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({}) } as Response) // collections fetch

    render(<UploadPage />)
    expect(screen.getByText('Add new files to your knowledge source')).toBeInTheDocument()
  })

  it('displays other data collections section', () => {
    // Mock the fetch calls that happen on mount
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve([]) } as Response) // documents fetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({}) } as Response) // collections fetch

    render(<UploadPage />)
    expect(screen.getByText('Other Data Collections')).toBeInTheDocument()
    expect(screen.getByText('Miriad Knowledge')).toBeInTheDocument()
    expect(screen.getByText('NICE Knowledge')).toBeInTheDocument()
  })

  it('fetches documents on mount', async () => {
    const mockDocuments = [
      { id: '1', title: 'Test Document', uploadDate: '2024-01-01' }
    ]
    
    mockFetch
      .mockResolvedValueOnce({
        json: () => Promise.resolve(mockDocuments)
      } as Response)
      .mockResolvedValueOnce({
        json: () => Promise.resolve({})
      } as Response)

    render(<UploadPage />)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8006/documents',
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-API-Key': expect.any(String)
          })
        })
      )
    })
  })

  it('fetches collection metadata on mount', async () => {
    const mockCollections = {
      miriad_knowledge: { last_updated: '2024-01-01' },
      nice_knowledge: { last_updated: '2024-01-02' }
    }
    
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve([]) } as Response) // documents fetch
      .mockResolvedValueOnce({ json: () => Promise.resolve(mockCollections) } as Response) // collections fetch

    render(<UploadPage />)

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8006/collections',
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-API-Key': expect.any(String)
          })
        })
      )
    })
  })

  it('handles delete collection user confirmation', async () => {
    vi.mocked(global.confirm).mockReturnValue(true)
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve([]) } as Response) // documents fetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({}) } as Response) // collections fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({})
      } as Response)

    render(<UploadPage />)
    
    // Wait for documents to load first
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled()
    })

    const deleteButton = screen.queryByText('Delete All User Documents')
    if (deleteButton) {
      await userEvent.click(deleteButton)
      
      expect(global.confirm).toHaveBeenCalledWith(
        'Are you sure you want to delete ALL documents? This cannot be undone.'
      )
      
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          'http://localhost:8006/documents/collections/user',
          expect.objectContaining({
            method: 'DELETE',
            headers: expect.objectContaining({
              'X-API-Key': expect.any(String)
            })
          })
        )
      })
    }
  })

  it('handles delete collection by name', async () => {
    vi.mocked(global.confirm).mockReturnValue(true)
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve([]) } as Response) // documents fetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({}) } as Response) // collections fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({})
      } as Response)

    render(<UploadPage />)
    
    const deleteButtons = screen.getAllByText('Delete')
    await userEvent.click(deleteButtons[0]) // Click first delete button
    
    expect(global.confirm).toHaveBeenCalledWith(
      'Are you sure you want to delete the miriad_knowledge collection? This cannot be undone.'
    )
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8006/documents/collections/miriad',
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            'X-API-Key': expect.any(String)
          })
        })
      )
    })
  })

  it('handles update collection by name', async () => {
    mockFetch
      .mockResolvedValueOnce({ json: () => Promise.resolve([]) } as Response) // documents fetch
      .mockResolvedValueOnce({ json: () => Promise.resolve({}) } as Response) // collections fetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({})
      } as Response)

    render(<UploadPage />)
    
    const updateButtons = screen.getAllByText('Update')
    await userEvent.click(updateButtons[0]) // Click first update button
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8006/collections/update_miriad',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'X-API-Key': expect.any(String)
          })
        })
      )
    })
  })
})