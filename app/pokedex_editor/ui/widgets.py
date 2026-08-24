"""Reusable list-editing widgets shared across the species edit form.

Tkinter has no built-in "tag input" or editable-table widget, so these wrap
a Listbox with small add/remove controls. Each widget exposes ``get()``
returning plain Python data (list[str], list[dict], ...) matching the JSON
shape it edits, and ``set(values)`` to reload it — that's the only contract
the forms above them rely on.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Optional

from ..models import Ability, Form, LevelUpMove, LocationEntry


class StringListWidget(ttk.Frame):
    """Tag-input style editor for a flat list of strings (egg groups, TM lists, ...)."""

    def __init__(self, master, values: Optional[list[str]] = None, height: int = 4):
        super().__init__(master)
        self.listbox = tk.Listbox(self, height=height, exportselection=False)
        self.listbox.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.columnconfigure(0, weight=1)

        self.entry = ttk.Entry(self)
        self.entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.entry.bind("<Return>", lambda _e: self._add())

        btns = ttk.Frame(self)
        btns.grid(row=1, column=1, sticky="e", pady=(4, 0))
        ttk.Button(btns, text="Add", command=self._add, width=6).pack(side="left")
        ttk.Button(btns, text="Remove", command=self._remove, width=8).pack(side="left")

        self.set(values or [])

    def _add(self) -> None:
        value = self.entry.get().strip()
        if value:
            self.listbox.insert("end", value)
            self.entry.delete(0, "end")

    def _remove(self) -> None:
        for index in reversed(self.listbox.curselection()):
            self.listbox.delete(index)

    def get(self) -> list[str]:
        return list(self.listbox.get(0, "end"))

    def set(self, values: list[str]) -> None:
        self.listbox.delete(0, "end")
        for v in values:
            self.listbox.insert("end", v)


class LevelUpListWidget(ttk.Frame):
    """Editor for the learnset's level-up list: move name + the level it's learned at."""

    def __init__(self, master, values: Optional[list[LevelUpMove]] = None, height: int = 5):
        super().__init__(master)
        columns = ("move", "level")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=height)
        self.tree.heading("move", text="Move")
        self.tree.heading("level", text="Level")
        self.tree.column("move", width=160)
        self.tree.column("level", width=60, anchor="center")
        self.tree.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.columnconfigure(0, weight=1)

        self.move_entry = ttk.Entry(self, width=18)
        self.move_entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.level_entry = ttk.Entry(self, width=6)
        self.level_entry.grid(row=1, column=1, sticky="ew", pady=(4, 0), padx=(4, 0))

        btns = ttk.Frame(self)
        btns.grid(row=1, column=2, sticky="e", pady=(4, 0))
        ttk.Button(btns, text="Add", command=self._add, width=6).pack(side="left")
        ttk.Button(btns, text="Remove", command=self._remove, width=8).pack(side="left")

        self.set(values or [])

    def _add(self) -> None:
        move = self.move_entry.get().strip()
        level_text = self.level_entry.get().strip()
        if not move:
            return
        try:
            level = int(level_text) if level_text else 1
        except ValueError:
            level = 1
        self.tree.insert("", "end", values=(move, level))
        self.move_entry.delete(0, "end")
        self.level_entry.delete(0, "end")

    def _remove(self) -> None:
        for item in self.tree.selection():
            self.tree.delete(item)

    def get(self) -> list[LevelUpMove]:
        result = []
        for item in self.tree.get_children():
            move, level = self.tree.item(item, "values")
            result.append(LevelUpMove(move=move, level=int(level)))
        return result

    def set(self, values: list[LevelUpMove]) -> None:
        self.tree.delete(*self.tree.get_children())
        for m in values:
            self.tree.insert("", "end", values=(m.move, m.level))


class StructuredLocationTable(ttk.Frame):
    """Editor for structured encounter rows: location / method / min level / max level."""

    def __init__(self, master, entries: Optional[list[LocationEntry]] = None, height: int = 5):
        super().__init__(master)
        columns = ("location", "method", "minLevel", "maxLevel")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=height)
        for col, label, width in (
            ("location", "Location", 160), ("method", "Method", 100),
            ("minLevel", "Min Lv", 60), ("maxLevel", "Max Lv", 60),
        ):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center" if "Lv" in col else "w")
        self.tree.grid(row=0, column=0, columnspan=5, sticky="nsew")
        self.columnconfigure(0, weight=1)

        self.location_entry = ttk.Entry(self, width=16)
        self.location_entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.method_entry = ttk.Entry(self, width=12)
        self.method_entry.grid(row=1, column=1, sticky="ew", pady=(4, 0), padx=(4, 0))
        self.min_level_entry = ttk.Entry(self, width=6)
        self.min_level_entry.grid(row=1, column=2, sticky="ew", pady=(4, 0), padx=(4, 0))
        self.max_level_entry = ttk.Entry(self, width=6)
        self.max_level_entry.grid(row=1, column=3, sticky="ew", pady=(4, 0), padx=(4, 0))

        btns = ttk.Frame(self)
        btns.grid(row=1, column=4, sticky="e", pady=(4, 0))
        ttk.Button(btns, text="Add", command=self._add, width=6).pack(side="left")
        ttk.Button(btns, text="Remove", command=self._remove, width=8).pack(side="left")

        self.set(entries or [])

    def _add(self) -> None:
        location = self.location_entry.get().strip()
        if not location:
            return
        method = self.method_entry.get().strip()

        def parse_level(text: str) -> int:
            try:
                return int(text)
            except ValueError:
                return 1

        min_level = parse_level(self.min_level_entry.get().strip())
        max_level = parse_level(self.max_level_entry.get().strip())
        self.tree.insert("", "end", values=(location, method, min_level, max_level))
        for entry in (self.location_entry, self.method_entry, self.min_level_entry, self.max_level_entry):
            entry.delete(0, "end")

    def _remove(self) -> None:
        for item in self.tree.selection():
            self.tree.delete(item)

    def get(self) -> list[LocationEntry]:
        result = []
        for item in self.tree.get_children():
            location, method, min_level, max_level = self.tree.item(item, "values")
            result.append(LocationEntry(location=location, method=method, minLevel=int(min_level), maxLevel=int(max_level)))
        return result

    def set(self, entries: list[LocationEntry]) -> None:
        self.tree.delete(*self.tree.get_children())
        for e in entries:
            self.tree.insert("", "end", values=(e.location, e.method, e.minLevel, e.maxLevel))


class AbilityListWidget(ttk.Frame):
    """Editor for the abilities list: name, hidden flag, and effect text."""

    def __init__(self, master, values: Optional[list[Ability]] = None, height: int = 5):
        super().__init__(master)
        columns = ("name", "hidden", "effect")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=height)
        self.tree.heading("name", text="Name")
        self.tree.heading("hidden", text="Hidden?")
        self.tree.heading("effect", text="Effect")
        self.tree.column("name", width=120)
        self.tree.column("hidden", width=60, anchor="center")
        self.tree.column("effect", width=280)
        self.tree.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.columnconfigure(0, weight=1)

        self.name_entry = ttk.Entry(self, width=16)
        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.hidden_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Hidden", variable=self.hidden_var).grid(row=1, column=1, padx=(4, 0), pady=(4, 0))
        self.effect_entry = ttk.Entry(self, width=32)
        self.effect_entry.grid(row=1, column=2, sticky="ew", pady=(4, 0), padx=(4, 0))

        btns = ttk.Frame(self)
        btns.grid(row=1, column=3, sticky="e", pady=(4, 0))
        ttk.Button(btns, text="Add", command=self._add, width=6).pack(side="left")
        ttk.Button(btns, text="Remove", command=self._remove, width=8).pack(side="left")

        self.set(values or [])

    def _add(self) -> None:
        name = self.name_entry.get().strip()
        if not name:
            return
        self.tree.insert("", "end", values=(name, self.hidden_var.get(), self.effect_entry.get().strip()))
        self.name_entry.delete(0, "end")
        self.effect_entry.delete(0, "end")
        self.hidden_var.set(False)

    def _remove(self) -> None:
        for item in self.tree.selection():
            self.tree.delete(item)

    def get(self) -> list[Ability]:
        result = []
        for item in self.tree.get_children():
            name, hidden, effect = self.tree.item(item, "values")
            result.append(Ability(name=name, hidden=str(hidden) in ("1", "True", "true"), effect=effect))
        return result

    def set(self, values: list[Ability]) -> None:
        self.tree.delete(*self.tree.get_children())
        for a in values:
            self.tree.insert("", "end", values=(a.name, a.hidden, a.effect))


class FormsListWidget(ttk.Frame):
    """Editor for the forms list: form code, form name, and whether it's the female form."""

    def __init__(self, master, values: Optional[list[Form]] = None, height: int = 5):
        super().__init__(master)
        columns = ("formCode", "formName", "isFemale")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=height)
        self.tree.heading("formCode", text="Form Code")
        self.tree.heading("formName", text="Form Name")
        self.tree.heading("isFemale", text="Female?")
        self.tree.column("formCode", width=100)
        self.tree.column("formName", width=160)
        self.tree.column("isFemale", width=60, anchor="center")
        self.tree.grid(row=0, column=0, columnspan=4, sticky="nsew")
        self.columnconfigure(0, weight=1)

        self.code_entry = ttk.Entry(self, width=12)
        self.code_entry.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.name_entry = ttk.Entry(self, width=20)
        self.name_entry.grid(row=1, column=1, sticky="ew", pady=(4, 0), padx=(4, 0))
        self.is_female_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="Female", variable=self.is_female_var).grid(row=1, column=2, padx=(4, 0), pady=(4, 0))

        btns = ttk.Frame(self)
        btns.grid(row=1, column=3, sticky="e", pady=(4, 0))
        ttk.Button(btns, text="Add", command=self._add, width=6).pack(side="left")
        ttk.Button(btns, text="Remove", command=self._remove, width=8).pack(side="left")

        self.set(values or [Form()])

    def _add(self) -> None:
        code = self.code_entry.get().strip() or None
        name = self.name_entry.get().strip() or None
        self.tree.insert("", "end", values=(code or "", name or "", self.is_female_var.get()))
        self.code_entry.delete(0, "end")
        self.name_entry.delete(0, "end")
        self.is_female_var.set(False)

    def _remove(self) -> None:
        selected = self.tree.selection()
        if len(self.tree.get_children()) - len(selected) < 1:
            return  # a species must always keep at least one form
        for item in selected:
            self.tree.delete(item)

    def get(self) -> list[Form]:
        result = []
        for item in self.tree.get_children():
            code, name, is_female = self.tree.item(item, "values")
            result.append(Form(
                formCode=code or None, formName=name or None,
                isFemale=str(is_female) in ("1", "True", "true"),
            ))
        return result or [Form()]

    def set(self, values: list[Form]) -> None:
        self.tree.delete(*self.tree.get_children())
        for f in (values or [Form()]):
            self.tree.insert("", "end", values=(f.formCode or "", f.formName or "", f.isFemale))
