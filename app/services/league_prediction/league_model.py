import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


class LeaguePredictor:

    def __init__(self, model_dir="app/models"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.model = None

    def train(self, df: pd.DataFrame):
        """
        Train model on historical data
        """

        if df is None or df.empty:
            return None

        # --- FEATURES ---
        feature_cols = [
            "ppg_now", "gd_per_game_now",
            "ppg_s1", "gd_per_game_s1",
            "ppg_s2", "gd_per_game_s2",
            "ppg_s3", "gd_per_game_s3"
        ]

        # Make sure all exist
        feature_cols = [col for col in feature_cols if col in df.columns]

        X = df[feature_cols]

        # --- TARGET ---
        if "target_points" not in df.columns:
            raise ValueError("Missing target_points column for training")

        y = df["target_points"]

        # --- MODEL ---
        self.model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )

        self.model.fit(X, y)

        # Save model
        path = os.path.join(self.model_dir, "league_model.pkl")
        joblib.dump(self.model, path)

        return self.model

    def load_model(self):
        """
        Load existing model
        """
        path = os.path.join(self.model_dir, "league_model.pkl")

        if os.path.exists(path):
            self.model = joblib.load(path)

        return self.model

    def predict(self, df: pd.DataFrame):
        """
        Predict final points and return sorted table
        """

        if self.model is None:
            return None

        feature_cols = [
            "ppg_now",
            "gd_per_game_now"
        ]

        feature_cols = [col for col in feature_cols if col in df.columns]

        X = df[feature_cols]

        predictions = self.model.predict(X)

        # Add predictions to DataFrame
        df_result = df.copy()
        df_result["predicted_points"] = predictions

        # Sort descending (highest points first)
        df_result = df_result.sort_values(
            by="predicted_points",
            ascending=False
        )

        # Add predicted rank
        df_result["predicted_rank"] = range(1, len(df_result) + 1)

        return df_result[[
            "team",
            "predicted_points",
            "predicted_rank"
        ]]