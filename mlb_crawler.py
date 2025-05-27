import pandas as pd
import requests

team_ids = {
    "Angels": 108, "Dbacks": 109, "Orioles": 110, "Red Sox": 111, "Cubs": 112,
    "Reds": 113, "Guardians": 114, "Rockies": 115, "Tigers": 116, "Astros": 117,
    "Royals": 118, "Dodgers": 119, "Nationals": 120, "Mets": 121, "Athletics": 133,
    "Pirates": 134, "Padres": 135, "Mariners": 136, "Giants": 137, "Cardinals": 138,
    "Rays": 139, "Rangers": 140, "Blue Jays": 141, "Twins": 142, "Phillies": 143,
    "Braves": 144, "White Sox": 145, "Marlins": 146, "Yankees": 147, "Brewers": 158,
}

def crawler(year):
    url = "https://bdfed.stitch.mlbinfra.com/bdfed/stats/player"
    datas = []
    for team_name, team_id in team_ids.items():
        params = {
            "env": "prod",
            "season": year,
            "sportId": "1",
            "stats": "season",
            "group": 'hitting',
            "gameType": "R",
            "limit": "500",
            "offset": "0",
            "sortStat": "homeRuns",
            "order": "desc",
            "teamId": team_id
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()
            players = data.get('stats', [])
            for player in players:
                player['team'] = team_name
                datas.append(player)
        except requests.RequestException as e:
            print(f"⚠️ 無法取得 {team_name} ({team_id}) 的資料: {e}")
            continue
    return pd.DataFrame(datas)

def Team_data(year):
    url = f"https://bdfed.stitch.mlbinfra.com/bdfed/stats/team?&env=prod&sportId=1&gameType=R&group=hitting&order=desc&sortStat=homeRuns&stats=season&season={year}&limit=30&offset=0"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json().get('stats', {})
        df = pd.DataFrame(data)
        df.to_csv(f"{year}_Team_stat.csv", index=False, encoding="utf-8-sig")
        return df
    except requests.RequestException as e:
        print(f"⚠️ 無法取得球隊數據: {e}")
        return pd.DataFrame([])