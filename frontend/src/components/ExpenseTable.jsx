import { Link } from 'react-router-dom'
import { formatDate, formatMoney } from '../data/mockExpenses'

export default function ExpenseTable({ expenses, onDelete }) {
  if (!expenses.length) {
    return (
      <p className="empty">No expenses match these filters yet.</p>
    )
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Title</th>
            <th>Category</th>
            <th className="num">Amount</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((item) => (
            <tr key={item.id}>
              <td>{formatDate(item.expense_date)}</td>
              <td>{item.title}</td>
              <td>
                <span className={`badge ${item.category.toLowerCase()}`}>
                  {item.category}
                </span>
              </td>
              <td className="num">{formatMoney(item.amount)}</td>
              <td className="actions">
                <Link className="link" to={`/expenses/${item.id}/edit`}>
                  Edit
                </Link>
                {onDelete ? (
                  <button
                    type="button"
                    className="link danger"
                    onClick={() => onDelete(item.id)}
                  >
                    Delete
                  </button>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
