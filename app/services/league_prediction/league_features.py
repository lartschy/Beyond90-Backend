import pandas as pd


class LeagueFeatureBuilder:

    def build_dataframe(self, current_table, prev_tables):
        """
        current_table: list of teams (current season)
        prev_tables: list of lists (each = one previous season)
        """

        # Map previous seasons by team name
        prev_maps = [self._map_by_team(table) for table in prev_tables]

        rows = []

        for team in current_table:
            try:
                team_name = team.get("strTeam")

                # --- CURRENT SEASON ---
                played = int(team.get("intPlayed") or 1)

                row = {
                    "team": team_name,
                    "rank_now": int(team.get("intRank") or 0),
                    "points_now": int(team.get("intPoints") or 0),
                    "gd_now": int(team.get("intGoalDifference") or 0),
                    "ppg_now": int(team.get("intPoints") or 0) / played,
                    "gd_per_game_now": int(team.get("intGoalDifference") or 0) / played,
                }

                # --- PREVIOUS SEASONS ---
                for i, season_map in enumerate(prev_maps, start=1):
                    prev = season_map.get(team_name)

                    if prev:
                        prev_played = int(prev.get("intPlayed") or 1)

                        row.update({
                            f"rank_s{i}": int(prev.get("intRank") or 0),
                            f"points_s{i}": int(prev.get("intPoints") or 0),
                            f"gd_s{i}": int(prev.get("intGoalDifference") or 0),
                            f"ppg_s{i}": int(prev.get("intPoints") or 0) / prev_played,
                            f"gd_per_game_s{i}": int(prev.get("intGoalDifference") or 0) / prev_played,
                        })
                    else:
                        # Team not found in previous season (promoted/relegated)
                        row.update({
                            f"rank_s{i}": 20,
                            f"points_s{i}": 0,
                            f"gd_s{i}": 0,
                            f"ppg_s{i}": 0,
                            f"gd_per_game_s{i}": 0,
                        })

                rows.append(row)

            except Exception:
                continue

        return pd.DataFrame(rows)

    def _map_by_team(self, table):
        """
        Convert list → dict for fast lookup
        """
        return {
            team.get("strTeam"): team
            for team in table
        }