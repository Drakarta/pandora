import asyncio
import discord
from discord.ext import tasks
from discord.ext.commands import Cog
import datetime
import pytz

from utils.config import Config


class Streaming(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.config2 = Config().get_section("main")


async def setup(bot):
    await bot.add_cog(Streaming(bot), guilds=[discord.Object(id=734455624036909126)])
