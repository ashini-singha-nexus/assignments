def safe_div(a: float, b: float) -> float | None:
    """Return a / b, or None if b is 0."""
    return a / b if b != 0 else None


def slugify(s: str) -> str:
    """Convert string to slug: lowercase, trim, spaces to single hyphens, remove punctuation except hyphens."""
    # Convert to lowercase and trim whitespace
    s = s.lower().strip()

    result = []
    in_space = False  # flag to track consecutive spaces

    for char in s:
        if char == ' ':
            if not in_space:
                result.append('-')  # replace the first space with '-'
                in_space = True
        else:
            result.append(char)
            in_space = False  # reset when a non-space character comes

    s = ''.join(result)
    s = ''.join(ch for ch in s if ch.isalnum() or ch == '-')

    return s


def median(nums: list[float]) -> float:
    """Return the median of a list of numbers. Raises ValueError if empty."""
    if not nums:
        raise ValueError("empty")
    sorted_nums = sorted(nums)
    n = len(sorted_nums)
    mid = n // 2
    if n % 2 == 1:
        return sorted_nums[mid]
    else:
        return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2
