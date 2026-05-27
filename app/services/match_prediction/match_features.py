import pandas as pd


class MatchFeatureBuilder:

    def build_base_dataframe(self, matches):
        rows = []

        for m in matches:
            try:
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

            except:
                continue

        return pd.DataFrame(rows)

    # feature engineering külön
    def build_features(self, df: pd.DataFrame):
        home_avg = df["home_goals_scored"].mean()
        away_avg = df["away_goals_scored"].mean()

        features = pd.DataFrame({
            "home_avg_scored": [home_avg] * len(df),
            "away_avg_scored": [away_avg] * len(df),
            "goal_ratio": df["home_goals_scored"] / (df["away_goals_scored"] + 1),
            "home_advantage": df["home_advantage"]
        })

        return features, df["result"]

    # prediction input külön
    def build_prediction_sample(self, df: pd.DataFrame):
        home_avg = df["home_goals_scored"].mean()
        away_avg = df["away_goals_scored"].mean()

        return pd.DataFrame([{
            "home_avg_scored": home_avg,
            "away_avg_scored": away_avg,
            "goal_ratio": home_avg / (away_avg + 1),
            "home_advantage": 1
        }])