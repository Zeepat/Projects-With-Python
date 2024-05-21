from flask import Flask, render_template, request, jsonify
import requests
import os
import io

app = Flask(__name__)

# Function to get API key from file
def get_api_key():
    with open('/Users/asajad/Desktop/GithubForSchool/Projects-With-Python/League/api_key.txt', 'r') as file:
        return file.read().strip()

# Function to get PUUID
def get_puuid(game_name, name_tag):
    api_key = get_api_key()
    url_puuid = f'https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{name_tag}?api_key={api_key}'
    response_puuid = requests.get(url_puuid)
    response_puuid.raise_for_status()
    return response_puuid.json()['puuid']

# Function to get summoner info by PUUID
def get_summoner_info_by_puuid(puuid):
    api_key = get_api_key()
    url_summoner = f'https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={api_key}'
    response_summoner = requests.get(url_summoner)
    response_summoner.raise_for_status()
    summoner_info = response_summoner.json()
    
    summoner_id = summoner_info['id']
    profile_icon_id = summoner_info['profileIconId']
    summoner_level = summoner_info['summonerLevel']

    # Get rank information
    url_rank = f'https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={api_key}'
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

# Function to get match IDs
def get_matchids(puuid, amount_of_games=20):  # Show latest 20 games
    api_key = get_api_key()
    url_matches = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={amount_of_games}&api_key={api_key}'
    response_matches = requests.get(url_matches)
    response_matches.raise_for_status()
    return response_matches.json()

# Function to get match data
def get_match_data(match_id):
    api_key = get_api_key()
    url_match = f'https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={api_key}'
    response_match = requests.get(url_match)
    response_match.raise_for_status()
    return response_match.json()

# Fetch champion data from Data Dragon
def fetch_champion_data():
    url = "https://ddragon.leagueoflegends.com/cdn/12.14.1/data/en_US/champion.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    champions = data['data']
    return {champ: f"http://ddragon.leagueoflegends.com/cdn/12.14.1/img/champion/{champions[champ]['image']['full']}" for champ in champions}

# Fetch item data from Data Dragon
def fetch_item_data():
    url = "https://ddragon.leagueoflegends.com/cdn/12.14.1/data/en_US/item.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    items = data['data']
    return {item: f"http://ddragon.leagueoflegends.com/cdn/12.14.1/img/item/{items[item]['image']['full']}" for item in items}

# Fetch the champion and item data once and store it in dictionaries
CHAMPION_DATA = fetch_champion_data()
ITEM_DATA = fetch_item_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data', methods=['POST'])
def get_data():
    data = request.get_json()
    game_name = data['game_name']
    name_tag = data['name_tag']
    try:
        # Get PUUID
        puuid = get_puuid(game_name, name_tag)
        # Get summoner information
        summoner_info = get_summoner_info_by_puuid(puuid)
        # Get match data
        match_ids = get_matchids(puuid, amount_of_games=20)
        match_data = [get_match_data(match_id) for match_id in match_ids]
        filtered_data = filter_data(match_data, puuid)
        return jsonify({
            'summoner_info': summoner_info,
            'matches': filtered_data,
            'champion_data': CHAMPION_DATA,
            'item_data': ITEM_DATA
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

if __name__ == '__main__':
    app.run(debug=True)
