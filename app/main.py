#!/usr/bin/env python3
"""Entry point for the Pokédex Data Editor.

Run with:  python3 main.py [--data-dir PATH]
Defaults to the ../data directory shipped alongside this app.
"""
from __future__ import annotations

import argparse
import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pokedex_editor.repository import JsonFileGamesRepository, JsonFileSpeciesRepository  # noqa: E402
from pokedex_editor.ui.app import App  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Pokédex Data Editor")
    default_data_dir = Path(__file__).resolve().parent.parent / "data"
    parser.add_argument("--data-dir", type=Path, default=default_data_dir, help="Directory containing species/ and games.json")
    args = parser.parse_args()

    species_repo = JsonFileSpeciesRepository(args.data_dir / "species")
    games_repo = JsonFileGamesRepository(args.data_dir / "games.json")

    root = tk.Tk()
    root.title("Pokédex Data Editor")
    root.geometry("900x650")
    App(root, species_repo, games_repo)
    root.mainloop()


if __name__ == "__main__":
    main()
