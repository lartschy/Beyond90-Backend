import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("THESPORTSDB_KEY", "3")  # 3 is the demo key
BASE_URL = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}"
