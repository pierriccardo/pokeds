import re

FORMATS = [
    "[Gen 8] Random Battle",
    "[Gen 9] OU",
    "[Gen 9] Random Battle",
    "[Gen 9] VGC 2025 Reg G",
    "[Gen 9] National Dex",
    #"[Gen 8] OU",
]

ROOMLIST = [
    "lobby",
    "tournaments",
    "overused",
    "randombattles",
    "help",
    "vgc",
    "nationaldexou"
]

RETRIES = 7

# TODO: make it generic for every format
def to_compact_notation(bracket_format):
    """
    Convert battle format to compact notation
    e.g., '[Gen 9] OU' -> 'gen9ou'
    """
    match = re.match(r"\[Gen (\d+)\] (.+)", bracket_format)
    if not match:
        return None  # Invalid format
    gen, format_name = match.groups()

    # Lowercase and remove spaces
    compact_format = f"gen{gen}{format_name.lower().replace(' ', '')}"
    return compact_format

if __name__ == "__main__":
    print(to_compact_notation("[Gen 9] VGC 2025 Reg G"))