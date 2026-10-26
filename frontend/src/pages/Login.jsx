import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import AuthLayout from '../components/AuthLayout'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })

  if (user) {
    return <Navigate to="/" replace />
  }

  function handleSubmit(event) {
    event.preventDefault()
    login({
      name: form.email.split('@')[0] || 'You',
      email: form.email,
    })
    navigate('/')
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to review spending. This screen is UI-only for now."
    >
      <form className="stack" onSubmit={handleSubmit}>
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
          Sign in
        </button>
      </form>
      <p className="auth-switch">
        New here? <Link to="/register">Create an account</Link>
      </p>
    </AuthLayout>
  )
}
