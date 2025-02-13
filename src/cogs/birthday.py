import asyncio
import datetime
from typing import List
import discord
from discord import app_commands
from discord.ext import tasks
from discord.ext.commands import Cog

from utils.DB import Database
from utils.wait import Wait


class Birthday(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = Database()
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS birthday(
                user_id INT PRIMARY KEY, 
                birthday TEXT DEFAULT NULL,
                server_id INT DEFAULT NULL
            )
            """
        )

        self.check_birthday.start()

    @tasks.loop(hours=24)
    async def check_birthday(self):
        today = datetime.datetime.now().strftime("%m-%d")

        birthdays = self.db.execute(
            "SELECT * FROM birthday WHERE birthday = ?", (today,)
        )
        for birthday in birthdays:
            user_id, _, guild_id = birthday

            if discord.Object(id=guild_id).fetch_member(user_id) == discord.NotFound:
                self.db.execute("DELETE FROM birthday WHERE user_id = ?", (user_id,))
                continue

            result = self.db.execute(
                "SELECT channel_id FROM main_channel WHERE guild_id = ?", (guild_id,)
            )
            channel_id = result[0][0]
            channel = self.bot.get_channel(channel_id)

            if channel:
                await channel.send(f"# 🎉 Happy Birthday <@{user_id}>! 🎂")

    @check_birthday.before_loop
    async def before_clock(self):
        await self.bot.wait_until_ready()
        await Wait.wait_until_time(0, 0)

    @app_commands.command(name="birthday", description="Set your birthday")
    @app_commands.describe(
        month="The month of your birthday.",
        day="The day of your birthday.",
    )
    @app_commands.guilds(
        discord.Object(id=734455624036909126), discord.Object(id=744191097554862171)
    )
    async def set_birthday(
        self,
        ctx,
        month: str,
        day: app_commands.Range[int, 1, 31],
    ):
        months = {
            "january": 1,
            "jan": 1,
            "1": 1,
            "febuary": 2,
            "feb": 2,
            "2": 2,
            "march": 3,
            "mar": 3,
            "3": 3,
            "april": 4,
            "apr": 4,
            "4": 4,
            "may": 5,
            "5": 5,
            "june": 6,
            "jun": 6,
            "6": 6,
            "july": 7,
            "jul": 7,
            "7": 7,
            "august": 8,
            "aug": 8,
            "8": 8,
            "september": 9,
            "sep": 9,
            "9": 9,
            "october": 10,
            "oct": 10,
            "10": 10,
            "november": 11,
            "nov": 11,
            "11": 11,
            "december": 12,
            "dec": 12,
            "12": 12,
        }
        month = month.lower()
        month = months.get(month, -1)
        if not (1 <= int(month) <= 12):
            await ctx.response.send_message(
                "Invalid month. Please enter a valid month name.", ephemeral=True
            )
            return
        birthday = f"{int(month):02d}-{day:02d}"
        self.db.execute(
            "INSERT OR REPLACE INTO birthday (user_id, birthday, server_id) VALUES (?, ?, ?)",
            (ctx.user.id, birthday, ctx.guild.id),
        )
        await ctx.response.send_message("Birthday set.", ephemeral=True)

    @set_birthday.autocomplete("month")
    async def month_autocomplete(
        self, ctx, current: str
    ) -> List[app_commands.Choice[str]]:
        months = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]
        return [
            app_commands.Choice(name=month, value=month)
            for month in months
            if current.lower() in month.lower()
        ]

    @app_commands.command(name="removebirthday", description="Remove your birthday")
    @app_commands.guilds(
        discord.Object(id=734455624036909126), discord.Object(id=744191097554862171)
    )
    async def remove_birthday(self, ctx):
        self.db.execute("DELETE FROM birthday WHERE user_id = ?", (ctx.user.id,))
        await ctx.response.send_message("Birthday removed.")


async def setup(bot):
    await bot.add_cog(Birthday(bot))
