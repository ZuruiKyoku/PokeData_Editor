"""Games catalog screen — full CRUD on data/games.json (feature 4)."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Optional

from ..models import GameEntry
from ..reference_data import ENCOUNTER_DATA_SOURCES
from ..repository import IGamesRepository


class GameEntryDialog(simpledialog.Dialog):
    """Modal add/edit form for one games-catalog entry."""

    def __init__(self, master, existing_ids: set[str], game: Optional[GameEntry] = None):
        self.existing_ids = existing_ids
        self.game = game or GameEntry()
        self.editing_id = game.id if game else None
        self.result_game: Optional[GameEntry] = None
        title = f"Edit {self.game.displayName}" if game else "New Game"
        super().__init__(master, title=title)

    def body(self, master):
        rows = [
            ("Id (slug)", "id_var", self.game.id),
            ("Display name", "displayName_var", self.game.displayName),
            ("Release order", "releaseOrder_var", str(self.game.releaseOrder)),
            ("Generation", "generation_var", str(self.game.generation)),
            ("Release date (YYYY-MM-DD)", "releaseDate_var", self.game.releaseDate),
            ("Region", "region_var", self.game.region),
        ]
        for i, (label, attr, value) in enumerate(rows):
            ttk.Label(master, text=label).grid(row=i, column=0, sticky="w", padx=4, pady=2)
            var = tk.StringVar(value=value)
            setattr(self, attr, var)
            ttk.Entry(master, textvariable=var, width=30).grid(row=i, column=1, sticky="ew", padx=4, pady=2)

        row = len(rows)
        ttk.Label(master, text="Encounter data source").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        self.encounterDataSource_var = tk.StringVar(value=self.game.encounterDataSource or ENCOUNTER_DATA_SOURCES[0])
        ttk.Combobox(
            master, textvariable=self.encounterDataSource_var, values=ENCOUNTER_DATA_SOURCES, state="readonly", width=27,
        ).grid(row=row, column=1, sticky="ew", padx=4, pady=2)

        row += 1
        ttk.Label(master, text="Notes").grid(row=row, column=0, sticky="nw", padx=4, pady=2)
        self.notes_text = tk.Text(master, width=30, height=4)
        self.notes_text.insert("1.0", self.game.notes)
        self.notes_text.grid(row=row, column=1, sticky="ew", padx=4, pady=2)
        return master

    def validate(self) -> bool:
        game_id = self.id_var.get().strip()
        if not game_id:
            messagebox.showerror("Invalid game", "Id is required.", parent=self)
            return False
        if game_id != self.editing_id and game_id in self.existing_ids:
            messagebox.showerror("Invalid game", f"A game with id '{game_id}' already exists.", parent=self)
            return False
        if not self.displayName_var.get().strip():
            messagebox.showerror("Invalid game", "Display name is required.", parent=self)
            return False
        for numeric_var, label in ((self.releaseOrder_var, "Release order"), (self.generation_var, "Generation")):
            try:
                int(numeric_var.get().strip() or "0")
            except ValueError:
                messagebox.showerror("Invalid game", f"{label} must be a whole number.", parent=self)
                return False
        return True

    def apply(self) -> None:
        self.result_game = GameEntry(
            id=self.id_var.get().strip(),
            displayName=self.displayName_var.get().strip(),
            releaseOrder=int(self.releaseOrder_var.get().strip() or "0"),
            generation=int(self.generation_var.get().strip() or "0"),
            releaseDate=self.releaseDate_var.get().strip(),
            region=self.region_var.get().strip(),
            encounterDataSource=self.encounterDataSource_var.get(),
            notes=self.notes_text.get("1.0", "end").strip(),
        )


class GamesCatalogFrame(ttk.Frame):
    def __init__(self, master, games_repo: IGamesRepository):
        super().__init__(master)
        self.games_repo = games_repo

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=8)
        ttk.Button(toolbar, text="New Game", command=self._new_game).pack(side="left")
        ttk.Button(toolbar, text="Edit", command=self._edit_selected).pack(side="left", padx=(4, 0))
        ttk.Button(toolbar, text="Delete", command=self._delete_selected).pack(side="left", padx=(4, 0))
        ttk.Button(toolbar, text="Refresh", command=self.refresh).pack(side="left", padx=(4, 0))

        columns = ("id", "displayName", "generation", "releaseDate", "region", "encounterDataSource")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        headings = {
            "id": "Id", "displayName": "Name", "generation": "Gen",
            "releaseDate": "Released", "region": "Region", "encounterDataSource": "Encounter Source",
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=120 if col not in ("displayName",) else 160)
        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.tree.bind("<Double-1>", lambda _e: self._edit_selected())

        self.refresh()

    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for game in self.games_repo.get_all():
            self.tree.insert("", "end", iid=game.id, values=(
                game.id, game.displayName, game.generation, game.releaseDate, game.region, game.encounterDataSource,
            ))

    def _selected_id(self) -> Optional[str]:
        selection = self.tree.selection()
        return selection[0] if selection else None

    def _new_game(self) -> None:
        existing_ids = {g.id for g in self.games_repo.get_all()}
        dialog = GameEntryDialog(self, existing_ids=existing_ids)
        if dialog.result_game:
            self.games_repo.save(dialog.result_game)
            self.refresh()

    def _edit_selected(self) -> None:
        game_id = self._selected_id()
        if not game_id:
            return
        game = self.games_repo.get_by_id(game_id)
        if not game:
            return
        existing_ids = {g.id for g in self.games_repo.get_all()} - {game_id}
        dialog = GameEntryDialog(self, existing_ids=existing_ids, game=game)
        if dialog.result_game:
            if dialog.result_game.id != game_id:
                self.games_repo.delete(game_id)
            self.games_repo.save(dialog.result_game)
            self.refresh()

    def _delete_selected(self) -> None:
        game_id = self._selected_id()
        if not game_id:
            return
        if messagebox.askyesno("Delete game", f"Delete '{game_id}' from the catalog?\n\nSpecies still referencing it will fail validation until fixed."):
            self.games_repo.delete(game_id)
            self.refresh()
