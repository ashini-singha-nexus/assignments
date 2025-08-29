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

--path PATH (required)
--sort {amount_asc,amount_desc,category} (default amount_desc)
--top N (optional)
--filter "category=<name>" (optional)



```

#### Bank Ledger
```bash
python bank_cli.py --owner "Alice" --balance 100.00 --from-csv bank_transactions.csv
```

#### TODO System
```bash
python todo_cli.py add "Write tests" --tags dev,qa --due 2025-09-05
python todo_cli.py list --status open --tags dev --sort-by due
python todo_cli.py complete 3
python todo_cli.py update 2 --title "Refactor core" --tags backend
python todo_cli.py delete 5

```

---


