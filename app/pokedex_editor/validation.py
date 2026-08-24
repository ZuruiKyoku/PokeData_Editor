"""Pre-save validation for a species record.

Mirrors the "Validation before save" list in the build brief exactly:
dex required/positive, type1 required, enum fields restricted to the known
lists, games map keys must exist in the catalog, and evolution references
must point at real dex numbers when non-null.
"""
from __future__ import annotations

from .models import SpeciesRecord
from .reference_data import COLORS, GROWTH_RATES, POKEMON_TYPES, SHAPES


def validate_species(
    species: SpeciesRecord,
    valid_game_ids: set[str],
    valid_dex_numbers: set[int],
) -> list[str]:
    """Return a list of human-readable validation errors (empty = valid)."""
    errors: list[str] = []

    if species.dex is None or species.dex <= 0:
        errors.append("Dex number is required and must be positive.")

    if not species.type1:
        errors.append("Type 1 is required.")
    elif species.type1 not in POKEMON_TYPES:
        errors.append(f"Type 1 '{species.type1}' is not a known type.")

    if species.type2 is not None and species.type2 not in POKEMON_TYPES:
        errors.append(f"Type 2 '{species.type2}' is not a known type.")

    if species.breeding.growthRate and species.breeding.growthRate not in GROWTH_RATES:
        errors.append(f"Growth rate '{species.breeding.growthRate}' is not a known growth rate.")

    if species.classification.color and species.classification.color not in COLORS:
        errors.append(f"Color '{species.classification.color}' is not a known color.")

    if species.classification.shape and species.classification.shape not in SHAPES:
        errors.append(f"Shape '{species.classification.shape}' is not a known shape.")

    for game_id in species.games.keys():
        if game_id not in valid_game_ids:
            errors.append(f"Game '{game_id}' under this species is not in the games catalog.")

    # A species can legitimately be missing from valid_dex_numbers while it's
    # still being created (its own record hasn't been saved yet), so only
    # check the numbers it *references*, not its own dex.
    if species.evolution.evolvesFromDex is not None and species.evolution.evolvesFromDex not in valid_dex_numbers:
        errors.append(f"evolvesFromDex #{species.evolution.evolvesFromDex} does not match any known species.")

    for into_dex in species.evolution.evolvesIntoDex:
        if into_dex not in valid_dex_numbers:
            errors.append(f"evolvesIntoDex #{into_dex} does not match any known species.")

    return errors
