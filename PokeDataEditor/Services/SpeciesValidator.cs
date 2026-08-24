using PokeDataEditor.Models;

namespace PokeDataEditor.Services;

/// <summary>The known-good values for a handful of fields, so a typo shows up immediately as
/// a validation error instead of silently corrupting the record. Not exhaustive by design -
/// free-text fields (location names, flavor text, move names) stay free-text.</summary>
public static class PokemonTypes
{
    public static readonly string[] All =
    {
        "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting", "Poison", "Ground",
        "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon", "Dark", "Steel", "Fairy",
    };
}

public class ValidationResult
{
    public List<string> Errors { get; } = new();
    public bool IsValid => Errors.Count == 0;
}

public static class SpeciesValidator
{
    public static ValidationResult Validate(SpeciesRecord species, IReadOnlyCollection<int> knownDexNumbers, IReadOnlyCollection<string> knownGameIds)
    {
        var result = new ValidationResult();

        if (species.Dex <= 0)
            result.Errors.Add("Dex number must be positive.");

        if (string.IsNullOrWhiteSpace(species.Name))
            result.Errors.Add("Name is required.");

        if (string.IsNullOrWhiteSpace(species.Type1))
            result.Errors.Add("Type 1 is required.");
        else if (!PokemonTypes.All.Contains(species.Type1))
            result.Errors.Add($"\"{species.Type1}\" isn't a known type.");

        if (species.Type2 != null && !PokemonTypes.All.Contains(species.Type2))
            result.Errors.Add($"\"{species.Type2}\" isn't a known type.");

        if (species.Evolution.EvolvesFromDex is int fromDex && !knownDexNumbers.Contains(fromDex))
            result.Errors.Add($"Evolves-from dex #{fromDex} doesn't match any species on file.");

        foreach (var intoDex in species.Evolution.EvolvesIntoDex)
        {
            if (!knownDexNumbers.Contains(intoDex))
                result.Errors.Add($"Evolves-into dex #{intoDex} doesn't match any species on file.");
        }

        foreach (var gameId in species.Games.Keys)
        {
            if (!knownGameIds.Contains(gameId))
                result.Errors.Add($"\"{gameId}\" isn't a game in the catalog.");
        }

        return result;
    }
}
