import { createContext, useContext, useMemo, useState } from 'react'
import { initialExpenses } from '../data/mockExpenses'

const ExpenseContext = createContext(null)

export function ExpenseProvider({ children }) {
  const [expenses, setExpenses] = useState(initialExpenses)

  const value = useMemo(
    () => ({
      expenses,
      addExpense(expense) {
        setExpenses((current) => [
          { ...expense, id: Date.now() },
          ...current,
        ])
      },
      updateExpense(id, updates) {
        setExpenses((current) =>
          current.map((item) =>
            item.id === Number(id) ? { ...item, ...updates, id: Number(id) } : item,
          ),
        )
      },
      deleteExpense(id) {
        setExpenses((current) => current.filter((item) => item.id !== Number(id)))
      },
      getExpense(id) {
        return expenses.find((item) => item.id === Number(id))
      },
    }),
    [expenses],
  )

  return (
    <ExpenseContext.Provider value={value}>{children}</ExpenseContext.Provider>
  )
}

export function useExpenses() {
  const context = useContext(ExpenseContext)
  if (!context) {
    throw new Error('useExpenses must be used inside ExpenseProvider')
  }
  return context
}
