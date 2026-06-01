import { useEffect, useState } from 'react'
import api, { errorMessage } from '../api/client.js'
import Skeleton from '../components/Skeleton.jsx'
import { useToast } from '../components/Toast.jsx'

export default function Inventory() {
  const [transactions, setTransactions] = useState([])
  const [products, setProducts] = useState({})
  const [loading, setLoading] = useState(true)
  const notify = useToast()

  useEffect(() => {
    async function load() {
      try {
        const [txns, prods] = await Promise.all([
          api.get('/inventory-transactions'),
          api.get('/products', { params: { page_size: 1000 } }),
        ])
        setTransactions(txns.data)
        // Map product id -> name so we can show names instead of ids.
        const byId = {}
        prods.data.items.forEach((p) => {
          byId[p.id] = p.name
        })
        setProducts(byId)
      } catch (err) {
        notify(errorMessage(err), 'error')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <div>
      <div className="page-head">
        <h2>Inventory History</h2>
      </div>

      {loading ? (
        <Skeleton rows={5} />
      ) : transactions.length === 0 ? (
        <div className="empty">No stock movements yet.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>When</th>
                <th>Product</th>
                <th>Type</th>
                <th>Change</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map((t) => (
                <tr key={t.id}>
                  <td>{new Date(t.created_at).toLocaleString()}</td>
                  <td>{products[t.product_id] || '(deleted product)'}</td>
                  <td>{t.transaction_type}</td>
                  <td className={t.quantity_changed < 0 ? 'change-down' : 'change-up'}>
                    {t.quantity_changed > 0 ? `+${t.quantity_changed}` : t.quantity_changed}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
