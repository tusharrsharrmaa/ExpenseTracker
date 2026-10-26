import { useMemo, useState } from 'react'
import StatCard from '../components/StatCard'
import { useExpenses } from '../context/ExpenseContext'
import { MONTHS, formatMoney } from '../data/mockExpenses'

export default function MonthlySummary() {
  const { expenses } = useExpenses()
  const [month, setMonth] = useState(String(new Date().getMonth() + 1))

  const summary = useMemo(() => {
    const rows = expenses.filter(
      (item) => Number(item.expense_date.slice(5, 7)) === Number(month),
    )
    const byCategory = rows.reduce((acc, item) => {
      acc[item.category] = (acc[item.category] || 0) + item.amount
      return acc
    }, {})
    const total = rows.reduce((sum, item) => sum + item.amount, 0)
    return { rows, byCategory, total }
  }, [expenses, month])

  return (
    <div className="stack-lg">
      <section className="panel">
        <div className="panel-head">
          <h2>{MONTHS[Number(month) - 1]} overview</h2>
          <label className="inline">
            Month
            <select value={month} onChange={(event) => setMonth(event.target.value)}>
              {MONTHS.map((name, index) => (
                <option key={name} value={String(index + 1)}>
                  {name}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="stats-grid">
          <StatCard label="Total spent" value={formatMoney(summary.total)} />
          <StatCard label="Transactions" value={String(summary.rows.length)} />
          <StatCard
            label="Top category"
            value={
              Object.entries(summary.byCategory).sort((a, b) => b[1] - a[1])[0]?.[0] ||
              '—'
            }
          />
        </div>
      </section>

      <section className="panel">
        <h2>By category</h2>
        <div className="summary-grid">
          {Object.entries(summary.byCategory).map(([category, amount]) => (
            <article key={category} className="summary-card">
              <p>{category}</p>
              <strong>{formatMoney(amount)}</strong>
              <span>
                {summary.total
                  ? `${Math.round((amount / summary.total) * 100)}% of month`
                  : '0%'}
              </span>
            </article>
          ))}
          {!Object.keys(summary.byCategory).length ? (
            <p className="empty">No expenses in this month.</p>
          ) : null}
        </div>
      </section>
    </div>
  )
}
