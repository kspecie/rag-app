import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '../../components/ui/button'

describe('Button', () => {
  it('renders without crashing', () => {
    render(<Button>Test Button</Button>)
    expect(screen.getByRole('button', { name: 'Test Button' })).toBeInTheDocument()
  })

  it('renders with default variant and size', () => {
    render(<Button>Default Button</Button>)
    const button = screen.getByRole('button', { name: 'Default Button' })
    expect(button).toHaveClass('bg-primary', 'text-primary-foreground', 'h-9', 'px-4', 'py-2')
  })

  it('renders with destructive variant', () => {
    render(<Button variant="destructive">Delete</Button>)
    const button = screen.getByRole('button', { name: 'Delete' })
    expect(button).toHaveClass('bg-destructive', 'text-white')
  })

  it('renders with outline variant', () => {
    render(<Button variant="outline">Outline</Button>)
    const button = screen.getByRole('button', { name: 'Outline' })
    expect(button).toHaveClass('border', 'bg-background')
  })

  it('renders with secondary variant', () => {
    render(<Button variant="secondary">Secondary</Button>)
    const button = screen.getByRole('button', { name: 'Secondary' })
    expect(button).toHaveClass('bg-secondary', 'text-secondary-foreground')
  })

  it('renders with ghost variant', () => {
    render(<Button variant="ghost">Ghost</Button>)
    const button = screen.getByRole('button', { name: 'Ghost' })
    expect(button).toHaveClass('hover:bg-accent', 'hover:text-accent-foreground')
  })

  it('renders with link variant', () => {
    render(<Button variant="link">Link</Button>)
    const button = screen.getByRole('button', { name: 'Link' })
    expect(button).toHaveClass('text-primary', 'underline-offset-4')
  })

  it('renders with small size', () => {
    render(<Button size="sm">Small</Button>)
    const button = screen.getByRole('button', { name: 'Small' })
    expect(button).toHaveClass('h-8', 'rounded-md', 'gap-1.5', 'px-3')
  })

  it('renders with large size', () => {
    render(<Button size="lg">Large</Button>)
    const button = screen.getByRole('button', { name: 'Large' })
    expect(button).toHaveClass('h-10', 'rounded-md', 'px-6')
  })

  it('renders with icon size', () => {
    render(<Button size="icon">Icon</Button>)
    const button = screen.getByRole('button', { name: 'Icon' })
    expect(button).toHaveClass('size-9')
  })

  it('handles click events', async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Clickable</Button>)
    
    const button = screen.getByRole('button', { name: 'Clickable' })
    await userEvent.click(button)
    
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('can be disabled', () => {
    render(<Button disabled>Disabled</Button>)
    const button = screen.getByRole('button', { name: 'Disabled' })
    expect(button).toBeDisabled()
    expect(button).toHaveClass('disabled:pointer-events-none', 'disabled:opacity-50')
  })

  it('accepts custom className', () => {
    render(<Button className="custom-class">Custom</Button>)
    const button = screen.getByRole('button', { name: 'Custom' })
    expect(button).toHaveClass('custom-class')
  })

  it('renders as child component when asChild is true', () => {
    render(
      <Button asChild>
        <a href="/test">Link Button</a>
      </Button>
    )
    const link = screen.getByRole('link', { name: 'Link Button' })
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/test')
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<Button ref={ref}>Ref Button</Button>)
    expect(ref.current).toBeInstanceOf(HTMLButtonElement)
  })
})

