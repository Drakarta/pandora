import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Cog


class Admin(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = discord.Object(id=734455624036909126)

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync(guild=self.guild)
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

    @app_commands.command(name="ping", description="Check the bot's latency")
    @app_commands.guilds(discord.Object(id=734455624036909126))
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        await ctx.response.send_message(f"pong! ({latency}ms)")


async def setup(bot):
    await bot.add_cog(Admin(bot))
