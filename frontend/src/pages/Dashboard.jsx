import { useEffect, useState } from 'react'
import api, { errorMessage } from '../api/client.js'
import Skeleton from '../components/Skeleton.jsx'
import { useToast } from '../components/Toast.jsx'

const cards = [
  { key: 'totalProducts', label: 'Products' },
  { key: 'totalCustomers', label: 'Customers' },
  { key: 'totalOrders', label: 'Orders' },
]

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const notify = useToast()

  useEffect(() => {
    api
      .get('/dashboard')
      .then((res) => setData(res.data))
      .catch((err) => notify(errorMessage(err), 'error'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Skeleton rows={4} />
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
          <div className="stat-value">{data.lowStockProducts.length}</div>
        </div>
      </div>

      <div className="card">
        <h3>Low stock products</h3>
        {data.lowStockProducts.length === 0 ? (
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
                {data.lowStockProducts.map((p) => (
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
