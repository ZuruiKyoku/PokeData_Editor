"""Species list (feature 1): searchable/filterable table sorted by dex number,
row selection opens the species in the edit form.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from ..models import SpeciesRecord
from ..repository import ISpeciesRepository


class SpeciesListFrame(ttk.Frame):
    def __init__(self, master, species_repo: ISpeciesRepository, on_select: Callable[[int], None]):
        super().__init__(master)
        self.species_repo = species_repo
        self.on_select = on_select
        self._all_species: list[SpeciesRecord] = []

        search_row = ttk.Frame(self)
        search_row.pack(fill="x", padx=8, pady=8)
        ttk.Label(search_row, text="Search (dex # or name):").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_a: self._apply_filter())
        ttk.Entry(search_row, textvariable=self.search_var, width=24).pack(side="left", padx=(4, 12))

        ttk.Label(search_row, text="Generation:").pack(side="left")
        self.gen_var = tk.StringVar(value="All")
        self.gen_combo = ttk.Combobox(search_row, textvariable=self.gen_var, state="readonly", width=6)
        self.gen_combo.pack(side="left", padx=(4, 12))
        self.gen_combo.bind("<<ComboboxSelected>>", lambda _e: self._apply_filter())

        ttk.Button(search_row, text="Refresh", command=self.refresh).pack(side="left")

        columns = ("dex", "name", "type1", "type2", "generation")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        headings = {"dex": "Dex #", "name": "Name", "type1": "Type 1", "type2": "Type 2", "generation": "Gen"}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=100 if col != "name" else 160, anchor="center" if col in ("dex", "generation") else "w")
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.tree.bind("<<TreeviewSelect>>", self._on_row_selected)
        self.tree.bind("<Double-1>", self._on_row_selected)

        self.refresh()

    def refresh(self) -> None:
        self._all_species = self.species_repo.get_all()
        generations = sorted({s.classification.generationIntroduced for s in self._all_species})
        self.gen_combo["values"] = ["All"] + [str(g) for g in generations]
        self._apply_filter()

    def _apply_filter(self) -> None:
        query = self.search_var.get().strip().lower()
        gen_filter = self.gen_var.get()

        self.tree.delete(*self.tree.get_children())
        for species in self._all_species:
            if gen_filter != "All" and str(species.classification.generationIntroduced) != gen_filter:
                continue
            if query and query not in species.name.lower() and query not in str(species.dex):
                continue
            self.tree.insert("", "end", iid=str(species.dex), values=(
                f"{species.dex:04d}", species.name, species.type1, species.type2 or "",
                species.classification.generationIntroduced,
            ))

    def _on_row_selected(self, _event) -> None:
        selection = self.tree.selection()
        if selection:
            self.on_select(int(selection[0]))
