namespace PokeDataEditor.ViewModels;

/// <summary>Lightweight row for the species list - avoids keeping every full record (with its
/// nested games/learnset data) in memory just to render a scrollable list.</summary>
public class SpeciesListItem
{
    public int Dex { get; set; }
    public string Name { get; set; } = "";
    public string DexLabel => $"#{Dex:D4}";
    public string Display => $"{DexLabel}  {Name}";
}
