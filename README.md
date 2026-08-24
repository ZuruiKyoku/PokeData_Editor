# PokeData Editor

A .NET 8 WPF app for CRUD-editing the Pokédex reference data that ships with
PokeTracker. Drop a new game in, fill out its per-species data, done.

## Running it

```
dotnet run --project PokeDataEditor
```

Requires the .NET 8 SDK. The app finds its `data/` folder by walking up from
wherever it's running, so `dotnet run` and a published build both resolve
the same place.

## Data layout

- `data/games.json` - the games catalog (id, display name, release order,
  generation, region, whether PokeAPI has structured encounter data for it).
  Add a new game here first; it then shows up in the per-species "add a
  game" picker.
- `data/species/NNNN.json` - one file per National Dex number. Identity,
  stats, abilities, breeding, classification, and evolution are species-wide.
  Everything that varies by game - dex number, sprite, that game's own dex
  entry, where to find it, and its learnset there - lives under `games`,
  keyed by a game id from the catalog. National Dex views use `homeSprites`
  instead of any one game's sprite.

`Models/SpeciesRecord.cs` is the canonical shape - PokeTracker's Android app
reads the same JSON.

## Where the seed data came from

Identity/stats/abilities/breeding/classification/evolution and Home sprites
came from PokeTracker's own bundled dex assets (spreadsheet + PokeAPI).
Per-game dex numbers, encounters, and learnsets came from PokeAPI's GraphQL
API; current-gen titles PokeAPI has no encounter tables for (BDSP, PLA, SV,
PLZA) got free-text location data from Bulbapedia instead. Per-game sprites
and flavor text were fetched from PokeAPI, filtered to each species' actual
debut generation or later (PokeAPI's per-version sprite endpoint otherwise
returns placeholder URLs for games that predate a species).

This was a bulk migration - expect gaps and the occasional wrong value.
That's what this app is for.
