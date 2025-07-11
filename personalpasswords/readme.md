# PersonalPasswords

## Description
PersonalPasswords is a Python script that generates customized password lists based on OSINT-style prompts. By combining user-provided names, dates (with multiple formats), and character substitutions, it creates comprehensive wordlists useful for password spraying, red teaming, and personal security testing.

The list length will vary depending on inputs. On average, tens of thousands to hundreds of thousands of unique passwords are generated per run.

## Features
- Generates personalized password lists using combinations of names, dates, and custom input.
- Supports popular password formats and combinations.
- Highly customizable input, allowing for unique password lists.

## Requirements
- **Python 3.x** or later
- Works across multiple operating systems: Windows, macOS, and Linux

## Installation and Setup
1. Ensure Python 3.x is installed on your machine. You can check your Python version by running:
   ```bash
   python --version
  or
  ```bash
  python3 --version
  ```
2. Clone this repository to your local machine using Git:

  ```bash
  git clone https://github.com/your-username/PersonalPasswords.git
```

## Usage
To generate a password list using PersonalPasswords:

1. Run the script from your terminal:

  ```bash
  python PersonalPasswords.py
```
2. Follow the prompts to provide the script with inputs, including:

- Names (e.g., first name, last name)
- Important dates (e.g., birthdates, anniversaries)
- Any other relevant details (e.g., pet names, favorite colors)

3. The script will generate a list of potential passwords based on your inputs and save it to a text file.

4. The generated password list can be found in the project directory under the name **password_list.txt**.

## Example:
  ``` bash
  python PersonalPasswords.py
```
## Customization
If you wish to modify how passwords are generated or want to add new formats:
- Edit the PersonalPasswords.py script to add or adjust the combinations of names, dates, and formats used to create the password list.
- You can also modify the length of passwords or restrict/expand specific character types used.

## Disclaimer
This script is intended for educational and personal use only. Please use it responsibly, and ensure that generated passwords are not used for malicious purposes. Only test against systems or accounts that you have explicit permission to assess.

## Contributing
Contributions are welcome!
