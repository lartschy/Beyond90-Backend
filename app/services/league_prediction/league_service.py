from app.services.league_prediction.league_fetcher import LeagueFetcher
from app.services.league_prediction.league_features import LeagueFeatureBuilder
from app.services.league_prediction.league_training import LeagueTrainingBuilder
from app.services.league_prediction.league_model import LeaguePredictor


class LeagueService:

    def __init__(self):
        self.fetcher = LeagueFetcher()
        self.feature_builder = LeagueFeatureBuilder()
        self.training_builder = LeagueTrainingBuilder()
        self.predictor = LeaguePredictor()

    async def predict_league_table(self, league_id: str):
        """
        Main pipeline:
        - fetch data
        - train model
        - predict current table
        """

        # --- 1. FETCH CURRENT SEASON ---
        current_table = await self.fetcher.fetch_current_table(league_id)

        if not current_table:
            return None

        # --- 2. FETCH PREVIOUS SEASONS ---
        seasons = ["2024-2025", "2023-2024", "2022-2023"]

        prev_tables = await self.fetcher.fetch_last_n_seasons(
            league_id,
            seasons
        )

        # --- 3. BUILD TRAINING DATA ---
        train_df = self.training_builder.build_training_data(prev_tables)

        if train_df is None or train_df.empty:
            return None

        # --- 4. TRAIN MODEL ---
        self.predictor.train(train_df)

        # --- 5. BUILD CURRENT FEATURES ---
        df_current = self.feature_builder.build_dataframe(
            current_table,
            prev_tables
        )

        # --- 6. PREDICT ---
        prediction_df = self.predictor.predict(df_current)

        if prediction_df is None:
            return None

        # --- 7. FORMAT RESPONSE ---
        result = []

        for _, row in prediction_df.iterrows():
            result.append({
                "team": row["team"],
                "predicted_points": round(row["predicted_points"], 1),
                "predicted_rank": int(row["predicted_rank"])
            })

        return {
            "league_id": league_id,
            "predicted_table": result,
            "teams": len(result)
        }