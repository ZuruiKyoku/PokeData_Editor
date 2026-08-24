import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from pokedex_editor.models import SpeciesRecord, GameEntry  # noqa: E402

FIXTURE_DIR = Path(__file__).resolve().parent.parent / "data"


class TestSpeciesRoundTrip(unittest.TestCase):
    def test_round_trip_preserves_shape(self):
        with (FIXTURE_DIR / "species" / "0001.json").open() as f:
            raw = json.load(f)
        species = SpeciesRecord.from_dict(raw)
        round_tripped = species.to_dict()
        self.assertEqual(raw, round_tripped)

    def test_null_fields_stay_present_not_omitted(self):
        species = SpeciesRecord(dex=999, keyword="test", name="Test", type1="Normal")
        d = species.to_dict()
        # These must be present-as-null, never dropped from the dict.
        for key in ("japaneseName", "type2", "genderDifference", "cries"):
            self.assertIn(key, d)
            self.assertIsNone(d[key])

    def test_new_species_has_default_single_form(self):
        species = SpeciesRecord(dex=1, keyword="x", name="X", type1="Normal")
        self.assertEqual(len(species.forms), 1)

    def test_games_map_round_trips(self):
        with (FIXTURE_DIR / "species" / "0001.json").open() as f:
            raw = json.load(f)
        species = SpeciesRecord.from_dict(raw)
        self.assertIn("sword-shield", species.games)
        self.assertEqual(species.games["sword-shield"].locations.type, "structured")
        self.assertEqual(species.games["scarlet-violet"].locations.type, "freeText")
        self.assertEqual(species.games["scarlet-violet"].locations.entries, ["Coastal Biome, Torchlit Labyrinth"])


class TestGameEntryRoundTrip(unittest.TestCase):
    def test_round_trip(self):
        with (FIXTURE_DIR / "games.json").open() as f:
            raw = json.load(f)
        entries = [GameEntry.from_dict(g) for g in raw]
        round_tripped = [g.to_dict() for g in entries]
        self.assertEqual(raw, round_tripped)


if __name__ == "__main__":
    unittest.main()
