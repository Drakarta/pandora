import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog
import random

from utils.impersonate_webhook import ImpersonateWebhook
from utils.config import Config
from utils.DB import Database


class Yoeri(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.config = Config().get_section("yoeri")

        self.allowed_guild_id = self.config.guild_id
        self.yoeri_id = self.config.user_id

        self.db = Database()
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS yoeri_quotes (
                quote TEXT PRIMARY KEY
            )
            """
        )
        self.quotes = [row[0] for row in self.db.execute("SELECT * FROM yoeri_quotes")]

    @Cog.listener("on_message")
    async def yoeri(self, message):
        if message.author.bot:
            return

        if message.guild.id != self.allowed_guild_id:
            return

        if message.author.id == self.yoeri_id:
            return

        if random.random() < 0.02 and self.quotes:
            random_quote = random.choice(self.quotes)
            webhook = ImpersonateWebhook(self.bot, message.channel.id, "yoeri-hook")
            await webhook.impersonate_message(self.yoeri_id, random_quote)

    @app_commands.command(
        name="yoeri", description="Add a quote to the Yoeri impersonation."
    )
    @app_commands.describe(quote="The quote to add.")
    @app_commands.guilds(
        discord.Object(id=734455624036909126), discord.Object(id=744191097554862171)
    )
    async def add_quote(self, ctx, quote: str):
        try:
            self.db.execute("INSERT INTO yoeri_quotes (quote) VALUES (?)", (quote,))
            self.quotes.append(quote)
            await ctx.response.send_message(f'Quote "{quote}" added.')
        except Exception as e:
            await ctx.response.send_message("This quote already exists.")

    @commands.command()
    @commands.is_owner()
    async def removequote(self, ctx):
        message = ctx.message.content.replace("!removequote ", "")
        self.db.execute("DELETE FROM yoeri_quotes WHERE quote = ?", (message,))
        self.quotes = self.db.execute("SELECT quote FROM yoeri_quotes")
        await ctx.send(f"""Quote "{message}" removed.""")


async def setup(bot):
    await bot.add_cog(Yoeri(bot))
