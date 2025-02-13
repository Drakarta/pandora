import datetime
from typing import List
import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import Cog

from utils.DB import Database


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
            user = discord.Object(id=birthday[0])

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
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
            "1": 1,
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "11": 11,
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
