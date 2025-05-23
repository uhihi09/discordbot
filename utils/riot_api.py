# utils/riot_api.py
import aiohttp
from config import RIOT_API_KEY

BASE_URL = "https://kr.api.riotgames.com/lol"
SPECTATOR_URL = "https://kr.api.riotgames.com/lol/spectator/v4"
MATCH_URL = "https://kr.api.riotgames.com/lol/match/v5" # 아시아 서버 매치 V5

async def get_summoner_info(session, summoner_name):
    url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    print("📡 요청 URL:", url)
    print("🔑 헤더:", headers)
    async with session.get(url, headers=headers) as response:
        print("📬 응답 상태 코드:", response.status)
        if response.status != 200:
            raise Exception(f"라이엇 API 오류: {response.status}")
        return await response.json()

async def get_league_entries(session, summoner_id):
    url = f"{BASE_URL}/league/v4/entries/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            raise Exception(f"라이엇 API 오류: {response.status}")

async def get_current_game_info(session, summoner_id):
    url = f"{SPECTATOR_URL}/active-games/by-summoner/{summoner_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        elif response.status == 404:
            return None
        else:
            raise Exception(f"라이엇 API 오류: {response.status}")

async def get_match_ids_by_puuid(session, puuid, count=20): # 최근 경기 ID 목록
    url = f"{MATCH_URL}/matches/by-puuid/{puuid}/ids?count={count}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            raise Exception(f"라이엇 API 오류: {response.status}")

async def get_match_detail(session, match_id):
    url = f"{MATCH_URL}/matches/{match_id}"
    headers = {"X-Riot-Token": RIOT_API_KEY}
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            raise Exception(f"라이엇 API 오류: {response.status}")