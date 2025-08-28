# Python Learning Assignments

This repository contains four comprehensive Python assignments that demonstrate various programming concepts including utility functions, CLI applications, data processing, and system design.

## Table of Contents

- [Assessment 1: Utility Belt Functions](#assessment-1-utility-belt-functions)
- [Assessment 2: Expense Summarizer CLI](#assessment-2-expense-summarizer-cli)
- [Assessment 3: Bank Ledger System](#assessment-3-bank-ledger-system)
- [Assessment 4: JSON TODO with Tags & Due Dates](#assessment-4-json-todo-with-tags--due-dates)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Getting Started](#getting-started)

---

## Assessment 1: Utility Belt Functions

**Objective**: Implement three small, pure functions and write edge-case tests.

### Functions Implemented

#### 1. `safe_div(a: float, b: float) -> float | None`
- **Purpose**: Safely divide two numbers without raising exceptions
- **Behavior**: Returns `a / b` if `b != 0`, otherwise returns `None`
- **Edge Cases Handled**: Division by zero, negative numbers, float inputs

#### 2. `slugify(s: str) -> str`
- **Purpose**: Convert strings to URL-friendly slugs
- **Behavior**: 
  - Converts to lowercase and trims whitespace
  - Replaces internal spaces with single hyphens
  - Removes punctuation except hyphens
  - Handles multiple consecutive spaces
- **Examples**: 
  - `" Hello, World! "` → `"hello-world"`
  - `"A—B"` → `"ab"`
  - `"multiple   spaces"` → `"multiple-spaces"`

#### 3. `median(nums: list[float]) -> float`
- **Purpose**: Calculate the median of a list of numbers
- **Behavior**:
  - For odd-length lists: returns middle value when sorted
  - For even-length lists: returns average of two middle values
  - Raises `ValueError("empty")` for empty lists
- **Performance**: O(n log n) due to sorting

### Key Features
- **Pure Functions**: No side effects, no I/O operations
- **Standard Library Only**: No external dependencies
- **Comprehensive Edge Case Handling**: Multiple spaces, punctuation clusters, negative/float inputs
- **Robust Error Handling**: Graceful handling of edge cases

---

## Assessment 2: Expense Summarizer CLI

**Objective**: Parse a CSV of expenses and produce summaries via a small CLI.

### Core Functions

#### `load_expenses(path: str) -> tuple[list[dict], int]`
- **Purpose**: Load and validate expenses from CSV file
- **Returns**: Tuple of (valid expenses list, count of skipped rows)
- **Validation**: Skips rows with missing/invalid amounts, counts skipped rows
- **Error Handling**: File not found, permission errors, CSV parsing errors

#### `sum_by_category(expenses: list[dict]) -> dict[str, float]`
- **Purpose**: Aggregate expenses by category
- **Returns**: Dictionary with category as key and total amount as value

### CLI Features

#### Command Line Interface (`expenses_cli.py`)
```bash
python expenses_cli.py --path expenses.csv --sort amount_desc --top 5 --filter "category=food"
```

#### Available Options
- `--path PATH` (required): Path to CSV file
- `--sort {amount_asc,amount_desc,category}` (default: amount_desc)
- `--top N` (optional): Show only top N categories
- `--filter "category=<name>"` (optional): Filter by category

#### Output Format
```
 category  total
travel    200.00
food      42.50
misc      10.00
```

### Data Format
CSV with headers: `category,amount,date` (date is optional)
```
food,12.50,2025-08-01
travel,100,2025-08-03
food,30,
misc,10,2025-08-04
travel,100,2025-08-06
```

### Key Features
- **Robust CSV Parsing**: Handles missing dates, invalid amounts gracefully
- **Flexible Filtering**: Category-based filtering and sorting options
- **Error Handling**: Clear error messages for file access issues
- **Clean Separation**: Core logic testable without CLI dependencies

---

## Assessment 3: Bank Ledger System

**Objective**: Extend a BankAccount model and import/apply a batch of transactions.

### Core Classes

#### `BankAccount` Dataclass
- **Attributes**: `owner` (str), `balance` (Decimal)
- **Methods**:
  - `apply(tx: dict)`: Apply single transaction
  - `statement()`: Generate transaction history with running balances

#### Key Features
- **Decimal Arithmetic**: Uses `decimal.Decimal` for precise monetary calculations
- **Transaction Types**: Supports `deposit` and `withdraw` operations
- **Fail-Fast Behavior**: Stops processing on insufficient funds
- **Transaction History**: Maintains chronological transaction log

### Utility Functions

#### `load_transactions(csv_path: str) -> list[dict]`
- **Purpose**: Load transactions from CSV file
- **Format**: CSV with headers `type,amount,note`
- **Validation**: Converts amounts to Decimal for precision

#### `apply_all(account: BankAccount, txns: list[dict]) -> None`
- **Purpose**: Apply batch of transactions in order
- **Behavior**: Fail-fast on insufficient funds or invalid transaction types

### CLI Interface (`bank_cli.py`)
```bash
python bank_cli.py --owner "Alice" --balance 100.00 --from-csv bank_transactions.csv
```

#### Output Format
```
Statement for Alice
------------------------------------------------------------
Index  Type       Amount       Balance       Note
------------------------------------------------------------
1      deposit    100.00       200.00        initial funding
2      withdraw   25.55        174.45        coffee & snacks
3      withdraw   1000.00      174.45        too much
4      deposit    50.00        174.45        payday top-up
------------------------------------------------------------
Final Balance: 174.45
```

### Data Format
CSV with headers: `type,amount,note`
```
deposit,100.00,initial funding
withdraw,25.55,coffee & snacks
withdraw,1000.00,too much
deposit,50.00,payday top-up
```

### Key Features
- **Precise Arithmetic**: Decimal-based calculations prevent floating-point errors
- **Robust Error Handling**: Clear error messages for invalid transaction types
- **Transaction Integrity**: Fail-fast behavior maintains account consistency
- **Comprehensive Reporting**: Detailed transaction history with running balances

---

## Assessment 4: JSON TODO with Tags & Due Dates

**Objective**: Build a small JSON-backed TODO system with filtering, sorting, and a CLI.

### Core Functions

#### Task Management
- **`add_task(path, title, tags=None, due=None)`**: Create new task with validation
- **`list_tasks(path, status=None, tags=None, due_before=None, sort_by="due")`**: List tasks with filtering/sorting
- **`complete_task(path, task_id)`**: Mark task as completed
- **`update_task(path, task_id, **fields)`**: Update task fields (title, tags, due)
- **`delete_task(path, task_id)`**: Remove task from system

### Task Schema
```json
{
  "id": 1,
  "title": "Write tests",
  "done": false,
  "tags": ["dev", "qa"],
  "due": "2025-09-05",
  "created_at": "2025-08-27T18:01:10.423936"
}
```

### CLI Commands

#### Add Task
```bash
python todo_cli.py add "Write tests" --tags dev,qa --due 2025-09-05
```

#### List Tasks
```bash
python todo_cli.py list --status open --tags dev --sort-by due
```

#### Complete Task
```bash
python todo_cli.py complete 3
```

#### Update Task
```bash
python todo_cli.py update 2 --title "Refactor core" --tags backend
```

#### Delete Task
```bash
python todo_cli.py delete 5
```

### Key Features
- **Flexible Filtering**: By status, tags, due dates
- **Multiple Sort Options**: By due date, creation date, or title
- **Date Validation**: ISO YYYY-MM-DD format with past-due warnings
- **Tag Management**: Comma-separated tags with deduplication
- **Stable Sorting**: Consistent ordering with ID-based tie-breaking
- **Past-Due Handling**: Configurable warnings for overdue tasks

---

## Project Structure

```
assignments/
├── __init__.py
├── assignment.txt              # Assignment specifications
├── basics.py                   # Assessment 1: Utility functions
├── expenses.py                 # Assessment 2: Core expense logic
├── expenses_cli.py            # Assessment 2: CLI interface
├── bank.py                    # Assessment 3: Bank account system
├── bank_cli.py               # Assessment 3: Bank CLI
├── todo_core.py              # Assessment 4: Core TODO logic
├── todo_cli.py               # Assessment 4: TODO CLI
├── expenses.csv               # Sample expense data
├── bank_transactions.csv      # Sample bank transaction data
├── todo.json                  # Sample TODO data
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_basics_extra.py  # Assessment 1 tests
│   ├── test_expenses.py      # Assessment 2 tests
│   ├── test_bank_ledger.py   # Assessment 3 tests
│   └── test_todo_advanced.py # Assessment 4 tests
└── README.MD                  # This file
```

---

## Testing

Each assessment includes comprehensive test coverage:

### Assessment 1: `test_basics_extra.py`
- **safe_div**: Normal operations, zero divisor handling
- **slugify**: Basic conversion, multiple spaces, punctuation handling
- **median**: Odd/even lengths, empty lists, unsorted inputs

### Assessment 2: `test_expenses.py`
- **load_expenses**: Valid data, missing dates, invalid amounts, missing columns
- **sum_by_category**: Aggregation accuracy, edge cases
- **CLI Integration**: File handling, error scenarios

### Assessment 3: `test_bank_ledger.py`
- **BankAccount**: Transaction processing, balance calculations
- **Error Handling**: Insufficient funds, invalid transaction types
- **Batch Operations**: CSV loading, transaction application

### Assessment 4: `test_todo_advanced.py`
- **CRUD Operations**: Create, read, update, delete tasks
- **Filtering & Sorting**: Status, tags, due dates, multiple sort fields
- **Validation**: Date formats, tag handling, schema integrity

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_basics_extra.py

# Run with verbose output
pytest -v
```

---

## Getting Started

### Prerequisites
- Python 3.8+
- Standard library modules (no external dependencies)

### Installation
1. Clone or download the repository
2. Navigate to the `assignments` directory
3. Ensure Python is in your PATH

### Quick Examples

#### Utility Functions
```python
from basics import safe_div, slugify, median

# Safe division
result = safe_div(10, 2)  # 5.0
result = safe_div(10, 0)  # None

# Slugify
slug = slugify(" Hello, World! ")  # "hello-world"

# Median
med = median([1, 3, 2])  # 2
med = median([1, 2, 3, 4])  # 2.5
```

#### Expense Summarizer
```bash
python expenses_cli.py --path expenses.csv --sort amount_desc
```

#### Bank Ledger
```bash
python bank_cli.py --owner "Alice" --balance 100.00 --from-csv bank_transactions.csv
```

#### TODO System
```bash
python todo_cli.py add "Learn Python" --tags learning,python --due 2025-12-31
python todo_cli.py list --status open --sort-by due
```

---


