import { Route, Routes } from 'react-router-dom'
import Nav from './components/Nav.jsx'
import { ToastProvider } from './components/Toast.jsx'
import Dashboard from './pages/Dashboard.jsx'
import Products from './pages/Products.jsx'
import Customers from './pages/Customers.jsx'
import Orders from './pages/Orders.jsx'
import Inventory from './pages/Inventory.jsx'

export default function App() {
  return (
    <ToastProvider>
      <Nav />
      <main className="container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/products" element={<Products />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/inventory" element={<Inventory />} />
        </Routes>
      </main>
    </ToastProvider>
  )
}
