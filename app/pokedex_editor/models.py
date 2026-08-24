"""Data model for the species and games-catalog JSON schema.

Every dataclass field name matches the JSON key it serializes to, so
``to_dict``/``from_dict`` stay a straight mapping instead of a name
translation layer. Fields that the schema allows to be ``null`` default to
``None`` and are still emitted on save (the schema brief is explicit that
nothing should be omitted just because it's empty).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


def _from(cls, data: Optional[dict]) -> Optional[Any]:
    """Build a nested dataclass from a dict, passing None through untouched."""
    if data is None:
        return None
    return cls.from_dict(data)


@dataclass
class JapaneseName:
    kana: str = ""
    romaji: str = ""

    def to_dict(self) -> dict:
        return {"kana": self.kana, "romaji": self.romaji}

    @classmethod
    def from_dict(cls, d: dict) -> "JapaneseName":
        return cls(kana=d.get("kana", ""), romaji=d.get("romaji", ""))


@dataclass
class Stats:
    hp: int = 0
    attack: int = 0
    defense: int = 0
    specialAttack: int = 0
    specialDefense: int = 0
    speed: int = 0

    def to_dict(self) -> dict:
        return {
            "hp": self.hp, "attack": self.attack, "defense": self.defense,
            "specialAttack": self.specialAttack, "specialDefense": self.specialDefense,
            "speed": self.speed,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Stats":
        return cls(
            hp=d.get("hp", 0), attack=d.get("attack", 0), defense=d.get("defense", 0),
            specialAttack=d.get("specialAttack", 0), specialDefense=d.get("specialDefense", 0),
            speed=d.get("speed", 0),
        )


@dataclass
class Ability:
    name: str = ""
    hidden: bool = False
    effect: str = ""

    def to_dict(self) -> dict:
        return {"name": self.name, "hidden": self.hidden, "effect": self.effect}

    @classmethod
    def from_dict(cls, d: dict) -> "Ability":
        return cls(name=d.get("name", ""), hidden=bool(d.get("hidden", False)), effect=d.get("effect", ""))


@dataclass
class Breeding:
    eggGroups: list[str] = field(default_factory=list)
    genderRateEighthsFemale: int = -1
    hatchCycles: int = 0
    captureRate: int = 0
    baseFriendship: int = 0
    growthRate: str = ""

    def to_dict(self) -> dict:
        return {
            "eggGroups": list(self.eggGroups),
            "genderRateEighthsFemale": self.genderRateEighthsFemale,
            "hatchCycles": self.hatchCycles,
            "captureRate": self.captureRate,
            "baseFriendship": self.baseFriendship,
            "growthRate": self.growthRate,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Breeding":
        return cls(
            eggGroups=list(d.get("eggGroups", [])),
            genderRateEighthsFemale=d.get("genderRateEighthsFemale", -1),
            hatchCycles=d.get("hatchCycles", 0),
            captureRate=d.get("captureRate", 0),
            baseFriendship=d.get("baseFriendship", 0),
            growthRate=d.get("growthRate", ""),
        )


@dataclass
class Classification:
    color: str = ""
    shape: str = ""
    habitat: Optional[str] = None
    isLegendary: bool = False
    isMythical: bool = False
    isBaby: bool = False
    generationIntroduced: int = 1

    def to_dict(self) -> dict:
        return {
            "color": self.color, "shape": self.shape, "habitat": self.habitat,
            "isLegendary": self.isLegendary, "isMythical": self.isMythical, "isBaby": self.isBaby,
            "generationIntroduced": self.generationIntroduced,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Classification":
        return cls(
            color=d.get("color", ""), shape=d.get("shape", ""), habitat=d.get("habitat"),
            isLegendary=bool(d.get("isLegendary", False)), isMythical=bool(d.get("isMythical", False)),
            isBaby=bool(d.get("isBaby", False)), generationIntroduced=d.get("generationIntroduced", 1),
        )


@dataclass
class Evolution:
    evolvesFromDex: Optional[int] = None
    evolvesIntoDex: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"evolvesFromDex": self.evolvesFromDex, "evolvesIntoDex": list(self.evolvesIntoDex)}

    @classmethod
    def from_dict(cls, d: dict) -> "Evolution":
        return cls(evolvesFromDex=d.get("evolvesFromDex"), evolvesIntoDex=list(d.get("evolvesIntoDex", [])))


@dataclass
class Sprites:
    regular: str = ""
    shiny: str = ""

    def to_dict(self) -> dict:
        return {"regular": self.regular, "shiny": self.shiny}

    @classmethod
    def from_dict(cls, d: dict) -> "Sprites":
        return cls(regular=d.get("regular", ""), shiny=d.get("shiny", ""))


@dataclass
class Cries:
    latest: str = ""
    legacy: str = ""

    def to_dict(self) -> dict:
        return {"latest": self.latest, "legacy": self.legacy}

    @classmethod
    def from_dict(cls, d: dict) -> "Cries":
        return cls(latest=d.get("latest", ""), legacy=d.get("legacy", ""))


@dataclass
class Form:
    formCode: Optional[str] = None
    formName: Optional[str] = None
    isFemale: bool = False

    def to_dict(self) -> dict:
        return {"formCode": self.formCode, "formName": self.formName, "isFemale": self.isFemale}

    @classmethod
    def from_dict(cls, d: dict) -> "Form":
        return cls(formCode=d.get("formCode"), formName=d.get("formName"), isFemale=bool(d.get("isFemale", False)))


@dataclass
class LocationEntry:
    """One row of a *structured* location table."""
    location: str = ""
    method: str = ""
    minLevel: int = 1
    maxLevel: int = 1

    def to_dict(self) -> dict:
        return {"location": self.location, "method": self.method, "minLevel": self.minLevel, "maxLevel": self.maxLevel}

    @classmethod
    def from_dict(cls, d: dict) -> "LocationEntry":
        return cls(
            location=d.get("location", ""), method=d.get("method", ""),
            minLevel=d.get("minLevel", 1), maxLevel=d.get("maxLevel", 1),
        )


@dataclass
class Locations:
    type: str = "structured"  # "structured" | "freeText"
    source: str = ""
    entries: list = field(default_factory=list)  # list[LocationEntry] if structured, list[str] if freeText

    def to_dict(self) -> dict:
        if self.type == "freeText":
            entries = list(self.entries)
        else:
            entries = [e.to_dict() if isinstance(e, LocationEntry) else e for e in self.entries]
        return {"type": self.type, "source": self.source, "entries": entries}

    @classmethod
    def from_dict(cls, d: dict) -> "Locations":
        loc_type = d.get("type", "structured")
        raw_entries = d.get("entries", [])
        if loc_type == "freeText":
            entries = list(raw_entries)
        else:
            entries = [LocationEntry.from_dict(e) for e in raw_entries]
        return cls(type=loc_type, source=d.get("source", ""), entries=entries)


@dataclass
class LevelUpMove:
    move: str = ""
    level: int = 1

    def to_dict(self) -> dict:
        return {"move": self.move, "level": self.level}

    @classmethod
    def from_dict(cls, d: dict) -> "LevelUpMove":
        return cls(move=d.get("move", ""), level=d.get("level", 1))


@dataclass
class Learnset:
    levelUp: list[LevelUpMove] = field(default_factory=list)
    machine: list[str] = field(default_factory=list)
    egg: list[str] = field(default_factory=list)
    tutor: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "levelUp": [m.to_dict() for m in self.levelUp],
            "machine": list(self.machine),
            "egg": list(self.egg),
            "tutor": list(self.tutor),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Learnset":
        return cls(
            levelUp=[LevelUpMove.from_dict(m) for m in d.get("levelUp", [])],
            machine=list(d.get("machine", [])),
            egg=list(d.get("egg", [])),
            tutor=list(d.get("tutor", [])),
        )


@dataclass
class GameSpeciesData:
    """The per-game payload nested under ``species.games[<gameId>]``."""
    dexNumber: str = ""
    locations: Locations = field(default_factory=Locations)
    learnset: Learnset = field(default_factory=Learnset)

    def to_dict(self) -> dict:
        return {
            "dexNumber": self.dexNumber,
            "locations": self.locations.to_dict(),
            "learnset": self.learnset.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GameSpeciesData":
        return cls(
            dexNumber=d.get("dexNumber", ""),
            locations=Locations.from_dict(d.get("locations", {})),
            learnset=Learnset.from_dict(d.get("learnset", {})),
        )


@dataclass
class MetaInfo:
    sources: list[str] = field(default_factory=list)
    lastUpdated: str = ""

    def to_dict(self) -> dict:
        return {"sources": list(self.sources), "lastUpdated": self.lastUpdated}

    @classmethod
    def from_dict(cls, d: dict) -> "MetaInfo":
        return cls(sources=list(d.get("sources", [])), lastUpdated=d.get("lastUpdated", ""))


@dataclass
class SpeciesRecord:
    dex: int = 0
    keyword: str = ""
    name: str = ""
    japaneseName: Optional[JapaneseName] = None
    type1: str = ""
    type2: Optional[str] = None
    genus: str = ""
    heightM: float = 0.0
    weightKg: float = 0.0
    flavorText: str = ""
    flavorTextSourceGame: str = ""
    stats: Stats = field(default_factory=Stats)
    abilities: list[Ability] = field(default_factory=list)
    breeding: Breeding = field(default_factory=Breeding)
    classification: Classification = field(default_factory=Classification)
    genderDifference: Optional[str] = None
    evolution: Evolution = field(default_factory=Evolution)
    sprites: Sprites = field(default_factory=Sprites)
    cries: Optional[Cries] = None
    forms: list[Form] = field(default_factory=lambda: [Form()])
    games: dict[str, GameSpeciesData] = field(default_factory=dict)
    meta: MetaInfo = field(default_factory=MetaInfo)

    def to_dict(self) -> dict:
        return {
            "dex": self.dex,
            "keyword": self.keyword,
            "name": self.name,
            "japaneseName": self.japaneseName.to_dict() if self.japaneseName else None,
            "type1": self.type1,
            "type2": self.type2,
            "genus": self.genus,
            "heightM": self.heightM,
            "weightKg": self.weightKg,
            "flavorText": self.flavorText,
            "flavorTextSourceGame": self.flavorTextSourceGame,
            "stats": self.stats.to_dict(),
            "abilities": [a.to_dict() for a in self.abilities],
            "breeding": self.breeding.to_dict(),
            "classification": self.classification.to_dict(),
            "genderDifference": self.genderDifference,
            "evolution": self.evolution.to_dict(),
            "sprites": self.sprites.to_dict(),
            "cries": self.cries.to_dict() if self.cries else None,
            "forms": [f.to_dict() for f in self.forms],
            "games": {gid: gdata.to_dict() for gid, gdata in self.games.items()},
            "meta": self.meta.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SpeciesRecord":
        return cls(
            dex=d.get("dex", 0),
            keyword=d.get("keyword", ""),
            name=d.get("name", ""),
            japaneseName=_from(JapaneseName, d.get("japaneseName")),
            type1=d.get("type1", ""),
            type2=d.get("type2"),
            genus=d.get("genus", ""),
            heightM=d.get("heightM", 0.0),
            weightKg=d.get("weightKg", 0.0),
            flavorText=d.get("flavorText", ""),
            flavorTextSourceGame=d.get("flavorTextSourceGame", ""),
            stats=Stats.from_dict(d.get("stats", {})),
            abilities=[Ability.from_dict(a) for a in d.get("abilities", [])],
            breeding=Breeding.from_dict(d.get("breeding", {})),
            classification=Classification.from_dict(d.get("classification", {})),
            genderDifference=d.get("genderDifference"),
            evolution=Evolution.from_dict(d.get("evolution", {})),
            sprites=Sprites.from_dict(d.get("sprites", {})),
            cries=_from(Cries, d.get("cries")),
            forms=[Form.from_dict(f) for f in d.get("forms", [])] or [Form()],
            games={gid: GameSpeciesData.from_dict(gdata) for gid, gdata in d.get("games", {}).items()},
            meta=MetaInfo.from_dict(d.get("meta", {})),
        )


@dataclass
class GameEntry:
    """One row of the games catalog (``data/games.json``)."""
    id: str = ""
    displayName: str = ""
    releaseOrder: int = 0
    generation: int = 1
    releaseDate: str = ""
    region: str = ""
    encounterDataSource: str = "manual"  # "pokeapi" | "bulbapedia" | "manual" | "none"
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id, "displayName": self.displayName, "releaseOrder": self.releaseOrder,
            "generation": self.generation, "releaseDate": self.releaseDate, "region": self.region,
            "encounterDataSource": self.encounterDataSource, "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GameEntry":
        return cls(
            id=d.get("id", ""), displayName=d.get("displayName", ""), releaseOrder=d.get("releaseOrder", 0),
            generation=d.get("generation", 1), releaseDate=d.get("releaseDate", ""), region=d.get("region", ""),
            encounterDataSource=d.get("encounterDataSource", "manual"), notes=d.get("notes", ""),
        )
