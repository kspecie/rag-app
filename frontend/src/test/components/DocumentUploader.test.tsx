import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DocumentUploader } from '../../components/ui/upload'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch


describe('DocumentUploader', () => {
  const mockOnUploadSuccess = vi.fn()
  const mockOnUploadError = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockClear()
  })

  it('renders without crashing', () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    expect(document.body).toBeInTheDocument()
  })

  it('displays title and description', () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    expect(screen.getByText('Document Upload')).toBeInTheDocument()
    // Use getAllByText since there are multiple elements with this text
    const dragDropElements = screen.getAllByText('Drag and drop your document(s) here, or click to select.')
    expect(dragDropElements.length).toBeGreaterThan(0)
  })

  it('shows drag and drop area', () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    // Use getAllByText since there are multiple elements with this text
    const dragDropElements = screen.getAllByText('Drag and drop your document(s) here, or click to select.')
    expect(dragDropElements.length).toBeGreaterThan(0)
  })

  it('handles file selection', async () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    await userEvent.upload(fileInput!, file)
    
    // File selection should trigger the dropzone onDrop callback
    // This is handled by react-dropzone internally
  })

  it('shows upload button when files are selected', async () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    await userEvent.upload(fileInput!, file)
    
    // The upload button should appear after file selection
    await waitFor(() => {
      expect(screen.getByText('Upload Document')).toBeInTheDocument()
    })
  })

  it('handles successful upload', async () => {
    const mockResponse = {
      uploaded_files: [
        { id: 'test-id', filename: 'test.pdf' }
      ]
    }
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    } as Response)

    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    await userEvent.upload(fileInput!, file)
    
    await waitFor(() => {
      expect(screen.getByText('Upload Document')).toBeInTheDocument()
    })
    
    const uploadButton = screen.getByText('Upload Document')
    await userEvent.click(uploadButton)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8006/documents/upload/',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'X-API-Key': expect.any(String)
          }
        })
      )
    })
    
    await waitFor(() => {
      expect(mockOnUploadSuccess).toHaveBeenCalledWith({
        id: 'test-id',
        filename: 'test.pdf'
      })
    })
  })

  it('handles upload error', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Upload failed'))

    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    await userEvent.upload(fileInput!, file)
    
    await waitFor(() => {
      expect(screen.getByText('Upload Document')).toBeInTheDocument()
    })
    
    const uploadButton = screen.getByText('Upload Document')
    await userEvent.click(uploadButton)
    
    await waitFor(() => {
      expect(mockOnUploadError).toHaveBeenCalledWith('Upload failed')
    })
  })

  it('shows clear button when files are selected', async () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    await userEvent.upload(fileInput!, file)
    
    await waitFor(() => {
      expect(screen.getByText('Clear')).toBeInTheDocument()
    })
  })

  it('clears files when clear button is clicked', async () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    await userEvent.upload(fileInput!, file)
    
    await waitFor(() => {
      expect(screen.getByText('Clear')).toBeInTheDocument()
    })
    
    const clearButton = screen.getByText('Clear')
    await userEvent.click(clearButton)
    
    // After clearing, the upload button should disappear
    await waitFor(() => {
      expect(screen.queryByText('Upload Document')).not.toBeInTheDocument()
    })
  })

  it('shows file information when files are selected', async () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    const fileInput = document.querySelector('input[type="file"]')
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    await userEvent.upload(fileInput!, file)
    
    await waitFor(() => {
      expect(screen.getByText('Selected File:')).toBeInTheDocument()
      expect(screen.getByText(/test\.pdf/)).toBeInTheDocument()
    })
  })

  it('handles drag and drop events', () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
      />
    )
    
    // Get the first drag and drop element (the actual drop area)
    const dragDropElements = screen.getAllByText('Drag and drop your document(s) here, or click to select.')
    const dropArea = dragDropElements[1].closest('div') // The second one is the actual drop area
    
    expect(dropArea).toBeInTheDocument()
    
    // Test drag over
    fireEvent.dragOver(dropArea!)
    // Test drop with proper dataTransfer structure
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    fireEvent.drop(dropArea!, { 
      dataTransfer: { 
        files: [file],
        clearData: vi.fn(),
        setData: vi.fn(),
        getData: vi.fn()
      } 
    })
  })

  it('accepts custom className', () => {
    render(
      <DocumentUploader
        onUploadSuccess={mockOnUploadSuccess}
        onUploadError={mockOnUploadError}
        className="custom-class"
      />
    )
    
    // Find the root card element that should have the custom class
    const card = screen.getByText('Document Upload').closest('[data-slot="card"]')
    expect(card).toHaveClass('custom-class')
  })
})