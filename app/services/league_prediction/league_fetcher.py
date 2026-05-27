import httpx
from app.core.config import BASE_URL


class LeagueFetcher:

    async def fetch_current_table(self, league_id: str):
        """
        Fetch current season table
        """
        url = f"{BASE_URL}/lookuptable.php"
        params = {"l": league_id}

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            return data.get("table", [])


    async def fetch_table_by_season(self, league_id: str, season: str):
        """
        Fetch table for a specific season (e.g. "2020-2021")
        """
        url = f"{BASE_URL}/lookuptable.php"
        params = {
            "l": league_id,
            "s": season
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()

            return data.get("table", [])


    async def fetch_last_n_seasons(self, league_id: str, seasons: list[str]):
        """
        Fetch multiple previous seasons
        """
        results = []

        async with httpx.AsyncClient() as client:
            for season in seasons:
                url = f"{BASE_URL}/lookuptable.php"
                params = {"l": league_id, "s": season}

                response = await client.get(url, params=params)
                data = response.json().get("table", [])

                print(f"Fetched {len(data)} teams for season {season}")

                results.append(data)

        return results