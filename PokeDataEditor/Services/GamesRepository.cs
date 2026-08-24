using System.IO;
using System.Text.Json;
using PokeDataEditor.Models;

namespace PokeDataEditor.Services;

/// <summary>CRUD over <c>data/games.json</c> - the whole games catalog in one file, since it's
/// small (one row per mainline title) and every species' edit form needs the full list at
/// once anyway.</summary>
public class GamesRepository
{
    private readonly string _path;

    public GamesRepository(string path)
    {
        _path = path;
        var dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
    }

    public List<GameCatalogEntry> GetAll()
    {
        if (!File.Exists(_path)) return new List<GameCatalogEntry>();
        var json = File.ReadAllText(_path);
        var entries = JsonSerializer.Deserialize<List<GameCatalogEntry>>(json, JsonOptions.Default)
                      ?? new List<GameCatalogEntry>();
        return entries.OrderBy(g => g.ReleaseOrder).ToList();
    }

    public void SaveAll(IEnumerable<GameCatalogEntry> games)
    {
        var ordered = games.OrderBy(g => g.ReleaseOrder).ToList();
        var json = JsonSerializer.Serialize(ordered, JsonOptions.Default);
        File.WriteAllText(_path, json);
    }
}
