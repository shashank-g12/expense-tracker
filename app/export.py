import csv
from report import generate_report

def export_report_to_csv(db, currency_symbol, user_id, filename='financial_report.csv'):
    # Pass db, currency_symbol, and user_id to generate_report
    transactions, total_income, total_expenses, net_savings, category_expenses = generate_report(db, currency_symbol, user_id, return_data=True)

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Date', 'Type', 'Amount', 'Category', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for t in transactions:
            writer.writerow({'Date': t.date, 'Type': t.type, 'Amount': t.amount, 'Category': t.category, 'Description': t.description})

    print(f"Report exported to {filename}")
