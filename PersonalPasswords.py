import os
from datetime import datetime

# Constants
FILENAME = "PasswordList.txt"
FILE_COUNTER = 1

INT_LIST = list(range(10))
SPECIAL_CHAR_LIST = ["!", "@", "#", "$", "%", "^", "&", "*", "?", "~", "-", "_", "+", "=", "*"]

QUESTION_NAME_LIST = [
    "Enter first name of subject",
    "Enter middle name of subject",
    "Enter last name of subject",
    "Enter Spouse First Name",
    "Enter Pet Name",
    "Enter Known UserName or alias"
]

QUESTION_DATE_LIST = [
    "Enter Birthday of subject (format:DDMMYYYY)",
    "Enter Birthday of spouse (format:DDMMYYYY)",
    "Enter Birthday of pet (format:DDMMYYYY)",
    "Enter Anniversary date (format:DDMMYYYY)"
]

CHAR_SUBSTITUTIONS = {
    'a': '@', 'i': '!', 'o': '0', 'l': '1', 't': '7',
    'g': '9', 'b': '8', 'z': '2', 'e': '3', 's': '5'
}

# Input functions
def start_prompt():
    input("Welcome to PersonalPasswords. Press Enter to continue...\n")

def get_date_input(prompt):
    while True:
        val = input(prompt)
        if not val:
            return None
        if len(val) == 8 and val.isdigit():
            return int(val)
        print("Invalid format! Use DDMMYYYY.")

def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input! Please enter an integer.")

# Data collection
def collect_osint_data():
    name_list = []
    date_list = []

    for question in QUESTION_NAME_LIST:
        answer = input(question + ": ")
        if answer:
            name_list.append(answer)

    child_count = get_int_input("Enter number of children: ")
    for i in range(child_count):
        name = input(f"Enter Child {i+1} Name: ")
        name_list.append(name)
        birthday = get_date_input(f"Enter Child {i+1} Birthday (format:DDMMYYYY): ")
        if birthday:
            date_list.append(birthday)

    extra_count = get_int_input("Enter number of additional names to include: ")
    for i in range(extra_count):
        extra = input(f"Enter Name {i+1}: ")
        name_list.append(extra)

    for question in QUESTION_DATE_LIST:
        date = get_date_input(question + ": ")
        if date:
            date_list.append(date)

    return name_list, date_list

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

# Password generation
def generate_passwords(name_list, date_list):
    password_set = set()
    modified_names = set()

    for name in name_list:
        modified_names.update(capitalization_variants(name))
        modified_names.add(substitute_chars(name))
        modified_names.add(reversed_name(name))

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
def create_unique_filename(base_name, counter):
    while os.path.exists(base_name):
        base_name = f'PersonalPasswordList_{counter}.txt'
        counter += 1
    return base_name

# Main script execution
start_prompt()
names, dates = collect_osint_data()
dates = modify_dates(dates)
output_file = create_unique_filename(FILENAME, FILE_COUNTER)
passwords = generate_passwords(names, dates)

with open(output_file, 'w') as file:
    for pwd in sorted(passwords):
        file.write(pwd + '\n')

# Output stats
print("\nPassword list generated!")
print(f"Output file: {output_file}")
print(f"Total unique passwords: {len(passwords)}")
