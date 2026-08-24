using System.Collections.ObjectModel;
using System.IO;
using System.Windows;
using PokeDataEditor.Models;
using PokeDataEditor.Services;

namespace PokeDataEditor.ViewModels;

public class MainViewModel : ObservableObject
{
    private readonly SpeciesRepository _speciesRepo;
    private readonly GamesRepository _gamesRepo;

    public ObservableCollection<SpeciesListItem> SpeciesList { get; } = new();
    public ObservableCollection<GameCatalogEntry> Games { get; } = new();

    private List<SpeciesListItem> _allSpecies = new();

    private SpeciesRecord? _currentSpecies;
    public SpeciesRecord? CurrentSpecies
    {
        get => _currentSpecies;
        set
        {
            if (SetField(ref _currentSpecies, value))
            {
                SelectedGame = null;
                OnPropertyChanged(nameof(HasSelection));
                OnPropertyChanged(nameof(AvailableGamesToAdd));
                OnPropertyChanged(nameof(AssignedGames));
            }
        }
    }

    public bool HasSelection => CurrentSpecies != null;

    private GameCatalogEntry? _selectedGame;
    public GameCatalogEntry? SelectedGame
    {
        get => _selectedGame;
        set
        {
            if (SetField(ref _selectedGame, value))
                OnPropertyChanged(nameof(SelectedGameData));
        }
    }

    /// <summary>The current species' data for whichever game is selected in the Games tab -
    /// created on first touch if this species has nothing for that game yet, so there's no
    /// separate "add this game" step before you can start typing.</summary>
    public GameSpeciesData? SelectedGameData
    {
        get
        {
            if (CurrentSpecies == null || SelectedGame == null) return null;
            if (!CurrentSpecies.Games.TryGetValue(SelectedGame.Id, out var data))
            {
                data = new GameSpeciesData();
                CurrentSpecies.Games[SelectedGame.Id] = data;
                OnPropertyChanged(nameof(AssignedGames));
                OnPropertyChanged(nameof(AvailableGamesToAdd));
            }
            return data;
        }
    }

    /// <summary>Games this species doesn't have an entry for yet - offered in "add a game" pickers.</summary>
    public IEnumerable<GameCatalogEntry> AvailableGamesToAdd =>
        CurrentSpecies == null ? Enumerable.Empty<GameCatalogEntry>() : Games.Where(g => !CurrentSpecies.Games.ContainsKey(g.Id));

    /// <summary>Games this species currently has data for, in release order.</summary>
    public IEnumerable<GameCatalogEntry> AssignedGames =>
        CurrentSpecies == null ? Enumerable.Empty<GameCatalogEntry>() : Games.Where(g => CurrentSpecies.Games.ContainsKey(g.Id));

    private string _searchText = "";
    public string SearchText
    {
        get => _searchText;
        set
        {
            if (SetField(ref _searchText, value))
                ApplyFilter();
        }
    }

    private string _statusMessage = "";
    public string StatusMessage
    {
        get => _statusMessage;
        set => SetField(ref _statusMessage, value);
    }

    public RelayCommand SaveCommand { get; }
    public RelayCommand NewSpeciesCommand { get; }
    public RelayCommand DeleteSpeciesCommand { get; }
    public RelayCommand RemoveSelectedGameCommand { get; }

    public MainViewModel(string dataFolder)
    {
        _speciesRepo = new SpeciesRepository(Path.Combine(dataFolder, "species"));
        _gamesRepo = new GamesRepository(Path.Combine(dataFolder, "games.json"));

        SaveCommand = new RelayCommand(Save, _ => CurrentSpecies != null);
        NewSpeciesCommand = new RelayCommand(NewSpecies);
        DeleteSpeciesCommand = new RelayCommand(DeleteSpecies, _ => CurrentSpecies != null);
        RemoveSelectedGameCommand = new RelayCommand(RemoveSelectedGame, _ => CurrentSpecies != null && SelectedGame != null);

        Reload();
    }

    public void Reload()
    {
        Games.Clear();
        foreach (var g in _gamesRepo.GetAll()) Games.Add(g);

        _allSpecies = _speciesRepo.GetAll()
            .Select(s => new SpeciesListItem { Dex = s.Dex, Name = s.Name })
            .ToList();
        ApplyFilter();
    }

    private void ApplyFilter()
    {
        SpeciesList.Clear();
        var query = SearchText.Trim();
        IEnumerable<SpeciesListItem> items = _allSpecies;
        if (query.Length > 0)
        {
            items = items.Where(s =>
                s.Name.Contains(query, StringComparison.OrdinalIgnoreCase) ||
                s.Dex.ToString().Contains(query));
        }
        foreach (var item in items) SpeciesList.Add(item);
    }

    public void SelectByDex(int dex)
    {
        CurrentSpecies = _speciesRepo.GetByDex(dex);
    }

    private void Save(object? _)
    {
        if (CurrentSpecies == null) return;

        var knownDex = _allSpecies.Select(s => s.Dex).ToHashSet();
        knownDex.Add(CurrentSpecies.Dex);
        var knownGameIds = Games.Select(g => g.Id).ToHashSet();

        var result = SpeciesValidator.Validate(CurrentSpecies, knownDex, knownGameIds);
        if (!result.IsValid)
        {
            MessageBox.Show(string.Join("\n", result.Errors), "Can't save yet",
                MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        CurrentSpecies.Meta.LastUpdated = DateTime.Now.ToString("yyyy-MM-dd");
        _speciesRepo.Save(CurrentSpecies);
        Reload();
        StatusMessage = $"Saved #{CurrentSpecies.Dex:D4} {CurrentSpecies.Name}.";
    }

    private void NewSpecies(object? _)
    {
        var dex = _speciesRepo.NextDex();
        CurrentSpecies = new SpeciesRecord
        {
            Dex = dex,
            Name = "",
            Keyword = "",
            Type1 = PokemonTypes.All[0],
            Meta = new RecordMeta { LastUpdated = DateTime.Now.ToString("yyyy-MM-dd") },
        };
        StatusMessage = $"New species drafted at #{dex:D4} - fill it in and Save.";
    }

    private void DeleteSpecies(object? _)
    {
        if (CurrentSpecies == null) return;
        var confirm = MessageBox.Show(
            $"Delete #{CurrentSpecies.Dex:D4} {CurrentSpecies.Name}? This can't be undone.",
            "Delete species", MessageBoxButton.YesNo, MessageBoxImage.Warning);
        if (confirm != MessageBoxResult.Yes) return;

        _speciesRepo.Delete(CurrentSpecies.Dex);
        CurrentSpecies = null;
        Reload();
    }

    private void RemoveSelectedGame(object? _)
    {
        if (CurrentSpecies == null || SelectedGame == null) return;
        CurrentSpecies.Games.Remove(SelectedGame.Id);
        var removedId = SelectedGame.Id;
        SelectedGame = null;
        OnPropertyChanged(nameof(AssignedGames));
        OnPropertyChanged(nameof(AvailableGamesToAdd));
    }

    public void SaveGamesCatalog(IEnumerable<GameCatalogEntry> games)
    {
        _gamesRepo.SaveAll(games);
        Reload();
    }
}
