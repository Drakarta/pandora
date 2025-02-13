import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog

from utils.DB import Database


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot

        self.db = Database()
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS main_channel(
                guild_id INT PRIMARY KEY,
                channel_id INT DEFAULT NULL
            )
            """
        )

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync(guild=discord.Object(id=734455624036909126))
        await self.bot.tree.sync(guild=discord.Object(id=744191097554862171))
        await ctx.send("Command tree synced.")
        print("Command tree synced.")

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                cog_name = f"cogs.{filename[:-3]}"
                try:
                    await self.bot.unload_extension(cog_name)
                except commands.ExtensionNotLoaded:
                    pass
                finally:
                    await self.bot.load_extension(cog_name)
                    print(f"Reloaded {filename}")
        await ctx.send("Cogs reloaded.")

    @commands.command()
    @commands.is_owner()
    async def setmainchannel(self, ctx):
        self.db.execute(
            "INSERT OR REPLACE INTO main_channel (guild_id, channel_id) VALUES (?, ?)",
            (self.guild.id, ctx.channel.id),
        )
        await ctx.send(f"Main channel set to this channel.")

    @app_commands.command(name="ping", description="Check the bot's latency")
    @app_commands.guilds(
        discord.Object(id=734455624036909126), discord.Object(id=744191097554862171)
    )
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.response.send_message(f"pong! ({latency}ms)")


async def setup(bot):
    await bot.add_cog(Admin(bot))
