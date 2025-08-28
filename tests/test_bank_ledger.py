import pytest
import csv
import tempfile
import os
from decimal import Decimal
from assignments.bank import BankAccount, load_transactions, apply_all


def create_test_csv(content: str) -> str:
    """Helper function to create a temporary CSV file for testing."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", newline="") as f:
        f.write(content)
    return path


def test_bank_account_initialization():
    """Test BankAccount initialization with dataclass and Decimal."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))

    assert account.owner == "Alice"
    assert account.balance == Decimal("100.00")
    assert isinstance(account.balance, Decimal)


def test_bank_account_apply_deposit():
    """Test applying a deposit transaction."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))
    transaction = {"type": "deposit", "amount": Decimal("50.00"), "note": "payday"}

    account.apply(transaction)

    assert account.balance == Decimal("150.00")


def test_bank_account_apply_withdrawal():
    """Test applying a withdrawal transaction."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))
    transaction = {"type": "withdraw", "amount": Decimal("25.50"), "note": "coffee"}

    account.apply(transaction)

    assert account.balance == Decimal("74.50")


def test_bank_account_apply_invalid_type():
    """Test applying transaction with invalid type."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))
    transaction = {"type": "invalid", "amount": Decimal("50.00"), "note": "test"}

    with pytest.raises(ValueError, match="Invalid transaction type"):
        account.apply(transaction)


def test_bank_account_statement():
    """Test generating account statement."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))

    # Apply some transactions
    transactions = [
        {"type": "deposit", "amount": Decimal("50.00"), "note": "bonus"},
        {"type": "withdraw", "amount": Decimal("25.50"), "note": "lunch"},
        {"type": "withdraw", "amount": Decimal("10.00"), "note": "coffee"},
    ]

    for tx in transactions:
        account.apply(tx)

    statement = account.statement()

    assert len(statement) == 3

    # Check first transaction
    assert statement[0] == (1, "deposit", Decimal("50.00"), Decimal("150.00"), "bonus")
    # Check second transaction
    assert statement[1] == (2, "withdraw", Decimal("25.50"), Decimal("124.50"), "lunch")
    # Check third transaction
    assert statement[2] == (
        3,
        "withdraw",
        Decimal("10.00"),
        Decimal("114.50"),
        "coffee",
    )


def test_load_transactions_valid():
    """Test loading valid transactions from CSV."""
    csv_content = """type,amount,note
deposit,100.00,initial funding
withdraw,25.55,coffee & snacks
withdraw,10.00,lunch
deposit,50.00,payday top-up"""

    path = create_test_csv(csv_content)

    try:
        transactions = load_transactions(path)

        assert len(transactions) == 4
        assert transactions[0] == {
            "type": "deposit",
            "amount": Decimal("100.00"),
            "note": "initial funding",
        }
        assert transactions[1] == {
            "type": "withdraw",
            "amount": Decimal("25.55"),
            "note": "coffee & snacks",
        }
        assert transactions[2] == {
            "type": "withdraw",
            "amount": Decimal("10.00"),
            "note": "lunch",
        }
        assert transactions[3] == {
            "type": "deposit",
            "amount": Decimal("50.00"),
            "note": "payday top-up",
        }

        # Verify all amounts are Decimal
        for tx in transactions:
            assert isinstance(tx["amount"], Decimal)

    finally:
        os.unlink(path)


def test_apply_all_successful():
    """Test applying all transactions successfully."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))

    transactions = [
        {"type": "deposit", "amount": Decimal("50.00"), "note": "bonus"},
        {"type": "withdraw", "amount": Decimal("25.50"), "note": "lunch"},
        {"type": "withdraw", "amount": Decimal("10.00"), "note": "coffee"},
        {"type": "deposit", "amount": Decimal("20.00"), "note": "refund"},
    ]

    apply_all(account, transactions)

    assert account.balance == Decimal("134.50")  # 100 + 50 - 25.50 - 10 + 20


def test_apply_all_overdraft_fail_fast():
    """Test fail-fast behavior on overdraft attempt."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))

    transactions = [
        {"type": "withdraw", "amount": Decimal("50.00"), "note": "valid"},
        {"type": "withdraw", "amount": Decimal("60.00"), "note": "overdraft"},
        {"type": "deposit", "amount": Decimal("20.00"), "note": "should not apply"},
    ]

    with pytest.raises(ValueError, match="insufficient funds"):
        apply_all(account, transactions)

    # Verify only the first transaction was applied (fail-fast)
    assert account.balance == Decimal("50.00")  # 100 - 50


def test_apply_all_empty_transactions():
    """Test applying empty transactions list."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))

    apply_all(account, [])

    assert account.balance == Decimal("100.00")  # Unchanged


def test_decimal_precision_rounding():
    """Test that Decimal maintains proper precision for financial calculations."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))

    transactions = [
        {"type": "deposit", "amount": Decimal("0.01"), "note": "penny"},
        {"type": "deposit", "amount": Decimal("0.02"), "note": "pennies"},
        {"type": "deposit", "amount": Decimal("0.03"), "note": "more pennies"},
    ]

    apply_all(account, transactions)

    # Should be exactly 100.06, not 100.06000000000001
    assert account.balance == Decimal("100.06")


def test_large_transactions():
    """Test handling of large transaction amounts."""
    account = BankAccount(owner="Business", balance=Decimal("1000000.00"))

    transactions = [
        {"type": "withdraw", "amount": Decimal("500000.00"), "note": "large purchase"},
        {
            "type": "deposit",
            "amount": Decimal("250000.00"),
            "note": "investment return",
        },
    ]

    apply_all(account, transactions)

    assert account.balance == Decimal("750000.00")


def test_transaction_ordering():
    """Test that transactions are applied in correct order."""
    account = BankAccount(owner="Alice", balance=Decimal("100.00"))

    transactions = [
        {"type": "withdraw", "amount": Decimal("50.00"), "note": "first"},
        {"type": "deposit", "amount": Decimal("200.00"), "note": "second"},
        {"type": "withdraw", "amount": Decimal("100.00"), "note": "third"},
    ]

    apply_all(account, transactions)

    # Balance should be: 100 - 50 = 50, + 200 = 250, - 100 = 150
    assert account.balance == Decimal("150.00")

    # Verify statement order
    statement = account.statement()
    assert statement[0][3] == Decimal("50.00")  # Balance after first
    assert statement[1][3] == Decimal("250.00")  # Balance after second
    assert statement[2][3] == Decimal("150.00")  # Balance after third
