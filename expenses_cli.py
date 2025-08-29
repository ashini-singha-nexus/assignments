#!/usr/bin/env python3
import argparse
import sys
from typing import Dict, List
from expenses import load_expenses, sum_by_category
import logging
import logging_config

def parse_filter_arg(filter_str: str) -> Dict[str, str]:
    """Parse filter argument string into filter criteria."""
    filters = {}
    if filter_str:
        for criterion in filter_str.split(','):
            if '=' in criterion:
                key, value = criterion.split('=', 1)
                filters[key.strip()] = value.strip()
    return filters

def filter_expenses(expenses: List[Dict], filters: Dict[str, str]) -> List[Dict]:
    """Filter expenses based on criteria."""
    filtered = expenses
    
    if 'category' in filters:
        category_filter = filters['category']
        filtered = [e for e in filtered if e['category'] == category_filter]
    
    return filtered

def format_output(summary: Dict[str, float], sort_method: str, top_n: int = None) -> str:
    """Format the summary output as a table."""
    # Convert to list of tuples for sorting
    items = list(summary.items())
    
    # Apply sorting
    if sort_method == 'amount_asc':
        items.sort(key=lambda x: x[1])
    elif sort_method == 'amount_desc':
        items.sort(key=lambda x: x[1], reverse=True)
    elif sort_method == 'category':
        items.sort(key=lambda x: x[0])
    
    # Apply top N limit
    if top_n is not None and top_n > 0:
        items = items[:top_n]
    
    # Format as table
    max_category_len = max((len(category) for category, _ in items), default=0)
    max_category_len = max(max_category_len, len('category'))
    
    header = f"{'category':<{max_category_len}} {'total':>10}"
    lines = [header, '-' * (max_category_len + 11)]
    
    for category, total in items:
        lines.append(f"{category:<{max_category_len}} {total:10.2f}")
    
    return '\n'.join(lines)

def main():

    logger = logging.getLogger(__name__)
    logger.info("Application started")
    parser = argparse.ArgumentParser(description='Expense Summarizer CLI')
    parser.add_argument('--path', required=True, help='Path to the CSV file')
    parser.add_argument('--sort', choices=['amount_asc', 'amount_desc', 'category'], 
                       default='amount_desc', help='Sort method (default: amount_desc)')
    parser.add_argument('--top', type=int, help='Show only the top N categories')
    parser.add_argument('--filter', help='Filter criteria, e.g., "category=food"')
    
    args = parser.parse_args()
    
    try:
        # Load and validate expenses
        expenses, skipped = load_expenses(args.path)
        
        if skipped > 0:
            print(f"Warning: Skipped {skipped} invalid rows.", file=sys.stderr)
        
        # Apply filters if specified
        filters = parse_filter_arg(args.filter)
        filtered_expenses = filter_expenses(expenses, filters)
        
        # Generate and display summary
        summary = sum_by_category(filtered_expenses)
        output = format_output(summary, args.sort, args.top)
        print(output)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()