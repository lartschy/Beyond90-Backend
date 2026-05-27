from .dataset_builder import DatasetBuilder
from .team_stats import TeamStats
from .model import MatchModel
from .score import predict_score


class MatchService:

    def __init__(self):
        self.builder = DatasetBuilder()
        self.stats_builder = TeamStats()
        self.model = MatchModel()

        self.stats = None

    # TRAIN MODEL
    async def prepare(self):
        print("Fetching season data...")

        events = await self.builder.fetch_season("4328", "2024-2025")
        df = self.builder.build_team_rows(events)

        print(f"📊 Matches loaded: {len(df)}")

        self.stats = self.stats_builder.compute(df)

        print("🧠 Training model...")
        self.model.train(df, self.stats)

        print("✅ Model ready!")

    # PREDICT MATCH
    def predict_match(self, team1, team2):

        # SAFETY CHECK
        if self.stats is None:
            return {"error": "Model not trained. Call /train first."}

        # ML prediction
        pred, probs, classes = self.model.predict(team1, team2, self.stats)

        # NORMALIZE PROBABILITIES (VERY IMPORTANT)
        home_prob = 0
        draw_prob = 0
        away_prob = 0

        for c, p in zip(classes, probs):
            if c == "Win":
                home_prob = p
            elif c == "Draw":
                draw_prob = p
            else:
                away_prob = p

        # 🧠 APPLY FOOTBALL REALISM CORRECTION

        # minimum draw chance
        draw_prob = max(draw_prob, 0.18)

        # underdog boost
        away_prob = max(away_prob, 0.15)

        # reduce overconfidence
        home_prob = min(home_prob, 0.7)

        # normalize back to 1
        total = home_prob + draw_prob + away_prob

        home_prob /= total
        draw_prob /= total
        away_prob /= total

        # ⚽ score prediction
        home_goals, away_goals = predict_score(self.stats, team1, team2)

        # 🔥 FORCE CONSISTENCY BETWEEN PROBABILITY & SCORE
        if pred == "Win" and home_goals <= away_goals:
            home_goals = away_goals + 1

        elif pred == "Loss" and away_goals <= home_goals:
            away_goals = home_goals + 1

        elif pred == "Draw":
            home_goals = away_goals

        # HUMAN-READABLE PREDICTION
        prediction_label = (
            team1 if pred == "Win"
            else team2 if pred == "Loss"
            else "Draw"
        )

        # MAP PROBABILITIES
        result = {
            team1: round(home_prob * 100, 1),
            "Draw": round(draw_prob * 100, 1),
            team2: round(away_prob * 100, 1)
        }

        # FINAL RESPONSE
        return {
            "prediction": prediction_label,
            "probabilities": result,
            "score": f"{home_goals}-{away_goals}"
        }