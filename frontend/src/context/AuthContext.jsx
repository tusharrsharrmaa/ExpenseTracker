import { createContext, useContext, useMemo, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('set_user')
    return saved ? JSON.parse(saved) : null
  })

  const value = useMemo(
    () => ({
      user,
      login(nextUser) {
        setUser(nextUser)
        localStorage.setItem('set_user', JSON.stringify(nextUser))
      },
      logout() {
        setUser(null)
        localStorage.removeItem('set_user')
      },
    }),
    [user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
