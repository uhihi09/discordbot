# bot.py
import discord
from discord.ext import commands
import asyncio
import os
from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f'✅ 봇 이름: {bot.user}')
    await load_extensions()

if __name__ == "__main__":
    asyncio.run(bot.run(TOKEN))