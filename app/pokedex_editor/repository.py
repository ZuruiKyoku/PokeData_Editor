"""Storage layer.

Both repository interfaces are plain ABCs so a future non-JSON backend (the
build brief specifically calls out a Firestore-backed implementation for
multi-device sync) can be dropped in without touching the UI or validation
code — those only ever talk to ``ISpeciesRepository``/``IGamesRepository``.

``JsonFileSpeciesRepository`` is the only implementation shipped here: one
file per species under ``data/species/####.json``. ``JsonFileGamesRepository``
stores the games catalog as a single JSON array at ``data/games.json``.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from .models import GameEntry, SpeciesRecord

SPECIES_FILENAME_WIDTH = 4


class ISpeciesRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[SpeciesRecord]:
        ...

    @abstractmethod
    def get_by_dex(self, dex: int) -> Optional[SpeciesRecord]:
        ...

    @abstractmethod
    def save(self, species: SpeciesRecord) -> None:
        ...

    @abstractmethod
    def delete(self, dex: int) -> None:
        ...


class IGamesRepository(ABC):
    @abstractmethod
    def get_all(self) -> list[GameEntry]:
        ...

    @abstractmethod
    def get_by_id(self, game_id: str) -> Optional[GameEntry]:
        ...

    @abstractmethod
    def save(self, game: GameEntry) -> None:
        ...

    @abstractmethod
    def delete(self, game_id: str) -> None:
        ...


def _species_filename(dex: int) -> str:
    return f"{dex:0{SPECIES_FILENAME_WIDTH}d}.json"


class JsonFileSpeciesRepository(ISpeciesRepository):
    def __init__(self, species_dir: Path | str):
        self.species_dir = Path(species_dir)
        self.species_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, dex: int) -> Path:
        return self.species_dir / _species_filename(dex)

    def get_all(self) -> list[SpeciesRecord]:
        records = []
        for path in sorted(self.species_dir.glob("*.json")):
            with path.open("r", encoding="utf-8") as f:
                records.append(SpeciesRecord.from_dict(json.load(f)))
        records.sort(key=lambda s: s.dex)
        return records

    def get_by_dex(self, dex: int) -> Optional[SpeciesRecord]:
        path = self._path_for(dex)
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            return SpeciesRecord.from_dict(json.load(f))

    def save(self, species: SpeciesRecord) -> None:
        path = self._path_for(species.dex)
        with path.open("w", encoding="utf-8") as f:
            json.dump(species.to_dict(), f, indent=2, ensure_ascii=False)
            f.write("\n")

    def delete(self, dex: int) -> None:
        path = self._path_for(dex)
        if path.exists():
            path.unlink()


class JsonFileGamesRepository(IGamesRepository):
    def __init__(self, games_file: Path | str):
        self.games_file = Path(games_file)
        if not self.games_file.exists():
            self.games_file.parent.mkdir(parents=True, exist_ok=True)
            self.games_file.write_text("[]\n", encoding="utf-8")

    def _read_all(self) -> list[GameEntry]:
        with self.games_file.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        return [GameEntry.from_dict(g) for g in raw]

    def _write_all(self, games: list[GameEntry]) -> None:
        with self.games_file.open("w", encoding="utf-8") as f:
            json.dump([g.to_dict() for g in games], f, indent=2, ensure_ascii=False)
            f.write("\n")

    def get_all(self) -> list[GameEntry]:
        return sorted(self._read_all(), key=lambda g: g.releaseOrder)

    def get_by_id(self, game_id: str) -> Optional[GameEntry]:
        for g in self._read_all():
            if g.id == game_id:
                return g
        return None

    def save(self, game: GameEntry) -> None:
        games = self._read_all()
        for i, g in enumerate(games):
            if g.id == game.id:
                games[i] = game
                break
        else:
            games.append(game)
        self._write_all(games)

    def delete(self, game_id: str) -> None:
        games = [g for g in self._read_all() if g.id != game_id]
        self._write_all(games)
