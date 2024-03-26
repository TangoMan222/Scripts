import os
from datetime import datetime

FileNameCounter = 1
filename = "PasswordList.txt"
NameList = []
ModifiedNameList = []
DateList = []
ModDateList = []
IntList = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
SpecialCharList = ["!", "@", "#", "$", "%", "^",
                   "&", "*", "?", "~", "-", "_", "+", "=", "*"
                   # Add more Chars as needed
                   ]

QuestionNameList = ["Enter first name of subject",
                    "Enter middle name of subject",
                    "Enter last name of subject",
                    "Enter Spouse First Name",
                    "Enter Pet Name",
                    "Enter Known UserName or alias"
                    # Add More Questions as needed
                    ]

QuestionDateList = ["Enter Birthday of subject (format:DDMMYYYY)",
                    "Enter Birthday of spouse (format:DDMMYYYY)",
                    "Enter Birthday of pet (format:DDMMYYYY)",
                    "Enter Anniversary date (format:DDMMYYYY)"
                    # Add More Questions as needed
                    ]

CharSubstitutions = {
    'a': '@',
    'i': '!',
    'o': '0',
    'l': '1',
    't': '7',
    'g': '9',
    'b': '8',
    'z': '2',
    'e': '3',
    's': '5',
    # Add more substitutions as needed
}


def start_prompt():
    print(" Welcome to PersonalPasswords \n")
    print(" Press Enter to Continue \n")
    input()


def print_questions():
    for Question in QuestionNameList:
        print(Question)
        NameVar = input()
        if NameVar:
            NameList.append(NameVar)
        # Prints question and adds answers to the appropriate list

    print("Enter Number of children ")
    ChildCount = int(input())
    # Acquires Number so the following can loop the correct amount of times
    LoopVar = 1
    if ChildCount >= 0:
        while LoopVar <= ChildCount:
            print("Enter Child " + str(LoopVar) + " Name")
            ChildName = input()
            NameList.append(ChildName)
            print("Enter Child " + str(LoopVar) + " Birthday (format:DDMMYYYY)")
            ChildBirthday = int(input())
            if ChildBirthday:
                DateList.append(ChildBirthday)
            LoopVar += 1
        # Loops for every child, gets name and b-day and adds to the correct lists

    print("Enter how many additional names you would like to use")
    AdditionalNameCount = int(input())
    # prompts for additional names and gets a number to loop to

    LoopVar = 1
    if AdditionalNameCount >= 1:
        while LoopVar <= AdditionalNameCount:
            print("Enter Name" + str(LoopVar))
            ExtraName = input()
            NameList.append(ExtraName)
            LoopVar += 1
        # loops until desired name count is reached

    for Question in QuestionDateList:
        print(Question)
        DateVar = int(input())
        if DateVar:
            DateList.append(DateVar)
        # cycles through questions gets input and adds to list


def date_mod(List):
    newList = []
    for date in List:
        date_object = datetime.strptime(str(date), '%d%m%Y')
        formatted_date = date_object.strftime('%d%b%Y')  # Format the date as ddmonyyyy (e.g., 03mar1999)
        newList.append(formatted_date)
        # Generate modified date formats
        mod_date_list = [date_object.strftime(format) for date in newList for format in
                         ('%d%b%Y', '%Y', '%b', '%d', '%d%b', '%b%Y')]
        List.extend(mod_date_list)
        return List


def create_file(Counter, Name):
    while os.path.exists(Name):
        Name = f'PersonalPasswordList_{Counter}.txt'  # Change the filename by appending a number
        Counter += 1
    return Name
    # names file a new name


start_prompt()
print_questions()
DateList = date_mod(DateList)
filename = create_file(FileNameCounter, filename)

with open(filename, 'a') as file:  # opens file
    for name in NameList:  # loops through names and changes password chars with popular subs
        file.write(name + '\n')
        for p in range(len(name)):
            modified_password = ''
            previous_modified_password = ''
            for j, letter in enumerate(name):
                if j < p:
                    modified_password += letter
                else:
                    modified_password += CharSubstitutions.get(letter, letter)
            if modified_password != previous_modified_password:
                ModifiedNameList.append(modified_password)
                previous_modified_password = modified_password

    NameList.extend(ModifiedNameList)

    # The following loops through the names and dates and creates combinations to generate passwords
    for name in NameList:
        file.write(name + '\n')
        for i in IntList:
            file.write(name + str(i) + '\n')
            for char in SpecialCharList:
                file.write(name.capitalize() + str(i) + char + "\n")
                for name2 in NameList:
                    file.write(name.capitalize() + char + name2.capitalize() + "\n")
                    file.write(name.capitalize() + str(i) + char + name2.capitalize() + "\n")
        for date in DateList:
            file.write(str(date) + '\n')
            file.write(name + str(date) + '\n')
            file.write(name + '@' + str(date) + '\n')
            for char in SpecialCharList:
                file.write(name.capitalize() + str(date) + char + '\n')
                file.write(name.capitalize() + char + str(date) + '\n')
                file.write(name.capitalize() + char + str(date) + char + '\n')
