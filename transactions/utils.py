import xml.etree.ElementTree as ET
from datetime import datetime
from .models import Transaction, BankAccount
import re


# Keywords to identify relevant banks, such as SBI and Kotak
BANK_KEYWORDS = ['SBI', 'KOTAK']


def extract_amount(message):
    # Regex to match amounts following specific keywords
    match = re.search(r'\b(?:debited|credited|sent)\s+by\s+(\d+(?:\.\d+)?)', message, re.IGNORECASE)
    if match:
        return float(match.group(1))
    # Generic regex for amounts with or without 'Rs' prefix
    match = re.search(r'Rs\.?\s?(\d+(?:\.\d+)?)|(\d+(?:\.\d+)?)', message)
    if match:
        return float(match.group(1) or match.group(2))
    return 0.0


def parse_sms_xml(file,user):
    """
    Parses the uploaded XML file and extracts relevant bank transactions.
    Filters based on the presence of "SBI" or "Kotak" in the address.
    """
    tree = ET.parse(file)
    root = tree.getroot()
    
    transactions = []
    
    # Loop through each SMS in the XML file
    for message in root.findall('sms'):
        address = message.get('address')

        # Filter only messages from relevant banks (e.g., SBI, Kotak)
        if address and any(keyword in address for keyword in BANK_KEYWORDS):
            transaction_body = message.get('body')
            transaction_date = int(message.get('date')) // 1000  # Convert from milliseconds to seconds
            readable_date = message.get('readable_date')
            transaction_id = str(message.get('date_sent'))
            
            transaction_details = extract_transaction_details(transaction_body)
            
            if transaction_details:
                transactions.append({
                    'transaction_id': transaction_id,
                    'amount': transaction_details['amount'],
                    'transaction_type': transaction_details['transaction_type'],
                    'timestamp': datetime.fromtimestamp(transaction_date),
                    'description': '',
                    'new_balance': transaction_details.get('new_balance', None),
                    'readable_date': readable_date,
                })
    
    # Sort the transactions by timestamp (most recent first)
    transactions = sorted(transactions, key=lambda x: x['timestamp'], reverse=True)
    
    # Return only the most recent 10 transactions
    return transactions[:10]

def extract_transaction_details(body):
    """
    Extracts the details like amount, transaction type, and new balance from the SMS body.
    """
    import re
    if 'debited' in body:
        transaction_type = 'debit'
    elif 'credited' in body:
        transaction_type = 'credit'
    elif 'Sent' in body:
        transaction_type = 'debit'
    elif 'Received' in body:
        transaction_type = 'credit'
    else:
        return None

    # Extract the transaction amount from the message body (e.g., Rs.50.00)
    amount = extract_amount(body)

    # Extract the new balance from the message body (if available)
    balance_match = re.search(r'New balance: Rs\.(\d+\.\d{2})', body)
    new_balance = float(balance_match.group(1)) if balance_match else None

    return {
        'amount': amount,
        'transaction_type': transaction_type,
        'new_balance': new_balance,
    }

def save_transactions(transactions,bank_account):
    """
    Saves the list of transactions to the database, ensuring no duplicates.
    """
    for transaction_data in transactions:
        if not Transaction.objects.filter(transaction_id=transaction_data['transaction_id']).exists():

            Transaction.objects.create(
                account=bank_account,
                transaction_id=transaction_data['transaction_id'],
                amount=transaction_data['amount'],
                transaction_type=transaction_data['transaction_type'],
                description=transaction_data['description'],
                timestamp=transaction_data['timestamp'],
                new_balance=transaction_data['new_balance'],
                payment_type = 'Online',
            )
