import pandas as pd


class TeamStats:

    def compute(self, df: pd.DataFrame):

        stats = {}

        for team in df["team"].unique():
            tdf = df[df["team"] == team]

            attack = tdf["goals_scored"].mean()
            defense = tdf["goals_conceded"].mean()

            # NEW: goal difference (VERY IMPORTANT)
            goal_diff = attack - defense

            # (opcionális, de ajánlott) smoothing
            attack = (attack + 0.8) / 2
            defense = (defense + 0.8) / 2

            stats[team] = {
                "attack": attack,
                "defense": defense,
                "goal_diff": goal_diff,

                "home_win_rate": len(
                    tdf[(tdf["home"] == 1) & (tdf["result"] == "Win")]
                ) / max(len(tdf[tdf["home"] == 1]), 1),

                "away_win_rate": len(
                    tdf[(tdf["home"] == 0) & (tdf["result"] == "Win")]
                ) / max(len(tdf[tdf["home"] == 0]), 1),
            }

        return stats