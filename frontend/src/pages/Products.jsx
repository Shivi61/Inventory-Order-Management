import { useEffect, useState } from 'react'
import api, { errorMessage } from '../api/client.js'
import Modal from '../components/Modal.jsx'
import Skeleton from '../components/Skeleton.jsx'
import { useToast } from '../components/Toast.jsx'

const empty = { name: '', sku: '', price: '', quantity: '' }
const PAGE_SIZE = 10

export default function Products() {
  const [products, setProducts] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form, setForm] = useState(empty)
  const [errors, setErrors] = useState({})
  const notify = useToast()

  async function load() {
    setLoading(true)
    try {
      const res = await api.get('/products', {
        params: { page, page_size: PAGE_SIZE, search: search || undefined },
      })
      setProducts(res.data.items)
      setTotal(res.data.total)
    } catch (err) {
      notify(errorMessage(err), 'error')
    } finally {
      setLoading(false)
    }
  }

  // Reload on page change immediately, and debounce search input.
  useEffect(() => {
    const t = setTimeout(load, search ? 300 : 0)
    return () => clearTimeout(t)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, search])

  function openAdd() {
    setEditing(null)
    setForm(empty)
    setErrors({})
    setShowForm(true)
  }

  function openEdit(p) {
    setEditing(p)
    setForm({ name: p.name, sku: p.sku, price: p.price, quantity: p.quantity })
    setErrors({})
    setShowForm(true)
  }

  function validate() {
    const e = {}
    if (!form.name.trim()) e.name = 'Name is required'
    if (!form.sku.trim()) e.sku = 'SKU is required'
    if (form.price === '' || Number(form.price) <= 0) e.price = 'Price must be greater than 0'
    if (form.quantity === '' || Number(form.quantity) < 0 || !Number.isInteger(Number(form.quantity)))
      e.quantity = 'Enter a valid quantity'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function submit(ev) {
    ev.preventDefault()
    if (!validate()) return
    const payload = {
      name: form.name.trim(),
      sku: form.sku.trim(),
      price: Number(form.price),
      quantity: Number(form.quantity),
    }
    try {
      if (editing) {
        await api.put(`/products/${editing.id}`, payload)
        notify('Product updated')
      } else {
        await api.post('/products', payload)
        notify('Product added')
      }
      setShowForm(false)
      load()
    } catch (err) {
      notify(errorMessage(err), 'error')
    }
  }

  async function remove(p) {
    if (!confirm(`Delete "${p.name}"?`)) return
    try {
      await api.delete(`/products/${p.id}`)
      notify('Product deleted')
      load()
    } catch (err) {
      notify(errorMessage(err), 'error')
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return (
    <div>
      <div className="page-head">
        <h2>Products</h2>
        <button className="btn" onClick={openAdd}>
          + Add Product
        </button>
      </div>

      <div className="toolbar">
        <input
          placeholder="Search by name or SKU…"
          value={search}
          onChange={(e) => {
            setPage(1)
            setSearch(e.target.value)
          }}
        />
      </div>

      {loading ? (
        <Skeleton rows={5} />
      ) : products.length === 0 ? (
        <div className="empty">{search ? 'No matching products.' : 'No products yet.'}</div>
      ) : (
        <>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>SKU</th>
                  <th>Price</th>
                  <th>In stock</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td>{p.sku}</td>
                    <td>${Number(p.price).toFixed(2)}</td>
                    <td>{p.quantity}</td>
                    <td>
                      <div className="row-actions">
                        <button className="btn-link" onClick={() => openEdit(p)}>
                          Edit
                        </button>
                        <button className="btn-link" onClick={() => remove(p)}>
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="pagination">
            <button
              className="btn btn-secondary"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </button>
            <span className="muted">
              Page {page} of {totalPages}
            </span>
            <button
              className="btn btn-secondary"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        </>
      )}

      {showForm && (
        <Modal title={editing ? 'Edit Product' : 'Add Product'} onClose={() => setShowForm(false)}>
          <form onSubmit={submit}>
            <div className="form-group">
              <label>Name</label>
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
              />
              {errors.name && <div className="field-error">{errors.name}</div>}
            </div>
            <div className="form-group">
              <label>SKU / Code</label>
              <input
                value={form.sku}
                onChange={(e) => setForm({ ...form, sku: e.target.value })}
              />
              {errors.sku && <div className="field-error">{errors.sku}</div>}
            </div>
            <div className="form-group">
              <label>Price</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={form.price}
                onChange={(e) => setForm({ ...form, price: e.target.value })}
              />
              {errors.price && <div className="field-error">{errors.price}</div>}
            </div>
            <div className="form-group">
              <label>Quantity in stock</label>
              <input
                type="number"
                min="0"
                value={form.quantity}
                onChange={(e) => setForm({ ...form, quantity: e.target.value })}
              />
              {errors.quantity && <div className="field-error">{errors.quantity}</div>}
            </div>
            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                Cancel
              </button>
              <button type="submit" className="btn">
                {editing ? 'Save' : 'Add'}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
