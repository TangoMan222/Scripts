# PersonalPasswords

## Description

**PersonalPasswords** is a Python-based command-line tool that generates customized password lists using OSINT-style inputs. It accepts user-provided names, dates (with multiple formatting patterns), and applies various transformations such as character substitutions, capitalization, delimiters, and reversals to create highly personalized and targeted wordlists.

This tool is useful for password spraying, red teaming, penetration testing, CTFs, or personal security assessments.

---

## Features

- Generates wordlists using names, dates, and custom patterns
- Supports character substitutions (e.g., a → @, e → 3)
- Applies capitalization variants, string reversals, and delimiter-based combinations
- Merges external wordlists (e.g., rockyou.txt)
- Supports password length filtering via CLI options
- Fully automated and non-interactive when using command-line arguments

---

## Requirements

- Python 3.6 or later
- Works on Windows, macOS, and Linux

---

## Installation

Clone the repository and install in development mode:

```bash
git clone https://github.com/your-username/scripts.git
cd scripts/personalpasswords
pip install -e .
```

This makes the `personalpasswords` command globally available on your system.

---

## Usage

### Interactive Mode (Prompted Input)

```bash
personalpasswords
```

You will be prompted for:
- Names (first, last, aliases, pets, etc.)
- Important dates (birthdays, anniversaries) in DDMMYYYY format

### Non-Interactive Mode (Fully Automated)

```bash
personalpasswords \
  --names john doe admin \
  --dates 01011990 15082000 \
  --output john-doe-list.txt \
  --merge-wordlist rockyou.txt \
  --min-length 8 \
  --max-length 18 \
  --no-substitutions
```

---

## Command-Line Options

| Option               | Description |
|----------------------|-------------|
| `--names`            | List of names to include |
| `--dates`            | List of dates in `DDMMYYYY` format |
| `--output`, `-o`     | Output filename (default: PasswordList.txt) |
| `--merge-wordlist`, `-m` | Path to external wordlist to merge |
| `--no-substitutions` | Disable character substitutions |
| `--min-length`       | Minimum password length |
| `--max-length`       | Maximum password length |

---

## Output

A uniquely named text file will be generated in the current directory, containing all valid, deduplicated passwords based on your inputs and options.

---

## Customization

You can modify `personalpasswords/cli.py` to:
- Adjust transformation logic
- Change or expand character substitution rules
- Modify how names and dates are combined
- Add new CLI flags

---

## Disclaimer

This tool is intended for lawful, ethical, and educational use only. Do not use it against any system or account without explicit authorization. Misuse of this tool may violate laws and terms of service.

---

## Contributing

Contributions are welcome. Feel free to fork the repository and submit pull requests with improvements, bug fixes, or additional features.
