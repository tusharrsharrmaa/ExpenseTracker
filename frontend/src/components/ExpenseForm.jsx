import { useState } from 'react'
import { CATEGORIES } from '../data/mockExpenses'

export default function ExpenseForm({ initial, onSubmit, submitLabel }) {
  const [form, setForm] = useState({
    title: initial?.title || '',
    amount: initial?.amount || '',
    category: initial?.category || 'Food',
    expense_date: initial?.expense_date || new Date().toISOString().slice(0, 10),
  })

  function update(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  function handleSubmit(event) {
    event.preventDefault()
    onSubmit({
      ...form,
      amount: Number(form.amount),
    })
  }

  return (
    <form className="form-card" onSubmit={handleSubmit}>
      <label>
        Title
        <input
          name="title"
          value={form.title}
          onChange={update}
          required
          placeholder="Lunch, cab, electricity..."
        />
      </label>
      <div className="form-row">
        <label>
          Amount
          <input
            name="amount"
            type="number"
            min="1"
            value={form.amount}
            onChange={update}
            required
            placeholder="500"
          />
        </label>
        <label>
          Date
          <input
            name="expense_date"
            type="date"
            value={form.expense_date}
            onChange={update}
            required
          />
        </label>
      </div>
      <label>
        Category
        <select name="category" value={form.category} onChange={update}>
          {CATEGORIES.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </label>
      <button type="submit" className="btn primary">
        {submitLabel}
      </button>
    </form>
  )
}
