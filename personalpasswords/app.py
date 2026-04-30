from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from generator import (
    DEFAULT_FILENAME,
    create_unique_filename,
    filter_by_length,
    generate_passwords,
    merge_wordlist,
    modify_dates,
)


class PersonalPasswordsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PersonalPasswords - OSINT Wordlist Generator")
        self.root.geometry("860x740")

        self.output_var = tk.StringVar()
        self.wordlist_var = tk.StringVar()
        self.min_len_var = tk.StringVar()
        self.max_len_var = tk.StringVar()

        self.use_subs_var = tk.BooleanVar(value=True)
        self.sort_var = tk.BooleanVar(value=True)
        self.remove_dupes_var = tk.BooleanVar(value=True)

        self.last_output_file: Path | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Names / keywords (one per line):").pack(anchor="w")
        self.names_text = tk.Text(frame, height=8)
        self.names_text.pack(fill="x", pady=(0, 10))

        ttk.Label(frame, text="Dates in DDMMYYYY format (optional, one per line):").pack(anchor="w")
        self.dates_text = tk.Text(frame, height=6)
        self.dates_text.pack(fill="x", pady=(0, 10))

        self._file_picker_row(frame, "Output file:", self.output_var, self._browse_output, save=True)
        self._file_picker_row(frame, "External wordlist (optional):", self.wordlist_var, self._browse_wordlist, save=False)

        lens = ttk.Frame(frame)
        lens.pack(fill="x", pady=(8, 8))
        ttk.Label(lens, text="Minimum length (optional):").grid(row=0, column=0, sticky="w")
        ttk.Entry(lens, textvariable=self.min_len_var, width=12).grid(row=0, column=1, padx=(8, 18), sticky="w")
        ttk.Label(lens, text="Maximum length (optional):").grid(row=0, column=2, sticky="w")
        ttk.Entry(lens, textvariable=self.max_len_var, width=12).grid(row=0, column=3, padx=(8, 0), sticky="w")

        opts = ttk.LabelFrame(frame, text="Options", padding=8)
        opts.pack(fill="x", pady=(6, 10))
        ttk.Checkbutton(opts, text="Enable character substitutions", variable=self.use_subs_var).pack(anchor="w")
        ttk.Checkbutton(opts, text="Sort output alphabetically", variable=self.sort_var).pack(anchor="w")
        ttk.Checkbutton(opts, text="Remove duplicates (enforced)", variable=self.remove_dupes_var).pack(anchor="w")

        btns = ttk.Frame(frame)
        btns.pack(fill="x", pady=(4, 10))
        ttk.Button(btns, text="Generate Wordlist", command=self.generate_wordlist).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Clear Inputs", command=self.clear_inputs).pack(side="left", padx=(0, 8))
        ttk.Button(btns, text="Open Output Folder", command=self.open_output_folder).pack(side="left")

        ttk.Label(frame, text="Status:").pack(anchor="w")
        self.status_text = tk.Text(frame, height=12, state="disabled", wrap="word")
        self.status_text.pack(fill="both", expand=True)

        ttk.Label(
            frame,
            text=(
                "For authorized security testing, password auditing, lab work, "
                "and defensive assessments only."
            ),
            foreground="#555",
        ).pack(anchor="w", pady=(8, 0))

    def _file_picker_row(self, parent: ttk.Frame, label: str, variable: tk.StringVar, command, save: bool) -> None:
        row = ttk.Frame(parent)
        row.pack(fill="x", pady=(4, 6))
        ttk.Label(row, text=label).pack(anchor="w")
        inner = ttk.Frame(row)
        inner.pack(fill="x")
        ttk.Entry(inner, textvariable=variable).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(inner, text="Save As..." if save else "Browse...", command=command).pack(side="left")

    def _browse_output(self) -> None:
        chosen = filedialog.asksaveasfilename(
            title="Choose output file",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile=DEFAULT_FILENAME,
        )
        if chosen:
            self.output_var.set(chosen)

    def _browse_wordlist(self) -> None:
        chosen = filedialog.askopenfilename(
            title="Select external wordlist",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if chosen:
            self.wordlist_var.set(chosen)

    def _append_status(self, message: str) -> None:
        self.status_text.configure(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")

    def _clear_status(self) -> None:
        self.status_text.configure(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.configure(state="disabled")

    def _parse_optional_int(self, value: str, field_name: str) -> tuple[int | None, str | None]:
        cleaned = value.strip()
        if not cleaned:
            return None, None
        try:
            return int(cleaned), None
        except ValueError:
            return None, f"{field_name} must be an integer."

    def generate_wordlist(self) -> None:
        self._clear_status()

        names = [line.strip() for line in self.names_text.get("1.0", "end").splitlines() if line.strip()]
        raw_dates = [line.strip() for line in self.dates_text.get("1.0", "end").splitlines() if line.strip()]

        if not names:
            self._append_status("Error: Names / keywords are required.")
            return

        min_len, min_err = self._parse_optional_int(self.min_len_var.get(), "Minimum length")
        max_len, max_err = self._parse_optional_int(self.max_len_var.get(), "Maximum length")
        if min_err:
            self._append_status(f"Error: {min_err}")
            return
        if max_err:
            self._append_status(f"Error: {max_err}")
            return
        if min_len is not None and max_len is not None and max_len < min_len:
            self._append_status("Error: Maximum length cannot be smaller than minimum length.")
            return

        modified_dates, invalid_dates = modify_dates(raw_dates)
        if invalid_dates:
            self._append_status("Skipped invalid dates: " + ", ".join(invalid_dates))

        output_input = self.output_var.get().strip()
        if output_input:
            desired_output = Path(output_input)
        else:
            desired_output = Path(__file__).resolve().parent / DEFAULT_FILENAME

        output_file = create_unique_filename(desired_output)
        passwords = generate_passwords(names, modified_dates, use_subs=self.use_subs_var.get())

        passwords, merged, merge_error = merge_wordlist(passwords, self.wordlist_var.get().strip() or None)
        if merge_error:
            self._append_status(f"Warning: {merge_error}")

        passwords = filter_by_length(passwords, min_len, max_len)
        ordered = sorted(passwords) if self.sort_var.get() else list(passwords)

        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with output_file.open("w", encoding="utf-8") as fh:
                for pwd in ordered:
                    fh.write(pwd + "\n")
        except OSError as exc:
            self._append_status(f"Error: Could not write output file. {exc}")
            return

        self.last_output_file = output_file
        self._append_status("Success: Password list generated.")
        self._append_status(f"Output file: {output_file}")
        self._append_status(f"Total unique passwords generated: {len(passwords)}")
        self._append_status(f"External wordlist merged: {'Yes' if merged else 'No'}")

    def clear_inputs(self) -> None:
        self.names_text.delete("1.0", "end")
        self.dates_text.delete("1.0", "end")
        self.output_var.set("")
        self.wordlist_var.set("")
        self.min_len_var.set("")
        self.max_len_var.set("")
        self.use_subs_var.set(True)
        self.sort_var.set(True)
        self.remove_dupes_var.set(True)
        self._clear_status()
        self.last_output_file = None

    def open_output_folder(self) -> None:
        if self.last_output_file:
            folder = self.last_output_file.parent
        else:
            folder = Path(self.output_var.get()).expanduser().parent if self.output_var.get().strip() else Path(__file__).resolve().parent

        try:
            if sys.platform.startswith("win"):
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", str(folder)], check=False)
            else:
                subprocess.run(["xdg-open", str(folder)], check=False)
            self._append_status(f"Opened output folder: {folder}")
        except Exception as exc:
            self._append_status(f"Error: Could not open folder. {exc}")


def main() -> None:
    root = tk.Tk()
    app = PersonalPasswordsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
