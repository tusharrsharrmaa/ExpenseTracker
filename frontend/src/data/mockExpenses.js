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

export const initialExpenses = [
  {
    id: 1,
    title: 'Grocery run',
    amount: 1840,
    category: 'Food',
    expense_date: '2026-10-04',
  },
  {
    id: 2,
    title: 'Metro pass',
    amount: 600,
    category: 'Travel',
    expense_date: '2026-10-07',
  },
  {
    id: 3,
    title: 'Electricity bill',
    amount: 2450,
    category: 'Bills',
    expense_date: '2026-10-09',
  },
  {
    id: 4,
    title: 'Pharmacy',
    amount: 320,
    category: 'Health',
    expense_date: '2026-10-12',
  },
  {
    id: 5,
    title: 'Weekend dinner',
    amount: 980,
    category: 'Food',
    expense_date: '2026-10-18',
  },
  {
    id: 6,
    title: 'Headphones',
    amount: 3299,
    category: 'Shopping',
    expense_date: '2026-09-22',
  },
  {
    id: 7,
    title: 'Cab to airport',
    amount: 740,
    category: 'Travel',
    expense_date: '2026-09-14',
  },
  {
    id: 8,
    title: 'Internet',
    amount: 999,
    category: 'Bills',
    expense_date: '2026-09-01',
  },
]

export function formatMoney(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN')}`
}

export function formatDate(isoDate) {
  if (!isoDate) return '—'
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
