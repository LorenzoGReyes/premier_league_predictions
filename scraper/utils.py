import pandas as pd
import requests


base_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_understat(season: int) -> list:
    url = f"https://understat.com/getLeagueData/EPL/{season}"
    r = requests.get(
        url, 
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    full_data = r.json()
    if not full_data["teams"]:
        raise Exception("Season not available")

    return [
        pd.DataFrame(full_data["dates"]),
        pd.DataFrame(full_data["teams"]),
        pd.DataFrame(full_data["players"])
    ]


def scrape_understat_matches(matches) -> pd.DataFrame:
    
    df = pd.DataFrame()
    base = "https://understat.com/"
    headers = {"X-Requested-With": "XMLHttpRequest"}
    for match in matches:
        r = requests.get(f"{base}getMatchData/{match}", headers=headers)
        try:
            data = r.json()
        except:
            continue
        
        for x in ["h", "a"]:
            data_tmp = pd.DataFrame(data["rosters"][f"{x}"]).T.reset_index(drop=True)
            data_tmp.loc[:, "match_id"] = match
            df = pd.concat([df, data_tmp])
            del data_tmp
            
    return df



def scrape_tfmkt_values(player: int) -> pd.DataFrame:
    r = requests.get(
        f"https://tmapi-alpha.transfermarkt.technology/player/{player}/market-value-history",
        headers=base_headers
    )    
    data = r.json()
    try:
        data = data["data"]["history"]
    except:
        print(f"Invalid player {player}")
    
    df = pd.DataFrame([x["marketValue"] for x in data])
    df["clubId"] = pd.DataFrame([x["clubId"] for x in data])
    club_names = {}
    for club_id in set([x["clubId"] for x in data]):
        r = requests.get(f"https://tmapi-alpha.transfermarkt.technology/club/{club_id}",
        headers=base_headers
        )
        club_name = r.json()["data"]['name'] 
        club_names[club_id] = club_name
    df["clubName"] = df["clubId"].map(club_names)
    df["playerId"] = player
    player_name = 1
    r = requests.get(
        f"https://tmapi-alpha.transfermarkt.technology/player/{player}",
        headers=base_headers
    )
    player_name = r.json()["data"]['name']
    df["name"] = player_name
    return df.drop(["compact"], axis=1)
    
        


def add_matches_data(df: pd.DataFrame) -> pd.DataFrame:
    for t in ["h", "a"]:
        df.loc[:, f"{t}_id"] = df.loc[:, t].apply(lambda x: x["id"])
        df.loc[:, f"{t}_name"] = df.loc[:, t].apply(lambda x: x["title"])
        df.loc[:, f"{t}_goals"] = df.loc[:, "goals"].apply(lambda x: x[f"{t}"])
        df.loc[:, f"{t}_xG"] = df.loc[:, "xG"].apply(lambda x: x[f"{t}"])
    
    return df.drop(["h", "a", "goals", "xG"], axis=1)


def  add_teams_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.T.explode(["history"]).reset_index(drop=True)
    try:
        keys = df.loc[0, "history"].keys()
    except:
        print("Something wrong with the data")

    for key in keys:
        df.loc[:, f"{key}"] = df.loc[:, "history"].apply(lambda x: x[f"{key}"])

    return df


