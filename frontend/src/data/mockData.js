export const CATEGORIES = [
  'Food',
  'Travel',
  'Bills',
  'Shopping',
  'Health',
  'Other',
]

export const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
]

export const INITIAL_EXPENSES = [
  {
    id: 1,
    title: 'Grocery run',
    amount: 1840,
    category: 'Food',
    expense_date: '2026-09-12',
  },
  {
    id: 2,
    title: 'Metro pass',
    amount: 600,
    category: 'Travel',
    expense_date: '2026-09-08',
  },
  {
    id: 3,
    title: 'Electricity bill',
    amount: 2450,
    category: 'Bills',
    expense_date: '2026-09-03',
  },
  {
    id: 4,
    title: 'Pharmacy',
    amount: 320,
    category: 'Health',
    expense_date: '2026-08-28',
  },
  {
    id: 5,
    title: 'Weekend dinner',
    amount: 1290,
    category: 'Food',
    expense_date: '2026-09-14',
  },
  {
    id: 6,
    title: 'Headphones',
    amount: 3999,
    category: 'Shopping',
    expense_date: '2026-08-19',
  },
]

export function formatMoney(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN')}`
}

export function formatDate(value) {
  if (!value) return '—'
  return new Date(`${value}T00:00:00`).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
