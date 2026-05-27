import httpx
from app.core.config import BASE_URL


class MatchFetcher:

    async def fetch_h2h_matches(self, team1: str, team2: str):
        seasons = ["2024-2023", "2023-2022", "2022-2021"]
        matches = []

        async with httpx.AsyncClient() as client:
            for season in seasons:
                for variant in [f"{team1}_vs_{team2}", f"{team2}_vs_{team1}"]:
                    url = f"{BASE_URL}/searchevents.php"
                    params = {"e": variant, "s": season}
                    response = await client.get(url, params=params)
                    data = response.json().get("event") or []
                    matches.extend(data)

        return matches

    async def fetch_team_last_matches(self, team_name: str):
        async with httpx.AsyncClient() as client:
            # --- get team id ---
            search_url = f"{BASE_URL}/searchteams.php"
            team_resp = await client.get(search_url, params={"t": team_name})
            team_data = team_resp.json().get("teams", [])

            if not team_data:
                return []

            team_id = team_data[0]["idTeam"]

            # --- fetch LAST 15 matches instead of 1 ---
            url = f"{BASE_URL}/eventslast.php"
            params = {"id": team_id}

            response = await client.get(url, params=params)
            matches = response.json().get("results", [])

            return matches[:10]  # ✅ take up to 10