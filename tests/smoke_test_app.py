"""Headless end-to-end UI smoke test — drives the real Tkinter widget tree
under a virtual X server (Xvfb), rather than just importing modules.

Run with:  xvfb-run -a python3 tests/smoke_test_app.py

tkinter.messagebox opens real modal dialogs (a blocking wait_window loop) —
under Xvfb there's nothing to click them, so every messagebox function is
stubbed out for the duration of this script. Modal Dialog subclasses
(GameEntryDialog, GameSpeciesDataDialog, ImportJsonDialog) are exercised by
patching Dialog.wait_window to a no-op so __init__ returns immediately after
building its widgets, then calling validate()/apply() the same way clicking
OK would.
"""
import json
import shutil
import sys
import tempfile
import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "app"))

_messagebox_calls = []


def _fake_showerror(title, message, **_kw):
    _messagebox_calls.append(("error", title, message))
    print(f"  [messagebox.showerror] {title}: {message}")


def _fake_showinfo(title, message, **_kw):
    _messagebox_calls.append(("info", title, message))
    print(f"  [messagebox.showinfo] {title}: {message}")


def _fake_askyesno(title, message, **_kw):
    _messagebox_calls.append(("askyesno", title, message))
    return True


messagebox.showerror = _fake_showerror
messagebox.showinfo = _fake_showinfo
messagebox.askyesno = _fake_askyesno
simpledialog.Dialog.wait_window = lambda self, window=None: None

from pokedex_editor.models import (  # noqa: E402
    Ability, Form, GameEntry, GameSpeciesData, Learnset, LevelUpMove,
    LocationEntry, Locations, SpeciesRecord,
)
from pokedex_editor.repository import (  # noqa: E402
    JsonFileGamesRepository, JsonFileSpeciesRepository,
)
from pokedex_editor.ui.app import App  # noqa: E402
from pokedex_editor.ui.game_editor import GameSpeciesDataDialog  # noqa: E402
from pokedex_editor.ui.games_catalog import GameEntryDialog, GamesCatalogFrame  # noqa: E402
from pokedex_editor.ui.species_edit import ImportJsonDialog  # noqa: E402
from pokedex_editor.ui.widgets import (  # noqa: E402
    AbilityListWidget, FormsListWidget, LevelUpListWidget,
    StringListWidget, StructuredLocationTable,
)

root = tk.Tk()

# ---------------------------------------------------------------------
# Part 1: full app, against a throwaway copy of the seed data.
# ---------------------------------------------------------------------
tmp_data = Path(tempfile.mkdtemp()) / "data"
shutil.copytree(REPO / "data", tmp_data)

species_repo = JsonFileSpeciesRepository(tmp_data / "species")
games_repo = JsonFileGamesRepository(tmp_data / "games.json")

# Bulbasaur's seed data references evolvesIntoDex=[2] (Ivysaur) — give the
# validator something real to resolve that against.
species_repo.save(SpeciesRecord(dex=2, keyword="ivysaur", name="Ivysaur", type1="Grass", type2="Poison"))

app = App(root, species_repo, games_repo)
root.update()

all_rows = app.species_list.tree.get_children()
assert len(all_rows) == 2, f"expected 2 seeded species, got {len(all_rows)}"
assert set(all_rows) == {"1", "2"}
print("OK: species list populated")

app.species_list.search_var.set("bulba")
root.update()
assert len(app.species_list.tree.get_children()) == 1
app.species_list.search_var.set("zzz-not-a-match")
root.update()
assert len(app.species_list.tree.get_children()) == 0
app.species_list.search_var.set("")
root.update()
assert len(app.species_list.tree.get_children()) == 2
print("OK: search filter")

app.open_species(1)
root.update()
assert app.species_edit.winfo_ismapped()
assert app.species_edit.name_var.get() == "Bulbasaur"
assert app.species_edit.type1_var.get() == "Grass"
assert app.species_edit.type2_var.get() == "Poison"
assert app.species_edit.stat_vars["hp"].get() == "45"
abilities = app.species_edit.abilities_widget.get()
assert [a.name for a in abilities] == ["overgrow", "chlorophyll"]
assert app.species_edit.egg_groups_widget.get() == ["Monster", "Grass"]
games_loaded = app.species_edit.games_panel.get()
assert set(games_loaded.keys()) == {"sword-shield", "scarlet-violet"}
assert games_loaded["scarlet-violet"].locations.type == "freeText"
assert games_loaded["sword-shield"].locations.type == "structured"
print("OK: edit form loaded from record")

gathered = app.species_edit._gather()
assert gathered.name == "Bulbasaur"
assert gathered.games["sword-shield"].learnset.levelUp[0].move == "tackle"
assert gathered.evolution.evolvesIntoDex == [2]
print("OK: form gathers back into a SpeciesRecord")

app.species_edit.name_var.set("Bulbasaur (edited)")
app.species_edit.save()
root.update()
reloaded = species_repo.get_by_dex(1)
assert reloaded.name == "Bulbasaur (edited)", reloaded.name
print("OK: save persists edits to disk")

assert len(app.species_list.tree.get_children()) == 2

app.species_edit.new_species()
root.update()
assert app.species_edit.dex_var.get() == ""
app.species_edit.save()  # dex 0 -> validation must reject this, not create a file
root.update()
assert species_repo.get_by_dex(0) is None
assert any(kind == "error" for kind, _t, _m in _messagebox_calls)
print("OK: validation blocks an invalid (dex=0) save without throwing")

app.notebook.select(app.games_tab)
root.update()
assert len(app.games_tab.tree.get_children()) == 2
print("OK: games catalog tab shows seeded games")

app.open_species(1)
root.update()
new_game = GameEntry(id="legends-arceus", displayName="Legends: Arceus", releaseOrder=17, generation=8)
games_repo.save(new_game)
app.species_edit.games_panel.set_games_catalog(games_repo.get_all())
root.update()
assert "legends-arceus" in app.species_edit.games_panel.add_game_combo["values"]
print("OK: newly catalogued game becomes available to add to a species")

# ---------------------------------------------------------------------
# Part 2: shared list-editing widgets in isolation.
# ---------------------------------------------------------------------
w = StringListWidget(root, ["Monster", "Grass"])
root.update()
assert w.get() == ["Monster", "Grass"]
w.set(["Bug"])
assert w.get() == ["Bug"]

w = LevelUpListWidget(root, [LevelUpMove("tackle", 1), LevelUpMove("vine-whip", 15)])
root.update()
assert [(m.move, m.level) for m in w.get()] == [("tackle", 1), ("vine-whip", 15)]

w = StructuredLocationTable(root, [LocationEntry("Route 1", "Walk", 3, 5)])
root.update()
got = w.get()
assert len(got) == 1 and got[0].location == "Route 1" and got[0].maxLevel == 5

w = AbilityListWidget(root, [Ability("overgrow", False, "..."), Ability("chlorophyll", True, "...")])
root.update()
assert [a.hidden for a in w.get()] == [False, True]

w = FormsListWidget(root, [Form(None, None, False)])
root.update()
w.tree.selection_set(w.tree.get_children())
w._remove()
root.update()
assert len(w.get()) == 1, "must never end up with zero forms"
print("OK: shared list-editing widgets round-trip correctly")

# ---------------------------------------------------------------------
# Part 3: games-catalog CRUD frame against a real repo.
# ---------------------------------------------------------------------
tmp_games = Path(tempfile.mkdtemp()) / "games.json"
catalog_repo = JsonFileGamesRepository(tmp_games)
catalog_repo.save(GameEntry(id="sword-shield", displayName="Sword / Shield", releaseOrder=17, generation=8))
frame = GamesCatalogFrame(root, catalog_repo)
root.update()
assert frame.tree.get_children() == ("sword-shield",)

catalog_repo.save(GameEntry(id="scarlet-violet", displayName="Scarlet / Violet", releaseOrder=18, generation=9))
frame.refresh()
root.update()
assert set(frame.tree.get_children()) == {"sword-shield", "scarlet-violet"}

frame.tree.selection_set(("sword-shield",))
frame._delete_selected()
root.update()
assert set(frame.tree.get_children()) == {"scarlet-violet"}
assert catalog_repo.get_by_id("sword-shield") is None
print("OK: GamesCatalogFrame add/refresh/delete against a real repo")

# ---------------------------------------------------------------------
# Part 4: modal dialogs (validate + apply, as clicking OK would trigger).
# ---------------------------------------------------------------------
dialog = GameEntryDialog(root, existing_ids=set())
dialog.id_var.set("sword-shield")
dialog.displayName_var.set("Sword / Shield")
dialog.releaseOrder_var.set("17")
dialog.generation_var.set("8")
dialog.releaseDate_var.set("2019-11-15")
dialog.region_var.set("Galar")
assert dialog.validate() is True
dialog.apply()
assert dialog.result_game.id == "sword-shield"
assert dialog.result_game.releaseOrder == 17

dialog2 = GameEntryDialog(root, existing_ids={"sword-shield"})
dialog2.id_var.set("sword-shield")
dialog2.displayName_var.set("Whatever")
assert dialog2.validate() is False
print("OK: GameEntryDialog validate+apply, rejects duplicate id")

game = GameEntry(id="sword-shield", displayName="Sword / Shield")
dialog3 = GameSpeciesDataDialog(root, game=game)
dialog3.dex_number_var.set("A068")
dialog3.location_type_var.set("structured")
dialog3._swap_location_editor()
dialog3.structured_widget.set([LocationEntry("Route 1", "Walk", 3, 5)])
dialog3.apply()
assert dialog3.result_data.dexNumber == "A068"
assert dialog3.result_data.locations.type == "structured"
assert dialog3.result_data.locations.entries[0].location == "Route 1"

existing = GameSpeciesData(
    dexNumber="P080",
    locations=Locations(type="freeText", source="bulbapedia", entries=["Coastal Biome"]),
    learnset=Learnset(levelUp=[LevelUpMove("tackle", 1)]),
)
dialog4 = GameSpeciesDataDialog(root, game=game, data=existing)
assert dialog4.location_type_var.get() == "freeText"
assert dialog4.freetext_widget.get() == ["Coastal Biome"]
dialog4.apply()
assert dialog4.result_data.locations.type == "freeText"
assert dialog4.result_data.learnset.levelUp[0].move == "tackle"
print("OK: GameSpeciesDataDialog structured + freeText locations")

sample = json.loads((REPO / "data" / "species" / "0001.json").read_text())
dialog5 = ImportJsonDialog(root)
dialog5.text.insert("1.0", json.dumps(sample))
assert dialog5.validate() is True
assert dialog5.result_dict["name"] == "Bulbasaur"

dialog6 = ImportJsonDialog(root)
dialog6.text.insert("1.0", "{not valid json")
assert dialog6.validate() is False
print("OK: ImportJsonDialog parses valid JSON, rejects invalid JSON")

root.destroy()
print("\nALL SMOKE TESTS PASSED")
