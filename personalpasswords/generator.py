from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

DEFAULT_FILENAME = "PasswordList.txt"
INT_LIST = list(range(10))
SPECIAL_CHAR_LIST = ["!", "@", "#", "$", "%", "^", "&", "*", "?", "~", "-", "_", "+", "=", "*"]

CHAR_SUBSTITUTIONS = {
    "a": "@",
    "i": "!",
    "o": "0",
    "l": "1",
    "t": "7",
    "g": "9",
    "b": "8",
    "z": "2",
    "e": "3",
    "s": "5",
}


def substitute_chars(name: str) -> str:
    return "".join([CHAR_SUBSTITUTIONS.get(c, c) for c in name])


def capitalization_variants(name: str) -> set[str]:
    return {name.lower(), name.upper(), name.capitalize()}


def reversed_name(name: str) -> str:
    return name[::-1]


def delimiter_variants(name1: str, name2: str) -> set[str]:
    return {f"{name1}_{name2}", f"{name1}-{name2}", f"{name1}.{name2}"}


def modify_dates(date_list: Iterable[str]) -> tuple[list[str], list[str]]:
    mod_dates = set()
    valid_inputs = []
    invalid_dates = []

    for raw in date_list:
        date = str(raw).strip()
        if not date:
            continue
        if not (len(date) == 8 and date.isdigit()):
            invalid_dates.append(date)
            continue
        try:
            date_obj = datetime.strptime(date, "%d%m%Y")
            valid_inputs.append(date)
            mod_dates.update(
                [date_obj.strftime(fmt) for fmt in ("%d%b%Y", "%Y", "%b", "%d", "%d%b", "%b%Y")]
            )
        except ValueError:
            invalid_dates.append(date)

    return list(set(map(str, valid_inputs)) | mod_dates), invalid_dates


def generate_passwords(name_list: list[str], date_list: list[str], use_subs: bool = True) -> set[str]:
    password_set = set()
    modified_names = set()

    for name in name_list:
        modified_names.update(capitalization_variants(name))
        modified_names.add(reversed_name(name))
        if use_subs:
            modified_names.add(substitute_chars(name))

    all_names = list(set(name_list) | modified_names)

    for name in all_names:
        password_set.add(name)
        for i in INT_LIST:
            password_set.add(f"{name}{i}")
            for char in SPECIAL_CHAR_LIST:
                password_set.add(f"{name}{i}{char}")
                for name2 in all_names:
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


def create_unique_filename(base_name: str | Path) -> Path:
    target = Path(base_name)
    counter = 1
    candidate = target
    while candidate.exists():
        candidate = target.with_name(f"{target.stem}_{counter}{target.suffix or '.txt'}")
        counter += 1
    return candidate


def merge_wordlist(password_set: set[str], wordlist_path: str | Path | None) -> tuple[set[str], bool, str | None]:
    if not wordlist_path:
        return password_set, False, None

    path = Path(wordlist_path)
    if not path.exists() or not path.is_file():
        return password_set, False, f"Wordlist path not found: {path}"

    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    password_set.add(stripped)
        return password_set, True, None
    except OSError as exc:
        return password_set, False, f"Failed to merge wordlist: {exc}"


def filter_by_length(passwords: set[str], min_len: int | None, max_len: int | None) -> set[str]:
    return {
        pwd
        for pwd in passwords
        if (min_len is None or len(pwd) >= min_len) and (max_len is None or len(pwd) <= max_len)
    }
