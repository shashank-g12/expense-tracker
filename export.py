from app.export import export_report_to_csv as _export_report_to_csv

def export_report_to_csv(db, currency_symbol, user_id, filename='financial_report.csv'):
    """Wrapper function to call the app's export_report_to_csv function"""
    return _export_report_to_csv(db, currency_symbol, user_id, filename) 