import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card'

describe('Card Components', () => {
  describe('Card', () => {
    it('renders without crashing', () => {
      render(<Card>Test Card</Card>)
      expect(screen.getByText('Test Card')).toBeInTheDocument()
    })

    it('has correct default classes', () => {
      render(<Card>Test Card</Card>)
      const card = screen.getByText('Test Card').closest('div')
      expect(card).toHaveClass('bg-card', 'text-card-foreground', 'flex', 'flex-col', 'gap-6', 'rounded-xl', 'border', 'py-6', 'shadow-sm')
    })

    it('accepts custom className', () => {
      render(<Card className="custom-class">Test Card</Card>)
      const card = screen.getByText('Test Card').closest('div')
      expect(card).toHaveClass('custom-class')
    })

    it('forwards ref correctly', () => {
      const ref = { current: null }
      render(<Card ref={ref}>Test Card</Card>)
      expect(ref.current).toBeInstanceOf(HTMLDivElement)
    })
  })

  describe('CardHeader', () => {
    it('renders without crashing', () => {
      render(
        <Card>
          <CardHeader>Header Content</CardHeader>
        </Card>
      )
      expect(screen.getByText('Header Content')).toBeInTheDocument()
    })

    it('has correct default classes', () => {
      render(
        <Card>
          <CardHeader>Header Content</CardHeader>
        </Card>
      )
      const header = screen.getByText('Header Content').closest('div')
      expect(header).toHaveClass('@container/card-header', 'grid', 'auto-rows-min', 'grid-rows-[auto_auto]', 'items-start', 'gap-1.5', 'px-6')
    })

    it('accepts custom className', () => {
      render(
        <Card>
          <CardHeader className="custom-header">Header Content</CardHeader>
        </Card>
      )
      const header = screen.getByText('Header Content').closest('div')
      expect(header).toHaveClass('custom-header')
    })
  })

  describe('CardTitle', () => {
    it('renders without crashing', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
        </Card>
      )
      expect(screen.getByText('Card Title')).toBeInTheDocument()
    })

    it('renders as div by default', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
        </Card>
      )
      const title = screen.getByText('Card Title')
      expect(title).toBeInTheDocument()
      expect(title.tagName).toBe('DIV')
    })

    it('has correct default classes', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Card Title</CardTitle>
          </CardHeader>
        </Card>
      )
      const title = screen.getByText('Card Title')
      expect(title).toHaveClass('leading-none', 'font-semibold')
    })

    it('accepts custom className', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle className="custom-title">Card Title</CardTitle>
          </CardHeader>
        </Card>
      )
      const title = screen.getByText('Card Title')
      expect(title).toHaveClass('custom-title')
    })
  })

  describe('CardDescription', () => {
    it('renders without crashing', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Card Description</CardDescription>
          </CardHeader>
        </Card>
      )
      expect(screen.getByText('Card Description')).toBeInTheDocument()
    })

    it('has correct default classes', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription>Card Description</CardDescription>
          </CardHeader>
        </Card>
      )
      const description = screen.getByText('Card Description')
      expect(description).toHaveClass('text-sm', 'text-muted-foreground')
    })

    it('accepts custom className', () => {
      render(
        <Card>
          <CardHeader>
            <CardDescription className="custom-description">Card Description</CardDescription>
          </CardHeader>
        </Card>
      )
      const description = screen.getByText('Card Description')
      expect(description).toHaveClass('custom-description')
    })
  })

  describe('CardContent', () => {
    it('renders without crashing', () => {
      render(
        <Card>
          <CardContent>Card Content</CardContent>
        </Card>
      )
      expect(screen.getByText('Card Content')).toBeInTheDocument()
    })

    it('has correct default classes', () => {
      render(
        <Card>
          <CardContent>Card Content</CardContent>
        </Card>
      )
      const content = screen.getByText('Card Content').closest('div')
      expect(content).toHaveClass('px-6')
    })

    it('accepts custom className', () => {
      render(
        <Card>
          <CardContent className="custom-content">Card Content</CardContent>
        </Card>
      )
      const content = screen.getByText('Card Content').closest('div')
      expect(content).toHaveClass('custom-content')
    })
  })

  describe('Card Integration', () => {
    it('renders complete card structure', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
          <CardContent>Test Content</CardContent>
        </Card>
      )

      expect(screen.getByText('Test Title')).toBeInTheDocument()
      expect(screen.getByText('Test Description')).toBeInTheDocument()
      expect(screen.getByText('Test Content')).toBeInTheDocument()
    })

    it('maintains proper structure hierarchy', () => {
      render(
        <Card>
          <CardHeader>
            <CardTitle>Test Title</CardTitle>
            <CardDescription>Test Description</CardDescription>
          </CardHeader>
          <CardContent>Test Content</CardContent>
        </Card>
      )

      const card = screen.getByText('Test Title').closest('[class*="rounded-xl"]')
      expect(card).toBeInTheDocument()
      
      const header = screen.getByText('Test Title').closest('[class*="grid"]')
      expect(header).toBeInTheDocument()
      
      const content = screen.getByText('Test Content').closest('[class*="px-6"]')
      expect(content).toBeInTheDocument()
    })
  })
})
