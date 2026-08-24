# Pokédex Data Editor

A standalone desktop CRUD editor for the reference dataset behind PokeTracker's
specimen record page — dex numbers, stats, locations, learnsets, etc. This is
**reference data only**; it holds no user "caught" progress, which stays local
to the Android app.

## Why Python + Tkinter, not the WPF recommendation

The build brief's primary recommendation was C# WPF (.NET 8). This session's
sandbox has no network path to the .NET installer and no Windows host to build
or run a WPF app against, so anything written there would have been unverified
guesswork. The brief explicitly names **"Python + a desktop GUI toolkit"** as
an acceptable alternative when speed-to-build and verifiability matter more
than native polish — that's the path taken here. Every screen described in the
brief was built and exercised end-to-end under a headless X server
(`tests/smoke_test_app.py`), so what's in this repo is known to actually run,
not just compile.

If a native Windows build is wanted later, the storage/validation core
(`pokedex_editor/models.py`, `repository.py`, `validation.py`) has zero UI
dependencies and zero third-party packages — it's a straight port target.

## Running it

Requires Python 3.10+ with Tkinter (`python3 -m tkinter` should open a test
window; if it errors, install your OS's Tk package — e.g. `python3-tk` on
Debian/Ubuntu). No third-party dependencies.

```sh
cd app
python3 main.py                       # uses ../data by default
python3 main.py --data-dir /path/to/data
```

## Layout

```
app/
  main.py                     entry point
  pokedex_editor/
    models.py                 dataclasses mirroring the JSON schema 1:1
    repository.py             ISpeciesRepository / IGamesRepository + the
                               JSON-file implementations (data/species/*.json,
                               data/games.json)
    validation.py              pre-save validation rules
    reference_data.py          bundled enum lists (types, growth rates, ...)
    ui/
      app.py                   top-level window: Species tab + Games Catalog tab
      species_list.py          feature 1 — searchable/sortable species table
      species_edit.py          feature 2 — tabbed edit form, import/export,
                                validation-before-save (features 5, 6)
      game_editor.py           feature 3 — per-game sub-panel + edit dialog
      games_catalog.py         feature 4 — full CRUD on the games catalog
      widgets.py                shared tag-input / table-editing widgets
data/
  species/0001.json            one seeded example (Bulbasaur)
  games.json                   two seeded example games (Sword/Shield, Scarlet/Violet)
tests/
  test_models.py, test_repository.py, test_validation.py
                                unit tests (`python3 -m unittest discover -s tests`)
  smoke_test_app.py             headless end-to-end UI test (see below)
```

## Data model

One JSON file per species under `data/species/####.json` (zero-padded
National Dex number), plus one games catalog at `data/games.json`. Every
field in the schema is always present in a saved file — `null` rather than
omitted — so the app's parser never has to guess. See
`pokedex_editor/models.py` for the exact shape, or open
`data/species/0001.json` for a filled-in example.

Adding a new game to the whole system is: add one entry to the Games Catalog
screen, then it shows up as an option on every species' Games tab.

## Repository interface (forward design)

All storage goes through `ISpeciesRepository` / `IGamesRepository`
(`get_all` / `get_by_dex` (or `get_by_id`) / `save` / `delete`). The only
implementation shipped is `JsonFileSpeciesRepository` /
`JsonFileGamesRepository`. If a Firestore-backed implementation gets built
later for multi-device sync, it drops in behind the same interface and
nothing in `ui/` needs to change.

## Tests

```sh
python3 -m unittest discover -s tests -v      # model/repository/validation unit tests
xvfb-run -a python3 tests/smoke_test_app.py   # headless UI smoke test (needs Xvfb)
```

The smoke test drives the real widget tree: boots the app, filters the
species list, opens the seeded species into the edit form, round-trips every
tab, edits and saves it back to disk, confirms an invalid save (dex 0) is
rejected by validation instead of silently succeeding, and exercises the
games-catalog and per-game-data CRUD dialogs.
