import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Home from '../../pages/Home'

describe('Home', () => {
  it('renders without crashing', () => {
    render(<Home />)
    expect(document.body).toBeInTheDocument()
  })

  it('displays placeholder content', () => {
    render(<Home />)
    expect(screen.getByText('TBD.')).toBeInTheDocument()
  })

  it('has correct structure', () => {
    render(<Home />)
    const container = screen.getByText('TBD.').closest('div')
    expect(container).toHaveClass('space-y-8')
  })
})

