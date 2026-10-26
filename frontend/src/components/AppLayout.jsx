import { useState } from 'react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Sidebar from './Sidebar'

const titles = {
  '/': 'Dashboard',
  '/expenses': 'Expenses',
  '/expenses/new': 'Add expense',
  '/summary': 'Monthly summary',
}

export default function AppLayout() {
  const { user } = useAuth()
  const location = useLocation()
  const [open, setOpen] = useState(false)

  if (!user) {
    return <Navigate to="/login" replace />
  }

  const pageTitle = location.pathname.includes('/edit')
    ? 'Edit expense'
    : titles[location.pathname] || 'Expense tracker'

  return (
    <div className="app-shell">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      {open ? (
        <button
          type="button"
          className="backdrop"
          aria-label="Close menu"
          onClick={() => setOpen(false)}
        />
      ) : null}
      <div className="app-main">
        <header className="topbar">
          <button
            type="button"
            className="menu-btn"
            onClick={() => setOpen(true)}
          >
            Menu
          </button>
          <div>
            <p className="eyebrow">Personal finance</p>
            <h1>{pageTitle}</h1>
          </div>
        </header>
        <div className="page">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
