import { Link } from 'react-router-dom'
import StatCard from '../components/StatCard'
import ExpenseTable from '../components/ExpenseTable'
import { useExpenses } from '../context/ExpenseContext'
import { formatMoney } from '../data/mockExpenses'

export default function Dashboard() {
  const { expenses } = useExpenses()
  const month = new Date().getMonth() + 1
  const thisMonth = expenses.filter(
    (item) => Number(item.expense_date.slice(5, 7)) === month,
  )
  const total = thisMonth.reduce((sum, item) => sum + item.amount, 0)
  const largest = thisMonth.reduce(
    (max, item) => (item.amount > max ? item.amount : max),
    0,
  )
  const byCategory = thisMonth.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + item.amount
    return acc
  }, {})

  return (
    <div className="stack-lg">
      <section className="stats-grid">
        <StatCard label="This month" value={formatMoney(total)} hint={`${thisMonth.length} entries`} />
        <StatCard label="Largest spend" value={formatMoney(largest)} hint="Single transaction" />
        <StatCard
          label="Categories used"
          value={String(Object.keys(byCategory).length)}
          hint="Active this month"
        />
      </section>

      <section className="panel">
        <div className="panel-head">
          <h2>Category mix</h2>
          <Link to="/summary" className="link">
            Open summary
          </Link>
        </div>
        <div className="bars">
          {Object.entries(byCategory).map(([category, amount]) => (
            <div key={category} className="bar-row">
              <span>{category}</span>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${Math.max(8, (amount / total) * 100)}%` }}
                />
              </div>
              <strong>{formatMoney(amount)}</strong>
            </div>
          ))}
          {!Object.keys(byCategory).length ? (
            <p className="empty">No spending recorded for this month.</p>
          ) : null}
        </div>
      </section>

      <section className="panel">
        <div className="panel-head">
          <h2>Recent expenses</h2>
          <Link to="/expenses/new" className="btn primary">
            Add expense
          </Link>
        </div>
        <ExpenseTable expenses={expenses.slice(0, 5)} />
      </section>
    </div>
  )
}
