"""Species edit form (feature 2): every schema field, grouped into tabs
matching the schema's own grouping, plus import/export (feature 5) and
validation-before-save (feature 6).
"""
from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Callable, Optional

from ..models import (
    Breeding, Classification, Cries, Evolution, JapaneseName, MetaInfo,
    SpeciesRecord, Sprites, Stats,
)
from ..reference_data import COLORS, GROWTH_RATES, HABITATS, POKEMON_TYPES, SHAPES
from ..repository import IGamesRepository, ISpeciesRepository
from ..validation import validate_species
from .game_editor import GamesPanel
from .widgets import AbilityListWidget, FormsListWidget, StringListWidget

_NONE_LABEL = "(none)"


def _int_or(text: str, default: int = 0) -> int:
    text = text.strip()
    if not text:
        return default
    return int(text)


def _float_or(text: str, default: float = 0.0) -> float:
    text = text.strip()
    if not text:
        return default
    return float(text)


class ImportJsonDialog(simpledialog.Dialog):
    """Paste-a-JSON-blob dialog used to seed a new (or overwrite an open) species."""

    def __init__(self, master):
        self.result_dict: Optional[dict] = None
        super().__init__(master, title="Import species JSON")

    def body(self, master):
        ttk.Label(master, text="Paste a species JSON blob matching the schema:").pack(anchor="w", padx=4, pady=(4, 0))
        self.text = tk.Text(master, width=70, height=24)
        self.text.pack(fill="both", expand=True, padx=4, pady=4)
        return self.text

    def validate(self) -> bool:
        raw = self.text.get("1.0", "end").strip()
        if not raw:
            messagebox.showerror("Import failed", "Paste a JSON blob first.", parent=self)
            return False
        try:
            self.result_dict = json.loads(raw)
        except json.JSONDecodeError as e:
            messagebox.showerror("Import failed", f"Not valid JSON:\n{e}", parent=self)
            return False
        return True


class SpeciesEditFrame(ttk.Frame):
    def __init__(
        self,
        master,
        species_repo: ISpeciesRepository,
        games_repo: IGamesRepository,
        on_saved: Callable[[], None] = lambda: None,
        on_deleted: Callable[[], None] = lambda: None,
        on_back: Optional[Callable[[], None]] = None,
    ):
        super().__init__(master)
        self.species_repo = species_repo
        self.games_repo = games_repo
        self.on_saved = on_saved
        self.on_deleted = on_deleted
        self.current_dex: Optional[int] = None  # None while creating a not-yet-saved species

        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=8, pady=8)
        if on_back is not None:
            ttk.Button(toolbar, text="< Back to list", command=on_back).pack(side="left", padx=(0, 12))
        ttk.Button(toolbar, text="New Species", command=self.new_species).pack(side="left")
        ttk.Button(toolbar, text="Import JSON...", command=self._import_json).pack(side="left", padx=(4, 0))
        ttk.Button(toolbar, text="Export to file...", command=self._export_to_file).pack(side="left", padx=(4, 0))
        ttk.Button(toolbar, text="Save", command=self.save).pack(side="left", padx=(12, 0))
        ttk.Button(toolbar, text="Delete", command=self.delete).pack(side="left", padx=(4, 0))
        self.status_label = ttk.Label(toolbar, text="")
        self.status_label.pack(side="left", padx=(12, 0))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._build_identity_tab()
        self._build_stats_tab()
        self._build_abilities_tab()
        self._build_breeding_tab()
        self._build_classification_tab()
        self._build_evolution_tab()
        self._build_sprites_tab()
        self._build_forms_tab()
        self._build_games_tab()

        self.load(SpeciesRecord(dex=0, keyword="", name="", type1=POKEMON_TYPES[0]))

    # -- tab construction ------------------------------------------------

    def _build_identity_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Identity")

        self.dex_var = tk.StringVar()
        self.keyword_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.kana_var = tk.StringVar()
        self.romaji_var = tk.StringVar()
        self.type1_var = tk.StringVar()
        self.type2_var = tk.StringVar()
        self.genus_var = tk.StringVar()
        self.height_var = tk.StringVar()
        self.weight_var = tk.StringVar()
        self.flavor_source_var = tk.StringVar()
        self.gender_diff_var = tk.StringVar()

        row = 0
        for label, var in (("Dex #", self.dex_var), ("Keyword (slug)", self.keyword_var), ("Name", self.name_var)):
            ttk.Label(tab, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
            ttk.Entry(tab, textvariable=var, width=30).grid(row=row, column=1, sticky="w", padx=4, pady=2)
            row += 1

        ttk.Label(tab, text="Japanese kana").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.kana_var, width=30).grid(row=row, column=1, sticky="w", padx=4, pady=2)
        row += 1
        ttk.Label(tab, text="Japanese romaji").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.romaji_var, width=30).grid(row=row, column=1, sticky="w", padx=4, pady=2)
        row += 1

        ttk.Label(tab, text="Type 1").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Combobox(tab, textvariable=self.type1_var, values=POKEMON_TYPES, state="readonly", width=27).grid(row=row, column=1, sticky="w", padx=4, pady=2)
        row += 1
        ttk.Label(tab, text="Type 2").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Combobox(tab, textvariable=self.type2_var, values=(_NONE_LABEL,) + POKEMON_TYPES, state="readonly", width=27).grid(row=row, column=1, sticky="w", padx=4, pady=2)
        row += 1

        ttk.Label(tab, text="Genus").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.genus_var, width=30).grid(row=row, column=1, sticky="w", padx=4, pady=2)
        row += 1
        ttk.Label(tab, text="Height (m)").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.height_var, width=10).grid(row=row, column=1, sticky="w", padx=4, pady=2)
        row += 1
        ttk.Label(tab, text="Weight (kg)").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.weight_var, width=10).grid(row=row, column=1, sticky="w", padx=4, pady=2)
        row += 1

        ttk.Label(tab, text="Flavor text").grid(row=row, column=0, sticky="nw", padx=4, pady=2)
        self.flavor_text_widget = tk.Text(tab, width=50, height=4)
        self.flavor_text_widget.grid(row=row, column=1, sticky="w", padx=4, pady=2)
        row += 1
        ttk.Label(tab, text="Flavor text source game").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.flavor_source_var, width=30).grid(row=row, column=1, sticky="w", padx=4, pady=2)
        row += 1

        ttk.Label(tab, text="Gender difference note").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.gender_diff_var, width=30).grid(row=row, column=1, sticky="w", padx=4, pady=2)

    def _build_stats_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Stats")
        self.stat_vars: dict[str, tk.StringVar] = {}
        labels = [
            ("hp", "HP"), ("attack", "Attack"), ("defense", "Defense"),
            ("specialAttack", "Sp. Attack"), ("specialDefense", "Sp. Defense"), ("speed", "Speed"),
        ]
        for row, (key, label) in enumerate(labels):
            ttk.Label(tab, text=label).grid(row=row, column=0, sticky="w", padx=4, pady=2)
            var = tk.StringVar()
            self.stat_vars[key] = var
            ttk.Entry(tab, textvariable=var, width=10).grid(row=row, column=1, sticky="w", padx=4, pady=2)

    def _build_abilities_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Abilities")
        self.abilities_widget = AbilityListWidget(tab)
        self.abilities_widget.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_breeding_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Breeding")

        ttk.Label(tab, text="Egg groups").grid(row=0, column=0, sticky="nw", padx=4, pady=2)
        self.egg_groups_widget = StringListWidget(tab, height=3)
        self.egg_groups_widget.grid(row=0, column=1, sticky="w", padx=4, pady=2)

        self.gender_rate_var = tk.StringVar()
        self.hatch_cycles_var = tk.StringVar()
        self.capture_rate_var = tk.StringVar()
        self.base_friendship_var = tk.StringVar()
        self.growth_rate_var = tk.StringVar()

        rows = [
            ("Gender rate (eighths female, -1 genderless)", self.gender_rate_var),
            ("Hatch cycles", self.hatch_cycles_var),
            ("Capture rate", self.capture_rate_var),
            ("Base friendship", self.base_friendship_var),
        ]
        for i, (label, var) in enumerate(rows, start=1):
            ttk.Label(tab, text=label).grid(row=i, column=0, sticky="w", padx=4, pady=2)
            ttk.Entry(tab, textvariable=var, width=10).grid(row=i, column=1, sticky="w", padx=4, pady=2)

        row = len(rows) + 1
        ttk.Label(tab, text="Growth rate").grid(row=row, column=0, sticky="w", padx=4, pady=2)
        ttk.Combobox(tab, textvariable=self.growth_rate_var, values=GROWTH_RATES, state="readonly", width=27).grid(row=row, column=1, sticky="w", padx=4, pady=2)

    def _build_classification_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Classification")

        self.color_var = tk.StringVar()
        self.shape_var = tk.StringVar()
        self.habitat_var = tk.StringVar()
        self.is_legendary_var = tk.BooleanVar()
        self.is_mythical_var = tk.BooleanVar()
        self.is_baby_var = tk.BooleanVar()
        self.generation_var = tk.StringVar()

        ttk.Label(tab, text="Color").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        ttk.Combobox(tab, textvariable=self.color_var, values=COLORS, state="readonly", width=27).grid(row=0, column=1, sticky="w", padx=4, pady=2)
        ttk.Label(tab, text="Shape").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        ttk.Combobox(tab, textvariable=self.shape_var, values=SHAPES, state="readonly", width=27).grid(row=1, column=1, sticky="w", padx=4, pady=2)
        ttk.Label(tab, text="Habitat").grid(row=2, column=0, sticky="w", padx=4, pady=2)
        ttk.Combobox(tab, textvariable=self.habitat_var, values=(_NONE_LABEL,) + HABITATS, state="readonly", width=27).grid(row=2, column=1, sticky="w", padx=4, pady=2)
        ttk.Label(tab, text="Generation introduced").grid(row=3, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.generation_var, width=10).grid(row=3, column=1, sticky="w", padx=4, pady=2)

        ttk.Checkbutton(tab, text="Legendary", variable=self.is_legendary_var).grid(row=4, column=0, sticky="w", padx=4, pady=2)
        ttk.Checkbutton(tab, text="Mythical", variable=self.is_mythical_var).grid(row=5, column=0, sticky="w", padx=4, pady=2)
        ttk.Checkbutton(tab, text="Baby", variable=self.is_baby_var).grid(row=6, column=0, sticky="w", padx=4, pady=2)

    def _build_evolution_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Evolution")

        ttk.Label(tab, text="Evolves from dex # (blank = none)").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.evolves_from_var = tk.StringVar()
        ttk.Entry(tab, textvariable=self.evolves_from_var, width=10).grid(row=0, column=1, sticky="w", padx=4, pady=2)

        ttk.Label(tab, text="Evolves into (dex numbers)").grid(row=1, column=0, sticky="nw", padx=4, pady=2)
        self.evolves_into_widget = StringListWidget(tab, height=4)
        self.evolves_into_widget.grid(row=1, column=1, sticky="w", padx=4, pady=2)

    def _build_sprites_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Sprites / Cries")

        self.sprite_regular_var = tk.StringVar()
        self.sprite_shiny_var = tk.StringVar()
        ttk.Label(tab, text="Regular sprite path").grid(row=0, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.sprite_regular_var, width=40).grid(row=0, column=1, sticky="w", padx=4, pady=2)
        ttk.Label(tab, text="Shiny sprite path").grid(row=1, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.sprite_shiny_var, width=40).grid(row=1, column=1, sticky="w", padx=4, pady=2)

        self.has_cries_var = tk.BooleanVar()
        ttk.Checkbutton(tab, text="Has cry URLs", variable=self.has_cries_var).grid(row=2, column=0, sticky="w", padx=4, pady=(8, 2))
        self.cry_latest_var = tk.StringVar()
        self.cry_legacy_var = tk.StringVar()
        ttk.Label(tab, text="Latest cry URL").grid(row=3, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.cry_latest_var, width=50).grid(row=3, column=1, sticky="w", padx=4, pady=2)
        ttk.Label(tab, text="Legacy cry URL").grid(row=4, column=0, sticky="w", padx=4, pady=2)
        ttk.Entry(tab, textvariable=self.cry_legacy_var, width=50).grid(row=4, column=1, sticky="w", padx=4, pady=2)

    def _build_forms_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Forms")
        self.forms_widget = FormsListWidget(tab)
        self.forms_widget.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_games_tab(self) -> None:
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Games")
        self.games_panel = GamesPanel(tab, self.games_repo.get_all())
        self.games_panel.pack(fill="both", expand=True, padx=4, pady=4)

    # -- load / gather -----------------------------------------------------

    def load(self, species: SpeciesRecord) -> None:
        self.current_dex = species.dex if species.dex else None
        self._set_status("")

        self.dex_var.set(str(species.dex) if species.dex else "")
        self.keyword_var.set(species.keyword)
        self.name_var.set(species.name)
        self.kana_var.set(species.japaneseName.kana if species.japaneseName else "")
        self.romaji_var.set(species.japaneseName.romaji if species.japaneseName else "")
        self.type1_var.set(species.type1 or POKEMON_TYPES[0])
        self.type2_var.set(species.type2 or _NONE_LABEL)
        self.genus_var.set(species.genus)
        self.height_var.set(str(species.heightM))
        self.weight_var.set(str(species.weightKg))
        self.flavor_text_widget.delete("1.0", "end")
        self.flavor_text_widget.insert("1.0", species.flavorText)
        self.flavor_source_var.set(species.flavorTextSourceGame)
        self.gender_diff_var.set(species.genderDifference or "")

        for key, var in self.stat_vars.items():
            var.set(str(getattr(species.stats, key)))

        self.abilities_widget.set(species.abilities)

        self.egg_groups_widget.set(species.breeding.eggGroups)
        self.gender_rate_var.set(str(species.breeding.genderRateEighthsFemale))
        self.hatch_cycles_var.set(str(species.breeding.hatchCycles))
        self.capture_rate_var.set(str(species.breeding.captureRate))
        self.base_friendship_var.set(str(species.breeding.baseFriendship))
        self.growth_rate_var.set(species.breeding.growthRate or GROWTH_RATES[0])

        self.color_var.set(species.classification.color or COLORS[0])
        self.shape_var.set(species.classification.shape or SHAPES[0])
        self.habitat_var.set(species.classification.habitat or _NONE_LABEL)
        self.is_legendary_var.set(species.classification.isLegendary)
        self.is_mythical_var.set(species.classification.isMythical)
        self.is_baby_var.set(species.classification.isBaby)
        self.generation_var.set(str(species.classification.generationIntroduced))

        self.evolves_from_var.set(str(species.evolution.evolvesFromDex) if species.evolution.evolvesFromDex else "")
        self.evolves_into_widget.set([str(d) for d in species.evolution.evolvesIntoDex])

        self.sprite_regular_var.set(species.sprites.regular)
        self.sprite_shiny_var.set(species.sprites.shiny)
        self.has_cries_var.set(species.cries is not None)
        self.cry_latest_var.set(species.cries.latest if species.cries else "")
        self.cry_legacy_var.set(species.cries.legacy if species.cries else "")

        self.forms_widget.set(species.forms)

        self.games_panel.set_games_catalog(self.games_repo.get_all())
        self.games_panel.load(species.games)

        self._loaded_meta = species.meta

    def _gather(self) -> SpeciesRecord:
        kana = self.kana_var.get().strip()
        romaji = self.romaji_var.get().strip()
        japanese_name = JapaneseName(kana=kana, romaji=romaji) if (kana or romaji) else None

        type2 = self.type2_var.get()
        type2 = None if type2 in ("", _NONE_LABEL) else type2

        habitat = self.habitat_var.get()
        habitat = None if habitat in ("", _NONE_LABEL) else habitat

        evolves_from_text = self.evolves_from_var.get().strip()
        evolves_from = int(evolves_from_text) if evolves_from_text else None
        evolves_into = [int(v) for v in self.evolves_into_widget.get() if v.strip()]

        cries = Cries(latest=self.cry_latest_var.get().strip(), legacy=self.cry_legacy_var.get().strip()) if self.has_cries_var.get() else None

        meta = getattr(self, "_loaded_meta", None) or MetaInfo()
        from datetime import date
        meta.lastUpdated = date.today().isoformat()

        return SpeciesRecord(
            dex=_int_or(self.dex_var.get()),
            keyword=self.keyword_var.get().strip(),
            name=self.name_var.get().strip(),
            japaneseName=japanese_name,
            type1=self.type1_var.get(),
            type2=type2,
            genus=self.genus_var.get().strip(),
            heightM=_float_or(self.height_var.get()),
            weightKg=_float_or(self.weight_var.get()),
            flavorText=self.flavor_text_widget.get("1.0", "end").strip(),
            flavorTextSourceGame=self.flavor_source_var.get().strip(),
            stats=Stats(**{k: _int_or(v.get()) for k, v in self.stat_vars.items()}),
            abilities=self.abilities_widget.get(),
            breeding=Breeding(
                eggGroups=self.egg_groups_widget.get(),
                genderRateEighthsFemale=_int_or(self.gender_rate_var.get(), -1),
                hatchCycles=_int_or(self.hatch_cycles_var.get()),
                captureRate=_int_or(self.capture_rate_var.get()),
                baseFriendship=_int_or(self.base_friendship_var.get()),
                growthRate=self.growth_rate_var.get(),
            ),
            classification=Classification(
                color=self.color_var.get(),
                shape=self.shape_var.get(),
                habitat=habitat,
                isLegendary=self.is_legendary_var.get(),
                isMythical=self.is_mythical_var.get(),
                isBaby=self.is_baby_var.get(),
                generationIntroduced=_int_or(self.generation_var.get(), 1),
            ),
            genderDifference=self.gender_diff_var.get().strip() or None,
            evolution=Evolution(evolvesFromDex=evolves_from, evolvesIntoDex=evolves_into),
            sprites=Sprites(regular=self.sprite_regular_var.get().strip(), shiny=self.sprite_shiny_var.get().strip()),
            cries=cries,
            forms=self.forms_widget.get(),
            games=self.games_panel.get(),
            meta=meta,
        )

    # -- actions -------------------------------------------------------

    def new_species(self) -> None:
        self.load(SpeciesRecord(dex=0, keyword="", name="", type1=POKEMON_TYPES[0]))

    def save(self) -> None:
        try:
            species = self._gather()
        except ValueError as e:
            messagebox.showerror("Invalid input", f"Couldn't read the form: {e}")
            return

        valid_game_ids = {g.id for g in self.games_repo.get_all()}
        valid_dex_numbers = {s.dex for s in self.species_repo.get_all()} | {species.dex}
        errors = validate_species(species, valid_game_ids, valid_dex_numbers)
        if errors:
            messagebox.showerror("Validation failed", "\n".join(f"• {e}" for e in errors))
            return

        self.species_repo.save(species)
        self.current_dex = species.dex
        self._set_status(f"Saved #{species.dex:04d} {species.name}")
        self.on_saved()

    def delete(self) -> None:
        if self.current_dex is None:
            messagebox.showinfo("Nothing to delete", "This species hasn't been saved yet.")
            return
        if messagebox.askyesno("Delete species", f"Delete species #{self.current_dex:04d}? This cannot be undone."):
            self.species_repo.delete(self.current_dex)
            self.new_species()
            self.on_deleted()

    def _import_json(self) -> None:
        dialog = ImportJsonDialog(self)
        if dialog.result_dict is not None:
            try:
                species = SpeciesRecord.from_dict(dialog.result_dict)
            except Exception as e:
                messagebox.showerror("Import failed", f"Blob doesn't match the schema: {e}")
                return
            self.load(species)
            self._set_status("Imported — review and Save to write it to disk.")

    def _export_to_file(self) -> None:
        try:
            species = self._gather()
        except ValueError as e:
            messagebox.showerror("Invalid input", f"Couldn't read the form: {e}")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            initialfile=f"{species.dex:04d}.json" if species.dex else "species.json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            json.dump(species.to_dict(), f, indent=2, ensure_ascii=False)
            f.write("\n")
        self._set_status(f"Exported to {path}")

    def _set_status(self, text: str) -> None:
        self.status_label.config(text=text)
