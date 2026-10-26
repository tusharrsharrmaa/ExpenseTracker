import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })

  if (user) {
    return <Navigate to="/" replace />
  }

  function handleSubmit(event) {
    event.preventDefault()
    login({ name: form.name, email: form.email })
    navigate('/')
  }

  return (
    <AuthLayout
      title="Create your ledger"
      subtitle="Register locally so you can walk through the app screens."
    >
      <form className="stack" onSubmit={handleSubmit}>
        <label>
          Name
          <input
            required
            value={form.name}
            onChange={(event) =>
              setForm((current) => ({ ...current, name: event.target.value }))
            }
            placeholder="Your name"
          />
        </label>
        <label>
          Email
          <input
            type="email"
            required
            value={form.email}
            onChange={(event) =>
              setForm((current) => ({ ...current, email: event.target.value }))
            }
            placeholder="you@email.com"
          />
        </label>
        <label>
          Password
          <input
            type="password"
            required
            minLength={3}
            value={form.password}
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                password: event.target.value,
              }))
            }
          />
        </label>
        <button type="submit" className="btn primary">
          Create account
        </button>
      </form>
      <p className="auth-switch">
        Already have an account? <Link to="/login">Sign in</Link>
      </p>
    </AuthLayout>
  )
}
