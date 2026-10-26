import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import ExpenseTable from '../components/ExpenseTable'
import { useExpenses } from '../context/ExpenseContext'
import { CATEGORIES, MONTHS } from '../data/mockExpenses'

export default function Expenses() {
  const { expenses, deleteExpense } = useExpenses()
  const [filters, setFilters] = useState({
    category: '',
    month: '',
    min_amount: '',
    max_amount: '',
  })

  const filtered = useMemo(() => {
    return expenses.filter((item) => {
      if (filters.category && item.category !== filters.category) return false
      if (
        filters.month &&
        Number(item.expense_date.slice(5, 7)) !== Number(filters.month)
      ) {
        return false
      }
      if (filters.min_amount && item.amount < Number(filters.min_amount)) {
        return false
      }
      if (filters.max_amount && item.amount > Number(filters.max_amount)) {
        return false
      }
      return true
    })
  }, [expenses, filters])

  function update(event) {
    const { name, value } = event.target
    setFilters((current) => ({ ...current, [name]: value }))
  }

  return (
    <div className="stack-lg">
      <section className="panel">
        <div className="panel-head">
          <h2>All expenses</h2>
          <Link to="/expenses/new" className="btn primary">
            Add expense
          </Link>
        </div>
        <form className="filters" onSubmit={(event) => event.preventDefault()}>
          <label>
            Category
            <select name="category" value={filters.category} onChange={update}>
              <option value="">All</option>
              {CATEGORIES.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </label>
          <label>
            Month
            <select name="month" value={filters.month} onChange={update}>
              <option value="">All</option>
              {MONTHS.map((name, index) => (
                <option key={name} value={String(index + 1)}>
                  {name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Min
            <input
              name="min_amount"
              type="number"
              min="1"
              value={filters.min_amount}
              onChange={update}
              placeholder="0"
            />
          </label>
          <label>
            Max
            <input
              name="max_amount"
              type="number"
              min="1"
              value={filters.max_amount}
              onChange={update}
              placeholder="10000"
            />
          </label>
          <button
            type="button"
            className="btn ghost"
            onClick={() =>
              setFilters({
                category: '',
                month: '',
                min_amount: '',
                max_amount: '',
              })
            }
          >
            Reset
          </button>
        </form>
        <ExpenseTable expenses={filtered} onDelete={deleteExpense} />
      </section>
    </div>
  )
}
