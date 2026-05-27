import joblib
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier


class MatchModel:

    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            random_state=42
        )

    def train(self, df, stats):

        X, y = [], []

        for _, row in df.iterrows():
            team = row["team"]
            opp = row["opponent"]

            if team not in stats or opp not in stats:
                continue

            t = stats[team]
            o = stats[opp]

            attack_diff = t["attack"] - o["attack"]
            defense_diff = o["defense"] - t["defense"]

            X.append([
                attack_diff,
                defense_diff,
                t["goal_diff"] - o["goal_diff"],
                row["home"]
            ])

            y.append(row["result"])

        self.model.fit(X, y)

    def predict(self, team1, team2, stats):

        t1 = stats[team1]
        t2 = stats[team2]

        attack_diff = t1["attack"] - t2["attack"]
        defense_diff = t2["defense"] - t1["defense"]

        X = [[
            attack_diff,
            defense_diff,
            1
        ]]

        pred = self.model.predict(X)[0]
        probs = self.model.predict_proba(X)[0]

        probs = np.array(probs)
        probs = (probs + 0.05) / (probs + 0.05).sum()

        return pred, probs, self.model.classes_