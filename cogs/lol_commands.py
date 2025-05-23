import discord
from discord.ext import commands
import aiohttp
from utils.riot_api import (
    get_summoner_info,
    get_league_entries,
    get_current_game_info,
    get_match_ids_by_puuid,
    get_match_detail
)

class LolCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 전적(self, ctx, *, summoner_name):
        try:
            async with aiohttp.ClientSession() as session:
                summoner = await get_summoner_info(session, summoner_name)
                if not summoner:
                    await ctx.send("❌ 소환사를 찾을 수 없습니다.")
                    return

                summoner_id = summoner['id']
                puuid = summoner['puuid']
                level = summoner['summonerLevel']

                league_entries = await get_league_entries(session, summoner_id)
                ranked_info = {}
                for entry in league_entries:
                    queue_type = entry['queueType']
                    tier = entry['tier']
                    rank = entry['rank']
                    lp = entry['leaguePoints']
                    wins = entry['wins']
                    losses = entry['losses']
                    win_rate = wins / (wins + losses) * 100
                    ranked_info[queue_type] = f"{tier} {rank} {lp}LP ({wins}승 {losses}패, {win_rate:.2f}%)"

                embed = discord.Embed(title=f"소환사 {summoner_name} 전적", color=discord.Color.blue())
                embed.add_field(name="레벨", value=level, inline=False)
                if 'RANKED_SOLO_5x5' in ranked_info:
                    embed.add_field(name="솔로 랭크", value=ranked_info['RANKED_SOLO_5x5'], inline=False)
                if 'RANKED_FLEX_SR' in ranked_info:
                    embed.add_field(name="자유 랭크", value=ranked_info['RANKED_FLEX_SR'], inline=False)

                await ctx.send(embed=embed)

                # 최근 경기
                match_ids = await get_match_ids_by_puuid(session, puuid, count=5)
                if match_ids:
                    recent_matches = "최근 5경기 결과:\n"
                    for match_id in match_ids:
                        match_detail = await get_match_detail(session, match_id)
                        if match_detail:
                            game_duration = match_detail['info']['gameDuration'] / 60
                            for participant in match_detail['info']['participants']:
                                if participant['puuid'] == puuid:
                                    stats = participant
                                    break
                            else:
                                continue

                            win = stats['win']
                            champion_name = stats['championName']
                            kills = stats['kills']
                            deaths = stats['deaths']
                            assists = stats['assists']
                            kda = f"{kills}/{deaths}/{assists}"
                            result = "승리" if win else "패배"
                            recent_matches += f"- {champion_name} ({kda}) - {result} ({game_duration:.1f}분)\n"
                    await ctx.send(recent_matches)
                else:
                    await ctx.send("최근 경기 기록이 없습니다.")
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                await ctx.send("❌ Riot API 접근이 거부됐습니다. 유명한 소환사는 개발자 키로 조회할 수 없습니다.")
            elif "404" in error_msg:
                await ctx.send("❌ 소환사를 찾을 수 없습니다. 정확한 이름인지 확인하세요.")
            elif "429" in error_msg:
                await ctx.send("🚫 요청이 너무 많아요! 잠시 후 다시 시도해 주세요. (Rate Limit 초과)")
            else:
                await ctx.send(f"⚠️ 알 수 없는 오류 발생: `{error_msg}`")

    @commands.command()
    async def 게임중(self, ctx, *, summoner_name):
        try:
            async with aiohttp.ClientSession() as session:
                summoner = await get_summoner_info(session, summoner_name)
                if not summoner:
                    await ctx.send("❌ 소환사를 찾을 수 없습니다.")
                    return

                summoner_id = summoner['id']
                current_game = await get_current_game_info(session, summoner_id)
                if current_game:
                    embed = discord.Embed(title=f"{summoner_name}님 현재 게임 정보", color=discord.Color.green())
                    for participant in current_game['participants']:
                        champion_name = participant['championName']
                        summoner_name_in_game = participant['summonerName']
                        team_id = participant['teamId']
                        embed.add_field(name=f"팀 {team_id}", value=f"{summoner_name_in_game} ({champion_name})", inline=True)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"{summoner_name}님은 현재 게임을 하고 있지 않습니다.")
        except Exception as e:
            error_msg = str(e)
            if "403" in error_msg:
                await ctx.send("❌ Riot API 접근이 거부됐습니다. 이 계정은 접근할 수 없습니다.")
            else:
                await ctx.send(f"⚠️ 오류 발생: `{error_msg}`")

async def setup(bot):
    await bot.add_cog(LolCommands(bot))
