import re

FORMATS = [
    "[Gen 8] Random Battle",
    #"[Gen 9] OU",
    #"[Gen 9] Random Battle",
]


def to_compact_notation(bracket_format):
    """Convert '[Gen 9] OU' → 'gen9ou'."""
    match = re.match(r"\[Gen (\d+)\] (.+)", bracket_format)
    if not match:
        return None  # Invalid format
    gen, format_name = match.groups()

    # Lowercase and remove spaces
    compact_format = f"gen{gen}{format_name.lower().replace(' ', '')}"
    return compact_format