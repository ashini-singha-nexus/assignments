# Python Learning Assignments



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


