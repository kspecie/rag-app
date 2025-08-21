import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../../App'

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />)
    // Basic test to ensure the app renders
    expect(document.body).toBeInTheDocument()
  })

  it('renders main content', () => {
    render(<App />)
    // Add more specific tests based on your App component content
    // For example:
    // expect(screen.getByText(/medical/i)).toBeInTheDocument()
  })
}) 