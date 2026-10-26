import { NavLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/expenses', label: 'Expenses' },
  { to: '/expenses/new', label: 'Add expense' },
  { to: '/summary', label: 'Monthly summary' },
]

export default function Sidebar({ open, onClose }) {
  const { user, logout } = useAuth()

  return (
    <aside className={`sidebar ${open ? 'is-open' : ''}`}>
      <div className="brand">
        <span className="brand-mark">₹</span>
        <div>
          <p className="brand-kicker">Smart Tracker</p>
          <strong>Ledger</strong>
        </div>
      </div>

      <nav className="nav-links">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/' || link.to === '/expenses'}
            onClick={onClose}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-user">
        <p>{user?.name || 'Guest'}</p>
        <span>{user?.email || 'local preview'}</span>
        <button type="button" className="btn ghost" onClick={logout}>
          Sign out
        </button>
      </div>
    </aside>
  )
}
