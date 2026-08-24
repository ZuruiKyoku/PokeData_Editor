import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from pokedex_editor.models import Evolution, SpeciesRecord  # noqa: E402
from pokedex_editor.validation import validate_species  # noqa: E402


def make_species(**overrides) -> SpeciesRecord:
    base = dict(dex=1, keyword="bulbasaur", name="Bulbasaur", type1="Grass")
    base.update(overrides)
    return SpeciesRecord(**base)


class TestValidateSpecies(unittest.TestCase):
    def test_valid_species_has_no_errors(self):
        species = make_species()
        errors = validate_species(species, valid_game_ids=set(), valid_dex_numbers={1})
        self.assertEqual(errors, [])

    def test_dex_must_be_positive(self):
        species = make_species(dex=0)
        errors = validate_species(species, valid_game_ids=set(), valid_dex_numbers=set())
        self.assertTrue(any("Dex number" in e for e in errors))

    def test_type1_required(self):
        species = make_species(type1="")
        errors = validate_species(species, valid_game_ids=set(), valid_dex_numbers={1})
        self.assertTrue(any("Type 1 is required" in e for e in errors))

    def test_unknown_type_rejected(self):
        species = make_species(type1="Chaos")
        errors = validate_species(species, valid_game_ids=set(), valid_dex_numbers={1})
        self.assertTrue(any("not a known type" in e for e in errors))

    def test_unknown_game_id_rejected(self):
        from pokedex_editor.models import GameSpeciesData
        species = make_species()
        species.games["not-a-real-game"] = GameSpeciesData()
        errors = validate_species(species, valid_game_ids={"sword-shield"}, valid_dex_numbers={1})
        self.assertTrue(any("not-a-real-game" in e for e in errors))

    def test_evolution_references_must_exist(self):
        species = make_species(evolution=Evolution(evolvesFromDex=None, evolvesIntoDex=[999]))
        errors = validate_species(species, valid_game_ids=set(), valid_dex_numbers={1})
        self.assertTrue(any("evolvesIntoDex #999" in e for e in errors))

    def test_valid_evolution_reference_passes(self):
        species = make_species(evolution=Evolution(evolvesFromDex=None, evolvesIntoDex=[2]))
        errors = validate_species(species, valid_game_ids=set(), valid_dex_numbers={1, 2})
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
