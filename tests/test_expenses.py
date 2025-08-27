import pytest
import csv
import tempfile
import os
from pathlib import Path

# Import the functions to test
from assignments.expenses import load_expenses, sum_by_category

def create_test_csv(content: str) -> str:
    """Helper function to create a temporary CSV file for testing."""
    fd, path = tempfile.mkstemp(suffix='.csv')
    with os.fdopen(fd, 'w', newline='') as f:
        f.write(content)
    return path

def test_load_expenses_valid_data():
    """Test loading valid expenses with complete data."""
    csv_content = """category,amount,date
food,12.50,2025-08-01
travel,100.00,2025-08-03
food,30,
misc,10.0,2025-08-04
travel,100,2025-08-06"""
    
    path = create_test_csv(csv_content)
    
    try:
        expenses, skipped = load_expenses(path)
        
        assert len(expenses) == 5
        assert skipped == 0
        
        # Verify data is parsed correctly
        assert expenses[0] == {'category': 'food', 'amount': 12.50, 'date': '2025-08-01'}
        assert expenses[1] == {'category': 'travel', 'amount': 100.00, 'date': '2025-08-03'}
        assert expenses[2] == {'category': 'food', 'amount': 30.0, 'date': ''}
        assert expenses[3] == {'category': 'misc', 'amount': 10.0, 'date': '2025-08-04'}
        assert expenses[4] == {'category': 'travel', 'amount': 100.0, 'date': '2025-08-06'}
        
    finally:
        os.unlink(path)

def test_load_expenses_missing_date():
    """Test loading expenses with missing date (should be allowed)."""
    csv_content = """category,amount,date
food,12.50,
travel,100.00,
food,30,"""
    
    path = create_test_csv(csv_content)
    
    try:
        expenses, skipped = load_expenses(path)
        
        assert len(expenses) == 3
        assert skipped == 0
        
        for expense in expenses:
            assert expense['date'] == ''
        
    finally:
        os.unlink(path)

def test_load_expenses_invalid_amounts():
    """Test loading expenses with invalid amounts (should be skipped)."""
    csv_content = """category,amount,date
food,invalid,2025-08-01
travel,100,2025-08-03
food,,2025-08-02
misc,-5,2025-08-04
entertainment,0,2025-08-05
shopping,25.75,2025-08-06"""
    
    path = create_test_csv(csv_content)
    
    try:
        expenses, skipped = load_expenses(path)
        
        # Only valid rows: travel(100), shopping(25.75)
        assert len(expenses) == 2
        assert skipped == 4  # invalid, empty, negative, zero
        
        assert expenses[0] == {'category': 'travel', 'amount': 100.0, 'date': '2025-08-03'}
        assert expenses[1] == {'category': 'shopping', 'amount': 25.75, 'date': '2025-08-06'}
        
    finally:
        os.unlink(path)

def test_load_expenses_missing_required_columns():
    """Test loading CSV with missing required columns."""
    csv_content = """category,date
food,2025-08-01
travel,2025-08-03"""
    
    path = create_test_csv(csv_content)
    
    try:
        expenses, skipped = load_expenses(path)
        
        assert len(expenses) == 0
        assert skipped == 2  # Both rows missing amount column
        
    finally:
        os.unlink(path)

def test_load_expenses_empty_file():
    """Test loading an empty CSV file."""
    csv_content = """category,amount,date"""
    
    path = create_test_csv(csv_content)
    
    try:
        expenses, skipped = load_expenses(path)
        
        assert len(expenses) == 0
        assert skipped == 0
        
    finally:
        os.unlink(path)

def test_load_expenses_file_not_found():
    """Test handling of non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_expenses('non_existent_file.csv')

def test_sum_by_category_basic():
    """Test basic category summarization."""
    expenses = [
        {'category': 'food', 'amount': 12.50, 'date': '2025-08-01'},
        {'category': 'travel', 'amount': 100.0, 'date': '2025-08-03'},
        {'category': 'food', 'amount': 30.0, 'date': ''},
        {'category': 'misc', 'amount': 10.0, 'date': '2025-08-04'},
        {'category': 'travel', 'amount': 100.0, 'date': '2025-08-06'}
    ]
    
    summary = sum_by_category(expenses)
    
    expected = {
        'food': 42.50,
        'travel': 200.00,
        'misc': 10.00
    }
    
    assert summary == expected
    assert len(summary) == 3

def test_sum_by_category_empty_list():
    """Test summarizing empty expenses list."""
    expenses = []
    summary = sum_by_category(expenses)
    assert summary == {}

def test_sum_by_category_single_category():
    """Test summarizing expenses with only one category."""
    expenses = [
        {'category': 'food', 'amount': 10.0, 'date': '2025-08-01'},
        {'category': 'food', 'amount': 20.0, 'date': '2025-08-02'},
        {'category': 'food', 'amount': 30.0, 'date': '2025-08-03'}
    ]
    
    summary = sum_by_category(expenses)
    
    assert summary == {'food': 60.0}
    assert len(summary) == 1

def test_sum_by_category_floating_point_precision():
    """Test that floating point precision is handled correctly."""
    expenses = [
        {'category': 'food', 'amount': 0.1, 'date': '2025-08-01'},
        {'category': 'food', 'amount': 0.2, 'date': '2025-08-02'},
        {'category': 'food', 'amount': 0.3, 'date': '2025-08-03'}
    ]
    
    summary = sum_by_category(expenses)
    
    # Should be exactly 0.6, not 0.6000000000000001
    assert summary['food'] == pytest.approx(0.6)

def test_load_expenses_permission_error(monkeypatch):
    """Test handling of permission errors."""
    def mock_open(*args, **kwargs):
        raise PermissionError("Permission denied")
    
    monkeypatch.setattr('builtins.open', mock_open)
    
    with pytest.raises(PermissionError):
        load_expenses('test.csv')