import { Link, useNavigate, useParams } from 'react-router-dom'
import ExpenseForm from '../components/ExpenseForm'
import { useExpenses } from '../context/ExpenseContext'

export default function EditExpense() {
  const { id } = useParams()
  const { getExpense, updateExpense } = useExpenses()
  const navigate = useNavigate()
  const expense = getExpense(id)

  if (!expense) {
    return (
      <section className="panel">
        <h2>Expense not found</h2>
        <p className="lede">That record is not in the local preview list.</p>
        <Link to="/expenses" className="btn">
          Back to expenses
        </Link>
      </section>
    )
  }

  function handleSubmit(updates) {
    updateExpense(id, updates)
    navigate('/expenses')
  }

  return (
    <section className="panel narrow">
      <h2>Edit expense</h2>
      <p className="lede">Update the details, then save. No API call is made yet.</p>
      <ExpenseForm
        initial={expense}
        onSubmit={handleSubmit}
        submitLabel="Update expense"
      />
    </section>
  )
}
