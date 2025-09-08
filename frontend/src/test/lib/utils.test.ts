import { describe, it, expect } from 'vitest'
import { cn } from '../../lib/utils'

describe('utils', () => {
  describe('cn function', () => {
    it('merges class names correctly', () => {
      const result = cn('class1', 'class2')
      expect(result).toBe('class1 class2')
    })

    it('handles conditional classes', () => {
      const result = cn('base', true && 'conditional', false && 'hidden')
      expect(result).toBe('base conditional')
    })

    it('handles undefined and null values', () => {
      const result = cn('base', undefined, null, 'valid')
      expect(result).toBe('base valid')
    })

    it('handles empty strings', () => {
      const result = cn('base', '', 'valid')
      expect(result).toBe('base valid')
    })

    it('handles arrays of classes', () => {
      const result = cn(['class1', 'class2'], 'class3')
      expect(result).toBe('class1 class2 class3')
    })

    it('handles objects with boolean values', () => {
      const result = cn({
        'class1': true,
        'class2': false,
        'class3': true
      })
      expect(result).toBe('class1 class3')
    })

    it('handles mixed input types', () => {
      const result = cn(
        'base',
        ['array1', 'array2'],
        {
          'object1': true,
          'object2': false
        },
        'string',
        undefined,
        null
      )
      expect(result).toBe('base array1 array2 object1 string')
    })

    it('handles Tailwind class conflicts', () => {
      // This tests that tailwind-merge is working correctly
      const result = cn('p-2', 'p-4')
      expect(result).toBe('p-4') // p-4 should override p-2
    })

    it('handles complex Tailwind scenarios', () => {
      const result = cn('bg-red-500', 'bg-blue-500')
      expect(result).toBe('bg-blue-500') // bg-blue-500 should override bg-red-500
    })

    it('handles responsive classes', () => {
      const result = cn('p-2', 'md:p-4', 'lg:p-6')
      expect(result).toBe('p-2 md:p-4 lg:p-6')
    })

    it('handles state variants', () => {
      const result = cn('hover:bg-blue-500', 'focus:bg-blue-600')
      expect(result).toBe('hover:bg-blue-500 focus:bg-blue-600')
    })

    it('returns empty string for no input', () => {
      const result = cn()
      expect(result).toBe('')
    })

    it('handles single class', () => {
      const result = cn('single-class')
      expect(result).toBe('single-class')
    })

    it('handles whitespace correctly', () => {
      const result = cn('  class1  ', '  class2  ')
      expect(result).toBe('class1 class2')
    })
  })
})

