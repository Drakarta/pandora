import asyncio
import random
import discord
from discord.ext import tasks, commands
from discord.ext.commands import Cog
import datetime

from utils.DB import Database


class Activity(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = Database()
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_quotes (
                quote TEXT PRIMARY KEY
            )
            """
        )

        self.activities = [
            row[0] for row in self.db.execute("SELECT * FROM activity_quotes")
        ]

        self.change_activity.start()

    @tasks.loop(minutes=10)
    async def change_activity(self):
        random_activity = random.choice(self.activities)
        await self.bot.change_presence(
            status=discord.Status.idle,
            activity=discord.CustomActivity(name=random_activity),
        )

    @change_activity.before_loop
    async def before_clock(self):
        await self.bot.wait_until_ready()
        current_time = datetime.datetime.now()
        delay_seconds = (10 - (current_time.minute % 10)) * 60 - current_time.second
        await asyncio.sleep(delay_seconds)

    @commands.command()
    @commands.is_owner()
    async def addactivity(self, ctx):
        message = ctx.message.content.replace("!addactivity ", "")
        self.db.execute("INSERT INTO activity_quotes (quote) VALUES (?)", (message,))
        self.quotes = self.db.execute("SELECT quote FROM activity_quotes")
        await ctx.send(f"""Activity "{message}" added.""")

    @commands.command()
    @commands.is_owner()
    async def removeactivity(self, ctx):
        message = ctx.message.content.replace("!removeactivity ", "")
        self.db.execute("DELETE FROM activity_quotes WHERE quote = ?", (message,))
        self.quotes = self.db.execute("SELECT quote FROM activity_quotes")
        await ctx.send(f"""Activity "{message}" removed.""")


async def setup(bot):
    await bot.add_cog(Activity(bot))
