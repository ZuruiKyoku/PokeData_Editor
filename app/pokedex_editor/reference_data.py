"""Bundled reference lists used to populate dropdowns and drive validation.

These are the "small reference list bundled with the app" the build brief
calls for — kept as plain tuples so the editor form and the validator pull
from one shared source of truth.
"""

POKEMON_TYPES: tuple[str, ...] = (
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison",
    "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark",
    "Steel", "Fairy",
)

GROWTH_RATES: tuple[str, ...] = (
    "erratic", "fast", "medium", "medium-slow", "slow", "fluctuating",
)

COLORS: tuple[str, ...] = (
    "Black", "Blue", "Brown", "Gray", "Green", "Pink", "Purple", "Red",
    "White", "Yellow",
)

SHAPES: tuple[str, ...] = (
    "ball", "squiggle", "fish", "arms", "blob", "upright", "legs", "quadruped",
    "wings", "tentacles", "heads", "humanoid", "bug-wings", "armor",
)

HABITATS: tuple[str, ...] = (
    "cave", "forest", "grassland", "mountain", "rare", "rough-terrain",
    "sea", "urban", "waters-edge",
)

EGG_GROUPS: tuple[str, ...] = (
    "Monster", "Water 1", "Water 2", "Water 3", "Bug", "Flying", "Field",
    "Fairy", "Grass", "Human-Like", "Mineral", "Amorphous", "Dragon",
    "Undiscovered", "Ditto",
)

ENCOUNTER_DATA_SOURCES: tuple[str, ...] = ("pokeapi", "bulbapedia", "manual", "none")

LOCATION_TYPES: tuple[str, ...] = ("structured", "freeText")

# location.method values PokéAPI commonly returns; used to seed the method
# dropdown in the structured location editor. Free text is still allowed.
ENCOUNTER_METHODS: tuple[str, ...] = (
    "Walk", "Surf", "Old Rod", "Good Rod", "Super Rod", "Rock Smash",
    "Headbutt", "Gift", "Static Encounter",
)
