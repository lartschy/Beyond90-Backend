import os
import joblib
from sklearn.ensemble import RandomForestClassifier


class MatchPredictor:

    def __init__(self, model_dir="app/models"):
        self.model_dir = model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        self.model = None

    def train(self, X, y, team1: str, team2: str):
        if len(X) < 3:
            return None

        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

        self.model.fit(X, y)

        model_name = f"h2h_{team1.lower()}_{team2.lower()}.pkl"
        path = os.path.join(self.model_dir, model_name)

        joblib.dump(self.model, path)

        return self.model

    def predict(self, sample):
        if self.model is None:
            return None

        prediction = self.model.predict(sample)[0]
        probabilities = self.model.predict_proba(sample)[0]

        return prediction, probabilities, self.model.classes_