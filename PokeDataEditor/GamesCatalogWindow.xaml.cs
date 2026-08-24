using System.Collections.ObjectModel;
using System.Windows;
using PokeDataEditor.Models;

namespace PokeDataEditor;

public partial class GamesCatalogWindow : Window
{
    private readonly ObservableCollection<GameCatalogEntry> _games;

    public List<GameCatalogEntry> Result { get; private set; } = new();

    public GamesCatalogWindow(List<GameCatalogEntry> games)
    {
        InitializeComponent();
        _games = new ObservableCollection<GameCatalogEntry>(games);
        GamesGrid.ItemsSource = _games;
    }

    private void AddGame_Click(object sender, RoutedEventArgs e)
    {
        var nextOrder = _games.Select(g => g.ReleaseOrder).DefaultIfEmpty(0).Max() + 1;
        _games.Add(new GameCatalogEntry
        {
            Id = "new-game",
            DisplayName = "New Game",
            ReleaseOrder = nextOrder,
            Generation = 1,
            EncounterDataSource = "pokeapi",
        });
    }

    private void RemoveGame_Click(object sender, RoutedEventArgs e)
    {
        if (GamesGrid.SelectedItem is GameCatalogEntry entry)
            _games.Remove(entry);
    }

    private void Save_Click(object sender, RoutedEventArgs e)
    {
        Result = _games.ToList();
        DialogResult = true;
    }

    private void Cancel_Click(object sender, RoutedEventArgs e)
    {
        DialogResult = false;
    }
}
