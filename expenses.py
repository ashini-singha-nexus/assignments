import logging
import csv
from typing import List, Dict, Tuple
from pathlib import Path
logger = logging.getLogger(__name__)

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
        with open(path, 'r', newline='') as csvfile: #todo check why we are using 
            reader = csv.DictReader(csvfile)
            required_fields = ["category", "amount"]  # Required columns
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                # Validate required fields
                if not all(field in row and row[field].strip() for field in required_fields):
                    logger.warning(f"Row {row_num} skipped: missing required fields")
                    skipped += 1
                    continue
                
                # Validate amount
                try:
                    amount = float(row['amount'])
                    if amount <= 0:
                        raise ValueError("Amount must be positive")
                except (ValueError, TypeError):
                    logger.warning(f"Row {row_num} skipped: invalid amount '{row.get('amount')}'")
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
        logger.error(f"File not found: {path}")
        raise
    except PermissionError:
        logger.error(f"Permission denied: {path}")
        raise
    except Exception as e:
        logger.critical(f"Unexpected error reading file {path}: {e}")
        raise
    
    logger.info(f"Finished loading {len(expenses)} expenses, skipped {skipped} rows")
    return expenses, skipped

def sum_by_category(expenses: List[Dict]) -> Dict[str, float]:
    """
    Summarize expenses by category.
    
    Args:
        expenses: List of expense dictionaries
        
    Returns:
        Dictionary with category as key and total amount as value
    """
    # todo: use pydentic 
    summary = {}
    for expense in expenses:
        category = expense['category']
        amount = expense['amount']
        summary[category] = summary.get(category, 0) + amount
    
    return summary