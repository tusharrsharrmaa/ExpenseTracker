import { useNavigate } from 'react-router-dom'
import ExpenseForm from '../components/ExpenseForm'
import { useExpenses } from '../context/ExpenseContext'

export default function AddExpense() {
  const { addExpense } = useExpenses()
  const navigate = useNavigate()

  function handleSubmit(expense) {
    addExpense(expense)
    navigate('/expenses')
  }

  return (
    <section className="panel narrow">
      <h2>Log a new expense</h2>
      <p className="lede">Saved in the browser for now. FastAPI will be wired later.</p>
      <ExpenseForm onSubmit={handleSubmit} submitLabel="Save expense" />
    </section>
  )
}
