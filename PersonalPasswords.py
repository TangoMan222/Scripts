import os
import argparse
from datetime import datetime

# Constants
DEFAULT_FILENAME = "PasswordList.txt"
INT_LIST = list(range(10))
SPECIAL_CHAR_LIST = ["!", "@", "#", "$", "%", "^", "&", "*", "?", "~", "-", "_", "+", "=", "*"]

CHAR_SUBSTITUTIONS = {
    'a': '@', 'i': '!', 'o': '0', 'l': '1', 't': '7',
    'g': '9', 'b': '8', 'z': '2', 'e': '3', 's': '5'
}

# Transformations
def substitute_chars(name):
    return ''.join([CHAR_SUBSTITUTIONS.get(c, c) for c in name])

def capitalization_variants(name):
    return {name.lower(), name.upper(), name.capitalize()}

def reversed_name(name):
    return name[::-1]

def delimiter_variants(name1, name2):
    return {
        f"{name1}_{name2}",
        f"{name1}-{name2}",
        f"{name1}.{name2}"
    }

# Date formatting
def modify_dates(date_list):
    mod_dates = set()
    for date in date_list:
        try:
            date_obj = datetime.strptime(str(date), '%d%m%Y')
            mod_dates.update([
                date_obj.strftime(fmt) for fmt in
                ('%d%b%Y', '%Y', '%b', '%d', '%d%b', '%b%Y')
            ])
        except ValueError:
            continue
    return list(set(map(str, date_list)) | mod_dates)

# Password generation
def generate_passwords(name_list, date_list, use_subs=True):
    password_set = set()
    modified_names = set()

    for name in name_list:
        modified_names.update(capitalization_variants(name))
        modified_names.add(reversed_name(name))
        if use_subs:
            modified_names.add(substitute_chars(name))

    name_list = list(set(name_list) | modified_names)

    for name in name_list:
        password_set.add(name)
        for i in INT_LIST:
            password_set.add(f"{name}{i}")
            for char in SPECIAL_CHAR_LIST:
                password_set.add(f"{name}{i}{char}")
                for name2 in name_list:
                    password_set.add(f"{name}{char}{name2}")
                    password_set.add(f"{name}{i}{char}{name2}")
                    password_set.update(delimiter_variants(name, name2))
        for date in date_list:
            password_set.add(f"{name}{date}")
            password_set.add(f"{name}@{date}")
            for char in SPECIAL_CHAR_LIST:
                password_set.add(f"{name}{date}{char}")
                password_set.add(f"{name}{char}{date}")
                password_set.add(f"{name}{char}{date}{char}")

    password_set.update(date_list)
    return password_set

# File handling
def create_unique_filename(base_name):
    counter = 1
    orig_name = base_name
    while os.path.exists(base_name):
        base_name = f'{orig_name.rstrip(".txt")}_{counter}.txt'
        counter += 1
    return base_name

# Merge external wordlist
def merge_wordlist(password_set, wordlist_path):
    if wordlist_path and os.path.exists(wordlist_path):
        try:
            with open(wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    password_set.add(line.strip())
            print(f"✅ Merged wordlist from: {wordlist_path}")
        except Exception as e:
            print(f"❌ Failed to merge wordlist: {e}")
    return password_set

# Length filtering
def filter_by_length(passwords, min_len, max_len):
    return {
        pwd for pwd in passwords
        if (min_len is None or len(pwd) >= min_len) and (max_len is None or len(pwd) <= max_len)
    }

# Argument parsing
def parse_args():
    parser = argparse.ArgumentParser(description="Generate a custom password list using OSINT data.")
    parser.add_argument('--output', '-o', help="Output filename (default: PasswordList.txt)", default=DEFAULT_FILENAME)
    parser.add_argument('--no-substitutions', action='store_true', help="Disable character substitutions (e.g. a -> @)")
    parser.add_argument('--merge-wordlist', '-m', help="Path to external wordlist to merge")
    parser.add_argument('--min-length', type=int, help="Minimum password length")
    parser.add_argument('--max-length', type=int, help="Maximum password length")
    parser.add_argument('--names', nargs='*', help="List of names (first, last, aliases, etc.)")
    parser.add_argument('--dates', nargs='*', help="List of dates in DDMMYYYY format")
    return parser.parse_args()

# Main execution
def main():
    args = parse_args()
    print("🔐 PersonalPasswords: OSINT-based Wordlist Generator\n")

    if args.names and args.dates:
        names = args.names
        dates = [d for d in args.dates if len(d) == 8 and d.isdigit()]
        dates = modify_dates(dates)
    else:
        print("❌ Error: For non-interactive mode, both --names and --dates must be provided.")
        return

    output_file = create_unique_filename(args.output)
    passwords = generate_passwords(names, dates, use_subs=not args.no_substitutions)
    passwords = merge_wordlist(passwords, args.merge_wordlist)
    passwords = filter_by_length(passwords, args.min_length, args.max_length)

    with open(output_file, 'w') as file:
        for pwd in sorted(passwords):
            file.write(pwd + '\n')

    print("\n✅ Password list generated!")
    print(f"📄 Output file: {output_file}")
    print(f"🔢 Total unique passwords: {len(passwords)}")

if __name__ == "__main__":
    main()
