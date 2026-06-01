import { fireEvent, render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Products from '../Products.jsx'
import { ToastProvider } from '../../components/Toast.jsx'

// Stub the API so the component renders without a real backend.
vi.mock('../../api/client.js', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [], total: 0 } })),
    post: vi.fn(() => Promise.resolve({ data: {} })),
    put: vi.fn(),
    delete: vi.fn(),
  },
  errorMessage: () => 'error',
}))

import api from '../../api/client.js'

function renderPage() {
  return render(
    <ToastProvider>
      <Products />
    </ToastProvider>
  )
}

describe('Products form validation', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('shows required-field errors when submitting an empty form', async () => {
    renderPage()
    // Wait for the initial (empty) load to finish.
    await screen.findByText('No products yet.')

    fireEvent.click(screen.getByText('+ Add Product'))
    fireEvent.click(screen.getByRole('button', { name: 'Add' }))

    expect(await screen.findByText('Name is required')).toBeInTheDocument()
    expect(screen.getByText('SKU is required')).toBeInTheDocument()
    expect(screen.getByText('Price must be greater than 0')).toBeInTheDocument()
    // An invalid form must not hit the API.
    expect(api.post).not.toHaveBeenCalled()
  })

  it('rejects a price of zero', async () => {
    renderPage()
    await screen.findByText('No products yet.')

    fireEvent.click(screen.getByText('+ Add Product'))
    fireEvent.change(screen.getByLabelText('Name'), { target: { value: 'Thing' } })
    fireEvent.change(screen.getByLabelText('SKU / Code'), { target: { value: 'T1' } })
    fireEvent.change(screen.getByLabelText('Price'), { target: { value: '0' } })
    fireEvent.change(screen.getByLabelText('Quantity in stock'), { target: { value: '5' } })
    fireEvent.click(screen.getByRole('button', { name: 'Add' }))

    expect(await screen.findByText('Price must be greater than 0')).toBeInTheDocument()
    expect(api.post).not.toHaveBeenCalled()
  })
})
