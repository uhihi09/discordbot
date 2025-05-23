# cogs/match_analysis.py
import discord
from discord.ext import commands
import sqlite3
import asyncio
import aiohttp  # 이 줄이 이미 있는지 확인합니다. 없다면 추가합니다.
from utils.riot_api import get_match_detail, get_summoner_info

DATABASE_PATH = "data/match_history.db"

def create_tables():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            match_id TEXT PRIMARY KEY,
            timestamp INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS participants (
            match_id TEXT,
            puuid TEXT,
            summoner_name TEXT,
            team_id INTEGER,
            champion_name TEXT,
            kills INTEGER,
            deaths INTEGER,
            assists INTEGER,
            damage_dealt INTEGER,
            win INTEGER,
            FOREIGN KEY (match_id) REFERENCES matches(match_id)
        )
    """)
    conn.commit()
    conn.close()

class MatchAnalysis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        create_tables()

    @commands.command()
    async def 내전기록저장(self, ctx, match_id):
        async with aiohttp.ClientSession() as session:
            try:
                match_detail = await get_match_detail(session, match_id)
                if not match_detail:
                    await ctx.send(f"❌ 매치 ID '{match_id}'에 대한 정보를 찾을 수 없습니다.")
                    return

                timestamp = match_detail['info']['gameCreation']
                conn = sqlite3.connect(DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute("INSERT OR IGNORE INTO matches VALUES (?, ?)", (match_id, timestamp))

                for participant in match_detail['info']['participants']:
                    cursor.execute("""
                        INSERT INTO participants (match_id, puuid, summoner_name, team_id, champion_name, kills, deaths, assists, damage_dealt, win)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (match_id, participant['puuid'], participant['summonerName'], participant['teamId'],
                          participant['championName'], participant['kills'], participant['deaths'], participant['assists'],
                          participant['totalDamageDealtToChampions'], participant['win']))

                conn.commit()
                conn.close()
                await ctx.send(f"✅ 매치 ID '{match_id}' 기록을 저장했습니다.")

            except Exception as e:
                await ctx.send(f"❌ 매치 기록 저장 중 오류 발생: {e}")

    @commands.command()
    async def 내전통계(self, ctx):
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT summoner_name, COUNT(*) as games, SUM(win) as wins, (CAST(SUM(win) AS REAL) / COUNT(*)) * 100 as win_rate
            FROM participants
            GROUP BY summoner_name
            ORDER BY win_rate DESC
        """)
        results = cursor.fetchall()
        conn.close()

        if results:
            embed = discord.Embed(title="내전 통계", color=discord.Color.gold())
            for row in results:
                summoner_name, games, wins, win_rate = row
                embed.add_field(name=summoner_name, value=f"{games}전 {wins}승 ({win_rate:.2f}%)", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ 저장된 내전 기록이 없습니다.")

    # 추가적인 통계 명령어 (예: 개인별 KDA, 모스트 챔피언 등) 구현 가능

async def setup(bot):
    await bot.add_cog(MatchAnalysis(bot))