import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import os
import io

def get_api_key():
    """
    Retrieve the Riot API key from environment variables.

    Returns:
    str: API key.
    """
    with open('/Users/asajad/Desktop/GithubForSchool/Projects-With-Python/api_key.txt', 'r') as file:
        api_key = file.read().replace('\n', '')
    if not api_key:
        raise ValueError("API key not found. Please set the RIOT_API_KEY environment variable.")
    return api_key

def get_puuid(game_name, name_tag):
    api_key = get_api_key()
    url_puuid = f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{name_tag}?api_key={api_key}'
    print(f"URL for PUUID: {url_puuid}")  # Debugging print statement
    response_puuid = requests.get(url_puuid)
    response_puuid.raise_for_status()
    return response_puuid.json()['puuid']

def get_summoner_info_by_puuid(puuid):
    api_key = get_api_key()
    url_summoner = f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}'
    print(f"URL for summoner info: {url_summoner}")  # Debugging print statement
    response_summoner = requests.get(url_summoner)
    response_summoner.raise_for_status()
    summoner_info = response_summoner.json()
    
    summoner_id = summoner_info['id']
    profile_icon_id = summoner_info['profileIconId']
    summoner_level = summoner_info['summonerLevel']

    # Get rank information
    url_rank = f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}'
    print(f"URL for rank info: {url_rank}")  # Debugging print statement
    response_rank = requests.get(url_rank)
    response_rank.raise_for_status()
    rank_info = response_rank.json()

    rank_solo = "Unranked"
    rank_flex = "Unranked"
    for entry in rank_info:
        if entry['queueType'] == 'RANKED_SOLO_5x5':
            rank_solo = f"{entry['tier']} {entry['rank']}"
        elif entry['queueType'] == 'RANKED_FLEX_SR':
            rank_flex = f"{entry['tier']} {entry['rank']}"

    return {
        'profile_icon_id': profile_icon_id,
        'summoner_level': summoner_level,
        'rank_solo': rank_solo,
        'rank_flex': rank_flex
    }

def get_matchids(puuid, amount_of_games=10):
    api_key = get_api_key()
    url_matches = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={amount_of_games}&api_key={api_key}'
    print(f"URL for match IDs: {url_matches}")  # Debugging print statement
    response_matches = requests.get(url_matches)
    response_matches.raise_for_status()
    return response_matches.json()

def get_match_data(match_id):
    api_key = get_api_key()
    url_match = f'https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
    print(f"URL for match data: {url_match}")  # Debugging print statement
    response_match = requests.get(url_match)
    response_match.raise_for_status()
    return response_match.json()

def fetch_champion_data():
    url = "https://ddragon.leagueoflegends.com/cdn/12.14.1/data/en_US/champion.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    champions = data['data']
    return {champ: f"http://ddragon.leagueoflegends.com/cdn/12.14.1/img/champion/{champions[champ]['image']['full']}" for champ in champions}

CHAMPION_DATA = fetch_champion_data()

def fetch_image(url):
    response = requests.get(url)
    response.raise_for_status()
    image_data = response.content
    image = Image.open(io.BytesIO(image_data))
    return ImageTk.PhotoImage(image)

def filter_data(data, my_puuid):
    filtered_data = []
    for match in data:
        if 'info' not in match or 'participants' not in match['info']:
            continue

        participants = match['info']['participants']
        for participant in participants:
            if participant['puuid'] == my_puuid:
                my_team_id = participant['teamId']
                break

        team1 = [p for p in participants if p['teamId'] == 100]
        team2 = [p for p in participants if p['teamId'] == 200]

        filtered_data.append({
            'championName': participant['championName'],
            'kills': participant['kills'],
            'deaths': participant['deaths'],
            'assists': participant['assists'],
            'totalMinionsKilled': participant['totalMinionsKilled'],
            'neutralMinionsKilled': participant['neutralMinionsKilled'],
            'items': [participant[f'item{i}'] for i in range(6)],
            'team1': [p['championName'] for p in team1],
            'team2': [p['championName'] for p in team2]
        })

    return filtered_data

class LeagueStatsApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("League of Legends Stats")
        self.geometry("1200x800")

        self.create_widgets()

    def create_widgets(self):
        # Left Frame - Player Profile
        self.frame_left = tk.Frame(self, width=200, height=800)
        self.frame_left.grid(row=0, column=0, sticky="ns")
        self.frame_left.grid_propagate(False)

        self.lbl_game_name = tk.Label(self.frame_left, text="Game Name:")
        self.lbl_game_name.pack(pady=5)
        self.entry_game_name = tk.Entry(self.frame_left)
        self.entry_game_name.pack(pady=5)

        self.lbl_name_tag = tk.Label(self.frame_left, text="Name Tag:")
        self.lbl_name_tag.pack(pady=5)
        self.entry_name_tag = tk.Entry(self.frame_left)
        self.entry_name_tag.pack(pady=5)

        self.btn_get_data = tk.Button(self.frame_left, text="Get Data", command=self.get_data)
        self.btn_get_data.pack(pady=10)

        self.lbl_profile_icon = tk.Label(self.frame_left)
        self.lbl_profile_icon.pack(pady=5)
        self.lbl_player_name = tk.Label(self.frame_left, text="")
        self.lbl_player_name.pack(pady=5)
        self.lbl_rank_solo = tk.Label(self.frame_left, text="Solo/Duo Rank: ")
        self.lbl_rank_solo.pack(pady=5)
        self.lbl_rank_flex = tk.Label(self.frame_left, text="Flex Rank: ")
        self.lbl_rank_flex.pack(pady=5)

        # Middle Frame - Match History
        self.frame_middle = tk.Frame(self, width=800, height=800)
        self.frame_middle.grid(row=0, column=1, sticky="ns")
        self.frame_middle.grid_propagate(False)

        self.tree_matches = ttk.Treeview(self.frame_middle, columns=("Champion", "K/D/A", "CS", "Items", "Teams"), show='headings')
        self.tree_matches.heading("Champion", text="Champion")
        self.tree_matches.heading("K/D/A", text="K/D/A")
        self.tree_matches.heading("CS", text="CS")
        self.tree_matches.heading("Items", text="Items")
        self.tree_matches.heading("Teams", text="Teams")
        self.tree_matches.column("Champion", width=50)
        self.tree_matches.column("K/D/A", width=50)
        self.tree_matches.column("CS", width=50)
        self.tree_matches.column("Items", width=200)
        self.tree_matches.column("Teams", width=300)
        self.tree_matches.pack(fill="both", expand=True)

        # Right Frame - Top Champions
        self.frame_right = tk.Frame(self, width=200, height=800)
        self.frame_right.grid(row=0, column=2, sticky="ns")
        self.frame_right.grid_propagate(False)

        self.tree_top_champions = ttk.Treeview(self.frame_right, columns=("Champion", "Games", "Winrate", "K/D/A"), show='headings')
        self.tree_top_champions.heading("Champion", text="Champion")
        self.tree_top_champions.heading("Games", text="Games")
        self.tree_top_champions.heading("Winrate", text="Winrate")
        self.tree_top_champions.heading("K/D/A", text="K/D/A")
        self.tree_top_champions.pack(fill="both", expand=True)

    def get_data(self):
        game_name = self.entry_game_name.get()
        name_tag = self.entry_name_tag.get()

        try:
            # Get PUUID
            puuid = get_puuid(game_name, name_tag)
            print(f"PUUID: {puuid}")  # Debugging print statement

            # Get summoner information
            summoner_info = get_summoner_info_by_puuid(puuid)
            self.lbl_player_name.config(text=f"{game_name}#{name_tag}")
            self.lbl_rank_solo.config(text=f"Solo/Duo Rank: {summoner_info['rank_solo']}")
            self.lbl_rank_flex.config(text=f"Flex Rank: {summoner_info['rank_flex']}")

            # Fetch and display player icon (assuming you have a method to fetch and display the icon)
            icon_url = f"http://ddragon.leagueoflegends.com/cdn/12.14.1/img/profileicon/{summoner_info['profile_icon_id']}.png"
            icon_response = requests.get(icon_url)
            icon_image = tk.PhotoImage(data=icon_response.content)
            self.lbl_profile_icon.config(image=icon_image)
            self.lbl_profile_icon.image = icon_image

            # Get match data
            match_ids = get_matchids(puuid, amount_of_games=10)

            match_data = []
            for match_id in match_ids:
                match = get_match_data(match_id)
                if match:
                    match_data.append(match)

            filtered_data = filter_data(match_data, puuid)
            self.display_match_history(filtered_data)
            self.display_top_champions(filtered_data)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_match_history(self, data):
        for item in self.tree_matches.get_children():
            self.tree_matches.delete(item)

        for match in data:
            champion_icon = fetch_image(CHAMPION_DATA[match['championName']])
            kda = f"{match['kills']}/{match['deaths']}/{match['assists']}"
            cs = match['totalMinionsKilled'] + match['neutralMinionsKilled']
            items = ", ".join([str(i) for i in match['items']])  # Simplified item representation

            team1_icons = [fetch_image(CHAMPION_DATA[champ]) for champ in match['team1']]
            team2_icons = [fetch_image(CHAMPION_DATA[champ]) for champ in match['team2']]

            self.tree_matches.insert("", "end", values=("", kda, cs, items, ""))

            last_item = self.tree_matches.get_children()[-1]
            self.tree_matches.item(last_item, image=champion_icon)

            for idx, icon in enumerate(team1_icons):
                self.tree_matches.insert("", "end", values=(""), image=icon)
            for idx, icon in enumerate(team2_icons):
                self.tree_matches.insert("", "end", values=(""), image=icon)

    def display_top_champions(self, data):
        for item in self.tree_top_champions.get_children():
            self.tree_top_champions.delete(item)

        # Calculate top 5 champions
        champion_stats = {}
        for match in data:
            champion = match['championName']
            if champion not in champion_stats:
                champion_stats[champion] = {'games': 0, 'wins': 0, 'kills': 0, 'deaths': 0, 'assists': 0}
            champion_stats[champion]['games'] += 1
            champion_stats[champion]['kills'] += match['kills']
            champion_stats[champion]['deaths'] += match['deaths']
            champion_stats[champion]['assists'] += match['assists']
            if match['win']:
                champion_stats[champion]['wins'] += 1

        top_champions = sorted(champion_stats.items(), key=lambda x: x[1]['games'], reverse=True)[:5]
        for champ, stats in top_champions:
            games = stats['games']
            winrate = f"{stats['wins'] / games:.2%}"
            kda = f"{stats['kills'] / games:.1f}/{stats['deaths'] / games:.1f}/{stats['assists'] / games:.1f}"
            self.tree_top_champions.insert("", "end", values=(champ, games, winrate, kda))

if __name__ == "__main__":
    app = LeagueStatsApp()
    app.mainloop()
