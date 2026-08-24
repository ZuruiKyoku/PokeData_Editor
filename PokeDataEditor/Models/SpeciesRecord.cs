using System.Collections.ObjectModel;
using System.Text.Json.Serialization;

namespace PokeDataEditor.Models;

/// <summary>
/// One species' full reference record - everything on a Pokedex page, shared between this
/// editor and the PokeTracker Android app (which reads the same JSON shape). Per-game data
/// (dex number, sprite, this game's own dex-entry text, locations, learnset) lives under
/// <see cref="Games"/>, keyed by a game id from the games catalog. National Dex display uses
/// <see cref="HomeSprites"/> and no particular game's flavor text takes priority over another -
/// the app picks whichever is most relevant when nothing more specific is selected.
/// </summary>
public class SpeciesRecord
{
    public int Dex { get; set; }
    public string Keyword { get; set; } = "";
    public string Name { get; set; } = "";
    public JapaneseName? JapaneseName { get; set; }
    public string Type1 { get; set; } = "";
    public string? Type2 { get; set; }
    public string? Genus { get; set; }
    public double HeightM { get; set; }
    public double WeightKg { get; set; }

    public StatBlock? Stats { get; set; }
    public ObservableCollection<AbilityRef> Abilities { get; set; } = new();
    public BreedingInfo Breeding { get; set; } = new();
    public Classification Classification { get; set; } = new();
    public string? GenderDifference { get; set; }
    public EvolutionInfo Evolution { get; set; } = new();
    public SpriteSet HomeSprites { get; set; } = new();
    public Cries? Cries { get; set; }
    public ObservableCollection<FormVariant> Forms { get; set; } = new();

    /// <summary>Per-game data, keyed by a game id (e.g. "kanto", "swsh") from the games catalog.</summary>
    public Dictionary<string, GameSpeciesData> Games { get; set; } = new();

    public RecordMeta Meta { get; set; } = new();
}

public class JapaneseName
{
    public string Kana { get; set; } = "";
    public string Romaji { get; set; } = "";
}

public class StatBlock
{
    public int Hp { get; set; }
    public int Attack { get; set; }
    public int Defense { get; set; }
    public int SpecialAttack { get; set; }
    public int SpecialDefense { get; set; }
    public int Speed { get; set; }

    [JsonIgnore]
    public int Total => Hp + Attack + Defense + SpecialAttack + SpecialDefense + Speed;
}

public class AbilityRef
{
    public string Name { get; set; } = "";
    public bool Hidden { get; set; }
    public string? Effect { get; set; }
}

public class BreedingInfo
{
    public ObservableCollection<string> EggGroups { get; set; } = new();
    /// <summary>Eighths female, out of 8 - -1 means genderless.</summary>
    public int? GenderRateEighthsFemale { get; set; }
    public int? HatchCycles { get; set; }
    public int? CaptureRate { get; set; }
    public int? BaseFriendship { get; set; }
    public string? GrowthRate { get; set; }
}

public class Classification
{
    public string? Color { get; set; }
    public string? Shape { get; set; }
    public string? Habitat { get; set; }
    public bool IsLegendary { get; set; }
    public bool IsMythical { get; set; }
    public bool IsBaby { get; set; }
    public int? GenerationIntroduced { get; set; }
}

public class EvolutionInfo
{
    public int? EvolvesFromDex { get; set; }
    public ObservableCollection<int> EvolvesIntoDex { get; set; } = new();
}

public class SpriteSet
{
    public string? Regular { get; set; }
    public string? Shiny { get; set; }
}

public class Cries
{
    public string? Latest { get; set; }
    public string? Legacy { get; set; }
}

public class FormVariant
{
    public string? FormCode { get; set; }
    public string? FormName { get; set; }
    public bool IsFemale { get; set; }
}

/// <summary>Everything about one species that's specific to one game - its own dex number,
/// its own period-accurate sprite (falling back to the Home render when a game never had
/// traditional 2D sprites), its own dex-entry text, where to find it, and its learnset there.</summary>
public class GameSpeciesData
{
    public string? DexNumber { get; set; }
    public string? FlavorText { get; set; }
    public SpriteSet Sprites { get; set; } = new();
    public LocationInfo Locations { get; set; } = new();
    public LearnsetInfo Learnset { get; set; } = new();
}

public class LocationInfo
{
    /// <summary>"structured" (route/method/level rows, from PokeAPI) or "freeText" (a plain
    /// description, from Bulbapedia - current-gen games PokeAPI has no encounter table for).</summary>
    public string Type { get; set; } = "structured";
    public string? Source { get; set; }
    public ObservableCollection<LocationEntry> StructuredEntries { get; set; } = new();
    public ObservableCollection<string> FreeTextEntries { get; set; } = new();
}

public class LocationEntry
{
    public string Location { get; set; } = "";
    public string Method { get; set; } = "";
    public int MinLevel { get; set; }
    public int MaxLevel { get; set; }
}

public class LearnsetInfo
{
    public ObservableCollection<LevelUpMove> LevelUp { get; set; } = new();
    public ObservableCollection<string> Machine { get; set; } = new();
    public ObservableCollection<string> Egg { get; set; } = new();
    public ObservableCollection<string> Tutor { get; set; } = new();
}

public class LevelUpMove
{
    public string Move { get; set; } = "";
    public int? Level { get; set; }
}

public class RecordMeta
{
    public ObservableCollection<string> Sources { get; set; } = new();
    public string LastUpdated { get; set; } = "";
}

/// <summary>One entry in the games catalog - the full list of titles a species' <c>Games</c>
/// map can reference. Adding a new game to the app means adding one entry here.</summary>
public class GameCatalogEntry
{
    public string Id { get; set; } = "";
    public string DisplayName { get; set; } = "";
    public int ReleaseOrder { get; set; }
    public int Generation { get; set; }
    public string? ReleaseDate { get; set; }
    public string? Region { get; set; }
    /// <summary>"pokeapi" (has full location-area encounter tables) or "bulbapedia" (free-text
    /// locations only - PokeAPI never got wild-encounter data for this title).</summary>
    public string EncounterDataSource { get; set; } = "pokeapi";
    public string? Notes { get; set; }
}
