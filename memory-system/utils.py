"""
Utility Functions for Memory Management System
"""

import sys
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @classmethod
    def disable(cls):
        """Disable all colors."""
        cls.HEADER = ''
        cls.BLUE = ''
        cls.CYAN = ''
        cls.GREEN = ''
        cls.WARNING = ''
        cls.FAIL = ''
        cls.ENDC = ''
        cls.BOLD = ''
        cls.UNDERLINE = ''


def print_success(message: str, file: Optional[object] = sys.stdout):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.ENDC} {message}", file=file)


def print_error(message: str, file: Optional[object] = sys.stderr):
    """Print error message."""
    print(f"{Colors.FAIL}✗{Colors.ENDC} {message}", file=file)


def print_warning(message: str, file: Optional[object] = sys.stdout):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠{Colors.ENDC} {message}", file=file)


def print_info(message: str, file: Optional[object] = sys.stdout):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ{Colors.ENDC} {message}", file=file)


def print_header(message: str, file: Optional[object] = sys.stdout):
    """Print header message."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{message}{Colors.ENDC}", file=file)
    print(f"{Colors.CYAN}{'=' * len(message)}{Colors.ENDC}\n", file=file)


def confirm(prompt: str, default: bool = False) -> bool:
    """Ask for confirmation."""
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = input(f"{prompt}{suffix}").strip().lower()
    
    if not response:
        return default
    
    return response in ('y', 'yes')


def truncate(text: str, length: int, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def format_duration(hours: float) -> str:
    """Format duration in hours to human-readable string."""
    if hours < 1:
        return f"{int(hours * 60)}m"
    elif hours == int(hours):
        return f"{int(hours)}h"
    else:
        return f"{hours:.1f}h"


def format_date(date_str: str, format_in: str = "%Y-%m-%d", format_out: str = "%b %d, %Y") -> str:
    """Format date string."""
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, format_in)
        return dt.strftime(format_out)
    except ValueError:
        return date_str


def parse_date(date_str: str) -> Optional[str]:
    """Parse various date formats to ISO format."""
    from datetime import datetime
    
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%B %d, %Y",
        "%b %d, %Y"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    return None


def relative_time(date_str: str) -> str:
    """Convert date to relative time string."""
    from datetime import datetime
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "just now"
            elif diff.seconds < 3600:
                return f"{diff.seconds // 60}m ago"
            else:
                return f"{diff.seconds // 3600}h ago"
        elif diff.days == 1:
            return "yesterday"
        elif diff.days < 7:
            return f"{diff.days}d ago"
        elif diff.days < 30:
            return f"{diff.days // 7}w ago"
        elif diff.days < 365:
            return f"{diff.days // 30}mo ago"
        else:
            return f"{diff.days // 365}y ago"
    except (ValueError, TypeError):
        return date_str


def humanize_number(num: int) -> str:
    """Convert large numbers to human-readable format."""
    if num < 1000:
        return str(num)
    elif num < 1000000:
        return f"{num / 1000:.1f}K"
    else:
        return f"{num / 1000000:.1f}M"


def sanitize_filename(filename: str) -> str:
    """Sanitize string for use as filename."""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>"/\\|?*]', '', filename)
    # Limit length
    filename = filename[:100]
    return filename.strip()


def generate_summary(text: str, max_length: int = 200) -> str:
    """Generate summary from text."""
    # Simple summary - first sentence or truncated text
    sentences = text.split('.')
    if sentences and len(sentences[0]) < max_length:
        return sentences[0].strip()
    return text[:max_length].strip() + "..." if len(text) > max_length else text.strip()


def progress_bar(current: int, total: int, width: int = 30) -> str:
    """Generate ASCII progress bar."""
    if total == 0:
        return "[" + " " * width + "] 0%"
    
    filled = int(width * current / total)
    percent = int(100 * current / total)
    
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percent}%"


def colorize_priority(priority: str) -> str:
    """Return colorized priority string."""
    colors = {
        'critical': Colors.FAIL,
        'high': Colors.WARNING,
        'medium': Colors.CYAN,
        'low': Colors.GREEN
    }
    color = colors.get(priority.lower(), '')
    return f"{color}{priority.upper()}{Colors.ENDC}"


def colorize_status(status: str) -> str:
    """Return colorized status string."""
    colors = {
        'completed': Colors.GREEN,
        'active': Colors.GREEN,
        'in_progress': Colors.BLUE,
        'pending': Colors.CYAN,
        'blocked': Colors.FAIL,
        'mitigated': Colors.WARNING,
        'resolved': Colors.GREEN,
        'paused': Colors.WARNING,
        'archived': Colors.FAIL
    }
    color = colors.get(status.lower(), '')
    return f"{color}{status}{Colors.ENDC}"


def table(rows: list, headers: list = None, align: list = None) -> str:
    """Generate simple text table."""
    if not rows:
        return "No data"
    
    if headers:
        rows = [headers] + rows
    
    # Calculate column widths
    num_cols = len(rows[0])
    widths = [0] * num_cols
    
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    
    # Build table
    lines = []
    separator = "+" + "+".join(["-" * (w + 2) for w in widths]) + "+"
    
    lines.append(separator)
    
    for i, row in enumerate(rows):
        cells = []
        for j, cell in enumerate(row):
            cell_str = str(cell)
            # Align right for numbers
            if align and j < len(align) and align[j] == 'right':
                cells.append(cell_str.rjust(widths[j]))
            else:
                cells.append(cell_str.ljust(widths[j]))
        
        lines.append("| " + " | ".join(cells) + " |")
        
        if i == 0 and headers:
            lines.append(separator)
    
    lines.append(separator)
    
    return "\n".join(lines)


def deduplicate(items: list, key_func=None) -> list:
    """Remove duplicates from list while preserving order."""
    seen = set()
    result = []
    
    for item in items:
        key = key_func(item) if key_func else item
        if key not in seen:
            seen.add(key)
            result.append(item)
    
    return result


def group_by(items: list, key_func) -> dict:
    """Group items by key function."""
    groups = {}
    for item in items:
        key = key_func(item)
        if key not in groups:
            groups[key] = []
        groups[key].append(item)
    return groups
