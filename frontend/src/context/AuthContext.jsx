import { createContext, useContext, useMemo, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('trackerUser')
    return stored ? JSON.parse(stored) : null
  })

  const value = useMemo(
    () => ({
      user,
      login(nextUser) {
        localStorage.setItem('trackerUser', JSON.stringify(nextUser))
        setUser(nextUser)
      },
      logout() {
        localStorage.removeItem('trackerUser')
        setUser(null)
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
