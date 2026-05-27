import pandas as pd
from .match_fetcher import MatchFetcher
from .match_features import MatchFeatureBuilder
from .match_model import MatchPredictor


class MatchService:

    def __init__(self):
        self.fetcher = MatchFetcher()
        self.features = MatchFeatureBuilder()
        self.model = MatchPredictor()

    async def predict_match(self, team1: str, team2: str):

        # --- FETCH ---
        h2h = await self.fetcher.fetch_h2h_matches(team1, team2)
        last1 = await self.fetcher.fetch_team_last_matches(team1)
        last2 = await self.fetcher.fetch_team_last_matches(team2)

        # --- DATAFRAME ---
        df = self._build_df(h2h, last1, last2)

        if df.empty:
            return None

        df = self._ensure_classes(df)

        # --- FEATURES ---
        X, y = self.features.build_features(df)

        # --- TRAIN ---
        self.model.train(X, y, team1, team2)

        # --- PREDICT ---
        sample = self.features.build_prediction_sample(df)
        prediction, probs, classes = self.model.predict(sample)

        probabilities = self._map_probabilities(team1, team2, probs, classes)

        # --- SCORE ---
        home_goals, away_goals = self._predict_score(df)

        return {
            "prediction": prediction,
            "probabilities": probabilities,
            "score_prediction": f"{home_goals}-{away_goals}"
        }

    def _build_df(self, h2h, last1, last2):
        df1 = self.features.build_base_dataframe(h2h)
        df2 = self.features.build_base_dataframe(last1)
        df3 = self.features.build_base_dataframe(last2)

        return pd.concat([df1, df2, df3], ignore_index=True)

    def _ensure_classes(self, df):
        required = ["HomeWin", "Draw", "AwayWin"]

        for r in required:
            if r not in df["result"].values:
                df = pd.concat([df, pd.DataFrame([{
                    "home_goals_scored": 1,
                    "away_goals_scored": 1,
                    "home_advantage": 1,
                    "result": r
                }])])

        return df

    def _map_probabilities(self, team1, team2, probs, classes):
        result = {team1: 0, "Draw": 0, team2: 0}

        for cls, prob in zip(classes, probs):
            if cls == "HomeWin":
                result[team1] = round(prob * 100, 1)
            elif cls == "Draw":
                result["Draw"] = round(prob * 100, 1)
            elif cls == "AwayWin":
                result[team2] = round(prob * 100, 1)

        return result

    def _predict_score(self, df):
        return round(df["home_goals_scored"].mean()), round(df["away_goals_scored"].mean())