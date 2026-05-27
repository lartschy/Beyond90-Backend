import pandas as pd


class LeagueTrainingBuilder:

    def build_training_data(self, season_tables):
        """
        season_tables: list of tables (each = one full season)

        Returns:
            DataFrame with features + target_points
        """

        rows = []

        for table in season_tables:
            for team in table:
                try:
                    played = int(team.get("intPlayed") or 38)
                    total_points = int(team.get("intPoints") or 0)
                    gd = int(team.get("intGoalDifference") or 0)

                    # --- SIMULATE MID-SEASON ---
                    # assume current stats ≈ proportional to games played
                    mid_played = max(played // 2, 1)

                    ppg = total_points / played
                    gd_per_game = gd / played

                    mid_points = ppg * mid_played
                    mid_gd = gd_per_game * mid_played

                    row = {
                        # --- FEATURES (like current season) ---
                        "ppg_now": mid_points / mid_played,
                        "gd_per_game_now": mid_gd / mid_played,

                        # --- TARGET ---
                        "target_points": total_points
                    }

                    rows.append(row)

                except Exception as e:
                    print(f"Error building training row: {e}")
                    continue

        return pd.DataFrame(rows)