import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

from app.database import Database
from app.transaction import Transaction
from app.user import User
from app.report import generate_report
from app.config import save_currency_symbol, load_currency_symbol
from app.budget import Budget
from export import export_report_to_csv


def login_menu():
    print("\nPersonal Finance Tracker")
    print("1. Login")
    print("2. Sign Up")
    print("3. Exit")
    return input("Choose an option: ")

def main_menu():
    print("\nPersonal Finance Tracker")
    print("1. Add Transaction")
    print("2. View Transactions")
    print("3. Generate Report")
    print("4. Manage Budget")
    print("5. Clear All Transactions")
    print("6. Export Report to CSV") 
    print("7. Logout")
    return input("Choose an option: ")

def login(db):
    username = input("Username: ")
    password = input("Password: ")
    
    user = db.authenticate_user(username, password)
    if user:
        print(f"Welcome back, {user.username}!")
        return user
    else:
        print("Invalid username or password.")
        return None

def signup(db):
    print("\nCreate New Account")
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email (optional): ")
    
    if not email:
        email = None
    
    success = db.add_user(username, password, email)
    if success:
        print(f"Account created successfully! Please login.")
        return True
    else:
        print("Username or email already exists. Please try again.")
        return False

def add_transaction(db, currency_symbol, user_id):
    amount = float(input("Enter amount: "))
    category = input("Enter category: ")
    description = input("Enter description: ")
    transaction_type = input("Enter type (income/expense): ").lower()

    # Create a Transaction object
    transaction = Transaction(amount, category, description, transaction_type)
    
    # Add the transaction to the database
    db.add_transaction(transaction, user_id)
    print(f"Transaction added successfully! {currency_symbol}{amount:.2f}")

    transactions = db.get_all_transactions(user_id)

def view_transactions(db, currency_symbol, user_id):
    transactions = db.get_all_transactions(user_id)
    if not transactions:
        print("No transactions found.")
        return
    
    for txn in transactions:
        print(f"{txn.date}: {txn.type.capitalize()} - {currency_symbol}{txn.amount:.2f} - {txn.category} - {txn.description}")

def manage_budget(budget, currency_symbol):
    while True:
        print("\nBudget Management")
        print("1. Set Budget")
        print("2. View Budgets")
        print("3. Back to Main Menu")
        choice = input("Choose an option: ")

        if choice == '1':
            category = input("Enter category: ")
            amount = float(input("Enter budget amount: "))
            budget.set_budget(category, amount)
        elif choice == '2':
            budget.view_budgets()
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")        

def main():
    db = Database()
    current_user = None
    
    while True:
        if not current_user:
            choice = login_menu()
            if choice == '1':
                current_user = login(db)
            elif choice == '2':
                signup(db)
            elif choice == '3':
                print("Thank you for using Personal Finance Tracker!")
                sys.exit(0)
            else:
                print("Invalid choice. Please try again.")
        else:
            # Ask user to set currency symbol if not already set
            try:
                CURRENCY_SYMBOL = load_currency_symbol()
            except:
                currency_symbol = input("Enter your preferred currency symbol: ")
                save_currency_symbol(currency_symbol)
                CURRENCY_SYMBOL = load_currency_symbol()

            budget = Budget(CURRENCY_SYMBOL)

            while current_user:
                choice = main_menu()
                if choice == '1':
                    add_transaction(db, CURRENCY_SYMBOL, current_user.id)
                elif choice == '2':
                    view_transactions(db, CURRENCY_SYMBOL, current_user.id)
                elif choice == '3':
                    generate_report(db, CURRENCY_SYMBOL, current_user.id)
                elif choice == '4':
                    manage_budget(budget, CURRENCY_SYMBOL)
                elif choice == '5':
                    # Clear all transactions
                    db.clear_transactions(current_user.id)
                elif choice == '6':
                    export_report_to_csv(db, CURRENCY_SYMBOL, current_user.id)
                elif choice == '7':
                    print("Logging out...")
                    current_user = None
                    break
                else:
                    print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
