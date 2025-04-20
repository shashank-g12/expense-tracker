import json
import os

def save_currency_symbol(symbol):
    config = {
        'DB_FILE': 'finance_tracker.db',
        'DATE_FORMAT': '%Y-%m-%d %H:%M:%S',
        'CURRENCY_SYMBOL': symbol,
    }
    with open('config.json', 'w') as config_file:
        json.dump(config, config_file)

def load_config():
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            return config
    except FileNotFoundError:
        return {'CURRENCY_SYMBOL': '$'}

def load_currency_symbol():
    config = load_config()
    return config.get('CURRENCY_SYMBOL', '$')

