import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SummarizePage from '../../pages/Summarise'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch

// Mock FileReader
global.FileReader = vi.fn().mockImplementation(() => ({
  readAsText: vi.fn(),
  onload: null,
  onerror: null,
  result: null,
}))

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
})

// Mock toast from sonner
vi.mock('sonner', () => ({
  toast: Object.assign(vi.fn(), {
    success: vi.fn(),
    error: vi.fn(),
    default: vi.fn(),
  }),
  Toaster: () => <div data-testid="toaster" />,
}))

// Mock ReactMarkdown
vi.mock('react-markdown', () => ({
  default: ({ children }: { children: string }) => <div data-testid="markdown">{children}</div>,
}))

describe('SummarizePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockFetch.mockClear()
    mockLocalStorage.getItem.mockClear()
    mockLocalStorage.setItem.mockClear()
  })

  // Helper to get mocked toast
  const getMockedToast = async () => {
    const { toast } = await import('sonner')
    return toast
  }

  it('renders without crashing', () => {
    render(<SummarizePage />)
    expect(screen.getByText('Summarize Transcriptions')).toBeInTheDocument()
  })

  it('displays main heading', () => {
    render(<SummarizePage />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Summarize Transcriptions')
  })

  it('displays input and output cards', () => {
    render(<SummarizePage />)
    expect(screen.getByText('Input Transcription')).toBeInTheDocument()
    expect(screen.getByText('Templated Summary')).toBeInTheDocument()
  })

  it('has file upload area', () => {
    render(<SummarizePage />)
    expect(screen.getByText('Drag and drop a file here, or click to browse')).toBeInTheDocument()
    expect(screen.getByText('Supported formats: TXT, JSON, MD (Max 5MB)')).toBeInTheDocument()
  })

  it('has textarea for direct input', () => {
    render(<SummarizePage />)
    const textarea = screen.getByLabelText('Paste Transcription Text')
    expect(textarea).toBeInTheDocument()
    expect(textarea).toHaveAttribute('placeholder', 'Paste your conversation transcription here...')
  })

  it('has summarize button', () => {
    render(<SummarizePage />)
    const button = screen.getByRole('button', { name: 'Summarize' })
    expect(button).toBeInTheDocument()
  })

  it('handles text input change', async () => {
    const user = userEvent.setup()
    render(<SummarizePage />)
    
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    expect(textarea).toHaveValue('Test transcription')
  })

  it('truncates long text in display', async () => {
    const user = userEvent.setup()
    render(<SummarizePage />)
    
    const longText = 'a'.repeat(1500) // Longer than TRUNCATION_LENGTH (1000)
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, longText)
    
    expect(textarea.value).toContain('... [Full text, showing first 1000 characters] ...')
  })

  it('shows error when trying to summarize empty text', async () => {
    const user = userEvent.setup()
    
    render(<SummarizePage />)
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    const toast = await getMockedToast()
    expect(toast.error).toHaveBeenCalledWith('Please provide text or upload a file for summarization.')
  })

  it('handles successful summarization', async () => {
    const user = userEvent.setup()
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ summary: 'Generated summary' }),
    })
    
    render(<SummarizePage />)
    
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8006/summaries/generate/',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'X-API-Key': expect.any(String)
          }),
          body: JSON.stringify({ text: 'Test transcription', file_name: undefined })
        })
      )
    })
    
    await waitFor(async () => {
      const toast = await getMockedToast()
      expect(toast.success).toHaveBeenCalledWith('Summary generated successfully!')
    })
  })

  it('handles summarization error', async () => {
    const user = userEvent.setup()
    
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'API Error' }),
    })
    
    render(<SummarizePage />)
    
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    await waitFor(async () => {
      const toast = await getMockedToast()
      expect(toast.error).toHaveBeenCalledWith('Summarization error: "API Error"')
    })
  })

  it('handles file input change', async () => {
    const user = userEvent.setup()
    
    const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' })
    const mockFileReader = {
      readAsText: vi.fn(),
      onload: null,
      onerror: null,
      result: 'test content',
    }
    
    vi.mocked(FileReader).mockImplementation(() => mockFileReader as any)
    
    render(<SummarizePage />)
    
    const fileInput = document.getElementById('transcription-file-hidden') as HTMLInputElement
    await user.upload(fileInput, mockFile)
    
    // Simulate successful file read
    if (mockFileReader.onload) {
      mockFileReader.onload({ target: { result: 'test content' } } as any)
    }
    
    await waitFor(async () => {
      const toast = await getMockedToast()
      expect(toast.success).toHaveBeenCalledWith('File "test.txt" loaded successfully.')
    })
  })

  it('handles file input with unsupported type', async () => {
    const mockFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' })
    
    render(<SummarizePage />)
    
    const fileInput = document.getElementById('transcription-file-hidden') as HTMLInputElement
    fireEvent.change(fileInput, { target: { files: [mockFile] } })
    
    await waitFor(async () => {
      const toast = await getMockedToast()
      expect(toast.error).toHaveBeenCalledWith('Unsupported file type. Please upload a .txt, .json, or .md file.')
    })
  })

  it('handles file input with oversized file', async () => {
    const user = userEvent.setup()
    
    // Create a file larger than 5MB
    const mockFile = new File(['x'.repeat(6 * 1024 * 1024)], 'large.txt', { type: 'text/plain' })
    
    render(<SummarizePage />)
    
    const fileInput = document.getElementById('transcription-file-hidden') as HTMLInputElement
    await user.upload(fileInput, mockFile)
    
    await waitFor(async () => {
      const toast = await getMockedToast()
      expect(toast.error).toHaveBeenCalledWith('File is too large (max 5MB).')
    })
  })

  it('handles drag and drop events', async () => {
    const user = userEvent.setup()
    
    const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' })
    const mockFileReader = {
      readAsText: vi.fn(),
      onload: null,
      onerror: null,
      result: 'test content',
    }
    
    vi.mocked(FileReader).mockImplementation(() => mockFileReader as any)
    
    render(<SummarizePage />)
    
    const dropArea = screen.getByText('Drag and drop a file here, or click to browse')
    
    // Test drag over
    fireEvent.dragOver(dropArea)
    
    // Test drop
    fireEvent.drop(dropArea, {
      dataTransfer: {
        files: [mockFile],
        clearData: vi.fn(),
      },
    })
    
    // Simulate successful file read
    if (mockFileReader.onload) {
      mockFileReader.onload({ target: { result: 'test content' } } as any)
    }
    
    await waitFor(async () => {
      const toast = await getMockedToast()
      expect(toast.success).toHaveBeenCalledWith('File "test.txt" loaded successfully.')
    })
  })

  it('shows edit mode when edit button is clicked', async () => {
    const user = userEvent.setup()
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ summary: 'Generated summary' }),
    })
    
    render(<SummarizePage />)
    
    // Generate a summary first
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated summary')).toBeInTheDocument()
    })
    
    // Click edit button
    const editButton = screen.getByRole('button', { name: 'Edit' })
    await user.click(editButton)
    
    // Should show edit mode
    expect(screen.getByLabelText('Edit Summary (Markdown supported)')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Cancel' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Save' })).toBeInTheDocument()
  })

  it('handles cancel edit', async () => {
    const user = userEvent.setup()
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ summary: 'Generated summary' }),
    })
    
    render(<SummarizePage />)
    
    // Generate a summary first
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated summary')).toBeInTheDocument()
    })
    
    // Enter edit mode
    const editButton = screen.getByRole('button', { name: 'Edit' })
    await user.click(editButton)
    
    // Cancel edit
    const cancelButton = screen.getByRole('button', { name: 'Cancel' })
    await user.click(cancelButton)
    
    const toast = await getMockedToast()
    expect(toast).toHaveBeenCalledWith('Edit cancelled.')
    expect(screen.getByText('Generated summary')).toBeInTheDocument()
  })

  it('handles save summary', async () => {
    const user = userEvent.setup()
    
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ summary: 'Generated summary' }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ id: 'summary-123' }),
      })
    
    render(<SummarizePage />)
    
    // Generate a summary first
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated summary')).toBeInTheDocument()
    })
    
    // Enter edit mode
    const editButton = screen.getByRole('button', { name: 'Edit' })
    await user.click(editButton)
    
    // Edit the summary
    const editTextarea = screen.getByLabelText('Edit Summary (Markdown supported)')
    await user.clear(editTextarea)
    await user.type(editTextarea, 'Edited summary')
    
    // Save the summary
    const saveButton = screen.getByRole('button', { name: 'Save' })
    await user.click(saveButton)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8006/summaries/save/',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'X-API-Key': expect.any(String)
          }),
          body: JSON.stringify({ id: undefined, title: 'Clinical Summary', content: 'Edited summary' })
        })
      )
    })
    
    await waitFor(async () => {
      const toast = await getMockedToast()
      expect(toast.success).toHaveBeenCalledWith('Summary saved to database.')
    })
  })

  it('handles save summary error', async () => {
    const user = userEvent.setup()
    
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ summary: 'Generated summary' }),
      })
      .mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Save failed' }),
      })
    
    render(<SummarizePage />)
    
    // Generate a summary first
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated summary')).toBeInTheDocument()
    })
    
    // Enter edit mode
    const editButton = screen.getByRole('button', { name: 'Edit' })
    await user.click(editButton)
    
    // Edit the summary
    const editTextarea = screen.getByLabelText('Edit Summary (Markdown supported)')
    await user.clear(editTextarea)
    await user.type(editTextarea, 'Edited summary')
    
    // Save the summary
    const saveButton = screen.getByRole('button', { name: 'Save' })
    await user.click(saveButton)
    
    await waitFor(async () => {
      const toast = await getMockedToast()
      expect(toast.error).toHaveBeenCalledWith('Save failed')
    })
  })

  it('prevents saving empty summary', async () => {
    const user = userEvent.setup()
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ summary: 'Generated summary' }),
    })
    
    render(<SummarizePage />)
    
    // Generate a summary first
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated summary')).toBeInTheDocument()
    })
    
    // Enter edit mode
    const editButton = screen.getByRole('button', { name: 'Edit' })
    await user.click(editButton)
    
    // Clear the summary
    const editTextarea = screen.getByLabelText('Edit Summary (Markdown supported)')
    await user.clear(editTextarea)
    
    // Try to save empty summary
    const saveButton = screen.getByRole('button', { name: 'Save' })
    await user.click(saveButton)
    
    expect((await getMockedToast()).error).toHaveBeenCalledWith('Summary cannot be empty.')
  })

  it('shows loading state during summarization', async () => {
    const user = userEvent.setup()
    
    // Mock a delayed response
    mockFetch.mockImplementation(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve({ summary: 'Generated summary' }),
        }), 100)
      )
    )
    
    render(<SummarizePage />)
    
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    // Should show loading state
    expect(screen.getByRole('button', { name: 'Summarizing...' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Summarizing...' })).toBeDisabled()
  })

  it('shows loading state during save', async () => {
    const user = userEvent.setup()
    
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ summary: 'Generated summary' }),
      })
      .mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({
            ok: true,
            json: () => Promise.resolve({ id: 'summary-123' }),
          }), 100)
        )
      )
    
    render(<SummarizePage />)
    
    // Generate a summary first
    const textarea = screen.getByLabelText('Paste Transcription Text')
    await user.type(textarea, 'Test transcription')
    
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    await waitFor(() => {
      expect(screen.getByText('Generated summary')).toBeInTheDocument()
    })
    
    // Enter edit mode
    const editButton = screen.getByRole('button', { name: 'Edit' })
    await user.click(editButton)
    
    // Edit the summary
    const editTextarea = screen.getByLabelText('Edit Summary (Markdown supported)')
    await user.clear(editTextarea)
    await user.type(editTextarea, 'Edited summary')
    
    // Save the summary
    const saveButton = screen.getByRole('button', { name: 'Save' })
    await user.click(saveButton)
    
    // Should show loading state
    expect(screen.getByRole('button', { name: 'Saving...' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Saving...' })).toBeDisabled()
  })

  it('displays file name when file is uploaded', async () => {
    const user = userEvent.setup()
    
    const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' })
    const mockFileReader = {
      readAsText: vi.fn(),
      onload: null,
      onerror: null,
      result: 'test content',
    }
    
    vi.mocked(FileReader).mockImplementation(() => mockFileReader as any)
    
    render(<SummarizePage />)
    
    const fileInput = document.getElementById('transcription-file-hidden') as HTMLInputElement
    await user.upload(fileInput, mockFile)
    
    // Simulate successful file read
    if (mockFileReader.onload) {
      mockFileReader.onload({ target: { result: 'test content' } } as any)
    }
    
    await waitFor(() => {
      expect(screen.getByText('test.txt')).toBeInTheDocument()
    })
  })

  it('handles file read error', async () => {
    const user = userEvent.setup()
    
    const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' })
    const mockFileReader = {
      readAsText: vi.fn(),
      onload: null,
      onerror: null,
      result: null,
    }
    
    vi.mocked(FileReader).mockImplementation(() => mockFileReader as any)
    
    render(<SummarizePage />)
    
    const fileInput = document.getElementById('transcription-file-hidden') as HTMLInputElement
    await user.upload(fileInput, mockFile)
    
    // Simulate file read error
    if (mockFileReader.onerror) {
      mockFileReader.onerror({} as any)
    }
    
    await waitFor(async () => {
      const toast = await getMockedToast()
      expect(toast.error).toHaveBeenCalledWith('Failed to read file.')
    })
  })

  it('includes file name in summarization request when file is uploaded', async () => {
    const user = userEvent.setup()
    
    const mockFile = new File(['test content'], 'test.txt', { type: 'text/plain' })
    const mockFileReader = {
      readAsText: vi.fn(),
      onload: null,
      onerror: null,
      result: 'test content',
    }
    
    vi.mocked(FileReader).mockImplementation(() => mockFileReader as any)
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ summary: 'Generated summary' }),
    })
    
    render(<SummarizePage />)
    
    // Upload file
    const fileInput = document.getElementById('transcription-file-hidden') as HTMLInputElement
    await user.upload(fileInput, mockFile)
    
    // Simulate successful file read
    if (mockFileReader.onload) {
      mockFileReader.onload({ target: { result: 'test content' } } as any)
    }
    
    await waitFor(() => {
      expect(screen.getByText('test.txt')).toBeInTheDocument()
    })
    
    // Summarize
    const summarizeButton = screen.getByRole('button', { name: 'Summarize' })
    await user.click(summarizeButton)
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8006/summaries/generate/',
        expect.objectContaining({
          body: JSON.stringify({ text: 'test content', file_name: 'test.txt' })
        })
      )
    })
  })
})
