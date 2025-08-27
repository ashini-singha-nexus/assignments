"""
Bank Ledger Command Line Interface

This module provides a command-line interface for managing bank accounts
and processing transactions from CSV files.
"""

import argparse
from decimal import Decimal
from bank import BankAccount, load_transactions, apply_all

def main():
    """Main entry point for the bank ledger CLI application."""
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Process bank transactions from a CSV file and generate a statement'
    )
    parser.add_argument(
        '--owner', 
        required=True, 
        help='Name of the account owner'
    )
    parser.add_argument(
        '--balance', 
        required=True, 
        type=Decimal, 
        help='Initial account balance (decimal value)'
    )
    parser.add_argument(
        '--from-csv', 
        required=True, 
        help='Path to CSV file containing transactions'
    )
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Create bank account with initial balance
    account = BankAccount(args.owner, args.balance)
    
    try:
        # Load transactions from CSV file
        transactions = load_transactions(args.from_csv)
        
        # Apply all transactions to the account
        apply_all(account, transactions)
        
        # Generate and display account statement
        print(f"Statement for {account.owner}")
        print("-" * 60)
        print(f"{'Index':<6} {'Type':<10} {'Amount':<12} {'Balance':<12} {'Note'}")
        print("-" * 60)
        
        for idx, tx_type, amount, balance, note in account.statement():
            print(f"{idx:<6} {tx_type:<10} {amount:<12} {balance:<12} {note}")
        
        print("-" * 60)
        print(f"Final Balance: {account.balance}")
        
    except Exception as e:
        # Handle any errors that occur during processing
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == '__main__':
    main()