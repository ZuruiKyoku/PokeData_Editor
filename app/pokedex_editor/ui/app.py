"""Main application window — wires the species list, species edit form, and
games catalog screens together behind a top-level notebook.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..repository import IGamesRepository, ISpeciesRepository
from .games_catalog import GamesCatalogFrame
from .species_edit import SpeciesEditFrame
from .species_list import SpeciesListFrame


class App(ttk.Frame):
    def __init__(self, master: tk.Tk, species_repo: ISpeciesRepository, games_repo: IGamesRepository):
        super().__init__(master)
        self.master = master
        self.species_repo = species_repo
        self.games_repo = games_repo
        self.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Species tab: a container that swaps between the list screen and
        # the edit-form screen (selecting a row in the list opens the form).
        self.species_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.species_tab, text="Species")

        self.species_list = SpeciesListFrame(self.species_tab, species_repo, on_select=self.open_species)
        self.species_edit = SpeciesEditFrame(
            self.species_tab, species_repo, games_repo,
            on_saved=self._on_species_saved, on_deleted=self._on_species_deleted,
            on_back=self.show_species_list,
        )

        self.games_tab = GamesCatalogFrame(self.notebook, games_repo)
        self.notebook.add(self.games_tab, text="Games Catalog")

        self.show_species_list()

    def show_species_list(self) -> None:
        self.species_edit.pack_forget()
        self.species_list.pack(fill="both", expand=True)
        self.species_list.refresh()

    def show_species_edit(self) -> None:
        self.species_list.pack_forget()
        self.species_edit.pack(fill="both", expand=True)

    def open_species(self, dex: int) -> None:
        species = self.species_repo.get_by_dex(dex)
        if species is None:
            return
        self.species_edit.load(species)
        self.show_species_edit()

    def _on_species_saved(self) -> None:
        self.species_list.refresh()

    def _on_species_deleted(self) -> None:
        self.species_list.refresh()
        self.show_species_list()
