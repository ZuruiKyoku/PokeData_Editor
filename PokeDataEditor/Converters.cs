using System.Collections.ObjectModel;
using System.Globalization;
using System.Windows;
using System.Windows.Data;
using PokeDataEditor.Models;

namespace PokeDataEditor;

/// <summary>Edits an ObservableCollection&lt;string&gt; as one comma-separated TextBox instead
/// of needing a dedicated add/remove row UI for every simple string list in the schema
/// (egg groups, TM lists, free-text locations, etc.) - the "simple to edit" goal mattered more
/// here than a fully itemized list editor for every single field.</summary>
public class StringListConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is IEnumerable<string> list) return string.Join(", ", list);
        return "";
    }

    public object ConvertBack(object value, Type targetType, object? parameter, CultureInfo culture)
    {
        var text = value as string ?? "";
        var items = text.Split(',')
            .Select(s => s.Trim())
            .Where(s => s.Length > 0);
        return new ObservableCollection<string>(items);
    }
}

public class IntListConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is IEnumerable<int> list) return string.Join(", ", list);
        return "";
    }

    public object ConvertBack(object value, Type targetType, object? parameter, CultureInfo culture)
    {
        var text = value as string ?? "";
        var items = text.Split(',')
            .Select(s => s.Trim())
            .Where(s => s.Length > 0)
            .Select(s => int.TryParse(s, out var n) ? n : (int?)null)
            .Where(n => n.HasValue)
            .Select(n => n!.Value);
        return new ObservableCollection<int>(items);
    }
}

/// <summary>Level-up moves as "move:level" pairs, comma-separated - e.g. "tackle:1, growl:1,
/// vine-whip:15". A move with no level (shouldn't normally happen for this method, but kept
/// forgiving) is written as just the move name.</summary>
public class LevelUpListConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
    {
        if (value is IEnumerable<LevelUpMove> list)
        {
            return string.Join(", ", list.Select(m => m.Level.HasValue ? $"{m.Move}:{m.Level}" : m.Move));
        }
        return "";
    }

    public object ConvertBack(object value, Type targetType, object? parameter, CultureInfo culture)
    {
        var text = value as string ?? "";
        var moves = new ObservableCollection<LevelUpMove>();
        foreach (var raw in text.Split(','))
        {
            var part = raw.Trim();
            if (part.Length == 0) continue;
            var pieces = part.Split(':');
            var move = pieces[0].Trim();
            int? level = pieces.Length > 1 && int.TryParse(pieces[1].Trim(), out var lvl) ? lvl : null;
            moves.Add(new LevelUpMove { Move = move, Level = level });
        }
        return moves;
    }
}

/// <summary>Hides a placeholder TextBlock once a game has actually been picked (i.e. the bound
/// object is non-null).</summary>
public class NullToVisibilityConverter : IValueConverter
{
    public object Convert(object? value, Type targetType, object? parameter, CultureInfo culture) =>
        value == null ? Visibility.Visible : Visibility.Collapsed;

    public object ConvertBack(object value, Type targetType, object? parameter, CultureInfo culture) =>
        throw new NotSupportedException();
}
