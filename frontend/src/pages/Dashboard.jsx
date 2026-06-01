import { useEffect, useState } from 'react'
import api, { errorMessage } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'

const cards = [
  { key: 'total_products', label: 'Products' },
  { key: 'total_customers', label: 'Customers' },
  { key: 'total_orders', label: 'Orders' },
]

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const notify = useToast()

  useEffect(() => {
    api
      .get('/dashboard/summary')
      .then((res) => setData(res.data))
      .catch((err) => notify(errorMessage(err), 'error'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="muted">Loading…</p>
  if (!data) return <p className="muted">Could not load dashboard.</p>

  return (
    <div>
      <div className="page-head">
        <h2>Dashboard</h2>
      </div>

      <div className="stat-grid">
        {cards.map((c) => (
          <div className="card stat-card" key={c.key}>
            <div className="stat-label">{c.label}</div>
            <div className="stat-value">{data[c.key]}</div>
          </div>
        ))}
        <div className="card stat-card">
          <div className="stat-label">Low stock</div>
          <div className="stat-value">{data.low_stock_products.length}</div>
        </div>
      </div>

      <div className="card">
        <h3>Low stock products</h3>
        {data.low_stock_products.length === 0 ? (
          <p className="muted">Everything is well stocked.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>SKU</th>
                  <th>In stock</th>
                </tr>
              </thead>
              <tbody>
                {data.low_stock_products.map((p) => (
                  <tr key={p.id}>
                    <td>{p.name}</td>
                    <td>{p.sku}</td>
                    <td>
                      <span className="badge badge-low">{p.quantity} left</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
