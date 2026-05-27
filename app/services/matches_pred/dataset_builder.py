import httpx
import pandas as pd


class DatasetBuilder:

    BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"

    async def fetch_season(self, league_id: str, season: str):
        url = f"{self.BASE_URL}/eventsseason.php"

        async with httpx.AsyncClient() as client:
            r = await client.get(url, params={"id": league_id, "s": season})

        return r.json().get("events") or []

    def build_team_rows(self, events):
        rows = []

        for e in events:
            try:
                hs = int(e.get("intHomeScore") or 0)
                as_ = int(e.get("intAwayScore") or 0)

                if e.get("intHomeScore") is None:
                    continue  # skip unplayed matches

                # HOME PERSPECTIVE
                rows.append({
                    "team": e["strHomeTeam"],
                    "opponent": e["strAwayTeam"],
                    "goals_scored": hs,
                    "goals_conceded": as_,
                    "home": 1,
                    "result": "Win" if hs > as_ else "Draw" if hs == as_ else "Loss"
                })

                # AWAY PERSPECTIVE
                rows.append({
                    "team": e["strAwayTeam"],
                    "opponent": e["strHomeTeam"],
                    "goals_scored": as_,
                    "goals_conceded": hs,
                    "home": 0,
                    "result": "Win" if as_ > hs else "Draw" if as_ == hs else "Loss"
                })

            except:
                continue

        return pd.DataFrame(rows)