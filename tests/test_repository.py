import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "app"))

from pokedex_editor.models import GameEntry, SpeciesRecord  # noqa: E402
from pokedex_editor.repository import (  # noqa: E402
    JsonFileGamesRepository,
    JsonFileSpeciesRepository,
)


class TestJsonFileSpeciesRepository(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = JsonFileSpeciesRepository(Path(self.tmp.name) / "species")

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_then_get_by_dex(self):
        species = SpeciesRecord(dex=1, keyword="bulbasaur", name="Bulbasaur", type1="Grass")
        self.repo.save(species)
        loaded = self.repo.get_by_dex(1)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.name, "Bulbasaur")

    def test_filename_is_zero_padded(self):
        species = SpeciesRecord(dex=7, keyword="squirtle", name="Squirtle", type1="Water")
        self.repo.save(species)
        self.assertTrue((Path(self.tmp.name) / "species" / "0007.json").exists())

    def test_get_all_sorted_by_dex(self):
        for dex, name in [(3, "Venusaur"), (1, "Bulbasaur"), (2, "Ivysaur")]:
            self.repo.save(SpeciesRecord(dex=dex, keyword=name.lower(), name=name, type1="Grass"))
        all_species = self.repo.get_all()
        self.assertEqual([s.dex for s in all_species], [1, 2, 3])

    def test_delete_removes_file(self):
        species = SpeciesRecord(dex=1, keyword="bulbasaur", name="Bulbasaur", type1="Grass")
        self.repo.save(species)
        self.repo.delete(1)
        self.assertIsNone(self.repo.get_by_dex(1))

    def test_get_by_dex_missing_returns_none(self):
        self.assertIsNone(self.repo.get_by_dex(999))


class TestJsonFileGamesRepository(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = JsonFileGamesRepository(Path(self.tmp.name) / "games.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_starts_empty(self):
        self.assertEqual(self.repo.get_all(), [])

    def test_save_new_then_update_existing(self):
        game = GameEntry(id="sword-shield", displayName="Sword / Shield", releaseOrder=17)
        self.repo.save(game)
        self.assertEqual(len(self.repo.get_all()), 1)

        game.displayName = "Sword and Shield"
        self.repo.save(game)
        all_games = self.repo.get_all()
        self.assertEqual(len(all_games), 1)
        self.assertEqual(all_games[0].displayName, "Sword and Shield")

    def test_get_all_sorted_by_release_order(self):
        self.repo.save(GameEntry(id="b", displayName="B", releaseOrder=2))
        self.repo.save(GameEntry(id="a", displayName="A", releaseOrder=1))
        self.assertEqual([g.id for g in self.repo.get_all()], ["a", "b"])

    def test_delete(self):
        self.repo.save(GameEntry(id="a", displayName="A", releaseOrder=1))
        self.repo.delete("a")
        self.assertEqual(self.repo.get_all(), [])


if __name__ == "__main__":
    unittest.main()
