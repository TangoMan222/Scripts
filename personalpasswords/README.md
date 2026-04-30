# PersonalPasswords - OSINT Wordlist Generator

PersonalPasswords is a local desktop utility that generates custom password wordlists from names/keywords and optional dates. It applies capitalization and reverse variants, optional character substitutions, optional external wordlist merging, and optional length filtering.

## Legal and Ethical Use
This tool is for **authorized security testing, password auditing, lab work, and defensive assessments only**.
Do not use it against systems, accounts, or data without explicit permission.

## Features
- Simple desktop GUI (tkinter)
- Names/keywords input (one per line)
- Optional dates input in `DDMMYYYY` format (invalid dates are skipped and reported)
- Optional character substitutions
- Optional alphabetical sorting
- Duplicate removal (enforced internally)
- Optional external wordlist merge
- Optional min/max length filtering
- Automatic unique output filename generation (`PasswordList.txt`, `PasswordList_1.txt`, etc.)

## Project Structure
```
personalpasswords/
  app.py
  generator.py
  requirements.txt
  README.md
```

## Run from Source
From the `personalpasswords` directory:

```bash
python -m pip install -r requirements.txt
python app.py
```

> Note: `tkinter` is included with most Python installers, so no extra GUI package is required.

## Build a Windows Executable (PyInstaller)
From the `personalpasswords` directory:

```bash
python -m pip install -r requirements.txt
pyinstaller --onefile --windowed app.py --name PersonalPasswords
```

The executable will be created in:
- `dist/PersonalPasswords.exe`

## How to Use the GUI
1. Enter names/keywords (one per line). This field is required.
2. Optionally enter dates in `DDMMYYYY` format (one per line).
3. Optionally choose an output path. If blank, output defaults to `PasswordList.txt` in the app directory.
4. Optionally select an external wordlist to merge.
5. Optionally set minimum and/or maximum password length.
6. Click **Generate Wordlist**.
7. Review status messages for:
   - validation errors
   - skipped invalid dates
   - output file path
   - total unique passwords
   - whether external wordlist merge occurred
8. Use **Open Output Folder** to open the folder containing the output file.

## Date Format
Expected date format is `DDMMYYYY`.
Example:
- `01012000` (1 January 2000)

## Output Location
- If no output path is selected: saved in the app directory as `PasswordList.txt` (or uniquely suffixed).
- If an output path is selected: saved there, with unique filename handling if needed.

## Privacy and Safety
All generation happens locally on your machine.
The tool does not upload, transmit, or sync generated passwords.
