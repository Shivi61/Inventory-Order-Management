import { useEffect, useState } from 'react'
import api, { errorMessage } from '../api/client.js'
import Modal from '../components/Modal.jsx'
import Skeleton from '../components/Skeleton.jsx'
import { useToast } from '../components/Toast.jsx'

const STATUSES = ['pending', 'confirmed', 'completed', 'cancelled']

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [products, setProducts] = useState([])
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [detail, setDetail] = useState(null)
  const notify = useToast()

  // new-order form state
  const [customerId, setCustomerId] = useState('')
  const [lines, setLines] = useState([{ product_id: '', quantity: 1 }])
  const [formError, setFormError] = useState('')

  async function load() {
    setLoading(true)
    try {
      const [o, p, c] = await Promise.all([
        api.get('/orders'),
        api.get('/products', { params: { page_size: 1000 } }),
        api.get('/customers'),
      ])
      setOrders(o.data)
      setProducts(p.data.items)
      setCustomers(c.data)
    } catch (err) {
      notify(errorMessage(err), 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  function openForm() {
    setCustomerId('')
    setLines([{ product_id: '', quantity: 1 }])
    setFormError('')
    setShowForm(true)
  }

  function updateLine(i, field, value) {
    setLines((ls) => ls.map((l, idx) => (idx === i ? { ...l, [field]: value } : l)))
  }

  function addLine() {
    setLines((ls) => [...ls, { product_id: '', quantity: 1 }])
  }

  function removeLine(i) {
    setLines((ls) => ls.filter((_, idx) => idx !== i))
  }

  // Running total shown while building the order.
  const total = lines.reduce((sum, l) => {
    const product = products.find((p) => p.id === l.product_id)
    if (!product) return sum
    return sum + Number(product.price) * Number(l.quantity || 0)
  }, 0)

  async function submit(ev) {
    ev.preventDefault()
    setFormError('')
    if (!customerId) {
      setFormError('Please choose a customer')
      return
    }
    const items = lines
      .filter((l) => l.product_id && Number(l.quantity) > 0)
      .map((l) => ({ product_id: l.product_id, quantity: Number(l.quantity) }))
    if (items.length === 0) {
      setFormError('Add at least one product')
      return
    }
    try {
      await api.post('/orders', { customer_id: customerId, items })
      notify('Order created')
      setShowForm(false)
      load()
    } catch (err) {
      notify(errorMessage(err), 'error')
    }
  }

  async function cancelOrder(o) {
    if (!confirm(`Cancel order #${o.id}? Stock will be returned.`)) return
    try {
      await api.delete(`/orders/${o.id}`)
      notify('Order cancelled')
      load()
    } catch (err) {
      notify(errorMessage(err), 'error')
    }
  }

  async function changeStatus(order, status) {
    if (status === order.status) return
    try {
      const res = await api.patch(`/orders/${order.id}/status`, { status })
      notify(`Order marked ${status}`)
      setDetail(res.data)
      load()
    } catch (err) {
      notify(errorMessage(err), 'error')
    }
  }

  function customerName(id) {
    const c = customers.find((x) => x.id === id)
    return c ? c.full_name : `#${id}`
  }

  return (
    <div>
      <div className="page-head">
        <h2>Orders</h2>
        <button className="btn" onClick={openForm}>
          + New Order
        </button>
      </div>

      {loading ? (
        <Skeleton rows={5} />
      ) : orders.length === 0 ? (
        <div className="empty">No orders yet.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Items</th>
                <th>Total</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td>#{o.id.slice(0, 8)}</td>
                  <td>{customerName(o.customer_id)}</td>
                  <td>{o.items.length}</td>
                  <td>${Number(o.total_amount).toFixed(2)}</td>
                  <td>
                    <span className={`badge badge-${o.status}`}>{o.status}</span>
                  </td>
                  <td>
                    <div className="row-actions">
                      <button className="btn btn-sm btn-outline" onClick={() => setDetail(o)}>
                        View
                      </button>
                      <button
                        className="btn btn-sm btn-danger-soft"
                        onClick={() => cancelOrder(o)}
                        disabled={o.status === 'cancelled'}
                      >
                        Cancel
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <Modal title="New Order" onClose={() => setShowForm(false)}>
          <form onSubmit={submit} noValidate>
            <div className="form-group">
              <label>Customer</label>
              <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
                <option value="">Select a customer…</option>
                {customers.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.full_name}
                  </option>
                ))}
              </select>
            </div>

            <label className="muted">Products</label>
            {lines.map((line, i) => (
              <div className="line-item" key={i}>
                <select
                  value={line.product_id}
                  onChange={(e) => updateLine(i, 'product_id', e.target.value)}
                >
                  <option value="">Select product…</option>
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} (stock: {p.quantity})
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  min="1"
                  value={line.quantity}
                  onChange={(e) => updateLine(i, 'quantity', e.target.value)}
                />
                <button
                  type="button"
                  className="icon-btn"
                  onClick={() => removeLine(i)}
                  disabled={lines.length === 1}
                >
                  &times;
                </button>
              </div>
            ))}
            <button type="button" className="btn-link" onClick={addLine}>
              + Add product
            </button>

            <div className="order-total">Total: ${total.toFixed(2)}</div>

            {formError && <div className="field-error">{formError}</div>}

            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                Cancel
              </button>
              <button type="submit" className="btn">
                Create Order
              </button>
            </div>
          </form>
        </Modal>
      )}

      {detail && (
        <Modal title={`Order #${detail.id}`} onClose={() => setDetail(null)}>
          <p>
            <strong>Customer:</strong> {customerName(detail.customer_id)}
          </p>
          <div className="form-group">
            <label htmlFor="order-status">Status</label>
            <select
              id="order-status"
              value={detail.status}
              onChange={(e) => changeStatus(detail, e.target.value)}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>Qty</th>
                  <th>Unit price</th>
                  <th>Subtotal</th>
                </tr>
              </thead>
              <tbody>
                {detail.items.map((it, i) => (
                  <tr key={i}>
                    <td>{it.product_name || `#${it.product_id}`}</td>
                    <td>{it.quantity}</td>
                    <td>${Number(it.unit_price).toFixed(2)}</td>
                    <td>${(Number(it.unit_price) * it.quantity).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="order-total">Total: ${Number(detail.total_amount).toFixed(2)}</div>
        </Modal>
      )}
    </div>
  )
}
