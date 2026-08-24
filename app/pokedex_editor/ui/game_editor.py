"""Per-game data editor (feature 3): the sub-panel inside a species' edit form
that lists which games have an entry under ``games``, with add/edit/remove,
and the dialog used to edit one game's dexNumber/locations/learnset.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Optional

from ..models import GameEntry, GameSpeciesData, Learnset, Locations
from ..reference_data import LOCATION_TYPES
from .widgets import LevelUpListWidget, StringListWidget, StructuredLocationTable


class GameSpeciesDataDialog(simpledialog.Dialog):
    """Modal editor for one ``species.games[<gameId>]`` entry."""

    def __init__(self, master, game: GameEntry, data: Optional[GameSpeciesData] = None):
        self.game = game
        self.data = data or GameSpeciesData()
        self.result_data: Optional[GameSpeciesData] = None
        super().__init__(master, title=f"{game.displayName} data")

    def body(self, master):
        ttk.Label(master, text="Dex number in this game").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.dex_number_var = tk.StringVar(value=self.data.dexNumber)
        ttk.Entry(master, textvariable=self.dex_number_var, width=20).grid(row=0, column=1, sticky="w", padx=4, pady=2)

        loc_frame = ttk.LabelFrame(master, text="Locations")
        loc_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=4, pady=(8, 2))
        master.rowconfigure(1, weight=1)
        master.columnconfigure(1, weight=1)

        type_row = ttk.Frame(loc_frame)
        type_row.pack(fill="x", padx=4, pady=4)
        ttk.Label(type_row, text="Type:").pack(side="left")
        self.location_type_var = tk.StringVar(value=self.data.locations.type or LOCATION_TYPES[0])
        for lt in LOCATION_TYPES:
            ttk.Radiobutton(
                type_row, text=lt, value=lt, variable=self.location_type_var, command=self._swap_location_editor,
            ).pack(side="left", padx=(6, 0))

        source_row = ttk.Frame(loc_frame)
        source_row.pack(fill="x", padx=4)
        ttk.Label(source_row, text="Source:").pack(side="left")
        self.location_source_var = tk.StringVar(value=self.data.locations.source)
        ttk.Entry(source_row, textvariable=self.location_source_var, width=20).pack(side="left", padx=(6, 0))

        self.location_editor_container = ttk.Frame(loc_frame)
        self.location_editor_container.pack(fill="both", expand=True, padx=4, pady=4)
        self.structured_widget = StructuredLocationTable(
            self.location_editor_container,
            self.data.locations.entries if self.data.locations.type == "structured" else [],
        )
        self.freetext_widget = StringListWidget(
            self.location_editor_container,
            self.data.locations.entries if self.data.locations.type == "freeText" else [],
        )
        self._swap_location_editor()

        learn_frame = ttk.LabelFrame(master, text="Learnset")
        learn_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=4, pady=(8, 2))
        master.rowconfigure(2, weight=1)

        notebook = ttk.Notebook(learn_frame)
        notebook.pack(fill="both", expand=True, padx=4, pady=4)

        levelup_tab = ttk.Frame(notebook)
        notebook.add(levelup_tab, text="Level-up")
        self.levelup_widget = LevelUpListWidget(levelup_tab, self.data.learnset.levelUp)
        self.levelup_widget.pack(fill="both", expand=True, padx=4, pady=4)

        machine_tab = ttk.Frame(notebook)
        notebook.add(machine_tab, text="Machine")
        self.machine_widget = StringListWidget(machine_tab, self.data.learnset.machine)
        self.machine_widget.pack(fill="both", expand=True, padx=4, pady=4)

        egg_tab = ttk.Frame(notebook)
        notebook.add(egg_tab, text="Egg")
        self.egg_widget = StringListWidget(egg_tab, self.data.learnset.egg)
        self.egg_widget.pack(fill="both", expand=True, padx=4, pady=4)

        tutor_tab = ttk.Frame(notebook)
        notebook.add(tutor_tab, text="Tutor")
        self.tutor_widget = StringListWidget(tutor_tab, self.data.learnset.tutor)
        self.tutor_widget.pack(fill="both", expand=True, padx=4, pady=4)

        return master

    def _swap_location_editor(self) -> None:
        self.structured_widget.pack_forget()
        self.freetext_widget.pack_forget()
        if self.location_type_var.get() == "freeText":
            self.freetext_widget.pack(fill="both", expand=True)
        else:
            self.structured_widget.pack(fill="both", expand=True)

    def apply(self) -> None:
        loc_type = self.location_type_var.get()
        entries = self.freetext_widget.get() if loc_type == "freeText" else self.structured_widget.get()
        self.result_data = GameSpeciesData(
            dexNumber=self.dex_number_var.get().strip(),
            locations=Locations(type=loc_type, source=self.location_source_var.get().strip(), entries=entries),
            learnset=Learnset(
                levelUp=self.levelup_widget.get(),
                machine=self.machine_widget.get(),
                egg=self.egg_widget.get(),
                tutor=self.tutor_widget.get(),
            ),
        )


class GamesPanel(ttk.Frame):
    """Embedded panel listing a species' ``games`` entries with add/edit/remove."""

    def __init__(self, master, games_catalog: list[GameEntry]):
        super().__init__(master)
        self.games_catalog = {g.id: g for g in games_catalog}
        self.entries: dict[str, GameSpeciesData] = {}

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 4))
        ttk.Label(toolbar, text="Add game:").pack(side="left")
        self.add_game_var = tk.StringVar()
        self.add_game_combo = ttk.Combobox(toolbar, textvariable=self.add_game_var, state="readonly", width=24)
        self.add_game_combo.pack(side="left", padx=(4, 0))
        ttk.Button(toolbar, text="Add", command=self._add_game).pack(side="left", padx=(4, 0))
        ttk.Button(toolbar, text="Edit", command=self._edit_selected).pack(side="left", padx=(12, 0))
        ttk.Button(toolbar, text="Remove", command=self._remove_selected).pack(side="left", padx=(4, 0))

        self.tree = ttk.Treeview(self, columns=("game", "dexNumber"), show="headings", height=6)
        self.tree.heading("game", text="Game")
        self.tree.heading("dexNumber", text="Dex #")
        self.tree.column("game", width=180)
        self.tree.column("dexNumber", width=80, anchor="center")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", lambda _e: self._edit_selected())

    def set_games_catalog(self, games_catalog: list[GameEntry]) -> None:
        self.games_catalog = {g.id: g for g in games_catalog}
        self._refresh_add_combo()

    def load(self, entries: dict[str, GameSpeciesData]) -> None:
        self.entries = dict(entries)
        self._refresh_tree()
        self._refresh_add_combo()

    def get(self) -> dict[str, GameSpeciesData]:
        return dict(self.entries)

    def _refresh_add_combo(self) -> None:
        available = [gid for gid in self.games_catalog if gid not in self.entries]
        self.add_game_combo["values"] = available
        if available:
            self.add_game_var.set(available[0])
        else:
            self.add_game_var.set("")

    def _refresh_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for game_id, data in self.entries.items():
            display_name = self.games_catalog.get(game_id).displayName if game_id in self.games_catalog else game_id
            self.tree.insert("", "end", iid=game_id, values=(display_name, data.dexNumber))

    def _add_game(self) -> None:
        game_id = self.add_game_var.get()
        if not game_id:
            messagebox.showinfo("No games available", "Every catalog game is already on this species.")
            return
        game = self.games_catalog[game_id]
        dialog = GameSpeciesDataDialog(self, game=game)
        if dialog.result_data:
            self.entries[game_id] = dialog.result_data
            self._refresh_tree()
            self._refresh_add_combo()

    def _selected_id(self) -> Optional[str]:
        selection = self.tree.selection()
        return selection[0] if selection else None

    def _edit_selected(self) -> None:
        game_id = self._selected_id()
        if not game_id:
            return
        game = self.games_catalog.get(game_id) or GameEntry(id=game_id, displayName=game_id)
        dialog = GameSpeciesDataDialog(self, game=game, data=self.entries[game_id])
        if dialog.result_data:
            self.entries[game_id] = dialog.result_data
            self._refresh_tree()

    def _remove_selected(self) -> None:
        game_id = self._selected_id()
        if not game_id:
            return
        if messagebox.askyesno("Remove game data", f"Remove this species' data for '{game_id}'?"):
            del self.entries[game_id]
            self._refresh_tree()
            self._refresh_add_combo()
