export default function AuthLayout({ title, subtitle, children }) {
  return (
    <div className="auth-shell">
      <section className="auth-panel">
        <p className="brand-kicker">Smart Expense Tracker</p>
        <h1>{title}</h1>
        <p className="lede">{subtitle}</p>
        {children}
      </section>
    </div>
  )
}
