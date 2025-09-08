import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Textarea } from '../../components/ui/textarea'

describe('Textarea', () => {
  it('renders without crashing', () => {
    render(<Textarea />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toBeInTheDocument()
  })

  it('renders with placeholder text', () => {
    render(<Textarea placeholder="Enter text here" />)
    const textarea = screen.getByPlaceholderText('Enter text here')
    expect(textarea).toBeInTheDocument()
  })

  it('has correct default classes', () => {
    render(<Textarea />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveClass(
      'border-input',
      'placeholder:text-muted-foreground',
      'focus-visible:border-ring',
      'focus-visible:ring-ring/50',
      'min-h-16',
      'w-full',
      'rounded-md',
      'border',
      'bg-transparent',
      'px-3',
      'py-2',
      'text-base',
      'shadow-xs',
      'transition-[color,box-shadow]',
      'outline-none',
      'focus-visible:ring-[3px]',
      'disabled:cursor-not-allowed',
      'disabled:opacity-50',
      'md:text-sm'
    )
  })

  it('accepts custom className', () => {
    render(<Textarea className="custom-class" />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveClass('custom-class')
  })

  it('handles value changes', async () => {
    render(<Textarea />)
    const textarea = screen.getByRole('textbox')
    
    await userEvent.type(textarea, 'Hello World')
    
    expect(textarea).toHaveValue('Hello World')
  })

  it('can be controlled with value prop', () => {
    render(<Textarea value="Controlled value" />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveValue('Controlled value')
  })

  it('can be disabled', () => {
    render(<Textarea disabled />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toBeDisabled()
    expect(textarea).toHaveClass('disabled:cursor-not-allowed', 'disabled:opacity-50')
  })

  it('can be read-only', () => {
    render(<Textarea readOnly />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('readonly')
  })

  it('accepts rows prop', () => {
    render(<Textarea rows={5} />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('rows', '5')
  })

  it('accepts cols prop', () => {
    render(<Textarea cols={30} />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('cols', '30')
  })

  it('accepts maxLength prop', () => {
    render(<Textarea maxLength={100} />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('maxlength', '100')
  })

  it('accepts minLength prop', () => {
    render(<Textarea minLength={5} />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('minlength', '5')
  })

  it('handles onChange events', async () => {
    const handleChange = vi.fn()
    render(<Textarea onChange={handleChange} />)
    const textarea = screen.getByRole('textbox')
    
    await userEvent.type(textarea, 'test')
    
    expect(handleChange).toHaveBeenCalledTimes(4) // Called for each character
  })

  it('handles onFocus events', async () => {
    const handleFocus = vi.fn()
    render(<Textarea onFocus={handleFocus} />)
    const textarea = screen.getByRole('textbox')
    
    await userEvent.click(textarea)
    
    expect(handleFocus).toHaveBeenCalledTimes(1)
  })

  it('handles onBlur events', async () => {
    const handleBlur = vi.fn()
    render(<Textarea onBlur={handleBlur} />)
    const textarea = screen.getByRole('textbox')
    
    await userEvent.click(textarea)
    await userEvent.tab()
    
    expect(handleBlur).toHaveBeenCalledTimes(1)
  })

  it('forwards ref correctly', () => {
    const ref = { current: null }
    render(<Textarea ref={ref} />)
    expect(ref.current).toBeInstanceOf(HTMLTextAreaElement)
  })

  it('has proper accessibility attributes', () => {
    render(<Textarea aria-label="Test textarea" />)
    const textarea = screen.getByLabelText('Test textarea')
    expect(textarea).toBeInTheDocument()
  })

  it('supports aria-describedby', () => {
    render(
      <div>
        <Textarea aria-describedby="help-text" />
        <div id="help-text">This is help text</div>
      </div>
    )
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('aria-describedby', 'help-text')
  })

  it('supports aria-invalid', () => {
    render(<Textarea aria-invalid="true" />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('aria-invalid', 'true')
    expect(textarea).toHaveClass('aria-invalid:ring-destructive/20', 'aria-invalid:border-destructive')
  })

  it('has proper data-slot attribute', () => {
    render(<Textarea />)
    const textarea = screen.getByRole('textbox')
    expect(textarea).toHaveAttribute('data-slot', 'textarea')
  })
})

