import { useEffect, useState } from 'react'
import api, { errorMessage } from '../api/client.js'
import Modal from '../components/Modal.jsx'
import { useToast } from '../components/Toast.jsx'

const empty = { full_name: '', email: '', phone: '' }

export default function Customers() {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(empty)
  const [errors, setErrors] = useState({})
  const notify = useToast()

  async function load() {
    setLoading(true)
    try {
      const res = await api.get('/customers')
      setCustomers(res.data)
    } catch (err) {
      notify(errorMessage(err), 'error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  function openAdd() {
    setForm(empty)
    setErrors({})
    setShowForm(true)
  }

  function validate() {
    const e = {}
    if (!form.full_name.trim()) e.full_name = 'Name is required'
    // simple email shape check
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = 'Enter a valid email'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function submit(ev) {
    ev.preventDefault()
    if (!validate()) return
    try {
      await api.post('/customers', {
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || null,
      })
      notify('Customer added')
      setShowForm(false)
      load()
    } catch (err) {
      notify(errorMessage(err), 'error')
    }
  }

  async function remove(c) {
    if (!confirm(`Delete "${c.full_name}"?`)) return
    try {
      await api.delete(`/customers/${c.id}`)
      notify('Customer deleted')
      load()
    } catch (err) {
      notify(errorMessage(err), 'error')
    }
  }

  return (
    <div>
      <div className="page-head">
        <h2>Customers</h2>
        <button className="btn" onClick={openAdd}>
          + Add Customer
        </button>
      </div>

      {loading ? (
        <p className="muted">Loading…</p>
      ) : customers.length === 0 ? (
        <div className="empty">No customers yet.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {customers.map((c) => (
                <tr key={c.id}>
                  <td>{c.full_name}</td>
                  <td>{c.email}</td>
                  <td>{c.phone || '—'}</td>
                  <td>
                    <button className="btn-link" onClick={() => remove(c)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <Modal title="Add Customer" onClose={() => setShowForm(false)}>
          <form onSubmit={submit}>
            <div className="form-group">
              <label>Full name</label>
              <input
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              />
              {errors.full_name && <div className="field-error">{errors.full_name}</div>}
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
              {errors.email && <div className="field-error">{errors.email}</div>}
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
            </div>
            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>
                Cancel
              </button>
              <button type="submit" className="btn">
                Add
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}
