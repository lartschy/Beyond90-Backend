import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os


def process_matches(matches):
    rows = []
    for m in matches:
        try:
            home = m.get("strHomeTeam")
            away = m.get("strAwayTeam")
            hs = int(m.get("intHomeScore") or 0)
            as_ = int(m.get("intAwayScore") or 0)
            if hs == as_:
                result = "Draw"
            elif hs > as_:
                result = "HomeWin"
            else:
                result = "AwayWin"

            rows.append({
                "home_goals_scored": hs,
                "away_goals_scored": as_,
                "home_advantage": 1,
                "result": result
            })
        except Exception:
            continue

    return pd.DataFrame(rows)


def process_matches(matches):
    rows = []
    for m in matches:
        try:
            home = m.get("strHomeTeam")
            away = m.get("strAwayTeam")
            hs = int(m.get("intHomeScore") or 0)
            as_ = int(m.get("intAwayScore") or 0)
            if hs == as_:
                result = "Draw"
            elif hs > as_:
                result = "HomeWin"
            else:
                result = "AwayWin"

            rows.append({
                "home_goals_scored": hs,
                "away_goals_scored": as_,
                "home_advantage": 1,
                "result": result
            })
        except Exception:
            continue

    return pd.DataFrame(rows)


def train_and_save_model(df):
    if len(df) < 3:
        print("⚠️ Túl kevés adat a tanításhoz.")
        return None

    X = df[["home_goals_scored", "away_goals_scored", "home_advantage"]]
    y = df["result"]

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, "app/models/h2h_model.pkl")
    print("✅ Modell betanítva és elmentve.")
    return model


# Example data
data = pd.DataFrame({
    "home_goals_scored": [2, 1, 3, 0, 2],
    "home_goals_conceded": [0, 2, 1, 1, 3],
    "away_goals_scored": [1, 0, 2, 3, 1],
    "away_goals_conceded": [2, 1, 3, 0, 2],
    "possession": [58, 52, 63, 47, 55],
    "shots": [11, 8, 14, 6, 10],
    "home_advantage": [1, 1, 0, 0, 1],
    "result": ["Win", "Draw", "Win", "Lose", "Draw"]
})

# -Input (X) és goal (y)
X = data[[
    "home_goals_scored",
    "home_goals_conceded",
    "away_goals_scored",
    "away_goals_conceded",
    "shots",
    "possession",
    "home_advantage"
]]
y = data["result"]

# create model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# save model
model_dir = "app/models"
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, "match_model.pkl")

joblib.dump(model, model_path)
print(f"Model set and saved: {model_path}")

# datas
event = data["event"][0]  # first match

sample = pd.DataFrame([{
    "home_goals_scored": int(event.get("intHomeScore", 0)),
    "home_goals_conceded": int(event.get("intAwayScore", 0)),
    "away_goals_scored": int(event.get("intAwayScore", 0)),
    "away_goals_conceded": int(event.get("intHomeScore", 0)),
    "shots": int(event.get("intHomeShots", 10)),  # if no data then 1
    "possession": int(event.get("intHomePossession", 50)),  # if no data then 50%
    "home_advantage": 1
}])


prediction = model.predict(sample)[0]
probabilities = model.predict_proba(sample)[0]

print(f"Predicition: {prediction}")
print("Probabilities:")
for cls, prob in zip(model.classes_, probabilities):
    print(f"  {cls}: {prob:.2f}")
