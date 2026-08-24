using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Encodings.Web;
using System.Text.Unicode;

namespace PokeDataEditor.Services;

/// <summary>Shared serializer settings so every read/write of a species or games-catalog file
/// agrees on the exact same JSON shape - camelCase field names (matching the Kotlin app's own
/// convention), full Unicode passed through unescaped (Japanese names, accented text), and
/// indentation so the files stay readable/diffable in git.</summary>
public static class JsonOptions
{
    public static readonly JsonSerializerOptions Default = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        WriteIndented = true,
        Encoder = JavaScriptEncoder.Create(UnicodeRanges.All),
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        ReadCommentHandling = JsonCommentHandling.Skip,
    };
}
