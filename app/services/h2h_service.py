import httpx
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from app.core.config import BASE_URL

# fetch head-to-head matches from different seasons
async def fetch_h2h_matches(team1: str, team2: str):

    # seasons
    seasons = ["2023-2024", "2022-2023", "2021-2022"]
    matches = []

    async with httpx.AsyncClient() as client:
        for s in seasons:
            # 2 directions: home/away
            for variant in [f"{team1}_vs_{team2}", f"{team2}_vs_{team1}"]:
                url = f"{BASE_URL}/searchevents.php"
                params = {"e": variant, "s": s}
                response = await client.get(url, params=params)
                data = response.json().get("event") or []
                print(f"Querying {variant} for season {s} -> {len(data)} matches")
                if data:
                    matches.extend(data)

    return matches

# fetch a team's previous match
async def fetch_team_last_matches(team_name: str):
    async with httpx.AsyncClient() as client:
        # Get team id
        search_url = f"{BASE_URL}/searchteams.php"
        search_params = {"t": team_name}
        team_resp = await client.get(search_url, params=search_params)
        team_data = team_resp.json().get("teams", [])
        if not team_data:
            return []
        team_id = team_data[0]["idTeam"]

        # get last game
        last_matches_url = f"{BASE_URL}/eventslast.php"
        last_params = {"id": team_id}
        matches_resp = await client.get(last_matches_url, params=last_params)
        return matches_resp.json().get("results", [])


# Process data as Pandas DataFrame format
def process_matches(matches):

    # each row is a match
    rows = []

    for m in matches:
        try:
            home = m.get("strHomeTeam")
            away = m.get("strAwayTeam")
            hs = int(m.get("intHomeScore") or 0)
            as_ = int(m.get("intAwayScore") or 0)

            # Result
            if hs == as_:
                result = "Draw"
            elif hs > as_:
                result = "HomeWin"
            else:
                result = "AwayWin"

            rows.append({
                "home_team": home,
                "away_team": away,
                "home_goals_scored": hs,
                "away_goals_scored": as_,
                "home_advantage": 1,  # home advantage
                "result": result
            })
        except Exception:
            continue

    # Return the a Pandas DataFrame
    return pd.DataFrame(rows)


# Model train and save
def train_and_save_model(df, team1: str, team2: str):

    if len(df) < 3:
        # no model if not enough data
        return None

    # Input for train
    X = df[["home_goals_scored", "away_goals_scored", "home_advantage"]]
    # Output
    y = df["result"]

    # Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Save model
    model_dir = "app/models"
    os.makedirs(model_dir, exist_ok=True)
    #joblib.dump(model, os.path.join(model_dir, "h2h_model.pkl"))

    model_name = f"h2h_{team1.lower()}_{team2.lower()}.pkl"
    joblib.dump(model, os.path.join(model_dir, model_name))

    return model


# Prediction
def predict_next_match(model, df):
    sample = pd.DataFrame([{
        "home_goals_scored": df["home_goals_scored"].mean(),
        "away_goals_scored": df["away_goals_scored"].mean(),
        "home_advantage": 1
    }])
    return model.predict(sample)[0]

# Combine h2h and last game
async def prepare_and_train(team1, team2):
    # Fetch matches
    h2h = await fetch_h2h_matches(team1, team2)
    df_h2h = process_matches(h2h)

    last_team1 = await fetch_team_last_matches(team1)
    last_team2 = await fetch_team_last_matches(team2)

    df_last_team1 = process_matches(last_team1)
    df_last_team2 = process_matches(last_team2)

    df_all = pd.concat([df_h2h, df_last_team1, df_last_team2], ignore_index=True)

    print(f"H2H matches: {len(df_h2h)} | Team1 last: {len(last_team1)} | Team2 last: {len(last_team2)} | Total: {len(df_all)}")

    model = train_and_save_model(df_all, team1, team2)

    # --- statisztika számítás ---
    def count_results(df, team_name):
        wins = 0
        draws = 0
        losses = 0
        for _, row in df.iterrows():
            if row["home_team"] == team_name:
                if row["result"] == "HomeWin":
                    wins += 1
                elif row["result"] == "Draw":
                    draws += 1
                else:
                    losses += 1
            elif row["away_team"] == team_name:
                if row["result"] == "AwayWin":
                    wins += 1
                elif row["result"] == "Draw":
                    draws += 1
                else:
                    losses += 1
        return {"wins": wins, "draws": draws, "losses": losses}

    team1_stats = count_results(df_last_team1, team1)
    team2_stats = count_results(df_last_team2, team2)

    # --- Head-to-head statisztika ---
    h2h_team1_wins = len(df_h2h[
        ((df_h2h["home_team"] == team1) & (df_h2h["result"] == "HomeWin")) |
        ((df_h2h["away_team"] == team1) & (df_h2h["result"] == "AwayWin"))
    ])
    h2h_team2_wins = len(df_h2h[
        ((df_h2h["home_team"] == team2) & (df_h2h["result"] == "HomeWin")) |
        ((df_h2h["away_team"] == team2) & (df_h2h["result"] == "AwayWin"))
    ])
    h2h_draws = len(df_h2h[df_h2h["result"] == "Draw"])

    stats = {
        team1.lower(): team1_stats,
        team2.lower(): team2_stats,
        "h2h": {
            f"{team1.lower()}_wins": h2h_team1_wins,
            f"{team2.lower()}_wins": h2h_team2_wins,
            "draws": h2h_draws
        }
    }

    matches_used = {
        "h2h": len(df_h2h),
        "team1_last": len(df_last_team1),
        "team2_last": len(df_last_team2),
        "total": len(df_all)
    }

    # --- új rész: esélyszámítás százalékosan ---
    total_matches = max(matches_used["total"], 1)  # nullával osztás ellen

    # egyszerű valószínűség becslés
    home_chance = (h2h_team1_wins + team1_stats["wins"]) / total_matches
    away_chance = (h2h_team2_wins + team2_stats["wins"]) / total_matches
    draw_chance = (h2h_draws + team1_stats["draws"] + team2_stats["draws"]) / (total_matches * 1.5)

    # normalizálás 100%-ra
    total = home_chance + draw_chance + away_chance
    home_chance = round(home_chance / total * 100, 1)
    draw_chance = round(draw_chance / total * 100, 1)
    away_chance = round(away_chance / total * 100, 1)

    probabilities = {
        "home_win_percent": home_chance,
        "draw_percent": draw_chance,
        "away_win_percent": away_chance
    }

    # --- mindent visszaad ---
    return model, df_all, stats, matches_used, probabilities

