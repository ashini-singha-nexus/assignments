import csv
from typing import List, Dict, Tuple
from pathlib import Path

def load_expenses(path: str) -> Tuple[List[Dict], int]:
    """
    Load expenses from a CSV file, skipping invalid rows.
    
    Args:
        path: Path to the CSV file
        
    Returns:
        Tuple of (list of valid expense dictionaries, count of skipped rows)
    """
    expenses = []
    skipped = 0
    
    try:
        with open(path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                # Validate required fields
                if 'category' not in row or 'amount' not in row:
                    skipped += 1
                    continue
                
                # Validate amount
                try:
                    amount = float(row['amount'])
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                except (ValueError, TypeError):
                    skipped += 1
                    continue
                
                # Create expense record
                expense = {
                    'category': row['category'].strip(),
                    'amount': amount,
                    'date': row.get('date', '').strip()  # Date is optional
                }
                expenses.append(expense)
                
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {path}")
    except PermissionError:
        raise PermissionError(f"Permission denied: {path}")
    except Exception as e:
        raise Exception(f"Error reading file: {e}")
    
    return expenses, skipped

def sum_by_category(expenses: List[Dict]) -> Dict[str, float]:
    """
    Summarize expenses by category.
    
    Args:
        expenses: List of expense dictionaries
        
    Returns:
        Dictionary with category as key and total amount as value
    """
    summary = {}
    for expense in expenses:
        category = expense['category']
        amount = expense['amount']
        summary[category] = summary.get(category, 0) + amount
    
    return summary