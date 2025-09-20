

  const logoutBtn = document.getElementById('logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      alert('Logged out successfully!');
      window.location.href = 'login.html';
    });
  }

const expenseForm = document.getElementById('expense-form');
const expenseList = document.getElementById('expense-list');
const totalAmount = document.getElementById('total-amount');
const clearExpensesBtn = document.getElementById('clear-expenses');

let expenses = JSON.parse(localStorage.getItem('expenses')) || [];

if (expenseForm) {
  expenseForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = document.getElementById('expense-name').value.trim();
    const amount = parseFloat(document.getElementById('expense-amount').value);

    if (name && !isNaN(amount) && amount > 0) {
      expenses.push({ name, amount });
      localStorage.setItem('expenses', JSON.stringify(expenses));
      updateExpenseList();
      updateTotalAmount();
      expenseForm.reset();
    }
  });
}

function updateExpenseList() {
  expenseList.innerHTML = '';
  expenses.forEach((expense, index) => {
    const expenseItem = document.createElement('div');
    expenseItem.className = 'expense-item mb-2';
    expenseItem.innerHTML = `
      ${expense.name} - &#8377; ${expense.amount.toFixed(2)}
      <button class="btn btn-sm btn-primary" id="btn-delete" onclick="deleteExpense(${index})">X</button>
    
    `;
    expenseList.appendChild(expenseItem);
  });
}
function updateTotalAmount() {
  const total = expenses.reduce((acc, expense) => acc + expense.amount, 0);
  totalAmount.textContent = total.toFixed(2);
}

function deleteExpense(index) {
  expenses.splice(index, 1);
  localStorage.setItem('expenses', JSON.stringify(expenses));
  updateExpenseList();
  updateTotalAmount();
}

if (clearExpensesBtn) {
  clearExpensesBtn.addEventListener('click', () => {
    if (confirm("Are you sure you want to clear all expenses?")) {
      expenses = [];
      localStorage.removeItem('expenses');
      updateExpenseList();
      updateTotalAmount();
    }
  });
}

if (expenseForm) {
  updateExpenseList();
  updateTotalAmount();
}

  document.addEventListener("DOMContentLoaded", () => {
    const today = new Date();
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById("current-date").textContent = today.toLocaleDateString('en-IN', options);
  });

