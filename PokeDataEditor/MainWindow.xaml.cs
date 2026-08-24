using System.IO;
using System.Windows;
using System.Windows.Controls;
using PokeDataEditor.Models;
using PokeDataEditor.ViewModels;

namespace PokeDataEditor;

public partial class MainWindow : Window
{
    private readonly MainViewModel _vm;

    public MainWindow()
    {
        InitializeComponent();

        // data/ sits next to the solution, not next to the built exe - resolve relative to
        // the project so "dotnet run" and a published build both find the same folder.
        var dataFolder = FindDataFolder();
        _vm = new MainViewModel(dataFolder);
        DataContext = _vm;
    }

    private static string FindDataFolder()
    {
        var dir = new DirectoryInfo(AppContext.BaseDirectory);
        while (dir != null && !Directory.Exists(Path.Combine(dir.FullName, "data")))
            dir = dir.Parent;
        return dir != null ? Path.Combine(dir.FullName, "data") : Path.Combine(AppContext.BaseDirectory, "data");
    }

    private void SpeciesListBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (SpeciesListBox.SelectedItem is SpeciesListItem item)
            _vm.SelectByDex(item.Dex);
    }

    private void ManageGames_Click(object sender, RoutedEventArgs e)
    {
        var window = new GamesCatalogWindow(_vm.Games.ToList()) { Owner = this };
        if (window.ShowDialog() == true)
            _vm.SaveGamesCatalog(window.Result);
    }

    private void AddGame_Click(object sender, RoutedEventArgs e)
    {
        if (AddGameCombo.SelectedItem is GameCatalogEntry entry && _vm.CurrentSpecies != null)
        {
            if (!_vm.CurrentSpecies.Games.ContainsKey(entry.Id))
                _vm.CurrentSpecies.Games[entry.Id] = new GameSpeciesData();
            _vm.SelectedGame = entry;
            RefreshGameLists();
        }
    }

    private void AssignedGamesListBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (AssignedGamesListBox.SelectedItem is GameCatalogEntry entry)
            _vm.SelectedGame = entry;
    }

    private void RefreshGameLists()
    {
        // AvailableGamesToAdd/AssignedGames are computed properties - force a re-read by
        // re-raising CurrentSpecies changed, which is simpler than duplicating that logic here.
        var current = _vm.CurrentSpecies;
        _vm.CurrentSpecies = null;
        _vm.CurrentSpecies = current;
    }

    private void AddAbility_Click(object sender, RoutedEventArgs e)
    {
        _vm.CurrentSpecies?.Abilities.Add(new AbilityRef { Name = "", Hidden = false });
    }

    private void RemoveAbility_Click(object sender, RoutedEventArgs e)
    {
        var abilities = _vm.CurrentSpecies?.Abilities;
        if (abilities is { Count: > 0 }) abilities.RemoveAt(abilities.Count - 1);
    }

    private void AddLocationEntry_Click(object sender, RoutedEventArgs e)
    {
        _vm.SelectedGameData?.Locations?.StructuredEntries.Add(new LocationEntry());
    }

    private void RemoveLocationEntry_Click(object sender, RoutedEventArgs e)
    {
        var entries = _vm.SelectedGameData?.Locations?.StructuredEntries;
        if (entries is { Count: > 0 }) entries.RemoveAt(entries.Count - 1);
    }
}
