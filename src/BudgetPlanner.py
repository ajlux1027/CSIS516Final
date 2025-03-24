import tkinter as tk
from tkinter import messagebox, Toplevel
import sqlite3
import locale
from datetime import datetime

class BudgetTracker:
    def __init__(self, root):
        # Initialize main window
        self.root = root
        self.root.title("Personal Budget Tracker")
        self.root.geometry("400x500")
        
        # Connect to SQLite database
        self.conn = sqlite3.connect("budget.db")
        self.cursor = self.conn.cursor()
        self.create_table()
        
        # Load total income and expenses from database
        self.income, self.expenses = self.load_totals()
        
        # Currency selection dropdown
        self.currency_var = tk.StringVar(value='USD')
        self.currency_options = {'USD': 'en_US.UTF-8', 'EUR': 'de_DE.UTF-8', 'GBP': 'en_GB.UTF-8'}
        
        self.currency_menu = tk.OptionMenu(root, self.currency_var, *self.currency_options.keys(), command=self.update_currency)
        self.currency_menu.pack()
        
        self.set_locale()
        
        # Display labels for income, expenses, and balance
        self.label_income = tk.Label(root, text=f"Total Income: {self.format_currency(self.income)}", font=("Arial", 12))
        self.label_income.pack()
        
        self.label_expenses = tk.Label(root, text=f"Total Expenses: {self.format_currency(self.expenses)}", font=("Arial", 12))
        self.label_expenses.pack()
        
        self.label_balance = tk.Label(root, text=f"Spare Income: {self.format_currency(self.income - self.expenses)}", font=("Arial", 14, "bold"))
        self.label_balance.pack()
        
        # Entry fields for amount and description
        self.entry_amount = tk.Entry(root)
        self.entry_amount.pack()
        
        self.entry_label = tk.Entry(root)
        self.entry_label.pack()
        self.entry_label.insert(0, "Enter description")
        
        # Buttons for adding income, expenses, viewing transactions, and clearing input
        self.button_income = tk.Button(root, text="Add Income", command=self.add_income)
        self.button_income.pack()
        
        self.button_expense = tk.Button(root, text="Add Expense", command=self.add_expense)
        self.button_expense.pack()
        
        self.button_view = tk.Button(root, text="View Transactions", command=self.view_transactions)
        self.button_view.pack()
        
        self.button_clear = tk.Button(root, text="Clear", command=self.clear_entries)
        self.button_clear.pack()

        # Button for clearing the database
        self.button_clear_db = tk.Button(root, text="Clear Database", command=self.clear_database)
        self.button_clear_db.pack()
    
    def create_table(self):
        # Create transactions table if it does not exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL,
                type TEXT,
                description TEXT,
                date TEXT
            )
        ''')
        self.conn.commit()
        
    def set_locale(self):
        # Set locale for currency formatting
        locale.setlocale(locale.LC_ALL, self.currency_options[self.currency_var.get()])
        
    def update_currency(self, value):
        # Update currency format when the user selects a different currency
        self.set_locale()
        self.update_display()
        
    def format_currency(self, amount):
        # Format numbers as currency
        return locale.currency(amount, grouping=True)
        
    def parse_number(self, number_str):
        # Parse and convert user input to a float, removing commas if necessary
        try:
            number_str = number_str.replace(",", "")  # Remove commas
            return float(number_str)
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a valid number.")
            return None
        
    def add_transaction(self, amount, type, description):
        # Add a transaction to the database
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO transactions (amount, type, description, date) VALUES (?, ?, ?, ?)", (amount, type, description, date))
        self.conn.commit()
    
    def add_income(self):
        # Add an income entry
        amount = self.parse_number(self.entry_amount.get())
        description = self.entry_label.get()
        if amount is not None and description:
            self.income += amount
            self.add_transaction(amount, "income", description)
            self.update_display()
        
    def add_expense(self):
        # Add an expense entry
        amount = self.parse_number(self.entry_amount.get())
        description = self.entry_label.get()
        if amount is not None and description:
            self.expenses += amount
            self.add_transaction(amount, "expense", description)
            self.update_display()
    
    def load_totals(self):
        # Load total income and expenses from the database
        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='income'")
        income = self.cursor.fetchone()[0] or 0
        
        self.cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='expense'")
        expenses = self.cursor.fetchone()[0] or 0
        
        return income, expenses
    
    def update_display(self):
        # Update displayed values
        self.label_income.config(text=f"Total Income: {self.format_currency(self.income)}")
        self.label_expenses.config(text=f"Total Expenses: {self.format_currency(self.expenses)}")
        self.label_balance.config(text=f"Spare Income: {self.format_currency(self.income - self.expenses)}")
        self.clear_entries()
    
    def clear_entries(self):
        # Clear input fields
        self.entry_amount.delete(0, tk.END)
        self.entry_label.delete(0, tk.END)
        self.entry_label.insert(0, "Enter description")
    
    def view_transactions(self):
        # Open a new window to display transaction history
        window = Toplevel(self.root)
        window.title("Transaction History")
        window.geometry("500x400")
        
        self.cursor.execute("SELECT amount, type, description, date FROM transactions ORDER BY date DESC")
        transactions = self.cursor.fetchall()
        
        text = tk.Text(window, wrap=tk.WORD)
        text.pack(expand=True, fill=tk.BOTH)
        
        for transaction in transactions:
            text.insert(tk.END, f"{transaction[1].capitalize()} - {self.format_currency(transaction[0])} - {transaction[2]} - {transaction[3]}\n")
    
    def clear_database(self):
        # Ask for user confirmation before clearing the database
        confirm = messagebox.askyesno("Clear Database", "Are you sure you want to delete all transactions? This action cannot be undone.")
        if confirm:
            self.cursor.execute("DELETE FROM transactions")
            self.conn.commit()
            
            # Reset values
            self.income = 0
            self.expenses = 0
            self.update_display()
            
            messagebox.showinfo("Success", "All transactions have been deleted.")

if __name__ == "__main__":
    # Create and run the main application window
    root = tk.Tk()
    app = BudgetTracker(root)
    root.mainloop()
