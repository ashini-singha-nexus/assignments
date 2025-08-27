"""
Bank Ledger System

This module provides classes and functions for managing bank accounts
and processing financial transactions using decimal arithmetic for
accurate monetary calculations.
"""

from dataclasses import dataclass
from decimal import Decimal
import csv
from typing import List, Tuple, Dict

@dataclass
class BankAccount:
    """
    A bank account with transaction processing capabilities.
    
    Attributes:
        owner (str): The name of the account owner
        balance (Decimal): The current account balance
    """
    owner: str
    balance: Decimal
    
    def __init__(self, owner: str, balance: Decimal):
        """
        Initialize a new bank account.
        
        Args:
            owner (str): The name of the account owner
            balance (Decimal): The initial account balance
        """
        self.owner = owner
        self.initial_balance = Decimal(balance)  # Store initial balance separately
        self.balance = Decimal(balance)
        self._transactions = []  # Internal transaction history
    
    def apply(self, tx: dict) -> None:
        """
        Apply a single transaction to the account.
        
        Args:
            tx (dict): Transaction details with keys 'type', 'amount', 'note'
            
        Raises:
            ValueError: If transaction type is invalid or funds are insufficient
        """
        tx_type = tx['type']
        amount = Decimal(tx['amount'])
        note = tx['note']
        
        # Validate transaction type
        if tx_type not in ('deposit', 'withdraw'):
            raise ValueError(f"Invalid transaction type: {tx_type}")
        
        # Process transaction
        if tx_type == 'deposit':
            self.balance += amount
        elif tx_type == 'withdraw':
            # Check for sufficient funds before withdrawal
            if amount > self.balance:
                raise ValueError("insufficient funds")
            self.balance -= amount
        
        # Record transaction in history
        self._transactions.append((tx_type, amount, note))
    
    def statement(self) -> List[Tuple]:
        """
        Generate an account statement with transaction history.
        
        Returns:
            List of tuples containing (index, type, amount, balance_after, note)
            for each transaction in chronological order
        """
        stmt = []
        running_balance = self.initial_balance  # Start from initial balance
        
        # Replay all transactions to calculate running balances
        for i, (tx_type, amount, note) in enumerate(self._transactions, 1):
            if tx_type == 'deposit':
                running_balance += amount
            else:  # withdrawal
                running_balance -= amount
            stmt.append((i, tx_type, amount, running_balance, note))
        
        return stmt

def load_transactions(csv_path: str) -> List[Dict]:
    """
    Load transactions from a CSV file.
    
    Args:
        csv_path (str): Path to the CSV file containing transactions
        
    Returns:
        List of dictionaries with transaction data
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValueError: If the CSV format is invalid
    """
    transactions = []
    try:
        with open(csv_path, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert amount to Decimal for precise arithmetic
                row['amount'] = Decimal(row['amount'])
                transactions.append(row)
    except FileNotFoundError:
        raise FileNotFoundError(f"Transaction file not found: {csv_path}")
    except Exception as e:
        raise ValueError(f"Error parsing CSV file: {str(e)}")
    
    return transactions

def apply_all(account: BankAccount, txns: List[Dict]) -> None:
    """
    Apply a list of transactions to an account in order.
    
    Args:
        account (BankAccount): The account to apply transactions to
        txns (List[Dict]): List of transaction dictionaries
        
    Raises:
        ValueError: If any transaction fails (fail-fast behavior)
    """
    for tx in txns:
        try:
            account.apply(tx)
        except ValueError as e:
            # Re-raise with additional context
            raise ValueError(f"Transaction failed: {str(e)}")