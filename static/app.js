const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

const authView = document.getElementById("auth-view");
const appView = document.getElementById("app-view");
const authError = document.getElementById("auth-error");
const expenseError = document.getElementById("expense-error");
const userNameEl = document.getElementById("user-name");
const summaryMonth = document.getElementById("summary-month");
const summaryCards = document.getElementById("summary-cards");
const expenseRows = document.getElementById("expense-rows");
const emptyState = document.getElementById("empty-state");
const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const expenseForm = document.getElementById("expense-form");
const filterForm = document.getElementById("filter-form");

function currentUser() {
  const raw = localStorage.getItem("ledgerUser");
  return raw ? JSON.parse(raw) : null;
}

function setUser(user) {
  localStorage.setItem("ledgerUser", JSON.stringify(user));
}

function money(value) {
  return `₹${Number(value || 0).toLocaleString("en-IN")}`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });

  let data = null;
  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const detail = data && data.detail ? data.detail : "Something went wrong";
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  return data;
}

function showAuth() {
  authView.classList.remove("hidden");
  appView.classList.add("hidden");
}

function showApp(user) {
  authView.classList.add("hidden");
  appView.classList.remove("hidden");
  userNameEl.textContent = user.name || "there";
}

function fillMonthSelects() {
  const monthFilter = filterForm.elements.month;
  summaryMonth.innerHTML = "";
  monthFilter.innerHTML = '<option value="">All</option>';
  MONTHS.forEach((name, index) => {
    const value = String(index + 1);
    summaryMonth.insertAdjacentHTML("beforeend", `<option value="${value}">${name}</option>`);
    monthFilter.insertAdjacentHTML("beforeend", `<option value="${value}">${name}</option>`);
  });
  summaryMonth.value = String(new Date().getMonth() + 1);
}

function setError(el, message) {
  if (!message) {
    el.classList.add("hidden");
    el.textContent = "";
    return;
  }
  el.textContent = message;
  el.classList.remove("hidden");
}

async function loadSummary() {
  const month = Number(summaryMonth.value);
  const data = await api(`/expenses/summary?month=${month}`);
  const entries = Object.entries(data);
  const total = entries.reduce((sum, [, amount]) => sum + Number(amount), 0);
  summaryCards.innerHTML = `
    <article class="card">
      <span>Total</span>
      <strong>${money(total)}</strong>
    </article>
    ${entries.map(([category, amount]) => `
      <article class="card">
        <span>${category}</span>
        <strong>${money(amount)}</strong>
      </article>
    `).join("")}
  `;
  if (!entries.length) {
    summaryCards.innerHTML = `
      <article class="card">
        <span>Total</span>
        <strong>${money(0)}</strong>
      </article>
    `;
  }
}

async function loadExpenses() {
  const user = currentUser();
  const params = new URLSearchParams({ user_ID: String(user.id) });
  const category = filterForm.elements.category.value;
  const month = filterForm.elements.month.value;
  const minAmount = filterForm.elements.min_amount.value;
  const maxAmount = filterForm.elements.max_amount.value;

  if (category) params.set("category", category);
  if (month) params.set("month", month);
  if (minAmount) params.set("min_amount", minAmount);
  if (maxAmount) params.set("max_amount", maxAmount);

  const expenses = await api(`/expenses/?${params.toString()}`);
  expenseRows.innerHTML = expenses.map((item) => `
    <tr>
      <td>${item.expense_date || "—"}</td>
      <td>${item.title || "Untitled"}</td>
      <td>${item.category || "—"}</td>
      <td class="num">${money(item.amount)}</td>
    </tr>
  `).join("");
  emptyState.classList.toggle("hidden", expenses.length > 0);
}

async function refresh() {
  await Promise.all([loadSummary(), loadExpenses()]);
}

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("is-active"));
    tab.classList.add("is-active");
    const mode = tab.dataset.auth;
    loginForm.classList.toggle("hidden", mode !== "login");
    registerForm.classList.toggle("hidden", mode !== "register");
    setError(authError, "");
  });
});

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setError(authError, "");
  try {
    const form = new FormData(loginForm);
    const user = await api("/users/login", {
      method: "POST",
      body: JSON.stringify({
        email: form.get("email"),
        password: form.get("password")
      })
    });
    setUser(user);
    showApp(user);
    await refresh();
  } catch (error) {
    setError(authError, error.message);
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setError(authError, "");
  try {
    const form = new FormData(registerForm);
    const user = await api("/users/", {
      method: "POST",
      body: JSON.stringify({
        name: form.get("name"),
        email: form.get("email"),
        password_hash: form.get("password")
      })
    });
    setUser(user);
    showApp(user);
    await refresh();
  } catch (error) {
    setError(authError, error.message);
  }
});

expenseForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setError(expenseError, "");
  const user = currentUser();
  const form = new FormData(expenseForm);
  try {
    await api("/expenses/", {
      method: "POST",
      body: JSON.stringify({
        title: form.get("title") || null,
        amount: Number(form.get("amount")),
        category: form.get("category"),
        expense_date: form.get("expense_date"),
        user_ID: user.id
      })
    });
    expenseForm.reset();
    expenseForm.elements.expense_date.value = new Date().toISOString().slice(0, 10);
    await refresh();
  } catch (error) {
    setError(expenseError, error.message);
  }
});

filterForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await loadExpenses();
});

document.getElementById("reset-filters").addEventListener("click", async () => {
  filterForm.reset();
  await loadExpenses();
});

summaryMonth.addEventListener("change", loadSummary);

document.getElementById("logout-btn").addEventListener("click", () => {
  localStorage.removeItem("ledgerUser");
  showAuth();
});

fillMonthSelects();
expenseForm.elements.expense_date.value = new Date().toISOString().slice(0, 10);

const saved = currentUser();
if (saved) {
  showApp(saved);
  refresh().catch(() => {
    localStorage.removeItem("ledgerUser");
    showAuth();
  });
}
