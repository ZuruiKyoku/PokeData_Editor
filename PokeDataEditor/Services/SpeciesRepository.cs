using System.IO;
using System.Text.Json;
using PokeDataEditor.Models;

namespace PokeDataEditor.Services;

/// <summary>CRUD over <c>data/species/NNNN.json</c> - one file per National Dex number, so
/// edits diff cleanly and the editor never has to rewrite a multi-megabyte single file for a
/// one-species change.</summary>
public class SpeciesRepository
{
    private readonly string _folder;

    public SpeciesRepository(string folder)
    {
        _folder = folder;
        Directory.CreateDirectory(_folder);
    }

    private string PathFor(int dex) => Path.Combine(_folder, $"{dex:D4}.json");

    public List<SpeciesRecord> GetAll()
    {
        var results = new List<SpeciesRecord>();
        foreach (var file in Directory.EnumerateFiles(_folder, "*.json").OrderBy(f => f))
        {
            var json = File.ReadAllText(file);
            var record = JsonSerializer.Deserialize<SpeciesRecord>(json, JsonOptions.Default);
            if (record != null) results.Add(record);
        }
        return results.OrderBy(r => r.Dex).ToList();
    }

    public SpeciesRecord? GetByDex(int dex)
    {
        var path = PathFor(dex);
        if (!File.Exists(path)) return null;
        var json = File.ReadAllText(path);
        return JsonSerializer.Deserialize<SpeciesRecord>(json, JsonOptions.Default);
    }

    public void Save(SpeciesRecord record)
    {
        var json = JsonSerializer.Serialize(record, JsonOptions.Default);
        File.WriteAllText(PathFor(record.Dex), json);
    }

    public void Delete(int dex)
    {
        var path = PathFor(dex);
        if (File.Exists(path)) File.Delete(path);
    }

    /// <summary>The next unused dex number after the highest one currently on disk - the
    /// sensible default when adding a brand-new species.</summary>
    public int NextDex() => GetAll().Select(r => r.Dex).DefaultIfEmpty(0).Max() + 1;
}
