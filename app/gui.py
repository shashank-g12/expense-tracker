import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os
from collections import defaultdict
from datetime import datetime

# Import application modules
from .database import Database
from .transaction import Transaction
from .user import User
from .report import generate_report
from .config import save_currency_symbol, load_currency_symbol
from .budget import Budget

class FinanceTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FinWise")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Initialize database
        self.db = Database()
        self.current_user = None
        self.budget = None
        self.transactions = []
        
        # Try to load currency symbol
        try:
            self.currency_symbol = load_currency_symbol()
        except:
            self.currency_symbol = '$'
        
        # Create the main frame for login/signup
        self.create_auth_frame()
    
    def create_auth_frame(self):
        # Clear existing frames if any
        for widget in self.root.winfo_children():
            widget.destroy()
        
        auth_frame = ttk.Frame(self.root, padding="20")
        auth_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(auth_frame, text="FinWise", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Login Button
        login_btn = ttk.Button(auth_frame, text="Login", command=self.show_login)
        login_btn.pack(pady=10, ipadx=20, ipady=10)
        
        # Signup Button
        signup_btn = ttk.Button(auth_frame, text="Sign Up", command=self.show_signup)
        signup_btn.pack(pady=10, ipadx=20, ipady=10)
        
        # Exit Button
        exit_btn = ttk.Button(auth_frame, text="Exit", command=self.root.quit)
        exit_btn.pack(pady=10, ipadx=20, ipady=10)
    
    def show_login(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")
        login_window.geometry("400x300")
        login_window.grab_set()  # Make window modal
        
        # Login form
        frame = ttk.Frame(login_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Login", font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(frame, text="Username:").pack(anchor="w", pady=(10, 0))
        username_entry = ttk.Entry(frame, width=40)
        username_entry.pack(pady=(0, 10), fill="x")
        
        ttk.Label(frame, text="Password:").pack(anchor="w", pady=(10, 0))
        password_entry = ttk.Entry(frame, width=40, show="*")
        password_entry.pack(pady=(0, 10), fill="x")
        
        def attempt_login():
            username = username_entry.get()
            password = password_entry.get()
            user = self.db.authenticate_user(username, password)
            if user:
                messagebox.showinfo("Success", f"Welcome back, {user.username}!")
                self.current_user = user
                login_window.destroy()
                self.initialize_main_app()
            else:
                messagebox.showerror("Error", "Invalid username or password.")
        
        login_btn = ttk.Button(frame, text="Login", command=attempt_login)
        login_btn.pack(pady=10)
        
        # Make Enter key work for login
        password_entry.bind("<Return>", lambda event: attempt_login())
    
    def show_signup(self):
        signup_window = tk.Toplevel(self.root)
        signup_window.title("Sign Up")
        signup_window.geometry("400x350")
        signup_window.grab_set()  # Make window modal
        
        # Signup form
        frame = ttk.Frame(signup_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Create New Account", font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(frame, text="Username:").pack(anchor="w", pady=(10, 0))
        username_entry = ttk.Entry(frame, width=40)
        username_entry.pack(pady=(0, 10), fill="x")
        
        ttk.Label(frame, text="Password:").pack(anchor="w", pady=(10, 0))
        password_entry = ttk.Entry(frame, width=40, show="*")
        password_entry.pack(pady=(0, 10), fill="x")
        
        ttk.Label(frame, text="Email (optional):").pack(anchor="w", pady=(10, 0))
        email_entry = ttk.Entry(frame, width=40)
        email_entry.pack(pady=(0, 10), fill="x")
        
        def attempt_signup():
            username = username_entry.get()
            password = password_entry.get()
            email = email_entry.get() or None
            
            if not username or not password:
                messagebox.showerror("Error", "Username and password are required.")
                return
            
            success = self.db.add_user(username, password, email)
            if success:
                messagebox.showinfo("Success", "Account created successfully! Please login.")
                signup_window.destroy()
                self.show_login()
            else:
                messagebox.showerror("Error", "Username or email already exists. Please try again.")
        
        signup_btn = ttk.Button(frame, text="Sign Up", command=attempt_signup)
        signup_btn.pack(pady=10)
    
    def initialize_main_app(self):
        # Set currency if not already set
        if not self.currency_symbol:
            self.currency_symbol = simpledialog.askstring("Currency", "Enter your preferred currency symbol:", parent=self.root) or '$'
            save_currency_symbol(self.currency_symbol)
        
        self.budget = Budget(self.currency_symbol)
        
        # Clear existing frames and create main app UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_main_interface()
    
    def create_main_interface(self):
        self.root.title(f"FinWise - {self.current_user.username}")
        
        # Create menu
        menu_frame = ttk.Frame(self.root)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        menu_label = ttk.Label(menu_frame, text="Menu", font=("Arial", 14, "bold"))
        menu_label.pack(pady=20)
        
        # Menu buttons
        buttons = [
            ("Add Transaction", self.show_add_transaction),
            ("View Transactions", self.show_transactions),
            ("Generate Report", self.show_report),
            ("Manage Budget", self.show_budget),
            ("Clear Transactions", self.clear_transactions),
            ("Export to CSV", self.export_to_csv),
            ("Logout", self.logout)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(menu_frame, text=text, command=command, width=20)
            btn.pack(pady=5, padx=10)
        
        # Content frame
        self.content_frame = ttk.Frame(self.root, padding="20")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Default view - welcome message
        welcome_label = ttk.Label(self.content_frame, text=f"Welcome, {self.current_user.username}!", font=("Arial", 16, "bold"))
        welcome_label.pack(pady=20)
        
        # Summary info
        self.update_dashboard()
    
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_dashboard(self):
        self.clear_content_frame()
        
        dashboard_label = ttk.Label(self.content_frame, text="Dashboard", font=("Arial", 16, "bold"))
        dashboard_label.pack(pady=20)
        
        # Get financial summary
        try:
            transactions, total_income, total_expenses, net_savings, category_expenses = generate_report(
                self.db, self.currency_symbol, self.current_user.id, return_data=True)
            
            # Create summary frame
            summary_frame = ttk.Frame(self.content_frame)
            summary_frame.pack(fill="x", pady=10)
            
            # Display financial summary
            summary_text = (
                f"Total Income: {self.currency_symbol}{total_income:.2f}\n"
                f"Total Expenses: {self.currency_symbol}{total_expenses:.2f}\n"
                f"Net Savings: {self.currency_symbol}{net_savings:.2f}"
            )
            
            summary_label = ttk.Label(summary_frame, text=summary_text, font=("Arial", 12))
            summary_label.pack(pady=10)
            
            # Display recent transactions if any
            if transactions:
                recent_label = ttk.Label(self.content_frame, text="Recent Transactions", font=("Arial", 14, "bold"))
                recent_label.pack(pady=(20, 10))
                
                # Create treeview for transactions
                columns = ("Date", "Type", "Amount", "Category", "Description")
                tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=10)
                
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=100)
                
                # Add transactions to the tree (most recent first, limit to 5)
                for txn in sorted(transactions, key=lambda t: str(t.date) if t.date else "", reverse=True)[:5]:
                    tree.insert("", tk.END, values=(
                        txn.date,
                        txn.type.capitalize(),
                        f"{self.currency_symbol}{txn.amount:.2f}",
                        txn.category,
                        txn.description
                    ))
                
                tree.pack(fill="both", expand=True, padx=10, pady=10)
        except Exception as e:
            error_label = ttk.Label(self.content_frame, text=f"Error loading dashboard: {str(e)}", font=("Arial", 12))
            error_label.pack(pady=20)
    
    def show_add_transaction(self):
        self.clear_content_frame()
        
        title = ttk.Label(self.content_frame, text="Add Transaction", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Transaction type
        type_label = ttk.Label(form_frame, text="Transaction Type:")
        type_label.pack(anchor="w", pady=(10, 0))
        
        transaction_type = tk.StringVar(value="expense")
        type_frame = ttk.Frame(form_frame)
        type_frame.pack(fill="x", pady=(0, 10))
        
        expense_rb = ttk.Radiobutton(type_frame, text="Expense", variable=transaction_type, value="expense")
        expense_rb.pack(side=tk.LEFT, padx=(0, 10))
        
        income_rb = ttk.Radiobutton(type_frame, text="Income", variable=transaction_type, value="income")
        income_rb.pack(side=tk.LEFT)
        
        # Amount
        amount_label = ttk.Label(form_frame, text="Amount:")
        amount_label.pack(anchor="w", pady=(10, 0))
        
        amount_entry = ttk.Entry(form_frame)
        amount_entry.pack(fill="x", pady=(0, 10))
        
        # Category
        category_label = ttk.Label(form_frame, text="Category:")
        category_label.pack(anchor="w", pady=(10, 0))
        
        category_entry = ttk.Entry(form_frame)
        category_entry.pack(fill="x", pady=(0, 10))
        
        # Description
        desc_label = ttk.Label(form_frame, text="Description:")
        desc_label.pack(anchor="w", pady=(10, 0))
        
        desc_entry = ttk.Entry(form_frame)
        desc_entry.pack(fill="x", pady=(0, 10))
        
        # Submit button
        def submit_transaction():
            try:
                amount = float(amount_entry.get())
                category = category_entry.get()
                description = desc_entry.get()
                txn_type = transaction_type.get()
                
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than zero.")
                    return
                
                if not category:
                    messagebox.showerror("Error", "Category is required.")
                    return
                
                # Create transaction and add to database
                transaction = Transaction(amount, category, description, txn_type)
                self.db.add_transaction(transaction, self.current_user.id)
                
                # Check budget if it's an expense
                if txn_type == "expense" and self.budget:
                    self.budget.check_budget(category, amount)
                
                messagebox.showinfo("Success", f"Transaction added successfully! {self.currency_symbol}{amount:.2f}")
                
                # Clear form
                amount_entry.delete(0, tk.END)
                category_entry.delete(0, tk.END)
                desc_entry.delete(0, tk.END)
                
                # Update dashboard
                self.update_dashboard()
            
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")
        
        submit_btn = ttk.Button(form_frame, text="Add Transaction", command=submit_transaction)
        submit_btn.pack(pady=20)
    
    def show_transactions(self):
        self.clear_content_frame()
        
        title = ttk.Label(self.content_frame, text="Transactions", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        # Get transactions from database
        transactions = self.db.get_all_transactions(self.current_user.id)
        
        if not transactions:
            no_txn_label = ttk.Label(self.content_frame, text="No transactions found.", font=("Arial", 12))
            no_txn_label.pack(pady=20)
            return
        
        # Create treeview for transactions
        columns = ("Date", "Type", "Amount", "Category", "Description")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add transactions to the tree (most recent first)
        for txn in sorted(transactions, key=lambda t: str(t.date) if t.date else "", reverse=True):
            tree.insert("", tk.END, values=(
                txn.date,
                txn.type.capitalize(),
                f"{self.currency_symbol}{txn.amount:.2f}",
                txn.category,
                txn.description
            ))
    
    def show_report(self):
        self.clear_content_frame()
        
        title = ttk.Label(self.content_frame, text="Financial Report", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        # Get report data
        try:
            transactions, total_income, total_expenses, net_savings, category_expenses = generate_report(
                self.db, self.currency_symbol, self.current_user.id, return_data=True)
            
            # Summary frame
            summary_frame = ttk.LabelFrame(self.content_frame, text="Summary")
            summary_frame.pack(fill="x", padx=10, pady=10, ipady=5)
            
            # Display financial summary
            ttk.Label(summary_frame, text=f"Total Income: {self.currency_symbol}{total_income:.2f}").pack(anchor="w", padx=10, pady=5)
            ttk.Label(summary_frame, text=f"Total Expenses: {self.currency_symbol}{total_expenses:.2f}").pack(anchor="w", padx=10, pady=5)
            ttk.Label(summary_frame, text=f"Net Savings: {self.currency_symbol}{net_savings:.2f}").pack(anchor="w", padx=10, pady=5)
            
            # Category breakdown
            if category_expenses:
                category_frame = ttk.LabelFrame(self.content_frame, text="Expenses by Category")
                category_frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Create treeview for categories
                columns = ("Category", "Amount", "Percentage")
                tree = ttk.Treeview(category_frame, columns=columns, show="headings", height=10)
                
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=100)
                
                # Calculate percentages
                for category, amount in category_expenses.items():
                    percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
                    tree.insert("", tk.END, values=(
                        category,
                        f"{self.currency_symbol}{amount:.2f}",
                        f"{percentage:.1f}%"
                    ))
                
                tree.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Export button
            export_btn = ttk.Button(self.content_frame, text="Export to CSV", command=self.export_to_csv)
            export_btn.pack(pady=10)
            
        except Exception as e:
            error_label = ttk.Label(self.content_frame, text=f"Error generating report: {str(e)}", font=("Arial", 12))
            error_label.pack(pady=20)
    
    def show_budget(self):
        self.clear_content_frame()
        
        title = ttk.Label(self.content_frame, text="Budget Management", font=("Arial", 16, "bold"))
        title.pack(pady=20)
        
        # Budget form
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(form_frame, text="Category:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        category_entry = ttk.Entry(form_frame, width=30)
        category_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(form_frame, text="Budget Amount:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        amount_entry = ttk.Entry(form_frame, width=30)
        amount_entry.grid(row=1, column=1, pady=5, padx=5)
        
        def set_budget():
            try:
                category = category_entry.get()
                amount = float(amount_entry.get())
                
                if not category:
                    messagebox.showerror("Error", "Category is required.")
                    return
                
                if amount <= 0:
                    messagebox.showerror("Error", "Amount must be greater than zero.")
                    return
                
                self.budget.set_budget(category, amount)
                messagebox.showinfo("Success", f"Budget set: {category} - {self.currency_symbol}{amount:.2f}")
                
                # Clear entries
                category_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)
                
                # Refresh budgets view
                display_budgets()
            
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount.")
        
        set_btn = ttk.Button(form_frame, text="Set Budget", command=set_budget)
        set_btn.grid(row=2, column=1, pady=10, padx=5, sticky="e")
        
        # Budget display
        budget_frame = ttk.LabelFrame(self.content_frame, text="Current Budgets")
        budget_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Function to display budgets in the treeview
        def display_budgets():
            # Clear existing items
            for widget in budget_frame.winfo_children():
                widget.destroy()
            
            if not self.budget.budgets:
                no_budget_label = ttk.Label(budget_frame, text="No budgets set yet.", font=("Arial", 12))
                no_budget_label.pack(pady=20)
                return
            
            # Create treeview for budgets
            columns = ("Category", "Budget Amount")
            tree = ttk.Treeview(budget_frame, columns=columns, show="headings")
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            # Add budgets to the tree
            for category, amount in self.budget.budgets.items():
                tree.insert("", tk.END, values=(
                    category,
                    f"{self.currency_symbol}{amount:.2f}"
                ))
            
            tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial display of budgets
        display_budgets()
    
    def clear_transactions(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete all transactions? This cannot be undone."):
            self.db.clear_transactions(self.current_user.id)
            messagebox.showinfo("Success", "All transactions have been deleted.")
            self.update_dashboard()
    
    def export_to_csv(self):
        from app.export import export_report_to_csv
        try:
            filename = f"financial_report_{self.current_user.username}_{datetime.now().strftime('%Y%m%d')}.csv"
            export_report_to_csv(self.db, self.currency_symbol, self.current_user.id, filename)
            messagebox.showinfo("Success", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {str(e)}")
    
    def logout(self):
        self.current_user = None
        self.budget = None
        self.create_auth_frame()


def start_gui():
    root = tk.Tk()
    app = FinanceTrackerGUI(root)
    root.mainloop() 